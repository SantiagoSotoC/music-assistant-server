# Changelog

## 2.4.0 (2024-10-28)


### Features

* Radio mode enhancements ([#1654](https://github.com/SantiagoSotoC/music-assistant-server/issues/1654)) ([a0abddc](https://github.com/SantiagoSotoC/music-assistant-server/commit/a0abddc6a60f409e14dc5fa317a3522be14a8ec3))


### Bug Fixes

* 🐛 explicitly add dist to build context, ls contents ([#1648](https://github.com/SantiagoSotoC/music-assistant-server/issues/1648)) ([afc29d9](https://github.com/SantiagoSotoC/music-assistant-server/commit/afc29d93b6632857d60b0cbeaa9ece49b2905199))
* 🐛 Hopefully fix release ([#1644](https://github.com/SantiagoSotoC/music-assistant-server/issues/1644)) ([5e1ca3c](https://github.com/SantiagoSotoC/music-assistant-server/commit/5e1ca3cc21c2413f5ae5d0f83f0fcd7f1c05b577))
* 🐛 move download to after checkout, fix conditionals ([#1645](https://github.com/SantiagoSotoC/music-assistant-server/issues/1645)) ([930f2d7](https://github.com/SantiagoSotoC/music-assistant-server/commit/930f2d799e001259b63be29a4ebaf0fc10f09a46))
* account for playlists with less than 50 images/items ([02a5dfc](https://github.com/SantiagoSotoC/music-assistant-server/commit/02a5dfce0b52599d998f77c77fb0bbd6dd9476b1))
* album directory parsing with album versions ([#1683](https://github.com/SantiagoSotoC/music-assistant-server/issues/1683)) ([ec554ec](https://github.com/SantiagoSotoC/music-assistant-server/commit/ec554ecf127b9df47ee875a1fde61b6a29ff577d))
* Disable shuffle for radio mode ([#1673](https://github.com/SantiagoSotoC/music-assistant-server/issues/1673)) ([191200b](https://github.com/SantiagoSotoC/music-assistant-server/commit/191200bd0e141217da397f25248d86f5e35f06c0))
* Do not retry Snapcast connection if we want to exit ([6ad7503](https://github.com/SantiagoSotoC/music-assistant-server/commit/6ad750347962d73a281a2cef4f88f95627aab32f))
* don't enqueue next if flow mode is enabled ([12e2ccc](https://github.com/SantiagoSotoC/music-assistant-server/commit/12e2ccc81eb05644230218d67107cf64b747d1a9))
* Enqueue player feature not correctly set on cast groups and dlna players ([f9a855d](https://github.com/SantiagoSotoC/music-assistant-server/commit/f9a855de1f846de5c582c346d0cfbaa8394ba1e8))
* ensure Spotify token is fresh when retrieving streamdetails ([48a6983](https://github.com/SantiagoSotoC/music-assistant-server/commit/48a698316a78d00ee686c7f05d483e10bee221f5))
* faster retry on spotify token expiration ([c1aadac](https://github.com/SantiagoSotoC/music-assistant-server/commit/c1aadac77b8b53a0ccdde0131ef5619402051884))
* flow mode not being applied in all cases (while it should) ([#1672](https://github.com/SantiagoSotoC/music-assistant-server/issues/1672)) ([259252f](https://github.com/SantiagoSotoC/music-assistant-server/commit/259252f244a9bd1b4f8bbc4c74d73ee41ec51668))
* Group volume up/down not implemented ([a1eede9](https://github.com/SantiagoSotoC/music-assistant-server/commit/a1eede9b1675a52bb8cc3e03a95a449754e2255b))
* Handle radio stations providing non utf-8 in streamtitle ([#1664](https://github.com/SantiagoSotoC/music-assistant-server/issues/1664)) ([605b09f](https://github.com/SantiagoSotoC/music-assistant-server/commit/605b09fa381827b9d6a348237a7b7d0e5e9dadeb))
* Handle some small race conditions with sonos players ([d150b87](https://github.com/SantiagoSotoC/music-assistant-server/commit/d150b8750ffa3c8c63c4396abc21eae1840fdf92))
* playerqueue elapsed time not changing for cast players ([9fddafd](https://github.com/SantiagoSotoC/music-assistant-server/commit/9fddafd874d80917e3b553f4787a3d2562f7287e))
* Prevent playlist collage image take up all system memory ([f38770e](https://github.com/SantiagoSotoC/music-assistant-server/commit/f38770efc429911b2a94f1ef1b65586c3c2502a2))
* Prevent redundant lookup of full media item in queue controller ([734dc5b](https://github.com/SantiagoSotoC/music-assistant-server/commit/734dc5b99b705ed9ce6089d85ee72f4484836442))
* snapcast player in universal player group ([#1756](https://github.com/SantiagoSotoC/music-assistant-server/issues/1756)) ([f7ee100](https://github.com/SantiagoSotoC/music-assistant-server/commit/f7ee1007d79ab681c014e540da69d91e6457f4f1))


### Miscellaneous Chores

* release 2.4.0b1 ([1b6b216](https://github.com/SantiagoSotoC/music-assistant-server/commit/1b6b216a9d1c6f1be4909d7876361c1dac3bc16e))
