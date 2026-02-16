# CHANGELOG


## v1.0.2 (2026-02-16)

### Bug Fixes

* fix: properly includes templates on PyPI package ([`20daf92`](https://github.com/src-lua/cptools/commit/20daf923a54672c1b82787d612e5589fc2ff1ae5))

### Testing

* test: better test for config, status and entry-point ([`ac91d34`](https://github.com/src-lua/cptools/commit/ac91d34ee047bfe42b7b4dbb59ecfcbeb47eb3c6))


## v1.0.1 (2026-02-15)

### Bug Fixes

* fix: adjust development status ([`11a9a33`](https://github.com/src-lua/cptools/commit/11a9a334eff434daf6ea39d557d6eb4b3fbf3707))


## v1.0.0 (2026-02-15)

### Breaking

* feat!: stable v1.0 release with PyPI distribution ([`d712d4d`](https://github.com/src-lua/cptools/commit/d712d4dcb9d032f576dfebb17f46a6876ce400d9))

### Documentation

* docs: prepare PyPI release ([`46b6a9c`](https://github.com/src-lua/cptools/commit/46b6a9cfa8c86fe8d2dfdd769f686f1fc4161e88))


## v0.9.2 (2026-02-15)

### Bug Fixes

* fix: makes install script more robust and improove installation docs ([`a0205a6`](https://github.com/src-lua/cptools/commit/a0205a6783b100e566c1df10d4913b7a07e1e3de))

* fix: workflow typo and project dependecies on install ([`fae7f2e`](https://github.com/src-lua/cptools/commit/fae7f2e1f64a76b8552115081a9173ab31cf98d0))

### Documentation

* docs: adding judges tutorial ([`07254a8`](https://github.com/src-lua/cptools/commit/07254a8e7610f9a81a69df7b73fca521951a4554))


## v0.9.1 (2026-02-15)

### Bug Fixes

* fix: added flag --interactive for force interactive mode on test ([`be9247e`](https://github.com/src-lua/cptools/commit/be9247edfcbdfa81d3f32d12d5819599de6fb8c0))


## v0.9.0 (2026-02-15)

### Features

* feat: compact mode for status ([`eeb0ddd`](https://github.com/src-lua/cptools/commit/eeb0dddc5a24676ff3cb78df9ea74c2596373ad2))


## v0.8.0 (2026-02-15)

### Bug Fixes

* fix: version management ([`28c9f00`](https://github.com/src-lua/cptools/commit/28c9f0051b15c5517893a31337a8751c76a0b06e))

### Documentation

* docs: update docs ([`28882d4`](https://github.com/src-lua/cptools/commit/28882d49c6abfe73011772fc07863da0608c098e))

### Features

* feat: auto detect new modules ([`056d9d5`](https://github.com/src-lua/cptools/commit/056d9d545824d1b7a6187d6e1db8cee69d5d64f8))


## v0.7.0 (2026-02-14)

### Bug Fixes

* fix: mark ~ works as expected ([`6bece9b`](https://github.com/src-lua/cptools/commit/6bece9bb5669210a06d4fc0cedbfee5e9d357d5a))

* fix: remove now supports problem ranges ([`7edbd06`](https://github.com/src-lua/cptools/commit/7edbd06778c527e096ba19297d9909de6f5c0802))

### Features

* feat: add_header command and aks if user want to add if a header is missing ([`5e15588`](https://github.com/src-lua/cptools/commit/5e15588669b738ff00734568b76d18e6ce5727d9))


## v0.6.0 (2026-02-14)

### Bug Fixes

* fix: default name for training is the current date and problems are auto fetched if it's possible ([`fcac876`](https://github.com/src-lua/cptools/commit/fcac876f34290dc394a27e9001673b27a08acaf7))

* fix: rm and mark now handle properly if the file has or not .cpp extension ([`dbcd41b`](https://github.com/src-lua/cptools/commit/dbcd41be0de78573079dccdcbd2a54922bae2b0a))

* fix: autocomplete now completes files/folders ([`6f8e938`](https://github.com/src-lua/cptools/commit/6f8e93858aa717f74461aa0a4e5184ba8cd5c010))

### Features

* feat: better judge support ([`7a8c2b0`](https://github.com/src-lua/cptools/commit/7a8c2b0c581d131b15e317af6cbcf7b433d874e7))

* feat: cookie fetching for geting samples in auth-required pages ([`c5808a1`](https://github.com/src-lua/cptools/commit/c5808a1f16105893fa5db1189fb4e44cbbc78a08))

* feat: show process memory in tests ([`eba24c8`](https://github.com/src-lua/cptools/commit/eba24c8078c541d1bcc737d4c8f5546c8ce3b303))

* feat: files with same name after an hyphen '-' is considered the same solution ([`fea779b`](https://github.com/src-lua/cptools/commit/fea779bed7869df6ef59312b183ea6db5c980163))

* feat: support for SPOJ ([`eab7521`](https://github.com/src-lua/cptools/commit/eab7521e3afcaa92b47b9135ef0979baa99404df))


## v0.5.0 (2026-02-03)

### Bug Fixes

* fix: removed contest artifacts from problemset's info.md ([`9df3058`](https://github.com/src-lua/cptools/commit/9df30583bb042df46f93b9d9acaed21c85fc27b8))

* fix: casing matching ([`82c9a81`](https://github.com/src-lua/cptools/commit/82c9a81280b9b55a987ad1605411ebb9e9fd7396))

### Chores

* chore: add commitlint to github actions ([`9c111dd`](https://github.com/src-lua/cptools/commit/9c111ddd4350ab870fb2d58a881f55b3f24e95eb))

* chore: add commitlint configuration and husky hook ([`29c7c3a`](https://github.com/src-lua/cptools/commit/29c7c3a5658e68b4c60ef9b7dc22d8880a8f8729))

### Documentation

* docs: improve docstrings ([`a25741a`](https://github.com/src-lua/cptools/commit/a25741a91c14a543cc9c06f9bce6fc4298c26e8e))

### Features

* feat: improve editor fallback, fix some bugs and setup automation tooling ([`8087446`](https://github.com/src-lua/cptools/commit/80874461e586206487df5382e16e78564e083216))

* feat: better editor fallback on config and flag to choose an editor ([`15ecbfe`](https://github.com/src-lua/cptools/commit/15ecbfe464d0a68a46c6fb1af30c98c4897f5434))

* feat: auto fetch for supported platforms ([`d3d0e37`](https://github.com/src-lua/cptools/commit/d3d0e3729abc02a2b9d0f2a67e1ce4139b5f7b71))

### Unknown

* Merge branch 'main' into dev ([`65951a2`](https://github.com/src-lua/cptools/commit/65951a2d931d607fb2b43b1cc9f5be740ee0598e))


## v0.4.2 (2026-02-03)

### Bug Fixes

* fix: configure semantic release and pytest automation and fix some bugs

bugfixes & python-semantic-release ([`2729300`](https://github.com/src-lua/cptools/commit/2729300022dcb9a1b7a2edf9e5d895f1d75eb80d))

### Chores

* chore: remove .claude from repository ([`04aff2b`](https://github.com/src-lua/cptools/commit/04aff2b553a6085c3ea90b7e6ab10a75639cd99b))

* chore(release): configure python-semantic-release and fix toml syntax ([`daa52f9`](https://github.com/src-lua/cptools/commit/daa52f9711791a16e0ffe25678d6f8f859240fdf))

### Documentation

* docs: makes contributing.md smaller and easier to read ([`c312c8f`](https://github.com/src-lua/cptools/commit/c312c8f7eaf496179f2025f39b600603c03959b6))

### Refactoring

* refactor: standardize all flags ([`8f99e8d`](https://github.com/src-lua/cptools/commit/8f99e8d3ead1985a83d395a5e58c77b13899adec))

* refactor: remove hardcoded templates and make a template folder ([`97cbc2e`](https://github.com/src-lua/cptools/commit/97cbc2e3064d74720a44f686898aef6269bd5a46))

* refactor: move some utilitaries from update to lib ([`c14dec5`](https://github.com/src-lua/cptools/commit/c14dec57cc01d5fae55439bb2d193321621ddf35))

### Unknown

* bugfix: rm now removes info.md if there's no .cpp left ([`90812b7`](https://github.com/src-lua/cptools/commit/90812b722c435d69476fabf4a13a1c42ef7d35ae))

* bugfix: Now rm properly removes hashed files ([`a2e1fea`](https://github.com/src-lua/cptools/commit/a2e1feaf3329766dadc17f6939273f9dc02c273b))

* bugfix: init --gitignore now ignores .gitignore too ([`92699b4`](https://github.com/src-lua/cptools/commit/92699b4158fe4243e78492441719e46f78cbd5bd))

* bugfix: test_discovery now looks at lib/__init__.py ([`ce86be7`](https://github.com/src-lua/cptools/commit/ce86be7ab65439c2bfd80f795d82d0f3a2df6b8f))

* bugfix: fixed mark and parsing casing ([`25f1f3f`](https://github.com/src-lua/cptools/commit/25f1f3f7d5375d47faf17e0ff4c73c6e4c47fa84))


## v0.4.1 (2026-02-02)

### Testing

* test: Add comprehensive test suite ([`eb71a9c`](https://github.com/src-lua/cptools/commit/eb71a9c2844cfe704401a713582439f08844411d))


## v0.4.0 (2026-02-02)

### Refactoring

* refactor: DRY ([`eb3a821`](https://github.com/src-lua/cptools/commit/eb3a82112df88b8523f47d5687c6f224147af83a))

### Unknown

* Release v0.4.0 ([`6a4bb74`](https://github.com/src-lua/cptools/commit/6a4bb74b5396453720eaa47aed64e1a61e339d96))


## v0.3.0 (2026-01-31)

### Unknown

* Release v0.3.0 ([`6f4089b`](https://github.com/src-lua/cptools/commit/6f4089b52750c09bd95c8270557ee93d3ce3c932))


## v0.2.0 (2026-01-31)

### Unknown

* Release v0.2.0

New features:
- Add custom test cases with  and
- Add  flag for recursive clean (default is now non-recursive)
- Improve HTML parsing for Codeforces samples
- Better handling of test samples with gaps in numbering

Breaking changes:
-  command is now non-recursive by default (use  for recursive)

Documentation:
- Remove fetch beta notice
- Update directory structure with Problemset and Yosupo
- Add examples for new flags ([`6dba5cb`](https://github.com/src-lua/cptools/commit/6dba5cb6aef31292518d7e2ce2add0cd1eac0c53))


## v0.1.0 (2026-01-29)

### Unknown

* CPTools initial commit ([`c34a6c0`](https://github.com/src-lua/cptools/commit/c34a6c089456306067e0aa54e344a7756b477cb1))

* Initial commit: cptools - Competitive Programming Tools

CLI tool for managing competitive programming contest repos.
Commands: new, add, mark, status, clean, update. ([`15d9628`](https://github.com/src-lua/cptools/commit/15d962834594436d9c70a4be0760d2b5ce1720d4))
