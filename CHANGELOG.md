# CHANGELOG


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
