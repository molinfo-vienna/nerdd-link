# CHANGELOG


## v0.4.4 (2025-07-23)

### Fixes

* fix: Derive from Model base class (instead of SimpleModel) ([`66e0021`](https://github.com/molinfo-vienna/nerdd-link/commit/66e0021b75ddbc1552c9328abcae665e9b692068))

* fix: Bump version of nerdd-module ([`04c7869`](https://github.com/molinfo-vienna/nerdd-link/commit/04c7869504f6239c11d14ec745a22d16e1aeb7ba))

### Testing

* test: Process module messages in tests ([`343cf6d`](https://github.com/molinfo-vienna/nerdd-link/commit/343cf6dd2d4305c98bb450ec589208e8ce0d82b3))

### Unknown

* Merge pull request #55 from shirte/main

Adapt to most recent version of nerdd-module ([`b43b0cc`](https://github.com/molinfo-vienna/nerdd-link/commit/b43b0cce1462a86ad6f89afa63d052d02f45ecc2))


## v0.4.3 (2025-07-23)

### Fixes

* fix: Simplify logic for writing property files ([`2d0f785`](https://github.com/molinfo-vienna/nerdd-link/commit/2d0f785ee3348bb20a5c8593394bb9c99912392e))

### Unknown

* Merge pull request #54 from shirte/main

fix: Simplify logic for writing property files ([`ff85b7b`](https://github.com/molinfo-vienna/nerdd-link/commit/ff85b7b8979f790b641568d8b623f5b8854f807c))


## v0.4.2 (2025-07-23)

### Fixes

* fix: Replace all large properties with file paths ([`956f016`](https://github.com/molinfo-vienna/nerdd-link/commit/956f0166f6b7164acf481cb23bf62babc4fc3d92))

### Unknown

* Merge pull request #53 from shirte/main

fix: Replace all large properties with file paths ([`f6b0e45`](https://github.com/molinfo-vienna/nerdd-link/commit/f6b0e4551a7403fae48a571cc25cab1108e4a19c))


## v0.4.1 (2025-06-28)

### Fixes

* fix: Use SPDX license expression ([`9c3a0a1`](https://github.com/molinfo-vienna/nerdd-link/commit/9c3a0a1ffcab1e23a6c1f968629eaf7ce6448e55))

### Unknown

* Merge pull request #52 from shirte/main

fix: Use SPDX license expression ([`f2d0934`](https://github.com/molinfo-vienna/nerdd-link/commit/f2d0934023c1d9d88dcc53f5652b9eb0f6d77c8f))


## v0.4.0 (2025-06-28)

### Code Style

* style: Make ruff happy on test files ([`ac16404`](https://github.com/molinfo-vienna/nerdd-link/commit/ac16404f6a78d3c815e28480031416ac4522f971))

### Features

* feat: Add tombstone messages ([`14df516`](https://github.com/molinfo-vienna/nerdd-link/commit/14df5166b57de3f8f3066529c39ca1dd4733fb29))

### Fixes

* fix: Let SerializeJobAction handle tombstones ([`67ae451`](https://github.com/molinfo-vienna/nerdd-link/commit/67ae451c827a3616fc518bba97a065bbe7739655))

* fix: Let ProcessJobAction handle tombstones ([`f92872e`](https://github.com/molinfo-vienna/nerdd-link/commit/f92872ee529d0267f9cb97fd3cef70d787c55773))

* fix: Let PredictCheckpointAction handle tombstones ([`d17bd94`](https://github.com/molinfo-vienna/nerdd-link/commit/d17bd94d4c07bdeddcee4d05e118c70d953efe8d))

* fix: Let action class distinguish tombstones from messages ([`f7cd6b1`](https://github.com/molinfo-vienna/nerdd-link/commit/f7cd6b14b0d0fdf5cb34dcd6910e8971ffc4bd27))

* fix: Add methods for iterating over checkpoint files ([`f4c3c4a`](https://github.com/molinfo-vienna/nerdd-link/commit/f4c3c4abcb26d1ef22ae983cf4adaf232ec352d8))

* fix: Remove key_serializer in producer ([`a8686c6`](https://github.com/molinfo-vienna/nerdd-link/commit/a8686c61654d3047a27c8e7f4ddf5d32e88d760e))

* fix: Handle errors when decoding message keys ([`4dfd12c`](https://github.com/molinfo-vienna/nerdd-link/commit/4dfd12c8fb31e2af7e65d5363694d62ae874cefb))

* fix: Decouple channel implementations from Message classes ([`27bd7b1`](https://github.com/molinfo-vienna/nerdd-link/commit/27bd7b1386450dc6674faacf9d28219ea0de1a15))

* fix: Enable receiving and sending tombstones ([`e0a66f9`](https://github.com/molinfo-vienna/nerdd-link/commit/e0a66f9af1eed4332f761d962f117a657a7ae427))

* fix: Add typing-extensions dependency for old versions of Python ([`e3984f7`](https://github.com/molinfo-vienna/nerdd-link/commit/e3984f7b204053fc82a5b77ebf7dd66825940a54))

### Testing

* test: Add new tests for tombstones ([`b559a83`](https://github.com/molinfo-vienna/nerdd-link/commit/b559a8374ae9656426870ea67c636da17b15a8f9))

* test: Adapt tests to tombstone messages ([`ea87ac5`](https://github.com/molinfo-vienna/nerdd-link/commit/ea87ac5f237355563ce5da5bf31d619d51709417))

### Unknown

* Merge pull request #51 from shirte/main

Implement tombstone messages ([`8adf3cb`](https://github.com/molinfo-vienna/nerdd-link/commit/8adf3cbf5af406b159885605d96f036000b9c26c))


## v0.3.0 (2025-06-26)

### Features

* feat: Measure checkpoint processing time ([`75eba1c`](https://github.com/molinfo-vienna/nerdd-link/commit/75eba1c5c44f8cb0dca06a228d0a5c84b6b6ce5a))

### Testing

* test: Fix pytest-asyncio version for now ([`290256f`](https://github.com/molinfo-vienna/nerdd-link/commit/290256f01447c75559daddf67077611698bedb7d))

* test: Ignore measured processing time in unit tests ([`71036c0`](https://github.com/molinfo-vienna/nerdd-link/commit/71036c0f4bfdb873d118fc63e5cc7eb01b58088d))

### Unknown

* Merge pull request #50 from shirte/main

feat: Measure checkpoint processing time ([`43e2b9a`](https://github.com/molinfo-vienna/nerdd-link/commit/43e2b9a5f16c3005dd72f1c10df9e7e6c823ef44))


## v0.2.27 (2025-05-23)

### Unknown

* Merge pull request #49 from molinfo-vienna/arm64

fix: in debian-slim containers wget needs to be installed ([`4f2f45f`](https://github.com/molinfo-vienna/nerdd-link/commit/4f2f45f1854bc3c99aace5ab011e590d33e2b413))

* Merge branch 'main' into arm64 ([`512316d`](https://github.com/molinfo-vienna/nerdd-link/commit/512316d66cd82327754172aa68d4160f17d1946b))


## v0.2.26 (2025-05-23)

### Fixes

* fix: in debian-slim containers wget needs to be installed ([`fc9ed8b`](https://github.com/molinfo-vienna/nerdd-link/commit/fc9ed8b6df895a779ab8a79d415fe44857e7de67))

### Unknown

* Merge pull request #48 from molinfo-vienna/arm64

fix: in debian-slim containers wget needs to be installed ([`35b2b77`](https://github.com/molinfo-vienna/nerdd-link/commit/35b2b77e609f71978b29079a7eb8ecc774d8f417))

* Merge branch 'main' into arm64 ([`4b8993e`](https://github.com/molinfo-vienna/nerdd-link/commit/4b8993e706cb6d0151b965e52558f87826975d85))


## v0.2.25 (2025-05-23)

### Fixes

* fix: in debian-slim containers wget needs to be installed ([`edea234`](https://github.com/molinfo-vienna/nerdd-link/commit/edea234185cd96ddeb02481b635e8b3bae041b99))

* fix: Update Actions workflow and Dockerfiles for arm64 compatibility ([`c75f299`](https://github.com/molinfo-vienna/nerdd-link/commit/c75f299298a190e71539407f8b48e9be3ae195f6))

### Unknown

* Merge pull request #47 from molinfo-vienna/arm64

fix: Update Actions workflow and Dockerfiles for arm64 compatibility ([`74a9dc3`](https://github.com/molinfo-vienna/nerdd-link/commit/74a9dc3429683eedae22aa2db4bdda878ee22b18))


## v0.2.24 (2025-05-21)

### Fixes

* fix: Check type of property before writing ([`bd4ee81`](https://github.com/molinfo-vienna/nerdd-link/commit/bd4ee813044cbd931df22da06858772b7a34c8ed))

### Unknown

* Merge pull request #46 from shirte/main

fix: Check type of property before writing ([`c1f3329`](https://github.com/molinfo-vienna/nerdd-link/commit/c1f332959c62b0c7f7574852e2700d672a764829))


## v0.2.23 (2025-04-19)

### Fixes

* fix: Minimize number of files written to disk ([`f40afe2`](https://github.com/molinfo-vienna/nerdd-link/commit/f40afe212e7ef9f45fc48571a82e03d28dbc7f22))

### Unknown

* Merge pull request #45 from shirte/main

Minimize number of files written to disk ([`4da77f7`](https://github.com/molinfo-vienna/nerdd-link/commit/4da77f7ed0375991bbb2da3d59a805778f5dadc0))

* Remove unused import ([`fc9cede`](https://github.com/molinfo-vienna/nerdd-link/commit/fc9cede8f41eeb6138a642749e9559257482e89c))

* Apply cosmetic changes ([`410f0f0`](https://github.com/molinfo-vienna/nerdd-link/commit/410f0f084dd7143b4305f1c3d447fc3073d0beb4))


## v0.2.22 (2025-04-17)

### Fixes

* fix: Write large result properties to files ([`a9df4bc`](https://github.com/molinfo-vienna/nerdd-link/commit/a9df4bc703b75bee253800f237a9f08528073990))

* fix: Pass file_system and job_id to TopicWriter ([`fede063`](https://github.com/molinfo-vienna/nerdd-link/commit/fede0639fbbb7cddfcf499484cc9eacb5b4cc8f3))

### Unknown

* Merge pull request #44 from shirte/main

Write large result properties to files ([`a6f4b70`](https://github.com/molinfo-vienna/nerdd-link/commit/a6f4b70639eb9b5933cfe0f429a6069220fd949b))

* Remove redundant async_step function ([`b740b03`](https://github.com/molinfo-vienna/nerdd-link/commit/b740b03fead6aa486a0b00c16334a27380c479cd))

* Bump nerdd-module version ([`58fcaff`](https://github.com/molinfo-vienna/nerdd-link/commit/58fcaff17ce9c89655a0328ce40d3205ee9d7567))

* Add file paths to write large result properties ([`0294962`](https://github.com/molinfo-vienna/nerdd-link/commit/02949623722cf0d0f899ff4804270105930d9b03))


## v0.2.21 (2025-04-17)

### Fixes

* fix: Use lock to avoid parallel start of kafka consumers ([`62c1024`](https://github.com/molinfo-vienna/nerdd-link/commit/62c1024e7cc213c5898401fe3c48eb7b0cffe84f))

### Unknown

* Merge pull request #43 from shirte/main

fix: Use lock to avoid parallel start of kafka consumers ([`7beff90`](https://github.com/molinfo-vienna/nerdd-link/commit/7beff908cdbea83b02cfebb20790255bcb0e3632))


## v0.2.20 (2025-04-13)

### Fixes

* fix: Bump version of nerdd-module in requirements_serialization ([`142689c`](https://github.com/molinfo-vienna/nerdd-link/commit/142689c175a9fd46483b833e52a507472c8b914f))

* fix: Bump version of nerdd-module in requirements_processing ([`b11fd5f`](https://github.com/molinfo-vienna/nerdd-link/commit/b11fd5fc926c8772e3e38c5373f267abf2bc180e))

### Unknown

* Merge pull request #42 from shirte/main

Bump version of nerdd-module dependency ([`c80cdb9`](https://github.com/molinfo-vienna/nerdd-link/commit/c80cdb9a51b23fd5546d4441a06c816e8905dcb8))

* Rename Dockerfiles ([`66d040e`](https://github.com/molinfo-vienna/nerdd-link/commit/66d040ee478934e6be3305070dee529fb533157b))

* Add workflow to build container nerdd-process-jobs ([`2d677b2`](https://github.com/molinfo-vienna/nerdd-link/commit/2d677b2ea0743c0e352deb532b6506aaece1b9c7))

* Add workflow to build container nerdd-serialize-jobs ([`60bc44c`](https://github.com/molinfo-vienna/nerdd-link/commit/60bc44c7a51ea0a27f84ce7a26f3c1d0f3b1e71f))


## v0.2.19 (2025-02-19)

### Fixes

* fix: Improve Dockerfile for job processing ([`714f1f0`](https://github.com/molinfo-vienna/nerdd-link/commit/714f1f0f1c75748c3dba778b87bfd7c81210039e))

### Unknown

* Merge pull request #41 from shirte/main

Improve docker files ([`e8a16c7`](https://github.com/molinfo-vienna/nerdd-link/commit/e8a16c78fc2ffc26e47f125912dd01bc36efc5cf))

* Change Dockerfile labels ([`c582e0a`](https://github.com/molinfo-vienna/nerdd-link/commit/c582e0a2b8ddcc76d1cd3bf86b4522b032281fbd))

* Switch to BSD 3-Clause license ([`8394e8e`](https://github.com/molinfo-vienna/nerdd-link/commit/8394e8eb24941739b2ba87fb5f0df97cb54a86a6))

* Remove test packages from requirements_serialization.txt ([`6358121`](https://github.com/molinfo-vienna/nerdd-link/commit/635812120d426b7c63d177b68d3704ee623aa3b8))

* Add requirements.txt for job processing ([`d08fa8d`](https://github.com/molinfo-vienna/nerdd-link/commit/d08fa8d6b6a1a7ac1379b60b48014d9173048132))

* Improve Dockerfile of serialization job ([`a5b9597`](https://github.com/molinfo-vienna/nerdd-link/commit/a5b95971355bcdafd03ef7a07421dfed506404df))

* Add requirements file for serialization job ([`22f9a30`](https://github.com/molinfo-vienna/nerdd-link/commit/22f9a30072d5651bb14099573493f6ff6479be0d))

* Merge pull request #40 from shirte/main

Improve docker images ([`86881ef`](https://github.com/molinfo-vienna/nerdd-link/commit/86881efcd6be7b8717aa5e98020c51aa5bda2102))

* Run docker files with non-root user ([`528a55d`](https://github.com/molinfo-vienna/nerdd-link/commit/528a55d20e31968d7df0efd9300d2a004c65fd3c))

* Avoid apt dependencies in docker files ([`4852fc3`](https://github.com/molinfo-vienna/nerdd-link/commit/4852fc3da85de0b9ada6f7f19f6306673a9a05ca))

* Copy source code in docker files ([`a36e1b1`](https://github.com/molinfo-vienna/nerdd-link/commit/a36e1b12bb8a774c44a05bdd12ebce79f7f287ff))

* Remove git dependency in docker images ([`83d829c`](https://github.com/molinfo-vienna/nerdd-link/commit/83d829cce9e918c992c199292dc763eb0f6b7605))

* Remove defaults channel from conda envs ([`b8163f8`](https://github.com/molinfo-vienna/nerdd-link/commit/b8163f8fe4fa71df0a4c835094f0636218fc5376))


## v0.2.18 (2025-02-15)

### Fixes

* fix: Use config property instead of get_config ([`0cc2e02`](https://github.com/molinfo-vienna/nerdd-link/commit/0cc2e02fe161e4f5091e4f5acd7f4e3e7f3f26b1))

### Unknown

* Merge pull request #39 from shirte/main

Use config property instead of get_config ([`03325bc`](https://github.com/molinfo-vienna/nerdd-link/commit/03325bcd0626c9fd8e180eb3b061cba02a935815))

* Rename and adapt docker files ([`f51cb92`](https://github.com/molinfo-vienna/nerdd-link/commit/f51cb924532b41e4fd56f19f629580ac1f945d97))

* Use meaningful names for conda environments ([`5f7a9f0`](https://github.com/molinfo-vienna/nerdd-link/commit/5f7a9f02676fc31351885679fb514297e75157f5))


## v0.2.17 (2025-01-29)

### Fixes

* fix: Avoid tombstoned records ([`feb7675`](https://github.com/molinfo-vienna/nerdd-link/commit/feb7675b2b9ac7f5af87c226a74c1aeb6543c56d))

### Unknown

* Merge pull request #38 from shirte/main

fix: Avoid tombstoned records ([`aaf8edb`](https://github.com/molinfo-vienna/nerdd-link/commit/aaf8edb0f577230f3689a474edd880a33b72858f))


## v0.2.16 (2025-01-26)

### Fixes

* fix: Decrease checkpoint size to 100 ([`e7efa64`](https://github.com/molinfo-vienna/nerdd-link/commit/e7efa64bb882867ef721190b64ffc2530afe31af))

### Unknown

* Merge pull request #37 from shirte/main

fix: Decrease checkpoint size to 100 ([`069a711`](https://github.com/molinfo-vienna/nerdd-link/commit/069a7116eed2dbdfb83b73c51bc4ca0b9037099d))


## v0.2.15 (2025-01-26)

### Fixes

* fix: Tune timeout variables in Kafka ([`d53fe6c`](https://github.com/molinfo-vienna/nerdd-link/commit/d53fe6cd0979e8334e2bce734a1310f92e4ab276))

* fix: Always wait until all steps processed a record ([`4727eab`](https://github.com/molinfo-vienna/nerdd-link/commit/4727eab1b25baa772adf7cc438b841f277903343))

* fix: Send intermediate results ([`b816582`](https://github.com/molinfo-vienna/nerdd-link/commit/b8165825d257f4a328847d97a14152f3163b2aae))

* fix: Implement channel registry ([`26dad70`](https://github.com/molinfo-vienna/nerdd-link/commit/26dad7013e6fd63d9ca0dbae16060f5fbb74cf01))

### Unknown

* Merge pull request #36 from shirte/main

Send intermediate results ([`d0b582b`](https://github.com/molinfo-vienna/nerdd-link/commit/d0b582b8bbe722480ccb4de281d2dc6a34c60267))

* Adapt tests ([`946f8b7`](https://github.com/molinfo-vienna/nerdd-link/commit/946f8b7f6d3d0b1c9b2e77aeff97523f944e2d5e))

* Do not catch all exceptions in PredictCheckpointAction ([`03a9f11`](https://github.com/molinfo-vienna/nerdd-link/commit/03a9f11543bbadeabb29fb73bb0830d963ea9277))


## v0.2.14 (2025-01-23)

### Fixes

* fix: Reroute exceptions from threads to main thread ([`722a9d7`](https://github.com/molinfo-vienna/nerdd-link/commit/722a9d787ad3f6ca247196fb56ec4ac3b12ff8c5))

### Unknown

* Merge pull request #35 from shirte/main

fix: Reroute exceptions from threads to main thread ([`b844471`](https://github.com/molinfo-vienna/nerdd-link/commit/b8444718f0a79dbe92c8d0de8f01cda31c205a74))


## v0.2.13 (2025-01-20)

### Fixes

* fix: Catch exceptions in PredictCheckpointAction ([`2ef6285`](https://github.com/molinfo-vienna/nerdd-link/commit/2ef628555e15068601167667785c41129c24308c))

### Unknown

* Merge pull request #34 from shirte/main

fix: Catch exceptions in PredictCheckpointAction ([`802faae`](https://github.com/molinfo-vienna/nerdd-link/commit/802faaee179dff6a6d35f9c68777424c93ae5267))


## v0.2.12 (2025-01-18)

### Fixes

* fix: Adapt Writer classes to new version of nerdd-module ([`4316a3e`](https://github.com/molinfo-vienna/nerdd-link/commit/4316a3ee78b893afa2e96465c08385e4e87111e5))

### Unknown

* Merge pull request #33 from shirte/main

Adapt Writer classes to new version of nerdd-module ([`4b2ef63`](https://github.com/molinfo-vienna/nerdd-link/commit/4b2ef639a6b5b1fd7d39af901bf64ba700d17dfa))

* Draw atom highlights only on relevant molecules ([`f398c95`](https://github.com/molinfo-vienna/nerdd-link/commit/f398c951b000e84ced91ca7fa490f591d12785b9))


## v0.2.11 (2025-01-15)

### Fixes

* fix: Remove prediction process ([`97a80fa`](https://github.com/molinfo-vienna/nerdd-link/commit/97a80fa4ad41015148cbbaa583067cb1d78f396d))

* fix: Simplify MolPickleConverter and PickleConverter ([`04baad9`](https://github.com/molinfo-vienna/nerdd-link/commit/04baad98eaa08c5f7d7fb9fdc1b8774bb9c9747a))

* fix: Put highlight circles in mol images on top ([`c5f2840`](https://github.com/molinfo-vienna/nerdd-link/commit/c5f2840ee32bbd8358a63703f8527a8b7e00c98f))

* fix: Do not map sources to correct filenames in StructureJsonReader ([`684026d`](https://github.com/molinfo-vienna/nerdd-link/commit/684026d2428e0918a478d4ac02f0a239d98bab1c))

* fix: Add converters for problem lists and source lists ([`583ffa4`](https://github.com/molinfo-vienna/nerdd-link/commit/583ffa4a8de0e06ea062b7ece1746d72d55e4301))

* fix: Add image converter for json ([`5223d2c`](https://github.com/molinfo-vienna/nerdd-link/commit/5223d2c4d2d16711e1a40c683e44e46918103e4d))

* fix: Require aiokafka >= 0.12.0 ([`68736d5`](https://github.com/molinfo-vienna/nerdd-link/commit/68736d5a0ef3d770b8508721d269e1053a2e19d8))

### Unknown

* Merge pull request #32 from shirte/main

Many changes ([`fe2ebdb`](https://github.com/molinfo-vienna/nerdd-link/commit/fe2ebdb7969cb1af524c665a45978de456c869ba))

* Use most recent RDKit for writing output files ([`eea2e87`](https://github.com/molinfo-vienna/nerdd-link/commit/eea2e87cb0169bf088103b13c255786ea7dc8a36))

* Use old RDKit for writing input files ([`4d9f280`](https://github.com/molinfo-vienna/nerdd-link/commit/4d9f2801bf208d399a5fb6ebede9b7719c5e2ce0))


## v0.2.10 (2025-01-08)

### Fixes

* fix: Use base_model config in ReadCheckpointModel ([`ffc3958`](https://github.com/molinfo-vienna/nerdd-link/commit/ffc3958652f4b277f09af6b853d2348d6bae8613))

### Unknown

* Merge pull request #31 from shirte/main

fix: Use base_model config in ReadCheckpointModel ([`5926191`](https://github.com/molinfo-vienna/nerdd-link/commit/5926191eb8341bd405540715075fe0411f0515f4))


## v0.2.9 (2025-01-07)

### Fixes

* fix: Do prediction in different process ([`fa34a38`](https://github.com/molinfo-vienna/nerdd-link/commit/fa34a387ccd844bea99484501d389404192fe9fd))

### Unknown

* Merge pull request #30 from shirte/main

fix: Do prediction in different process ([`119a013`](https://github.com/molinfo-vienna/nerdd-link/commit/119a01358fab9847937e36949ec39893dfa87d8d))


## v0.2.8 (2025-01-06)

### Fixes

* fix: Do not wrap None in PropertyMol ([`21a9b4e`](https://github.com/molinfo-vienna/nerdd-link/commit/21a9b4ecc5ff9a34f0af066f5d08cf9603d2c266))

### Unknown

* Merge pull request #29 from shirte/main

fix: Do not wrap None in PropertyMol ([`0040108`](https://github.com/molinfo-vienna/nerdd-link/commit/0040108dfe73590d67294c8c72b201b3b80fc844))


## v0.2.7 (2025-01-06)

### Fixes

* fix: Use a queue to send messages ([`c6f4896`](https://github.com/molinfo-vienna/nerdd-link/commit/c6f489610819c531d9f13cf729adda2af049c8a0))

### Unknown

* Merge pull request #28 from shirte/main

Use a queue to send messages ([`8a5e14f`](https://github.com/molinfo-vienna/nerdd-link/commit/8a5e14f8bf7e400afe0e468cba7f7d09c2c78ead))

* Add a delay in unit tests ([`b18f0fe`](https://github.com/molinfo-vienna/nerdd-link/commit/b18f0fe83cd79f3480ab874eb2c853567a908aa3))

* Write older pickle version ([`7a75396`](https://github.com/molinfo-vienna/nerdd-link/commit/7a753967fb624aa023bd3945bd31c5a73273adbc))


## v0.2.6 (2025-01-05)

### Fixes

* fix: Run result sender in current event loop ([`d2597f1`](https://github.com/molinfo-vienna/nerdd-link/commit/d2597f1ba909244588cee5459a1a628a41f4f3e8))

### Unknown

* Merge pull request #27 from shirte/main

fix: Run result sender in current event loop ([`41dd87c`](https://github.com/molinfo-vienna/nerdd-link/commit/41dd87c7488ca95196a3f25ebea40a2113726129))


## v0.2.5 (2025-01-04)

### Fixes

* fix: Pass data_dir to RegisterModuleAction ([`7df33a0`](https://github.com/molinfo-vienna/nerdd-link/commit/7df33a022f26a7e2fa3d13c9476322e7d31cb705))

### Unknown

* Merge pull request #26 from shirte/main

fix: Pass data_dir to RegisterModuleAction ([`258e9b9`](https://github.com/molinfo-vienna/nerdd-link/commit/258e9b9935da6547b1409c1235e18fd3076d7af2))


## v0.2.4 (2025-01-03)

### Fixes

* fix: Rewrite import statement ([`011299e`](https://github.com/molinfo-vienna/nerdd-link/commit/011299edd20186d7e23a919eb004a0763b45bbe8))

### Unknown

* Merge pull request #25 from shirte/main

Use a single serialization job ([`36174e5`](https://github.com/molinfo-vienna/nerdd-link/commit/36174e58d5208ad97c7c36121cadf0b12acb9fd1))

* Add MolToImageConverter ([`878f93d`](https://github.com/molinfo-vienna/nerdd-link/commit/878f93d496ef7d1a975850128586f96d0b45f6c9))

* Use single serialization job ([`33acee0`](https://github.com/molinfo-vienna/nerdd-link/commit/33acee099759b49b9fad61bdd491a213a6adc78a))


## v0.2.3 (2025-01-02)

### Fixes

* fix: Start and stop channel in cli ([`4136159`](https://github.com/molinfo-vienna/nerdd-link/commit/4136159df9a603596252406dbf05be8773bb091d))

### Unknown

* Merge pull request #24 from shirte/main

fix: Start and stop channel in cli ([`e02fedf`](https://github.com/molinfo-vienna/nerdd-link/commit/e02fedf2e0b326fa3bacd1be26f077dbb0da87f8))


## v0.2.2 (2024-12-30)

### Fixes

* fix: Export files submodule ([`c83fa82`](https://github.com/molinfo-vienna/nerdd-link/commit/c83fa827ec371dd57cd7b6d88f3f43744f00c761))

### Unknown

* Merge pull request #23 from shirte/main

fix: Export files submodule ([`b8f4357`](https://github.com/molinfo-vienna/nerdd-link/commit/b8f435795cd1ba653d12223f1a854ba5f06a31b8))

* Merge pull request #22 from shirte/main

Minor changes ([`4307388`](https://github.com/molinfo-vienna/nerdd-link/commit/4307388fd1b1eb6c823014db1aafdff7a8211918))

* Add method to obtain source file path to FileSystem ([`9832bf6`](https://github.com/molinfo-vienna/nerdd-link/commit/9832bf6aa2ee320920ffddb4c1f8d98fcba8cfd7))

* Fix typo in ObservableList ([`730b414`](https://github.com/molinfo-vienna/nerdd-link/commit/730b4143809c58f12f983b2c4c5062df630d6931))


## v0.2.1 (2024-12-22)

### Fixes

* fix: Export SerializationRequestMessage ([`817c8ee`](https://github.com/molinfo-vienna/nerdd-link/commit/817c8ee258b42eb9377a6a907e00c8ce9b6801e7))

* fix: Export ResultCheckpoint ([`a0ac71e`](https://github.com/molinfo-vienna/nerdd-link/commit/a0ac71e36f01fe3379d2af0640a642f1ba000eca))

### Unknown

* Merge pull request #21 from shirte/main

Add confirmation messages for writing an output file ([`f55c481`](https://github.com/molinfo-vienna/nerdd-link/commit/f55c481b2ceaa4346bbce60e7a3581ef2400afeb))

* Check that serialization result message is sent ([`cfdb0a5`](https://github.com/molinfo-vienna/nerdd-link/commit/cfdb0a5ec2ca4a2ea39c0cf7d8d56c25ec5fe507))

* Start checking types for stringcase ([`d0e8f6a`](https://github.com/molinfo-vienna/nerdd-link/commit/d0e8f6a05cb34aea3444adf9115270e70e4829f2))

* Add serialization-results topic to channel ([`7e358a8`](https://github.com/molinfo-vienna/nerdd-link/commit/7e358a8b0103e05dd1d7fae5b64f689778d46ed6))

* Create SerializationResultMessage ([`92dcc20`](https://github.com/molinfo-vienna/nerdd-link/commit/92dcc2098291544cf8d0807904602b0bf498060c))

* Adapt unit tests ([`867d9ee`](https://github.com/molinfo-vienna/nerdd-link/commit/867d9eef9fa62feccfc5637fb8c87fcec2f83c49))

* Provide exactly one topic for result checkpoint messages ([`d98016d`](https://github.com/molinfo-vienna/nerdd-link/commit/d98016ddd20f5068029f39c2835f5811f85a996b))

* Report number of checkpoints after chunking a job ([`e09e920`](https://github.com/molinfo-vienna/nerdd-link/commit/e09e920e34daad97ee3fe382ae279eabd09cbb28))

* Delete timestamp field in JobMessage ([`212d311`](https://github.com/molinfo-vienna/nerdd-link/commit/212d311ccd0060da71c06caef763689407f89b48))

* Merge pull request #20 from shirte/main

Implement SerializeJobAction ([`ede3027`](https://github.com/molinfo-vienna/nerdd-link/commit/ede302757f7a2e950b876afefe2b59287ea29fd5))

* Implement serialization cli command ([`e6a6063`](https://github.com/molinfo-vienna/nerdd-link/commit/e6a6063ba6676a7e08d7d57dfb71aab1024edeeb))

* Improve tests ([`b0e3606`](https://github.com/molinfo-vienna/nerdd-link/commit/b0e36067a4ab6dca3d3b5cdb06afc45fc2a41a47))

* Test SerializeJobAction ([`5e1c84f`](https://github.com/molinfo-vienna/nerdd-link/commit/5e1c84f234e15b003943a5ff3c20ef631c5557b4))

* Implement SerializeJobAction ([`f43b47f`](https://github.com/molinfo-vienna/nerdd-link/commit/f43b47f2786c65f2b4bee08674a53fd523b7ec15))

* Add functions to FileSystem ([`fb7c005`](https://github.com/molinfo-vienna/nerdd-link/commit/fb7c00545f83d55aecc167300b675aba308c76c8))

* Fix type in ReadPickleStep ([`8bc6458`](https://github.com/molinfo-vienna/nerdd-link/commit/8bc6458d481c5ecc6c5f0a71fbbca8b08cd2c714))

* Adapt ProcessJobsAction to FileSystem ([`64ea81c`](https://github.com/molinfo-vienna/nerdd-link/commit/64ea81c91634ef1cc6614afaf903a724b406f9b6))

* Add serialization request topic and message ([`5587b68`](https://github.com/molinfo-vienna/nerdd-link/commit/5587b6833871e889fea42a13aa1bc69a6c06d505))

* Make variables private in PredictCheckpointsAction ([`045c5b6`](https://github.com/molinfo-vienna/nerdd-link/commit/045c5b6d6deb608a42c25593e2f6f08114934b78))

* Adapt PredictCheckpointAction to FileSystem ([`98b7fa1`](https://github.com/molinfo-vienna/nerdd-link/commit/98b7fa1bddb2cbbf51a71df4fe2127649a51faca))

* Add a class FileSystem for standardizing file access ([`9c5329c`](https://github.com/molinfo-vienna/nerdd-link/commit/9c5329c1a11fe3d507d3f6f5ec4a54cc26e20365))

* Log errors when processing messages ([`efdaa58`](https://github.com/molinfo-vienna/nerdd-link/commit/efdaa5832b1214e5f94e0987537cda39761887c0))


## v0.2.0 (2024-12-12)

### Features

* feat: Add start and stop method to Channel ([`f4997cf`](https://github.com/molinfo-vienna/nerdd-link/commit/f4997cfac8643307c1c6ed085fe8324a1ec5730c))

### Fixes

* fix: Keep molecule properties when serializing them to pickle (part 2) ([`110103b`](https://github.com/molinfo-vienna/nerdd-link/commit/110103be86e08a847ae62e0129d92292cb20ddbb))

* fix: Keep molecule properties when serializing them to pickle ([`1d9b0b8`](https://github.com/molinfo-vienna/nerdd-link/commit/1d9b0b83dc8c23f953a9a66fb2cdea913cb239c8))

### Unknown

* Merge pull request #19 from shirte/main

Add start and stop method to channels ([`a0f8451`](https://github.com/molinfo-vienna/nerdd-link/commit/a0f845197d4dd3949c3d83eebba82fa5a6f3446b))

* Make sure that all properties are serialized to pickle ([`dd46074`](https://github.com/molinfo-vienna/nerdd-link/commit/dd46074d0e524550c7b03df1a559d8e65a8d7047))

* Implement consumer groups in MemoryChannel ([`aa4f1f6`](https://github.com/molinfo-vienna/nerdd-link/commit/aa4f1f6aaf35d004aa77cd15a940ecc9af7ca2a9))

* Start consumers when restarting in KafkaChannel ([`f4d9e6f`](https://github.com/molinfo-vienna/nerdd-link/commit/f4d9e6f2e0a8fc07c2b127579088b9bcf41e4331))

* Add value serializer in KafkaChannel ([`47da130`](https://github.com/molinfo-vienna/nerdd-link/commit/47da13036c9d1ebae9f428dfd3292b5d26a7c480))

* Let KafkaChannel use consumer group as given ([`e918927`](https://github.com/molinfo-vienna/nerdd-link/commit/e9189276483ba0855645a3bc320cae94264e2735))

* Start kafka producer and consumers in _start method ([`721631e`](https://github.com/molinfo-vienna/nerdd-link/commit/721631eea05edb8e37bbe57bc2faa2e54c6379c1))

* Make channel only usable in running state ([`5ac0f29`](https://github.com/molinfo-vienna/nerdd-link/commit/5ac0f29aa9c4fabddb37d3d96c2c25615d7e7ee0))


## v0.1.0 (2024-12-06)

### Features

* feat: Move ObservableList to utils ([`0c5358d`](https://github.com/molinfo-vienna/nerdd-link/commit/0c5358db561a72ee2ec474d463ed439c44d4af7d))

### Unknown

* Merge pull request #18 from shirte/main

Fix types ([`1331854`](https://github.com/molinfo-vienna/nerdd-link/commit/13318542719128a97f70973620e9abef8b49fe83))

* Add initialize_system command ([`ce229f2`](https://github.com/molinfo-vienna/nerdd-link/commit/ce229f26291b22c6ac03f557171af30990b69c47))

* Add mypy to pre-commit hooks ([`6fe227b`](https://github.com/molinfo-vienna/nerdd-link/commit/6fe227b763693635ec1579890dd5293622426453))

* Ignore aiokafka when checking types ([`95e5d0f`](https://github.com/molinfo-vienna/nerdd-link/commit/95e5d0f6018e03b5767ca4bba9113062cdee9c94))

* Configure semantic release in pyproject.toml ([`500ae8c`](https://github.com/molinfo-vienna/nerdd-link/commit/500ae8c66e28f18239cd71f97a709a9e7bac8cb2))

* Add mypy plugin for pydantic ([`915bbad`](https://github.com/molinfo-vienna/nerdd-link/commit/915bbad81e2a5358ce83a1b7577d1fbbd09717c1))

* Fix types in MemoryChannel ([`339458e`](https://github.com/molinfo-vienna/nerdd-link/commit/339458e407283f6f2a941cb16a62a4b4f0806dc3))

* Merge pull request #17 from shirte/main

Rename DummyChannel and move to main code ([`f1c0235`](https://github.com/molinfo-vienna/nerdd-link/commit/f1c02353741257b3c62bf1278494baad96aa760b))

* Do not return spinalcase in PredictCheckpointsAction ([`5c928c9`](https://github.com/molinfo-vienna/nerdd-link/commit/5c928c9aa53d9d084f96c714139a5da5ec5564ea))

* Rename DummyChannel to MemoryChannel and move to channels submodule ([`78adf26`](https://github.com/molinfo-vienna/nerdd-link/commit/78adf26f568fb0de80644af2304d3184e99899f9))

* Use correct types in WriteOutputAction ([`9647a61`](https://github.com/molinfo-vienna/nerdd-link/commit/9647a61158ee8047738e5d3672946c03985a811c))

* Use logger in DummyChannel ([`9106a16`](https://github.com/molinfo-vienna/nerdd-link/commit/9106a1663c0eb5d208f839d2a8ead2180ef710be))

* Add types to channel classes ([`b62f0fa`](https://github.com/molinfo-vienna/nerdd-link/commit/b62f0fac04c4009b4d12ff727d013f363f140533))

* Add types to cli classes ([`d0c93e2`](https://github.com/molinfo-vienna/nerdd-link/commit/d0c93e23ef7fa3383c372d9e06fd288c3ec2f40a))

* Add types to delegate classes ([`0fbd987`](https://github.com/molinfo-vienna/nerdd-link/commit/0fbd98762c9e86952dc7fe045816b82cee78cf00))


## v0.0.2 (2024-12-05)

### Fixes

* fix: Use spinalcase for specified job_type ([`5c1f5a7`](https://github.com/molinfo-vienna/nerdd-link/commit/5c1f5a787815c0a8d610095a794dda7f87b19949))

### Unknown

* Merge pull request #16 from shirte/main

Add types ([`7e9a229`](https://github.com/molinfo-vienna/nerdd-link/commit/7e9a22935ea65f29a47d45bea86a50e1035f839a))

* Add types to async_to_sync ([`51b92d9`](https://github.com/molinfo-vienna/nerdd-link/commit/51b92d9216f879c4236dccec66dace754baa29ab))

* Add types to StructureJsonReader ([`a294c8a`](https://github.com/molinfo-vienna/nerdd-link/commit/a294c8ae25315e76a8f79e5e69b5e2fd4dc07fb6))

* Always use spinalcase ([`6956dc9`](https://github.com/molinfo-vienna/nerdd-link/commit/6956dc91adc9c82c3e28845a877c4fe845ee7673))

* Check that the given module has a config ([`00b8697`](https://github.com/molinfo-vienna/nerdd-link/commit/00b8697cc97273eb1619dfde721674cc813fe45e))

* Add types to actions ([`f960685`](https://github.com/molinfo-vienna/nerdd-link/commit/f96068534aa9f14a77a28b3104d129deeb6653d4))

* Add pyproject.toml to pre-commit-config ([`c67e8d5`](https://github.com/molinfo-vienna/nerdd-link/commit/c67e8d5590a3316aa658f53aff79b9eb36bcc2f2))

* Use logging in actions ([`4038256`](https://github.com/molinfo-vienna/nerdd-link/commit/4038256832739c41de89e2a6f4c22d056092f56a))


## v0.0.1 (2024-12-03)

### Fixes

* fix: Add update operation to ObservableList ([`d12ba0a`](https://github.com/molinfo-vienna/nerdd-link/commit/d12ba0a8458a60861dc6268193295b6c6b1a7159))

### Unknown

* Merge pull request #15 from shirte/main

Add types ([`965f5b3`](https://github.com/molinfo-vienna/nerdd-link/commit/965f5b3da10a2a8cbe77b1f255b1712c50263ea0))

* Remove kafka-python dependency ([`9949ce9`](https://github.com/molinfo-vienna/nerdd-link/commit/9949ce96750cdbba86b7deb5041063156bb4481b))

* Add types for safetee ([`72a5a67`](https://github.com/molinfo-vienna/nerdd-link/commit/72a5a67455f0afbab21b6d7ad1a9682eb0d29769))

* Add type stubs for stringcase ([`82d7e64`](https://github.com/molinfo-vienna/nerdd-link/commit/82d7e64acb1632e2bdb458e9e436231a7e62ac66))

* Ignore rdkit typing errors ([`e763b33`](https://github.com/molinfo-vienna/nerdd-link/commit/e763b3306da18c42aa73e8005b22a6082fe7fd5c))

* Merge pull request #14 from shirte/main

Let ObservableList track changes ([`6a99d06`](https://github.com/molinfo-vienna/nerdd-link/commit/6a99d0608556306c466ff7c25a0e1a7d7ca468e6))

* Finalize register_module feature test ([`a72d105`](https://github.com/molinfo-vienna/nerdd-link/commit/a72d105e4f8dea39e5a71c3e766659fbd8c8c7ac))

* Let ObservableList track changes ([`eeb4e4f`](https://github.com/molinfo-vienna/nerdd-link/commit/eeb4e4febce98cdebfc59a731946045f4de98e42))

* Merge pull request #13 from shirte/main

Introduce ObservableList ([`6f3a7a4`](https://github.com/molinfo-vienna/nerdd-link/commit/6f3a7a467774b2671505b2a96b6560c32f0e0495))

* Introduce ObservableList ([`d08d896`](https://github.com/molinfo-vienna/nerdd-link/commit/d08d89618ea65125fa02027c5d5b66cc3f556b3c))

* Adapt feature tests ([`72ebace`](https://github.com/molinfo-vienna/nerdd-link/commit/72ebace7f4e9b13d9db02d1f586b3902f63e4381))

* Move data directory step to main code ([`9f04504`](https://github.com/molinfo-vienna/nerdd-link/commit/9f04504ec71a8c2ec293fe4b2814e188ee334206))

* Merge pull request #12 from shirte/main

Add pre-commit hooks ([`0d0b405`](https://github.com/molinfo-vienna/nerdd-link/commit/0d0b405447701cc75f039e762d8439e9c27e0c39))

* Minor changes ([`c78b021`](https://github.com/molinfo-vienna/nerdd-link/commit/c78b021d88fcbb2910878d9adb33707769b6a849))

* Move test code into submodule ([`09dd25d`](https://github.com/molinfo-vienna/nerdd-link/commit/09dd25dec257b19c505e722c40bb0fa85a72f755))

* Run actions in pytest as async with cleanup code ([`ac8639a`](https://github.com/molinfo-vienna/nerdd-link/commit/ac8639aac841c6a6c11de4d19a7d9e6f4c50ce17))

* Reimplement DummyChannel correctly ([`7c0b9bf`](https://github.com/molinfo-vienna/nerdd-link/commit/7c0b9bf73822972ec1649ba7adb70166a06fdb81))

* Avoid mocked communication channel step ([`d2a34ac`](https://github.com/molinfo-vienna/nerdd-link/commit/d2a34ac0898bd121764bd2b8f0f195c98e6cf8b8))

* Use AsyncIterable instead of AsyncIterator ([`77db952`](https://github.com/molinfo-vienna/nerdd-link/commit/77db9527af5b1824b04795daa6c87e6df280d7d4))

* Add waiting step in tests ([`cff0147`](https://github.com/molinfo-vienna/nerdd-link/commit/cff01475480805b1aa87db5b2b7d019fbad518fd))

* Make cli commands async ([`1a48ca9`](https://github.com/molinfo-vienna/nerdd-link/commit/1a48ca9c68c9ba1a3bf450b3e485c30715ea2c64))

* Rename start to run ([`2f79b29`](https://github.com/molinfo-vienna/nerdd-link/commit/2f79b296f8ad5b984c950160cb8b316a6c0f2581))

* Run tests in pull requests ([`f41bc77`](https://github.com/molinfo-vienna/nerdd-link/commit/f41bc77040632b1a45a8c22f9fbefe6dd1372830))

* Increase ruff version ([`5228e8c`](https://github.com/molinfo-vienna/nerdd-link/commit/5228e8c2bfc106a61160aaf5b763a779bed4e3ce))

* Add submodules to main __init__ ([`923fc47`](https://github.com/molinfo-vienna/nerdd-link/commit/923fc47516576d58727a4e1daaf457533951f532))

* Add pre-commit hook ([`1ad6c65`](https://github.com/molinfo-vienna/nerdd-link/commit/1ad6c65054fb473db10aa139bd5ff5b546d638fb))

* Merge pull request #11 from shirte/main

Add async_to_sync helper function ([`d610da8`](https://github.com/molinfo-vienna/nerdd-link/commit/d610da8fe1ae8a09c2b4f8543fb583369dce19a3))

* Add async_to_sync helper function ([`5e61635`](https://github.com/molinfo-vienna/nerdd-link/commit/5e616358326823d28fba9721b48c5a91e2edf893))

* Merge pull request #10 from shirte/main

Downgrade aiokafka dependency ([`0da06ec`](https://github.com/molinfo-vienna/nerdd-link/commit/0da06ec2192b98cc335bca1774129f471d71a643))

* Downgrade aiokafka dependency ([`59677b7`](https://github.com/molinfo-vienna/nerdd-link/commit/59677b72e1ad8eadb1a23cc2b3d51cb29706479b))


## v0.0.0 (2024-11-21)

### Unknown

* Merge pull request #9 from shirte/main

Make code async ([`fddda99`](https://github.com/molinfo-vienna/nerdd-link/commit/fddda9921d75bda2f367fe88d6612dbb7e4ef242))

* Lint code ([`0bd6459`](https://github.com/molinfo-vienna/nerdd-link/commit/0bd6459a5b3933c4de8b88cb4645e6954d187ca7))

* Format code ([`e513022`](https://github.com/molinfo-vienna/nerdd-link/commit/e51302259d99727473ea7e8a0d16a70406d38980))

* Adapt tests to async code ([`090ea42`](https://github.com/molinfo-vienna/nerdd-link/commit/090ea42636284407b18b38f93be40150d602f49e))

* Let cli run async code ([`87ea9e2`](https://github.com/molinfo-vienna/nerdd-link/commit/87ea9e2fd7ce3346347c035e43f31af7e3cde5bc))

* Make actions async ([`a778c03`](https://github.com/molinfo-vienna/nerdd-link/commit/a778c03de6c8af15e85078c304eae74ed71fe7ce))

* Make channels async ([`60aade0`](https://github.com/molinfo-vienna/nerdd-link/commit/60aade046fe482a0b3cb0aec9da82bb31f6d3eca))

* Add aiokafka to pyproject.toml ([`af1bfa0`](https://github.com/molinfo-vienna/nerdd-link/commit/af1bfa0ccf92d869995e2b0dc79480b78863f57f))

* Merge pull request #8 from shirte/main

Simplify StructureJsonReader ([`42ca896`](https://github.com/molinfo-vienna/nerdd-link/commit/42ca896d4b3f564f8815f72340752fa70c21161f))

* Move py.typed file into package ([`daaf6fc`](https://github.com/molinfo-vienna/nerdd-link/commit/daaf6fccf121485000818503c781f9331889320f))

* Simplify StructureJsonReader ([`538a628`](https://github.com/molinfo-vienna/nerdd-link/commit/538a62871949c45f4942de8ebe8cd4b9843db794))

* Always import StructureJsonReader ([`d0ef8cd`](https://github.com/molinfo-vienna/nerdd-link/commit/d0ef8cda59dd9781ef1e3114778534aafa3ec233))

* Merge pull request #7 from shirte/main

Add semantic release ([`d2e2354`](https://github.com/molinfo-vienna/nerdd-link/commit/d2e2354db5df029582cb9a29165c46365540abf3))

* Format code ([`112cf1a`](https://github.com/molinfo-vienna/nerdd-link/commit/112cf1a10abf9a8e3c9cbc210fef11921f33c2b5))

* Convert messaes to pydantic models ([`1a21ee2`](https://github.com/molinfo-vienna/nerdd-link/commit/1a21ee21c39396db782abdd93f545e309cd57203))

* Treat configs as pydantic models ([`6f63315`](https://github.com/molinfo-vienna/nerdd-link/commit/6f63315542e045f2e4efc20b53a8b44a1ab453f7))

* Enable semantic release ([`b8445b6`](https://github.com/molinfo-vienna/nerdd-link/commit/b8445b6e265512e1571c7a5f749b0ecaf3cdf5f4))

* Allow low versions of pydantic ([`0361ec4`](https://github.com/molinfo-vienna/nerdd-link/commit/0361ec44f502fa88ef8e3cc7a2133e0c9019b790))

* Add pypi publishing action ([`a66964d`](https://github.com/molinfo-vienna/nerdd-link/commit/a66964ddb5f67afd2f1825470e6a1be0265df429))

* Add linting to github actions ([`5a75a56`](https://github.com/molinfo-vienna/nerdd-link/commit/5a75a5602e7e465692fff10365afdae759f9ddb5))

* Lint project ([`024898b`](https://github.com/molinfo-vienna/nerdd-link/commit/024898b22d04bbdd470844d5664e55799d5c3e5b))

* Merge pull request #6 from shirte/main

Add format check to github actions ([`392e246`](https://github.com/molinfo-vienna/nerdd-link/commit/392e246fc06d980ccc5dc55d7065819839896aed))

* Add format check to github actions ([`fdf3118`](https://github.com/molinfo-vienna/nerdd-link/commit/fdf311897dccae9b59932e682ba10ebadec55079))

* Format all files ([`9553862`](https://github.com/molinfo-vienna/nerdd-link/commit/9553862b9be6c8e552d0489136ad9b533a4a155c))

* Merge pull request #5 from shirte/main

Use consumer groups ([`45745d2`](https://github.com/molinfo-vienna/nerdd-link/commit/45745d2607cec8694434d0b246ca87110af0aa2d))

* Use consumer groups ([`1648fef`](https://github.com/molinfo-vienna/nerdd-link/commit/1648fef310c9815497bcb0682db58e882bbc9c31))

* Merge pull request #4 from shirte/main

Add files ([`d07a87d`](https://github.com/molinfo-vienna/nerdd-link/commit/d07a87d582c4a721fc1d00aa58253284cceb718c))

* Add structure json reader ([`57c0f97`](https://github.com/molinfo-vienna/nerdd-link/commit/57c0f9756e7be93b2a58a8f553fc34ba377b23ed))

* Add write output action ([`b66a157`](https://github.com/molinfo-vienna/nerdd-link/commit/b66a15713c2ecc7599a8de42d066cab869ab7ea4))

* Merge pull request #3 from shirte/main

Switch to pyproject.toml ([`ae85903`](https://github.com/molinfo-vienna/nerdd-link/commit/ae859039684645d55acfc13ec14a953a86137893))

* Convert setup.py to pyproject.toml ([`09fbab1`](https://github.com/molinfo-vienna/nerdd-link/commit/09fbab188f4df0adf00cc5a638b26486e5b0a6ff))

* Add py.typed file ([`04cd82c`](https://github.com/molinfo-vienna/nerdd-link/commit/04cd82c64969b6495cb9de683eb68e0e8905b777))

* Merge pull request #2 from shirte/main

Rename project to nerdd-link ([`98ca5b7`](https://github.com/molinfo-vienna/nerdd-link/commit/98ca5b705c4fd8556cca321944d8c02148d4f8af))

* Move and rewrite tests ([`b14b0f7`](https://github.com/molinfo-vienna/nerdd-link/commit/b14b0f7f9d436088ed873dfc28b435b31e10a3f5))

* Add message types ([`c644d91`](https://github.com/molinfo-vienna/nerdd-link/commit/c644d9196e44de3a5bb4424b39da99d6799e5604))

* Add utility functions ([`42c4ce1`](https://github.com/molinfo-vienna/nerdd-link/commit/42c4ce138d473d36dabe509f56b1a2b8a85eeaac))

* Add CLI classes ([`126feda`](https://github.com/molinfo-vienna/nerdd-link/commit/126feda08129cecba60e8935b9be5812765626bd))

* Move code to nerdd-link ([`3eecd8a`](https://github.com/molinfo-vienna/nerdd-link/commit/3eecd8aaf492331ad7c722d88ed8441263ce1496))

* Let PredictCheckpointAction write result checkpoints ([`9906cc8`](https://github.com/molinfo-vienna/nerdd-link/commit/9906cc8b00c10165374aa99cc8fa7e3b177d3ee5))

* Add helper classes ([`cc69d65`](https://github.com/molinfo-vienna/nerdd-link/commit/cc69d65e808422d8f8e92d0e5e9a0540d74e02d6))

* Rename project to nerdd-link ([`f122bac`](https://github.com/molinfo-vienna/nerdd-link/commit/f122bac7df0cf26726bfe4769e641ecc08a9e426))

* Merge pull request #1 from shirte/main

Provide basic project structure ([`e8b795c`](https://github.com/molinfo-vienna/nerdd-link/commit/e8b795c50f732b20cbdfb8ae51c55075ade893c2))

* Implement kafka channel ([`fa47d00`](https://github.com/molinfo-vienna/nerdd-link/commit/fa47d00536e008ab88373db815218a1d39cd3643))

* Add channel base class ([`aafc823`](https://github.com/molinfo-vienna/nerdd-link/commit/aafc8237ee2a4801e6ea8b5f09699f7a0a64e298))

* Add empty implementation for write output action ([`a609c32`](https://github.com/molinfo-vienna/nerdd-link/commit/a609c32e0f42e14dfaa25d7d7cbadcd49c3ab3c5))

* Implement register module action ([`0f3448a`](https://github.com/molinfo-vienna/nerdd-link/commit/0f3448a3bceeee44b2060fa2a991925999eddd75))

* Implement process jobs action ([`280bcfb`](https://github.com/molinfo-vienna/nerdd-link/commit/280bcfb9296c005f12835542cf98338b5a35ad35))

* Implement predict checkpoints action ([`ad67c95`](https://github.com/molinfo-vienna/nerdd-link/commit/ad67c95c843be5362e9d16cde4a8d86fef80b586))

* Add action base class ([`fbfb74b`](https://github.com/molinfo-vienna/nerdd-link/commit/fbfb74bf07b1792cc3aef6b6bb7c86906803be80))

* Add environment.yml ([`3c2963a`](https://github.com/molinfo-vienna/nerdd-link/commit/3c2963a467a3abcd74333e4a80fa73c01d8760fa))

* Add ruff_cache to gitignore ([`4549eab`](https://github.com/molinfo-vienna/nerdd-link/commit/4549eab88204dfeb1f36a8002f4565c4d3db9341))

* Fix test cases ([`0de54ed`](https://github.com/molinfo-vienna/nerdd-link/commit/0de54ed5cc8c08136e3944a754cff7e222a367b2))

* Populate repository ([`35aab5d`](https://github.com/molinfo-vienna/nerdd-link/commit/35aab5d50016b23b1524883fa37bd49b6fcc3a01))

* Initial commit ([`561e9f0`](https://github.com/molinfo-vienna/nerdd-link/commit/561e9f000d266e1acc80f207ca8759f0dc8be051))
