from __future__ import annotations

import asyncio

import snapcast.control
from typing import TYPE_CHECKING
from contextlib import suppress

from ffmpeg.asyncio import FFmpeg
from ffmpeg import Progress
import time

from music_assistant.common.models.config_entries import (
    CONF_ENTRY_OUTPUT_CODEC,
    ConfigEntry,
    ConfigValueType,
)
from music_assistant.common.models.enums import PlayerFeature, PlayerType, PlayerState
from music_assistant.common.models.errors import SetupFailedError

from music_assistant.constants import CONF_LOG_LEVEL, CONF_PLAYERS
from music_assistant.server.models.player_provider import PlayerProvider
from music_assistant.common.models.player import DeviceInfo, Player
from music_assistant.common.models.queue_item import QueueItem


if TYPE_CHECKING:
    from music_assistant.common.models.config_entries import PlayerConfig, ProviderConfig
    from music_assistant.common.models.provider import ProviderManifest
    from music_assistant.server import MusicAssistant
    from music_assistant.server.models import ProviderInstanceType
    from music_assistant.server.controllers.streams import MultiClientStreamJob

SNAPCAST_SERVER_HOST = "127.0.0.1"
SNAPCAST_SERVER_CONTROL_PORT = 1705


async def setup(
    mass: MusicAssistant, manifest: ProviderManifest, config: ProviderConfig
) -> ProviderInstanceType:
    """Initialize provider(instance) with given configuration."""
    prov = SnapCastProvider(mass, manifest, config)
    await prov.handle_setup()
    return prov


async def get_config_entries(
    mass: MusicAssistant,
    instance_id: str | None = None,
    action: str | None = None,
    values: dict[str, ConfigValueType] | None = None,
) -> tuple[ConfigEntry, ...]:
    """
    Return Config entries to setup this provider.

    instance_id: id of an existing provider instance (None if new instance setup).
    action: [optional] action key called from config entries UI.
    values: the (intermediate) raw values for config entries sent with the action.
    """
    # ruff: noqa: ARG001
    return tuple()  # we do not have any config entries (yet)


class SnapCastProvider(PlayerProvider):
    """Player provider for Snapcast based players"""

    _snapserver: [asyncio.Server | asyncio.BaseTransport]

    async def handle_setup(self) -> None:
        try:
            self._snapserver = await snapcast.control.create_server(
                self.mass.loop,
                SNAPCAST_SERVER_HOST,
                port=SNAPCAST_SERVER_CONTROL_PORT,
                reconnect=True,
            )
            self._snapserver.set_on_update_callback(self._handle_update)
            self._handle_update()
            self.logger.info(
                f"Started Snapserver connection {SNAPCAST_SERVER_HOST}:{SNAPCAST_SERVER_CONTROL_PORT}"
            )
        except OSError:
            raise SetupFailedError(f"Unable to start the Snapserver connection ?")

    def _handle_update(self):
        for client in self._snapserver.clients:
            self._handle_player_update(client)
            client.set_callback(self._handle_player_update)

    def _handle_player_update(self, client):
        player_id = client.identifier
        player = self.mass.players.get(player_id, raise_unavailable=False)
        if not player:
            player = Player(
                player_id=player_id,
                provider=self.domain,
                type=PlayerType.PLAYER,
                name=client.friendly_name,
                available=True,
                powered=client.connected,
                device_info=DeviceInfo(),
                supported_features=(
                    PlayerFeature.SYNC,
                    PlayerFeature.VOLUME_SET,
                    PlayerFeature.VOLUME_MUTE,
                ),
            )
        self.mass.players.register_or_update(player)
        # update player state on player events
        player.name = client.friendly_name
        player.volume_level = client.volume
        player.volume_muted = client.muted
        player.available = client.connected
        player.can_sync_with = tuple(
            x.identifier for x in self._snapserver.clients if x.identifier != player_id
        )
        player.synced_to = self._synced_to(player_id)
        self.mass.players.register_or_update(player)

    async def unload(self) -> None:
        self._snapserver.stop()

    async def cmd_volume_set(self, player_id: str, volume_level: int) -> None:
        self.mass.create_task(
            self._snapserver.client_volume(player_id, {"percent": volume_level, "muted": False})
        )

    async def cmd_play_url(
        self,
        player_id: str,
        url: str,
        queue_item: QueueItem | None,
    ) -> None:
        stream = self._get_client_stream(player_id)
        player = self.mass.players.get(player_id, raise_unavailable=False)
        if hasattr(stream, "ffmpeg"):
            try:
                print("Cancel Stream")
                stream.ffmpeg.terminate()
            except:
                pass

        ffmpeg = (
            FFmpeg()
            .option("y")
            .input(url)
            .output(f"{stream.path}", f="s16le", acodec="pcm_s16le", ac=2, ar=48000)
        )
        self.mass.create_task(ffmpeg.execute())

        @ffmpeg.on("start")
        def on_start(arguments: list[str]):
            print("start Stream")
            stream.ffmpeg = ffmpeg
            player.state = PlayerState.PLAYING
            player.current_url = url
            player.elapsed_time_last_updated = time.time()
            self.mass.players.register_or_update(player)

        @ffmpeg.on("progress")
        def on_progress(progress: Progress):
            player.state = PlayerState.PLAYING
            player.current_url = url
            self.mass.players.register_or_update(player)

        @ffmpeg.on("completed")
        def on_completed():
            player.current_url = ""
            player.state = PlayerState.IDLE
            self.mass.players.register_or_update(player)

        @ffmpeg.on("terminated")
        def on_terminated():
            player.current_url = ""
            player.state = PlayerState.IDLE
            self.mass.players.register_or_update(player)

    async def cmd_pause(self, player_id: str) -> None:
        try:
            print("Cancel Stream")
            self._get_client_stream(player_id).ffmpeg.terminate()
            player = self.mass.players.get(player_id, raise_unavailable=False)
            player.state = PlayerState.PAUSED
            self.mass.players.register_or_update(player)
        except:
            pass

    async def cmd_volume_mute(self, player_id, muted):
        self.mass.create_task(self._snapserver.client(player_id).set_muted(muted))

    async def _remove_stream(self, stream_id):
        self.mass.create_task(self._server.stream_remove_stream(stream_id))

    def _snapclient_get_group_clients_identifiers(self, identifier):
        group = self._get_client_group(player_id)
        return [ele for ele in group.clients if ele != identifier]

    async def cmd_sync(self, player_id: str, target_player: str) -> None:
        child_player = self.mass.players.get(player_id)
        assert child_player  # guard
        parent_player = self.mass.players.get(target_player)
        assert parent_player  # guard
        # always make sure that the parent player is part of the sync group
        parent_player.group_childs.add(parent_player.player_id)
        parent_player.group_childs.add(child_player.player_id)
        child_player.synced_to = parent_player.player_id

        group = self._get_client_group(target_player)
        self.mass.create_task(group.add_client(player_id))

        self.mass.players.update(child_player.player_id)
        self.mass.players.update(parent_player.player_id)

    async def cmd_unsync(self, player_id: str) -> None:
        group = self._get_client_group(player_id)
        await group.remove_client(player_id)
        group = self._get_client_group(player_id)
        stream = await self._snapserver.stream_add_stream(
            f"pipe:///tmp/music-assistant/{group.identifier}?name={group.identifier}"
        )
        await group.set_stream(stream.get("id"))

    def _get_client_group(self, player_id):
        client = self._snapserver.client(player_id)
        return client.group

    def _get_client_stream(self, player_id):
        group = self._get_client_group(player_id)
        return self._snapserver.stream(group.stream)

    def _synced_to(self, player_id):
        ret = None
        group = self._get_client_group(player_id)
        clients = list(filter(lambda x: x != player_id, group.clients))
        if player_id == group.clients[0]:  # Is player is Sync group
            player = self.mass.players.get(player_id)
            player.group_childs.clear()
            for client in clients:
                player.group_childs.add(client)
        else:
            if len(clients) > 0:
                ret = clients[0]
        return ret
