# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
## Unreleased

<small>[Compare with latest](https://gitlab.com/ikus-soft/rdiffweb/compare/6.2.5...HEAD)</small>

### Added

- sqlite: add PRAGMA synchronous=NORMAL on connect ([335e50f](https://gitlab.com/ikus-soft/rdiffweb/commit/335e50f5fd4ef71be9f412d41781d14a5542c0c0) by Patrik Dufresne).
- deps: add jinjax dependency with broken version exclusion ([933413b](https://gitlab.com/ikus-soft/rdiffweb/commit/933413b6c486ae8db1c8cba39c15fcf78105415c) by Patrik Dufresne).
- debian: add dedicated log directory for rdiffweb ([b620a7a](https://gitlab.com/ikus-soft/rdiffweb/commit/b620a7a76c1b9c1c08118d540d28f8dba02b10ea) by Patrik Dufresne).
- audit: add author_username column to Message model and remove author join ([4a73c6d](https://gitlab.com/ikus-soft/rdiffweb/commit/4a73c6d7c0c5428139c7619c102fa19a747ffe3d) by Patrik Dufresne).
- tokens: add validation for token name format and length ([62deae5](https://gitlab.com/ikus-soft/rdiffweb/commit/62deae571168b7e4c16bdffaa6b95829c51fd2cc) by Patrik Dufresne).
- css: add primary border subtle color variable using color-mix ([23b9e3d](https://gitlab.com/ikus-soft/rdiffweb/commit/23b9e3d698c9791b3e2aeb0142e8e558cc8a490f) by Patrik Dufresne).
- debian: add PEP440 version matching for cherrypy-foundation dependency ([877a49f](https://gitlab.com/ikus-soft/rdiffweb/commit/877a49f1614a9e0c29e4dbd344536a8b71aaa11f) by Patrik Dufresne).
- db: add clear_sessions() call before async database operations ([3907e94](https://gitlab.com/ikus-soft/rdiffweb/commit/3907e94a72ae4e8c7a1ebf573c7377da3e8e75bf) by Patrik Dufresne).
- stats: add condition for 'new' state ([faf4cad](https://gitlab.com/ikus-soft/rdiffweb/commit/faf4cadb18b091b665aaa9ef09e74cfee1ad4bb4) by Patrik Dufresne).
- jinja2: add auto_reload support in debug and development mode ([8323cea](https://gitlab.com/ikus-soft/rdiffweb/commit/8323cea058b76aa400ac16a6b1de99cbad2069d4) by Patrik Dufresne).
- sonar: add issue ignore rules for HTML templates ([99069fb](https://gitlab.com/ikus-soft/rdiffweb/commit/99069fbdf9736639a608525b4aa90fedd9c1de0c) by Patrik Dufresne).
- notification: add disk usage threshold and check latest options ([5735c6d](https://gitlab.com/ikus-soft/rdiffweb/commit/5735c6dab74ecb53ef3a96f7155759ba30839aec) by Patrik Dufresne).
- config: add disk-usage-time option to schedule disk usage analysis ([0bbd0e3](https://gitlab.com/ikus-soft/rdiffweb/commit/0bbd0e349bfab7dfa482d3a1875cfa210582f262) by Patrik Dufresne).
- browse: add disk usage size display with source and history breakdown ([ee24768](https://gitlab.com/ikus-soft/rdiffweb/commit/ee247683b0b5573effda2933486768e40c4e4059) by Patrik Dufresne).
- admin: Add a "Refresh repositories" when editing the user ([1910617](https://gitlab.com/ikus-soft/rdiffweb/commit/19106176e77f7d63727a81ed04f3a71c96d78a55) by Patrik Dufresne).
- home: Add back a "Refresh repositories" in home view ([b95b7f2](https://gitlab.com/ikus-soft/rdiffweb/commit/b95b7f2e7d56505f2f4f8993c26dfe868732fc2d) by Patrik Dufresne).
- ci: add GIT_STRATEGY none and improve e2e-test jobs ([8af38ac](https://gitlab.com/ikus-soft/rdiffweb/commit/8af38accd57f9dc4b9db9ff57158a7496415d6ec) by Patrik Dufresne).
- browse: add status column and improve deleted file display ([61ff3af](https://gitlab.com/ikus-soft/rdiffweb/commit/61ff3afc76e677ac29b4896a0200f4a32041d389) by Patrik Dufresne).
- ui: add border and rounded style to table in browse view ([7b7a28b](https://gitlab.com/ikus-soft/rdiffweb/commit/7b7a28beb4d6ec5b03287fea68f8cd9c07cdda54) by Patrik Dufresne).
- packaging: add wtforms and cherrypy-foundation data files to spec ([02ea048](https://gitlab.com/ikus-soft/rdiffweb/commit/02ea048756dd160ff4b0b3bab1fe158dee2903ef) by Patrik Dufresne).
- config: add umask, user, and group configuration options ([81f4820](https://gitlab.com/ikus-soft/rdiffweb/commit/81f4820a8766542551a21a8f4dbdc858359bd52e) by Patrik Dufresne).
- heatmap: add minimum days from edge ([1cfb254](https://gitlab.com/ikus-soft/rdiffweb/commit/1cfb2546c691a4e911b5687c3503a0ec22e99ab0) by Patrik Dufresne).
- settings: add inactivity period field and overdue/inactive status checks ([3905ae8](https://gitlab.com/ikus-soft/rdiffweb/commit/3905ae8d433b85fdbc6118c1dcf695baf72e073d) by Patrik Dufresne).
- ui: add support for jinjax render_assets ([9c24389](https://gitlab.com/ikus-soft/rdiffweb/commit/9c24389bf2dfe1f84cdee0c5ac4a7c0ace4f8bbe) by Patrik Dufresne).
- ui: add color modes ([642a6f7](https://gitlab.com/ikus-soft/rdiffweb/commit/642a6f7a396de4cdf159b04919a89b55b31e8408) by Patrik Dufresne).
- Add breadcrumb to the layout ([75c046a](https://gitlab.com/ikus-soft/rdiffweb/commit/75c046abc99f88faf00f9f60cf209628436d5acd) by Patrik Dufresne).

### Fixed

- main: fix jinjax logger verbosity in debug mode ([2bdaa46](https://gitlab.com/ikus-soft/rdiffweb/commit/2bdaa46bc9bba4d25b38f646ca5cee3579ecc7ae) by Patrik Dufresne).
- admin_session: fix icons shown when session time values are missing ([cbe171a](https://gitlab.com/ikus-soft/rdiffweb/commit/cbe171a4450eecf876b143837a0befb03e36a435) by Patrik Dufresne).
- diskusage: fix skip disk usage scan for non-existent repository folder ([7e2979c](https://gitlab.com/ikus-soft/rdiffweb/commit/7e2979c68a8ad753d55331df56e7ac7332e808d0) by Patrik Dufresne).
- sidebar: fix text truncation and add tooltip for repository name ([576d8da](https://gitlab.com/ikus-soft/rdiffweb/commit/576d8da696d1e2fb6c097d1b62d5ebb52ed6793c) by Patrik Dufresne).
- diskusage: fix typo in `_update_disk_usage` self parameter name ([33d215f](https://gitlab.com/ikus-soft/rdiffweb/commit/33d215f5b6031e649190ec7b8f93570782b22633) by Patrik Dufresne).
- controller: fix get_repo_nav_pages to filter by in_menu ([70df694](https://gitlab.com/ikus-soft/rdiffweb/commit/70df694ae757dddacf1ed7b047f7e14e0f07dfa5) by Patrik Dufresne).
- controller: fix shadowing of built-in id in PageRegistry methods ([0908e8c](https://gitlab.com/ikus-soft/rdiffweb/commit/0908e8c27213146f2330f59d27d525dd32032161) by Patrik Dufresne).
- ci: fix sonar scanner configuration ([26d4e88](https://gitlab.com/ikus-soft/rdiffweb/commit/26d4e88f81024769b1d9ad0c02dace3535ef69cc) by Patrik Dufresne).
- ci: fix coverage report ([061b7f0](https://gitlab.com/ikus-soft/rdiffweb/commit/061b7f0b395df74f4b0d962b683818461dce84c7) by Patrik Dufresne).
- repo: fix sonarqube issues ([5ecfc22](https://gitlab.com/ikus-soft/rdiffweb/commit/5ecfc2263636ea0131f911b73e3882a2e4e79265) by Patrik Dufresne).
- home: fix N+1 query by using lazy loading ([215ec9e](https://gitlab.com/ikus-soft/rdiffweb/commit/215ec9eb5af1a094e4fa9f608a4f92cf141e0d85) by Patrik Dufresne).
- admin/users: fix N+1 query by using joinedload for user relations ([80032cb](https://gitlab.com/ikus-soft/rdiffweb/commit/80032cbe6581863c44a4b5a7c47b9d077540b868) by Patrik Dufresne).
- admin_users: fix table cell alignment and mfa title rendering ([31df493](https://gitlab.com/ikus-soft/rdiffweb/commit/31df4939b29f2f366de33f6952170c7aecb808e0) by Patrik Dufresne).
- minarca-server: fix unit test execution ([9a22e5b](https://gitlab.com/ikus-soft/rdiffweb/commit/9a22e5bcdd630842d14b3efb88e8f85715677147) by Patrik Dufresne).
- minarca-server: fix pyproject.toml deps ([22c1c4c](https://gitlab.com/ikus-soft/rdiffweb/commit/22c1c4c0929ec66e2d032796d7f3cd4af89dad49) by Patrik Dufresne).
- layout: fix layout for error page without session ([1accf5f](https://gitlab.com/ikus-soft/rdiffweb/commit/1accf5f0a995d1a39997bb35c695438016202440) by Patrik Dufresne).
- ui: fix badge background ([6a7e71e](https://gitlab.com/ikus-soft/rdiffweb/commit/6a7e71e32dcef29d6a6f9870938c0712f15cde1d) by Patrik Dufresne).
- test: fix check links to handle anchor tags ([c1518c6](https://gitlab.com/ikus-soft/rdiffweb/commit/c1518c66d7e124782c8773a657bca958101e5ea5) by Patrik Dufresne).
- ui, notification: fix layout of report form ([6af8127](https://gitlab.com/ikus-soft/rdiffweb/commit/6af81278d04b8dbe3865e18f7480849e05dc0d6e) by Patrik Dufresne).
- Fix text overflow in sidebar ([34f2efa](https://gitlab.com/ikus-soft/rdiffweb/commit/34f2efac094acc676c74bedf9b8e56b16e9a4f9b) by Patrik Dufresne).

### Changed

- history: change limit to 100 ([01f5d2d](https://gitlab.com/ikus-soft/rdiffweb/commit/01f5d2de671a69f4ca51f1339de238e7503e96b7) by Patrik Dufresne).
- admin_sysinfo: change <td> to <th> for row header cells ([8012969](https://gitlab.com/ikus-soft/rdiffweb/commit/8012969405d2e00620248b05ec718cb29c10a3cc) by Patrik Dufresne).
- packaging: change privilege drop from systemd to config file ([9ac0358](https://gitlab.com/ikus-soft/rdiffweb/commit/9ac0358df9cf3f46cdf3533902bf0ba65c0b2d75) by Patrik Dufresne).
- home: change storage usage display to use repo objects with detailed size breakdown ([918a7b0](https://gitlab.com/ikus-soft/rdiffweb/commit/918a7b0030036539bfffb66ab80042a3b5738f05) by Patrik Dufresne).
- templates: change sticky header to span full width ([775cdf7](https://gitlab.com/ikus-soft/rdiffweb/commit/775cdf76c078ec1e37eaab775315789005cae02b) by Patrik Dufresne).
- ui: change datatable filter buttons styling and layout consistency ([6c54e89](https://gitlab.com/ikus-soft/rdiffweb/commit/6c54e899e43169d2f68c2fcaae8bf56872267c8b) by Patrik Dufresne).
- home: change "Backups" to "Repositories" in home and sidebar templates ([7f3bee3](https://gitlab.com/ikus-soft/rdiffweb/commit/7f3bee3f4cb27fcdda9b22a6080d06f96b53f18a) by Patrik Dufresne).
- ui: change KpiCard background to bg-light ([dbbbe89](https://gitlab.com/ikus-soft/rdiffweb/commit/dbbbe8986896cf75a70725aa13bacabec44b9344) by Patrik Dufresne).
- ui: change RepoCard and RepoStatus component styling ([2ad3e0b](https://gitlab.com/ikus-soft/rdiffweb/commit/2ad3e0ba615af692e1d5be341084f2177db8132b) by Patrik Dufresne).
- scheduler: change job identifiers from strings to callable references ([1485e3f](https://gitlab.com/ikus-soft/rdiffweb/commit/1485e3fb3829eb586035b93ab6a5147f8736867d) by Patrik Dufresne).
- templates: change table styling and layout improvements ([462ce98](https://gitlab.com/ikus-soft/rdiffweb/commit/462ce9818f9da7888ba94fb7421cb16d2e1b35c9) by Patrik Dufresne).
- librdiff: change RdiffTime implementation to be a subclass of datetime ([edf9523](https://gitlab.com/ikus-soft/rdiffweb/commit/edf9523dadaf74d22c221e53901fc6f2e3bd1ee7) by Patrik Dufresne).

### Removed

- minarca: remove unused imports and extend flake8 coverage ([baac400](https://gitlab.com/ikus-soft/rdiffweb/commit/baac4006b1fb41bc0b653719f1d29c18cd91bb85) by Patrik Dufresne).
- rdiffweb: remove ActivityPlugin and inline activity logging into model layer ([bd0e8df](https://gitlab.com/ikus-soft/rdiffweb/commit/bd0e8df445c048549c7b43396502fb476bb54bd1) by Patrik Dufresne).
- code: remove dead code ([ec4e867](https://gitlab.com/ikus-soft/rdiffweb/commit/ec4e867e248e5420320fb38417c326e806a77794) by Patrik Dufresne).
- templates: remove unused & legacy include macros ([c72dbfa](https://gitlab.com/ikus-soft/rdiffweb/commit/c72dbfaefb8e9e10764a79b6961aea0274f317cb) by Patrik Dufresne).
- debian: remove chart.js and chartkick.js symlink handling ([cd568c1](https://gitlab.com/ikus-soft/rdiffweb/commit/cd568c119e01eff2981407c6cce01fa39199d97e) by Patrik Dufresne).
- debian: remove bundled static asset exclusions and symlinks ([9eabd05](https://gitlab.com/ikus-soft/rdiffweb/commit/9eabd05d9952a31a1e826bd6efcff3a98bbccff0) by Patrik Dufresne).
- admin_user_edit: remove redundant empty style attribute ([dcea739](https://gitlab.com/ikus-soft/rdiffweb/commit/dcea73940d8e4987340572c9c0ac3b88a27fc495) by Patrik Dufresne).
- rdw_app: remove unused current_url template variable ([0b85769](https://gitlab.com/ikus-soft/rdiffweb/commit/0b8576948c31fbde32c0f179c73f5980d66c2201) by Patrik Dufresne).
- api_openapi: remove redundant list() call ([04e138d](https://gitlab.com/ikus-soft/rdiffweb/commit/04e138db30e6260e7e47095966fca1d1c503c934) by Patrik Dufresne).
- controller: remove TODO comment ([1c9f8e4](https://gitlab.com/ikus-soft/rdiffweb/commit/1c9f8e4b92abe87920f9e7cdfefeb52d3fd0da78) by Patrik Dufresne).
- controller: remove unused validate function ([af0231e](https://gitlab.com/ikus-soft/rdiffweb/commit/af0231e255fa258dd0c2d86b98f311289035dfc5) by Patrik Dufresne).
- rdwlog: remove duplicate property ([131ddea](https://gitlab.com/ikus-soft/rdiffweb/commit/131ddea0dd015797714694726cea7bfe2fac02c8) by Patrik Dufresne).
- code: remove unused rdw_helpers and related files ([e27cb57](https://gitlab.com/ikus-soft/rdiffweb/commit/e27cb575f773a88261497528a9ce44bd0064af1a) by Patrik Dufresne).
- templating: remove unused attrib helper and related files ([f34b854](https://gitlab.com/ikus-soft/rdiffweb/commit/f34b854d4484724474114dc223a024ea1955d877) by Patrik Dufresne).
- ui: remove checkbox from datatable filter button ([37310fc](https://gitlab.com/ikus-soft/rdiffweb/commit/37310fc6ef02ec624970900d413562dc55c45bfa) by Patrik Dufresne).
- minarca-server: remove `.vscode` folder ([78cb39b](https://gitlab.com/ikus-soft/rdiffweb/commit/78cb39ba3d9f1945750a8befc84759d91534c21b) by Patrik Dufresne).
- ci: remove duplicate sonar-project.properties ([96d887e](https://gitlab.com/ikus-soft/rdiffweb/commit/96d887eedbd8360bc963eb4ff348adf2851ecbb6) by Patrik Dufresne).
- git: remove duplicate gitignore from minarca-server ([0fae165](https://gitlab.com/ikus-soft/rdiffweb/commit/0fae165c5473b27485e81199f12521e8862cd59f) by Patrik Dufresne).
- storage-usage: remove obsolete code ([234a6ab](https://gitlab.com/ikus-soft/rdiffweb/commit/234a6ab2c81812590e7d2ab31ee1a0dbf9ebecf1) by Patrik Dufresne).
- css: remove obsolete rdw-btn-hover css ([0ab8ece](https://gitlab.com/ikus-soft/rdiffweb/commit/0ab8ecea078e8debafae5239aa353e571c127e81) by Patrik Dufresne).
- ui: remove color modes ([30e94fb](https://gitlab.com/ikus-soft/rdiffweb/commit/30e94fb22a2192d54a986e0ee886aaddb8cc489e) by Patrik Dufresne).
- ci: remove ubuntu plucky support ([b12c665](https://gitlab.com/ikus-soft/rdiffweb/commit/b12c665bb27179dfae9a70b4de7ba0b1bdd87140) by Patrik Dufresne).

### Misc

- i18n: update french translations and clean up formatting across templates and controllers ([1ddae4e](https://gitlab.com/ikus-soft/rdiffweb/commit/1ddae4eab622e099583c2e3f875bb286842cdc5a) by Patrik Dufresne).
- templates: replace inline time elements with RdwTime component ([2766ddc](https://gitlab.com/ikus-soft/rdiffweb/commit/2766ddcd8c53b36ae8186f4a6185bf9113fcdbf2) by Patrik Dufresne).
- librdiff: cache _entries property and invalidate on refresh ([ced0d69](https://gitlab.com/ikus-soft/rdiffweb/commit/ced0d69b2b6562ea6028bbdd1e005888b588f89a) by Patrik Dufresne).
- static: move main.css endpoint under /static/ and add cache headers ([20dd8e3](https://gitlab.com/ikus-soft/rdiffweb/commit/20dd8e3ac6c07dc3ed4300c6d1758409f3f0d273) by Patrik Dufresne).
- diskusage: handle unclean session ([7dd3305](https://gitlab.com/ikus-soft/rdiffweb/commit/7dd330539a825c62f530dcff7ae76367a96e4f10) by Patrik Dufresne).
- ui: recover notification page ([0514cb8](https://gitlab.com/ikus-soft/rdiffweb/commit/0514cb87908a12e71fdce7d48378e2dfdff76b5e) by Patrik Dufresne).
- page_admin_users: refactor user lookup into _get_user helper method ([18aaf59](https://gitlab.com/ikus-soft/rdiffweb/commit/18aaf594a765dd062082b5291391e79782575821) by Patrik Dufresne).
- minarca-server: optimize authorized_keys generation using direct query ([a0fa4c2](https://gitlab.com/ikus-soft/rdiffweb/commit/a0fa4c2fcbeab4a6d57ce50bad72e30e4a3bf6dc) by Patrik Dufresne).
- minarca: update branding ([8b18cb5](https://gitlab.com/ikus-soft/rdiffweb/commit/8b18cb5f8115fa25b9da91706b3c1e02739d69ff) by Patrik Dufresne).
- sidebar: show active user's repo ([25fe4b9](https://gitlab.com/ikus-soft/rdiffweb/commit/25fe4b9177fc10d62554026c42eb40d46e5bad5c) by Patrik Dufresne).
- table: Show/hide "Reset" button depending of filter selection ([2885bd1](https://gitlab.com/ikus-soft/rdiffweb/commit/2885bd1e3cf291da233cc6bf9f31c88dc4d9edf2) by Patrik Dufresne).
- sidebar: review color contrast for repo status ([18f1d20](https://gitlab.com/ikus-soft/rdiffweb/commit/18f1d20332d6769cbf6443fd0eac6c1f882b948c) by Patrik Dufresne).
- ui: improve contrast for badges and status indicators ([b40bcf9](https://gitlab.com/ikus-soft/rdiffweb/commit/b40bcf9056c84fbb3393efb2e747ffba41eb5b1c) by Patrik Dufresne).
- minarca: refactor startup sequence to use late_start and db autocreate ([6612756](https://gitlab.com/ikus-soft/rdiffweb/commit/6612756e6fc3261869d89ae82ad6b927879e9ced) by Patrik Dufresne).
- ci: make the pipeline execute for rdiffweb and minarca-server ([9c6fc7c](https://gitlab.com/ikus-soft/rdiffweb/commit/9c6fc7c3fde102d31c6f2877ffb7751562487bd8) by Patrik Dufresne).
- minarca-server: Drop support for rdiff-backup 1.2.8 ([4b9d9a1](https://gitlab.com/ikus-soft/rdiffweb/commit/4b9d9a19da5b75f8eb4c1c76f8dd578453cf0bab) by Patrik Dufresne).
- doc: update SECURITY.md ([58fb257](https://gitlab.com/ikus-soft/rdiffweb/commit/58fb257b04b99303afe7636f6c378edb4285bd46) by Patrik Dufresne).
- Import minarca-server as subfolder ([6aef690](https://gitlab.com/ikus-soft/rdiffweb/commit/6aef6908051cb50a28cc716baf2ac4ba96efb586) by Patrik Dufresne).
- templates: adjust sidebar colors to support light and dark color ([010b551](https://gitlab.com/ikus-soft/rdiffweb/commit/010b551ad04bf0ac0867163edf1a0bbfd1858984) by Patrik Dufresne).
- templates: update email layout ([af38c12](https://gitlab.com/ikus-soft/rdiffweb/commit/af38c122527f53950fec728fa75905962a5118e9) by Patrik Dufresne).
- templates: use configure navbar color for sidebar ([aed76f8](https://gitlab.com/ikus-soft/rdiffweb/commit/aed76f83807653514ff7fefd818b0f6e18833e57) by Patrik Dufresne).
- template: use new widget for report_time_range selection ([97f7f63](https://gitlab.com/ikus-soft/rdiffweb/commit/97f7f634b491c2b3599e1f6b6e3c62e304692e78) by Patrik Dufresne).
- ui: update admin logs page layout ([2270317](https://gitlab.com/ikus-soft/rdiffweb/commit/227031710296e7a6279b8b8234cae8de9f693f56) by Patrik Dufresne).
- ui, update sysinfo page layout ([67eba00](https://gitlab.com/ikus-soft/rdiffweb/commit/67eba00f74a7cc9741fdbb8b2fb0842daabf7f68) by Patrik Dufresne).
- activity: review implementation and layout of all activity view in repo, user and admin ([109a737](https://gitlab.com/ikus-soft/rdiffweb/commit/109a73727b903c058ba0fce063d5ab574ad3c910) by Patrik Dufresne).
- ui: update admin user sessions page layout ([7bba062](https://gitlab.com/ikus-soft/rdiffweb/commit/7bba06224dcf20871d3a5f8974a9652c1b0fa482) by Patrik Dufresne).
- home: sort repositories by name and adjust kpi size ([79b78a0](https://gitlab.com/ikus-soft/rdiffweb/commit/79b78a08e0e779e10734035863d1e4e6f0073be8) by Patrik Dufresne).
- templates: use page registry to render page title ([b4e0fe3](https://gitlab.com/ikus-soft/rdiffweb/commit/b4e0fe32dcb551e5a8d72f0486221ec9e9ebfdf7) by Patrik Dufresne).
- wip: admin users ([b429222](https://gitlab.com/ikus-soft/rdiffweb/commit/b429222057edc830282ad3e2808f8a64bc828579) by Patrik Dufresne).
- ui: update admin repos page layout ([542cf2f](https://gitlab.com/ikus-soft/rdiffweb/commit/542cf2f87e93e0f56e976c966064dd5cb74709cc) by Patrik Dufresne).
- templates: unified RepoStatus to support alter and badge ([b817574](https://gitlab.com/ikus-soft/rdiffweb/commit/b81757453de2cd09813d351aa346d48160d1be4a) by Patrik Dufresne).
- templates: relayout position of repo warnings ([7c02b27](https://gitlab.com/ikus-soft/rdiffweb/commit/7c02b27e6c43ffcbd7f4ba873e4afefd09b6e73c) by Patrik Dufresne).
- templates: use css for second sticky top ([6e7e254](https://gitlab.com/ikus-soft/rdiffweb/commit/6e7e2546689287aac9fbe50aa21e94d849ae9bcd) by Patrik Dufresne).
- templates: adjust container width ([9e9aa9d](https://gitlab.com/ikus-soft/rdiffweb/commit/9e9aa9d625fff9553d44b047e28a5a27ecef777f) by Patrik Dufresne).
- templates: review usage of all RdwIcon ([c6738ab](https://gitlab.com/ikus-soft/rdiffweb/commit/c6738abb54f4511e220f9a8b6c3d9f808c516124) by Patrik Dufresne).
- ui: update admin users page layout ([5b0c705](https://gitlab.com/ikus-soft/rdiffweb/commit/5b0c7051f77cd5a803bfa4d6384f956834a8a07b) by Patrik Dufresne).
- ui: update browser session layout ([b513afa](https://gitlab.com/ikus-soft/rdiffweb/commit/b513afa9f58b05cdd5c519baed60cbd9741d0884) by Patrik Dufresne).
- ui: update mfa page layout ([caa6b66](https://gitlab.com/ikus-soft/rdiffweb/commit/caa6b66f98251b4c5ee2ce99a46557458a27743a) by Patrik Dufresne).
- ui: update access token layout ([369e3cc](https://gitlab.com/ikus-soft/rdiffweb/commit/369e3cc0454fb10a68ab57f31a21e7dcb36f3430) by Patrik Dufresne).
- deps: upgrade cherrpy-foundation and make use of db & db_dession ([d53c5f1](https://gitlab.com/ikus-soft/rdiffweb/commit/d53c5f13e7b37074cb79e31df8467da296728c3a) by Patrik Dufresne).
- ui: adjust sshkeys layout ([aa5d46f](https://gitlab.com/ikus-soft/rdiffweb/commit/aa5d46ff491129126e51782fcfa79c4a9492059a) by Patrik Dufresne).
- ui: adjust css to use primary color branding ([bfe5688](https://gitlab.com/ikus-soft/rdiffweb/commit/bfe5688b06732e11cc968c6c677e49939f61bffc) by Patrik Dufresne).
- repo: avoid using RepoObject orm when updating schema ([0279f22](https://gitlab.com/ikus-soft/rdiffweb/commit/0279f2274da67284f16b78735bb8ba176681d20a) by Patrik Dufresne).
- ui: update account settings layout ([278e0d8](https://gitlab.com/ikus-soft/rdiffweb/commit/278e0d8ab652be7d7a9cacb52226608ccc311681) by Patrik Dufresne).
- ui: update layout of settings pages ([1d1b747](https://gitlab.com/ikus-soft/rdiffweb/commit/1d1b7470e4b52f45d6b6337429495dbea74675e2) by Patrik Dufresne).
- templating: adjust RdwTable layout ([7c8e3ed](https://gitlab.com/ikus-soft/rdiffweb/commit/7c8e3ed1d9fa207036f80fdda806cdff4a80c015) by Patrik Dufresne).
- graphs: adjust layout for smaller screen ([29d4819](https://gitlab.com/ikus-soft/rdiffweb/commit/29d4819a96d30ac0cc5b883ba714344ba8493443) by Patrik Dufresne).
- templating: review css and js sources ([66a8181](https://gitlab.com/ikus-soft/rdiffweb/commit/66a81815fd53ef49c72124fb9118b1f70086a3fc) by Patrik Dufresne).
- ui: adjust login page layout ([b290ca2](https://gitlab.com/ikus-soft/rdiffweb/commit/b290ca226d91ff90fdda626742940f48b5d845be) by Patrik Dufresne).
- templating: replace js-datetime with server-side format_datetime filter ([278ffb2](https://gitlab.com/ikus-soft/rdiffweb/commit/278ffb26c873b0dcf31218e0f97985a75743a24d) by Patrik Dufresne).
- ui: complete redesign of home page ([df909e0](https://gitlab.com/ikus-soft/rdiffweb/commit/df909e05734409f8fee7b1671e7e127202b3cdc4) by Patrik Dufresne).
- deps: bump cherrypy-foundation to v1.4.0 with namespace ([647b1d1](https://gitlab.com/ikus-soft/rdiffweb/commit/647b1d1c53bb27faa1626c403e1f43756a67c888) by Patrik Dufresne).
- graphs: complete review of repo graphs ([0f7127b](https://gitlab.com/ikus-soft/rdiffweb/commit/0f7127b3d54901c5b4a9aefc99548806d75aa605) by Patrik Dufresne).
- stats page: update layout using new components ([9873156](https://gitlab.com/ikus-soft/rdiffweb/commit/98731569b088bae8de231db148dda2d9069532ba) by Patrik Dufresne).
- logs page: adjust display ([7e4ab8f](https://gitlab.com/ikus-soft/rdiffweb/commit/7e4ab8fe0f54e0856393e97afe8d963247e15b6a) by Patrik Dufresne).
- stats page: adjust display ([536029b](https://gitlab.com/ikus-soft/rdiffweb/commit/536029b7b123c58e2c1887bf351a137c5dae4691) by Patrik Dufresne).
- ui: extract repo activity into it own page ([5f42e1a](https://gitlab.com/ikus-soft/rdiffweb/commit/5f42e1a1f46a3eccd6993d5e4cfb1716e4129f76) by Patrik Dufresne).
- browse page: adjust display ([92f9cdd](https://gitlab.com/ikus-soft/rdiffweb/commit/92f9cdd879e477c51e9aca9eb6178ec52660be76) by Patrik Dufresne).
- ui: replace font-awsome by bootstrap-icons ([4008e11](https://gitlab.com/ikus-soft/rdiffweb/commit/4008e11ba4da983f578f9a1cb31d8132837fdbb4) by Patrik Dufresne).
- ui: update to new Datatable implementation ([2489585](https://gitlab.com/ikus-soft/rdiffweb/commit/2489585a79cb25f08cef5d78a6e1b9e13d709322) by Patrik Dufresne).
- ui: update breadcrumb for all pages ([2a13343](https://gitlab.com/ikus-soft/rdiffweb/commit/2a13343547dc5c6d9d281fb423125c407c874d44) by Patrik Dufresne).
- ui: collapse and expand repo, admin and user profile menu based on active page ([9900896](https://gitlab.com/ikus-soft/rdiffweb/commit/9900896702651811e6484186097eaec15a301350) by Patrik Dufresne).
- ui: adjust overflow in sidebar menu ([b1e7877](https://gitlab.com/ikus-soft/rdiffweb/commit/b1e7877f8b89698c33ad8e81efdbe010be4ecec1) by Patrik Dufresne).
- ui: show nothing in navbar when no repositories ([c4d4112](https://gitlab.com/ikus-soft/rdiffweb/commit/c4d4112a5586de5784dced860571238fad2c0363) by Patrik Dufresne).
- ui: update login background image ([0369fa4](https://gitlab.com/ikus-soft/rdiffweb/commit/0369fa40fd3a3087d6bb3af8dc19942de592268b) by Patrik Dufresne).
- ui: use outlined button for OAuth provider(s) ([60b3380](https://gitlab.com/ikus-soft/rdiffweb/commit/60b3380225a60098dd7924c65ab0f40113f567b5) by Patrik Dufresne).
- ui: handle undefine variables for error page ([35eda4b](https://gitlab.com/ikus-soft/rdiffweb/commit/35eda4b9c3599648ecb90be36f745c10fb9daddc) by Patrik Dufresne).
- ui: make use if `class="container"` in User Profile views ([82dbbda](https://gitlab.com/ikus-soft/rdiffweb/commit/82dbbda44695d191423c182ed9393a30fb8c23b8) by Patrik Dufresne).
- ci: reformating ([245e478](https://gitlab.com/ikus-soft/rdiffweb/commit/245e4783ea43e1b05f9c231dc48e2613e7ea2f96) by Patrik Dufresne).
- ci: update black, djlint, isort ([9a42be0](https://gitlab.com/ikus-soft/rdiffweb/commit/9a42be0fb5eefaea25cef08b6a6206e528bed5e0) by Patrik Dufresne).
- ci: define two tox target for `format` and `lint` ([98599cc](https://gitlab.com/ikus-soft/rdiffweb/commit/98599cc46c7c653208fffe97de75881878160af3) by Patrik Dufresne).
- Use a component for the footer ([0b375a5](https://gitlab.com/ikus-soft/rdiffweb/commit/0b375a58dad41fbd6550aee021a87baab79438ed) by Patrik Dufresne).
- Define a new page registry to centralize page label & page icon ([9d3ebe9](https://gitlab.com/ikus-soft/rdiffweb/commit/9d3ebe98c874532317eaf0c39fe027568a78ef71) by Patrik Dufresne).
- Relocate flash messages ([2e6f699](https://gitlab.com/ikus-soft/rdiffweb/commit/2e6f6992d7cafb95c48731b9e292cbd878f8967f) by Patrik Dufresne).
- Update layout to use `<Flash>` component ([b5f9391](https://gitlab.com/ikus-soft/rdiffweb/commit/b5f9391c38b530e9e9e5e56a91df7e12a2ce5bce) by Patrik Dufresne).
- Update navigation layout ([7735b36](https://gitlab.com/ikus-soft/rdiffweb/commit/7735b364afa72974ea5053abbe2771a3a5509c1d) by Patrik Dufresne).
- Update login page layout ([7ca7389](https://gitlab.com/ikus-soft/rdiffweb/commit/7ca738928d20dcf1ee6a3cc8d6d854dbd9d3b65a) by Patrik Dufresne).
- Upgrade to use cherrypy-foundation ([c535fe3](https://gitlab.com/ikus-soft/rdiffweb/commit/c535fe34ebaed15964e88e0cd78258bb11f778d0) by Patrik Dufresne).
- Upgrade to bootstrap v5 ([61b0c50](https://gitlab.com/ikus-soft/rdiffweb/commit/61b0c50f1a6fc421e0d117647ed4728b1047e444) by Patrik Dufresne).
- Updating date in debian/changelog ([5c1e99b](https://gitlab.com/ikus-soft/rdiffweb/commit/5c1e99bee2b4510ccabac88d260972993cf9d08d) by Patrik Dufresne).
- Updating upstream contact in debian/copyright ([3433aef](https://gitlab.com/ikus-soft/rdiffweb/commit/3433aefd117509ad8c76a6fdc4936265a8f58f39) by Patrik Dufresne).
- Update Debian packaging ([40d80fd](https://gitlab.com/ikus-soft/rdiffweb/commit/40d80fdcfb844aa98c151a645698c498551fd837) by Patrik Dufresne).

<!-- insertion marker -->

## [6.2.5](https://gitlab.com/ikus-soft/rdiffweb/tags/6.2.5) - 2026-04-29

<small>[Compare with 6.2.4](https://gitlab.com/ikus-soft/rdiffweb/compare/6.2.4...6.2.5)</small>

### Misc

- ridffweb: bump to 2.11.5 to pre-fill login ([24b5c1a](https://gitlab.com/ikus-soft/rdiffweb/commit/24b5c1a17fb22fdccc2a9a36b4aa50b679179715) by Patrik Dufresne).

## [2.11.5](https://gitlab.com/ikus-soft/rdiffweb/tags/2.11.5) - 2026-04-28

<small>[Compare with 2.11.4](https://gitlab.com/ikus-soft/rdiffweb/compare/2.11.4...2.11.5)</small>

### Added

- login: add support for pre-filling login field via query string parameter ([ffe2bfe](https://gitlab.com/ikus-soft/rdiffweb/commit/ffe2bfea08f4cfe562d166c42ab4a4f050590c82) by Patrik Dufresne).

## [6.2.4](https://gitlab.com/ikus-soft/rdiffweb/tags/6.2.4) - 2026-04-24

<small>[Compare with 6.2.3](https://gitlab.com/ikus-soft/rdiffweb/compare/6.2.3...6.2.4)</small>

### Misc

-  rdiffweb: bump to v2.11.4 to fix foreign key error ([70e98ca](https://gitlab.com/ikus-soft/rdiffweb/commit/70e98ca976347cc2444e1ced0a0e617b59275bce) by Patrik Dufresne).

## [2.11.4](https://gitlab.com/ikus-soft/rdiffweb/tags/2.11.4) - 2026-04-23

<small>[Compare with 2.11.3](https://gitlab.com/ikus-soft/rdiffweb/compare/2.11.3...2.11.4)</small>

### Fixed

- db: fix user deletion raising foreign key errors ([7309658](https://gitlab.com/ikus-soft/rdiffweb/commit/73096587ce3453523d9770ad415d377bb8a46240) by Patrik Dufresne).

### Misc

- ci: pin image pipeline-trigger:2.9.0 ([b31ee73](https://gitlab.com/ikus-soft/rdiffweb/commit/b31ee730bec416b9947f83b2399c6c607f369c18) by Patrik Dufresne).

## [2.11.3](https://gitlab.com/ikus-soft/rdiffweb/tags/2.11.3) - 2026-04-09

<small>[Compare with 2.11.2](https://gitlab.com/ikus-soft/rdiffweb/compare/2.11.2...2.11.3)</small>

### Misc

- Update changelog ([579ce23](https://gitlab.com/ikus-soft/rdiffweb/commit/579ce233777e2e08e231fee7afb85c6226aeb31b) by Patrik Dufresne).
- api: restrict /api/users endpoint to administrators only ([b4ad4db](https://gitlab.com/ikus-soft/rdiffweb/commit/b4ad4dbf3cfc691d488b378afc4ee0308345f0fa) by Patrik Dufresne).

## [6.2.3](https://gitlab.com/ikus-soft/rdiffweb/tags/6.2.3) - 2026-04-09

<small>[Compare with 6.2.2](https://gitlab.com/ikus-soft/rdiffweb/compare/6.2.2...6.2.3)</small>

### Misc

- deps: bump rdiffweb to v2.11.3 ([9f7a3e0](https://gitlab.com/ikus-soft/rdiffweb/commit/9f7a3e036fbac4a2ac07b1ac9c59c43195ef4ac0) by Patrik Dufresne).
- rdiffweb: bump to v2.11.2 ([6fd6a3e](https://gitlab.com/ikus-soft/rdiffweb/commit/6fd6a3e88193ef6df9543a97f60ca8d8f55a9586) by Patrik Dufresne).
- ci: replace pipeline-trigger image ([206a09d](https://gitlab.com/ikus-soft/rdiffweb/commit/206a09d278026c4c593ae3a58abbe78d5392faab) by Patrik Dufresne).

## [2.11.2](https://gitlab.com/ikus-soft/rdiffweb/tags/2.11.2) - 2026-04-07

<small>[Compare with 2.11.1](https://gitlab.com/ikus-soft/rdiffweb/compare/2.11.1...2.11.2)</small>

### Fixed

- smtp: fix encoding for email_from ([7f25368](https://gitlab.com/ikus-soft/rdiffweb/commit/7f253685aa8e07181a12ee7dbd4b2ee084ebf699) by Patrik Dufresne).

## [6.2.2](https://gitlab.com/ikus-soft/rdiffweb/tags/6.2.2) - 2026-03-18

<small>[Compare with 6.2.1](https://gitlab.com/ikus-soft/rdiffweb/compare/6.2.1...6.2.2)</small>

### Misc

- rdiffweb: bump to v2.11.1 to fix argparse issue ([113611d](https://gitlab.com/ikus-soft/rdiffweb/commit/113611d72d76c887be5dc00d60353cb53ce6c64c) by Patrik Dufresne).

## [2.11.1](https://gitlab.com/ikus-soft/rdiffweb/tags/2.11.1) - 2026-03-11

<small>[Compare with 2.11.0](https://gitlab.com/ikus-soft/rdiffweb/compare/2.11.0...2.11.1)</small>

### Added

- fix: add support for configargparse >= 1.7.5 ([cbaf13a](https://gitlab.com/ikus-soft/rdiffweb/commit/cbaf13a3c7533ce21efab450b82c8213d624f550) by Patrik Dufresne).
- Add release date to changelog ([fb2915d](https://gitlab.com/ikus-soft/rdiffweb/commit/fb2915d18b161477ea42c7ba5eb2aa806c89f7cd) by Patrik Dufresne).

### Misc

- fix: bookwork test by pinning setuptools version ([ff517f1](https://gitlab.com/ikus-soft/rdiffweb/commit/ff517f141ba66be5bd7290ce115c7f089b8e1131) by Patrik Dufresne).

## [6.2.1](https://gitlab.com/ikus-soft/rdiffweb/tags/6.2.1) - 2026-02-27

<small>[Compare with 6.2.0](https://gitlab.com/ikus-soft/rdiffweb/compare/6.2.0...6.2.1)</small>

### Fixed

- Fix permissions set on /etc/minarca, /var/log & /var/lib/minarca during installation ([2c3bae4](https://gitlab.com/ikus-soft/rdiffweb/commit/2c3bae42925635e8882cab735658ddcacc448f00) by Patrik Dufresne).

## [6.2.0](https://gitlab.com/ikus-soft/rdiffweb/tags/6.2.0) - 2026-01-14

<small>[Compare with 6.1.3](https://gitlab.com/ikus-soft/rdiffweb/compare/6.1.3...6.2.0)</small>

### Added

- Add changelog entry for 6.2.0 ([8243344](https://gitlab.com/ikus-soft/rdiffweb/commit/8243344268b79bcc1a6de6b7e8d242798200989f) by Patrik Dufresne).

### Removed

- Remove `chattr` call on quota update ([b584394](https://gitlab.com/ikus-soft/rdiffweb/commit/b5843941098989c7c8bc620be298534454cc9a6f) by Patrik Dufresne).
- Remove `pkg_resources` dependency ([6edf600](https://gitlab.com/ikus-soft/rdiffweb/commit/6edf60090c1f089c20df681dd05e9945d88319fd) by Patrik Dufresne).

### Misc

- Upgrade rdiffweb to 2.11.0 ([0cb62e7](https://gitlab.com/ikus-soft/rdiffweb/commit/0cb62e727ecf0f2405c8722ee6b0159e46e3352a) by Patrik Dufresne).
- Update Copyright ([7d2c184](https://gitlab.com/ikus-soft/rdiffweb/commit/7d2c1842b483ba1aedbed42ee0c3e78556b8d095) by Patrik Dufresne).
- Upgrade rdiffweb to 2.11.0b5 ([79d841f](https://gitlab.com/ikus-soft/rdiffweb/commit/79d841f6bf2adf3726e0e68e0224d2ba18f98caf) by Patrik Dufresne).
- Upgrade rdiffweb to 2.11.0b4 ([1597a17](https://gitlab.com/ikus-soft/rdiffweb/commit/1597a178e48036a93d3b2a3f158027a70525d91d) by Patrik Dufresne).
- Upgrade rdiffweb to 2.11.0b3 ([3a5fc0c](https://gitlab.com/ikus-soft/rdiffweb/commit/3a5fc0c16b0e85e4c3625fcfc8d52d2de55d1d77) by Patrik Dufresne).
- Upgrade rdiffweb to 2.11.0b2 ([552f3a9](https://gitlab.com/ikus-soft/rdiffweb/commit/552f3a9f0a2a2fc2222abd634c3c7f3cafbadd9c) by Patrik Dufresne).
- Update docker documentation ([3f1e7ee](https://gitlab.com/ikus-soft/rdiffweb/commit/3f1e7eeb6423a8a4cd970ed6296e26570bdb27d8) by Patrik Dufresne).
- Stop capturing last log lines ([6e2ed4f](https://gitlab.com/ikus-soft/rdiffweb/commit/6e2ed4f4fb8f737cd873c4e53eaee5261f69620f) by Patrik Dufresne).
- Upgrade rdiffweb to 2.11.0b1 ([1ca3a9f](https://gitlab.com/ikus-soft/rdiffweb/commit/1ca3a9f70600ce7c1ea658b83df9a5949428a3df) by Patrik Dufresne).
- Upgrade pyinstaller to v7 ([b80974f](https://gitlab.com/ikus-soft/rdiffweb/commit/b80974f12cef70af1bb5f30e16d6c00c292f2ff7) by Patrik Dufresne).
- Update tzlocal ([47cb037](https://gitlab.com/ikus-soft/rdiffweb/commit/47cb0375c8cdcfd41942729d811a289e11369b39) by Patrik Dufresne).
- Update gitignore ([fc0ec0b](https://gitlab.com/ikus-soft/rdiffweb/commit/fc0ec0bf7661bcd0ac7507a65ce199e1b2732a57) by Patrik Dufresne).

## [2.11.0](https://gitlab.com/ikus-soft/rdiffweb/tags/2.11.0) - 2026-01-07

<small>[Compare with 2.10.5](https://gitlab.com/ikus-soft/rdiffweb/compare/2.10.5...2.11.0)</small>

### Added

- Add logging to `delete_user_with_data` job ([d319a9d](https://gitlab.com/ikus-soft/rdiffweb/commit/d319a9d863f78b3cf1377e8c67815e677ab19659) by Patrik Dufresne).
- Add release note ([ad0d3a3](https://gitlab.com/ikus-soft/rdiffweb/commit/ad0d3a335860b1f6a11985404cde83b20dc3a6b4) by Patrik Dufresne).
- Add activity log #345 ([e1c7675](https://gitlab.com/ikus-soft/rdiffweb/commit/e1c767569a85e6e3fea11e04aebddae062badad2) by Patrik Dufresne).
- Add foundation for audit log #345 ([66e9aa2](https://gitlab.com/ikus-soft/rdiffweb/commit/66e9aa2dcfabc22b80c8d20fc1254d2f8b89f214) by Patrik Dufresne).
- Add PT-BR translation ([1a98579](https://gitlab.com/ikus-soft/rdiffweb/commit/1a98579c9f709eda2c9f3e873be76434b7655458) by Eduardo Mozart de Oliveira).
- Add python 3.13 support (for trixie) ([4b0ee63](https://gitlab.com/ikus-soft/rdiffweb/commit/4b0ee637acad2b645b8a46386a319c78415a7e14) by Patrik Dufresne).
- Adding OAuth autentication support ([5d5dedb](https://gitlab.com/ikus-soft/rdiffweb/commit/5d5dedbfb048aac04452bd42f7f7713ddbe9a504) by Patrik Dufresne).

### Fixed

- Fix exception raised for invalid locale identifier ([17c6d10](https://gitlab.com/ikus-soft/rdiffweb/commit/17c6d10a5a50d46218649c708a030e6f43d6620e) by Patrik Dufresne).
- Fix token impersonation vulnerability ([4ce35fc](https://gitlab.com/ikus-soft/rdiffweb/commit/4ce35fc2d23ac1cc789186f32bf76603b2eddeb3) by Patrik Dufresne).
- Fix selenium execution with bookworm ([1fd8db3](https://gitlab.com/ikus-soft/rdiffweb/commit/1fd8db32b9eb738168f5b1b126f020652674be9d) by Patrik Dufresne).
- Fix doc upload #337 ([6d7219b](https://gitlab.com/ikus-soft/rdiffweb/commit/6d7219bd4348ad28e1704a4d708111751151fddc) by Patrik Dufresne).

### Removed

- Remove all deprecation warnings ([a412feb](https://gitlab.com/ikus-soft/rdiffweb/commit/a412febfdeabce9be06351f0fc7a44673c83bb24) by Patrik Dufresne).
- Remove Debian bullseye as it required backwork which is EOL ([8e55502](https://gitlab.com/ikus-soft/rdiffweb/commit/8e555028ce096586875a3261fdfafe97fa428705) by Patrik Dufresne).

### Misc

- Remove superfluous logging: using cache entries. ([75bd6fd](https://gitlab.com/ikus-soft/rdiffweb/commit/75bd6fdaf805ce5866fb1f19b52f4896b8ecd71b) by Patrik Dufresne).
- Update french translation #350 ([b817298](https://gitlab.com/ikus-soft/rdiffweb/commit/b8172985acfb5cfcdd1c1485311daec4eb2c2332) by Patrik Dufresne).
- Update Ldap plugin ([9cc2e1f](https://gitlab.com/ikus-soft/rdiffweb/commit/9cc2e1f75dbb1743e6f909f20cbc0024f0654427) by Patrik Dufresne).
- Update tools and plugins from cherrypy-foundation ([34d39f6](https://gitlab.com/ikus-soft/rdiffweb/commit/34d39f67ce3b3936a1a80be206c3b7ed759f632e) by Patrik Dufresne).
- Deploy trixie package in dev ([3db4e26](https://gitlab.com/ikus-soft/rdiffweb/commit/3db4e2698050645babff545b514b7734ac371735) by Patrik Dufresne).
- Update french translation ([4f5f534](https://gitlab.com/ikus-soft/rdiffweb/commit/4f5f5346829ed62d1347d67278a3199684bc163d) by Patrik Dufresne).
- Allow administrator to disable a user account #313 ([a5dee3e](https://gitlab.com/ikus-soft/rdiffweb/commit/a5dee3ee4e2400871ec55d60b244954b6c1b4f18) by Patrik Dufresne).
- Update login page ([69df53c](https://gitlab.com/ikus-soft/rdiffweb/commit/69df53c93fdcb01b214e051601bd3c0d7353a478) by Patrik Dufresne).
- Allow deleting user with or without data #335 ([4964b6f](https://gitlab.com/ikus-soft/rdiffweb/commit/4964b6f1f785e837b58c25fbd4c6cbddcab68b28) by Patrik Dufresne).
- Verify Oauth URL #339 ([311fac5](https://gitlab.com/ikus-soft/rdiffweb/commit/311fac53b096f2b4922b0a0bcf0f0e85e634c800) by Patrik Dufresne).
- Rename `userid` and `repoid` into `id` ([db15215](https://gitlab.com/ikus-soft/rdiffweb/commit/db152153785314ee77d899e1c30f213cfb6ecd2c) by Patrik Dufresne).
- Upgrade implementation of SQL timestamp ([7c46537](https://gitlab.com/ikus-soft/rdiffweb/commit/7c46537f6af35d86175b71865253586f1e1ee66f) by Patrik Dufresne).
- Update RestAPI plugins copyright ([606792f](https://gitlab.com/ikus-soft/rdiffweb/commit/606792fd43f7f20ffc652fa4bd7d0c65224a3d07) by Patrik Dufresne).
- Update copyright signatures ([1ca58c0](https://gitlab.com/ikus-soft/rdiffweb/commit/1ca58c02f43e6783172cce7d9e8c0928c8fd9dec) by Patrik Dufresne).
- Pin cheroot<11 ([26d99fd](https://gitlab.com/ikus-soft/rdiffweb/commit/26d99fd16f36a13d987d865fbb118288786781bd) by Patrik Dufresne).
- Upgrade auth & ldap plugins ([26b5ea7](https://gitlab.com/ikus-soft/rdiffweb/commit/26b5ea7d39cd6ec6c34d0e0575fdb1ff7b4fb737) by Patrik Dufresne).
- Upgrade smtp plugins ([afcef7b](https://gitlab.com/ikus-soft/rdiffweb/commit/afcef7b74da2b85cdcde78371ff0b4ef63f06a67) by Patrik Dufresne).
- Drop Ubuntu Oracular & Add Ubuntu Plucky & Debian Trixie support ([2a9aeaf](https://gitlab.com/ikus-soft/rdiffweb/commit/2a9aeafcd8953153ab8f96322659b72e2f7bc06d) by Patrik Dufresne).
- Cache listdir entries #331 ([5825ecb](https://gitlab.com/ikus-soft/rdiffweb/commit/5825ecb4fef1c37960e907935a3ac22cf6885239) by Patrik Dufresne).
- Allow uses of role name in POST /api/users #341 ([b57e308](https://gitlab.com/ikus-soft/rdiffweb/commit/b57e308582f52c7721155dd17a8c5284aa90fbfb) by Patrik Dufresne).
- Update ldap modules ([75d4c0f](https://gitlab.com/ikus-soft/rdiffweb/commit/75d4c0fa01025e027dd1d39dfea293960af352db) by Patrik Dufresne).
- Drop python 3.8 ([7842962](https://gitlab.com/ikus-soft/rdiffweb/commit/784296209a81ea5881ee9547f63540f602952cd9) by Patrik Dufresne).
- Upgrade secure headers modules ([d081308](https://gitlab.com/ikus-soft/rdiffweb/commit/d081308ac62dfac2e9dc40880a34ca19ae50bb6e) by Patrik Dufresne).
- Handle error sending email notification when repo is damage #326 ([d58d740](https://gitlab.com/ikus-soft/rdiffweb/commit/d58d7403e6db36e8af9e26bab178a35cb15a38a7) by Patrik Dufresne).
- Clean-up deprecated code ([2b71ff3](https://gitlab.com/ikus-soft/rdiffweb/commit/2b71ff319d37c087e4603532ab454d8fb5a3665d) by Patrik Dufresne).
- Update installation.md ([5f981bc](https://gitlab.com/ikus-soft/rdiffweb/commit/5f981bc5fc3583a89a90785d3b15822a2609ebdc) by gary test2021).

## [6.1.3](https://gitlab.com/ikus-soft/rdiffweb/tags/6.1.3) - 2025-10-03

<small>[Compare with 6.1.2](https://gitlab.com/ikus-soft/rdiffweb/compare/6.1.2...6.1.3)</small>

### Changed

- Change deployment to dev repos ([e558bf9](https://gitlab.com/ikus-soft/rdiffweb/commit/e558bf921374f8772b5e0a65878a07df5b29825d) by Patrik Dufresne).

### Misc

- Upgrade rdiffweb ([af117a5](https://gitlab.com/ikus-soft/rdiffweb/commit/af117a5d4a79b37df5347614f543eaebff6f9841) by Patrik Dufresne).
- Drop Ubuntu Oracular ([aa36033](https://gitlab.com/ikus-soft/rdiffweb/commit/aa36033b059f9b10fe9639751013e26e6f930088) by Patrik Dufresne).

## [6.1.2](https://gitlab.com/ikus-soft/rdiffweb/tags/6.1.2) - 2025-06-21

<small>[Compare with 6.1.1](https://gitlab.com/ikus-soft/rdiffweb/compare/6.1.1...6.1.2)</small>

### Misc

- Prepare release 6.1.2 ([18dd8d0](https://gitlab.com/ikus-soft/rdiffweb/commit/18dd8d09e0a82d631d52ce1c83aebf9da1fc1079) by Patrik Dufresne).
- Rename sysctl config file ([1ca4b62](https://gitlab.com/ikus-soft/rdiffweb/commit/1ca4b624edfb97f180b2cfe29119633d4f9c9750) by Patrik Dufresne).
- Adjust warnings handling ([5e73659](https://gitlab.com/ikus-soft/rdiffweb/commit/5e73659ed722d2658035a312a80c95100e6a1784) by Patrik Dufresne).
- Bump rdiffweb to 2.10.5 to fix warnings ([fd19fc8](https://gitlab.com/ikus-soft/rdiffweb/commit/fd19fc8d106490b163aa6e08ad0f2bc1761796a4) by Patrik Dufresne).

## [2.10.5](https://gitlab.com/ikus-soft/rdiffweb/tags/2.10.5) - 2025-06-20

<small>[Compare with 2.10.4](https://gitlab.com/ikus-soft/rdiffweb/compare/2.10.4...2.10.5)</small>

### Misc

- Capture warnings ([b274c30](https://gitlab.com/ikus-soft/rdiffweb/commit/b274c30fc9d039f52cdc05386cd525bd7bf881df) by Patrik Dufresne).

## [6.1.1](https://gitlab.com/ikus-soft/rdiffweb/tags/6.1.1) - 2025-06-18

<small>[Compare with 6.1.0](https://gitlab.com/ikus-soft/rdiffweb/compare/6.1.0...6.1.1)</small>

### Misc

- Upgrade debbuild to define conffiles ([19c5a68](https://gitlab.com/ikus-soft/rdiffweb/commit/19c5a682e47f8a207ab878a136aa7de768ccce0d) by Patrik Dufresne).

## [6.1.0](https://gitlab.com/ikus-soft/rdiffweb/tags/6.1.0) - 2025-06-13

<small>[Compare with 6.0.5](https://gitlab.com/ikus-soft/rdiffweb/compare/6.0.5...6.1.0)</small>

### Added

- Add support for Ubuntu Plucky 25.04 ([5bd44de](https://gitlab.com/ikus-soft/rdiffweb/commit/5bd44de82016fe1d4dc9f01ca37099a2d6868540) by Patrik Dufresne).
- Add Debian Trixie support ([f1b70ce](https://gitlab.com/ikus-soft/rdiffweb/commit/f1b70ce72ba9bcf9bfd3362676481394a967ea00) by Patrik Dufresne).
- Add `--no-install-recommends` in Dockerfile ([f0bd51e](https://gitlab.com/ikus-soft/rdiffweb/commit/f0bd51e646c64d7aa454b239f85aca4aacb03b6a) by Patrik Dufresne).

### Fixed

- Fix Docker image minarca#312 ([5515253](https://gitlab.com/ikus-soft/rdiffweb/commit/55152537528fef8d871a2f235e7986fd506b98fc) by Patrik Dufresne).
- Fix `/api/minarca` entrypoint ([d755c58](https://gitlab.com/ikus-soft/rdiffweb/commit/d755c586ba04fadab68417587f91f3fe57485cfc) by Patrik Dufresne).
- Fix version check in CICD pipeline ([a2b2e4a](https://gitlab.com/ikus-soft/rdiffweb/commit/a2b2e4aaf60bf3e85b1ccd6551a977638b7ddfce) by Patrik Dufresne).
- Fix license badge in README ([faabdae](https://gitlab.com/ikus-soft/rdiffweb/commit/faabdae245c19e210faeb408821f3f11094a66bb) by Patrik Dufresne).

### Removed

- Remove apt install from CICD build ([de19b0b](https://gitlab.com/ikus-soft/rdiffweb/commit/de19b0b61835de0611af2ae05909f31bd18c2796) by Patrik Dufresne).
- Remove dependencies on `libxcb1` ([d56f1ac](https://gitlab.com/ikus-soft/rdiffweb/commit/d56f1ac82bf2c99ce797c3f75c6fedb3c0bb5187) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-fix-ubuntu' into 'master' ([408f4f0](https://gitlab.com/ikus-soft/rdiffweb/commit/408f4f0ddcecc7fdceeaaf15febad1a0863eae0d) by Patrik Dufresne).
- Merge branch 'patrik-copyright' into 'master' ([db753d7](https://gitlab.com/ikus-soft/rdiffweb/commit/db753d7e3b4997c3142195d775d1b8629c0745c4) by Patrik Dufresne).
- Merge branch 'patrik-python-3.12' into 'master' ([1c99b6f](https://gitlab.com/ikus-soft/rdiffweb/commit/1c99b6fa934f7b50671bfc4e8eac3832d490c132) by Patrik Dufresne).
- Merge branch 'patrik-bump-rdiffweb' into 'master' ([33bddb1](https://gitlab.com/ikus-soft/rdiffweb/commit/33bddb1c08fbeff1ec4249b7d56f977bee882454) by Patrik Dufresne).
- Merge branch 'patrik-return-jail-error' into 'master' ([d2e5b6f](https://gitlab.com/ikus-soft/rdiffweb/commit/d2e5b6ff20a1582bc73eba2311aa68fdcd12f4e8) by Patrik Dufresne).
- Merge branch 'patrik-docker' into 'master' ([dad374d](https://gitlab.com/ikus-soft/rdiffweb/commit/dad374d565bdc6e54f2c0737a227dbbcf26c7b62) by Patrik Dufresne).
- Merge branch 'patrik-remove-libxcb1' into 'master' ([a024ced](https://gitlab.com/ikus-soft/rdiffweb/commit/a024ced7be4a402cc75f26a5cccf564548e8b35a) by Patrik Dufresne).
- Merge commit '7c86a1be95c4458cc71400699dcdf257ca323ec7' ([089f8d1](https://gitlab.com/ikus-soft/rdiffweb/commit/089f8d1e338e35d861320fddf8994cb6997c434b) by Patrik Dufresne).
- Merge branch 'patrik-fix-readme' into 'master' ([ec1b078](https://gitlab.com/ikus-soft/rdiffweb/commit/ec1b0780f8088ff1fcb95235ce30d22b1b74627f) by Patrik Dufresne).
- Merge branch 'patrik-pyproject-toml' into 'master' ([baa5280](https://gitlab.com/ikus-soft/rdiffweb/commit/baa5280c951cc40e158785405404e822e373a056) by Patrik Dufresne).

### Misc

- Prepare release 6.1.0 ([bb4f3c5](https://gitlab.com/ikus-soft/rdiffweb/commit/bb4f3c553917adaae7a2d9c161d5db5da34ef954) by Patrik Dufresne).
- Bump rdiffweb to version 2.10.4 ([3b1bb62](https://gitlab.com/ikus-soft/rdiffweb/commit/3b1bb629e44be8432afc58aa9b0653005446fed8) by Patrik Dufresne).
- Include SSL dependencies for HTTPS ([a4c85cd](https://gitlab.com/ikus-soft/rdiffweb/commit/a4c85cd96c95e7236822a1efa2ac374e1fbb1dd3) by Patrik Dufresne).
- Bump rdiffweb version to 2.104b2 ([9e2b7c0](https://gitlab.com/ikus-soft/rdiffweb/commit/9e2b7c03ecc6c4df9120a3e2824927442fcf60de) by Patrik Dufresne).
- Update Docker documentation for PostgreSQL ([6497c4b](https://gitlab.com/ikus-soft/rdiffweb/commit/6497c4b7aa6b4a17eaf83b21452269e18a1a8fb0) by Patrik Dufresne).
- Make postgresql support working minarca#311 ([4aa04e7](https://gitlab.com/ikus-soft/rdiffweb/commit/4aa04e75613113622a592f8662af2be47ecbbb0f) by Patrik Dufresne).
- Disable python warning in runtime ([614e493](https://gitlab.com/ikus-soft/rdiffweb/commit/614e4935564f853ce8eb7d750b5fe51a6bc91d01) by Patrik Dufresne).
- Bump rdiffweb to v2.10.4b1 ([1093eaa](https://gitlab.com/ikus-soft/rdiffweb/commit/1093eaa1d7e88fb5e00790b72b3563241d6b735f) by Patrik Dufresne).
- Removing `# -*- coding: utf-8 -*-` header ([22dce07](https://gitlab.com/ikus-soft/rdiffweb/commit/22dce0793bc3f842b52ce74b525f6f225a972fdf) by Patrik Dufresne).
- Optimize pyinstaller packaging ([6259f5c](https://gitlab.com/ikus-soft/rdiffweb/commit/6259f5c7a270066ea4346942395bc06733983ecc) by Patrik Dufresne).
- Bump rdiffweb to v2.10.3b1 ([bf9030e](https://gitlab.com/ikus-soft/rdiffweb/commit/bf9030e12f9ee8cde6ffe62f54113737c3c2637c) by Patrik Dufresne).
- Disable Ubuntu hardening apparmor_restrict_unprivileged_userns ([813ea17](https://gitlab.com/ikus-soft/rdiffweb/commit/813ea175283f855bb2c617e9e33a9e6a3ea49b81) by Patrik Dufresne).
- Update Copyright ([559cd77](https://gitlab.com/ikus-soft/rdiffweb/commit/559cd77be5a34be2ec2779c8cd98cc67256998ef) by Patrik Dufresne).
- Bump Python version to 3.12 minarca#297 ([a4de507](https://gitlab.com/ikus-soft/rdiffweb/commit/a4de50764ea5615660bc6a2e7af4556d0f498acf) by Patrik Dufresne).
- Bump rdiffweb to 2.10.0rc2 ([85abded](https://gitlab.com/ikus-soft/rdiffweb/commit/85abdedd51970826b1865fe188a63a7d91af5999) by Patrik Dufresne).
- Explicitly return error when jail fail ([27e8df5](https://gitlab.com/ikus-soft/rdiffweb/commit/27e8df5947a1b58f9f9e45aeb84ff2d0f0cc2f83) by Patrik Dufresne).
- Provide Docker Image #7 ([ae07327](https://gitlab.com/ikus-soft/rdiffweb/commit/ae07327715df3f685dd7e8bb351e42bc59db1d51) by Patrik Dufresne).
- Bump rdiffweb version to 2.10.1b2 ([9485cb9](https://gitlab.com/ikus-soft/rdiffweb/commit/9485cb993be7f470b7a95b404a2841cfc3ae2b8a) by Patrik Dufresne).
- Bump rdiffweb version to 2.10.0b1 ([980c691](https://gitlab.com/ikus-soft/rdiffweb/commit/980c6913ab5afe5d1f9e704eecc3e8ad4b3c1eaf) by Patrik Dufresne).
- Migrate to pyproject.toml and pyinstaller ([11e9aba](https://gitlab.com/ikus-soft/rdiffweb/commit/11e9aba180a73b8fb6c206c3b3f328c8bafe572e) by Patrik Dufresne).

## [2.10.4](https://gitlab.com/ikus-soft/rdiffweb/tags/2.10.4) - 2025-06-13

<small>[Compare with 2.9.7](https://gitlab.com/ikus-soft/rdiffweb/compare/2.9.7...2.10.4)</small>

### Added

- Add new API to manage users ([d11dd0d](https://gitlab.com/ikus-soft/rdiffweb/commit/d11dd0d985a281e31ab3fef85eb49f4b1f3b234f) by Patrik Dufresne).
- Add "Preparing your download" page #322 ([dc57725](https://gitlab.com/ikus-soft/rdiffweb/commit/dc577258b5e42892e2bb9e2bf1c96ab79e38df01) by Patrik Dufresne).
- Add swagger to document Rdiffweb API #325 ([6ecdf11](https://gitlab.com/ikus-soft/rdiffweb/commit/6ecdf11f4f0a6e9a13d9844f98313ec0aa503dbf) by Patrik Dufresne).
- Add `data-order` to Admin View User Repos #324 ([9f6bb59](https://gitlab.com/ikus-soft/rdiffweb/commit/9f6bb59217a52c84058c9f092a502c74630b385b) by Patrik Dufresne).
- Add caching for translation ([01ad7d6](https://gitlab.com/ikus-soft/rdiffweb/commit/01ad7d65a0362644791b6ea4c122eacf2babee06) by Patrik Dufresne).

### Fixed

- Fix database schema upgrade with null mfa, lang or report_time_range ([646bf64](https://gitlab.com/ikus-soft/rdiffweb/commit/646bf6456a25367b0cf454463c6db486666161cf) by Patrik Dufresne).
- Fix some unit test comments ([5aae78b](https://gitlab.com/ikus-soft/rdiffweb/commit/5aae78be70a0b318f9c022b5fe454451c6d201af) by Patrik Dufresne).
- Fix "Show more..." link in stats view #328 ([453e8e5](https://gitlab.com/ikus-soft/rdiffweb/commit/453e8e52e1c39e4164b4dc479205455b6ef1687d) by Patrik Dufresne).
- Fix selenium test stability ([3efab23](https://gitlab.com/ikus-soft/rdiffweb/commit/3efab2365d6b7f5db55bc5b0dca960b634dc8b69) by Patrik Dufresne).
- Fix title of Admin Repos view ([3bd6ef6](https://gitlab.com/ikus-soft/rdiffweb/commit/3bd6ef6589f250d79ce19569b34dd095de8946d0) by Patrik Dufresne).
- Fix display of filename with < > in stats view ([0af6d97](https://gitlab.com/ikus-soft/rdiffweb/commit/0af6d97c4d937607ad4be2704105e6266ae40536) by Patrik Dufresne).
- Fix `changes_dates` to ignore `*.missing` entry ([5cbd3de](https://gitlab.com/ikus-soft/rdiffweb/commit/5cbd3de806ff35e7af836c9534d4c50802e36e4a) by Patrik Dufresne).
- Fix email notification to include more information #312 ([c2ddacb](https://gitlab.com/ikus-soft/rdiffweb/commit/c2ddacbadd201edba000f16ee0df9905eaa563b9) by Patrik Dufresne).
- Fix sorting of dates in stats and logs view #321 ([ae3c90f](https://gitlab.com/ikus-soft/rdiffweb/commit/ae3c90f576976111f4de60cb67d3559cc8908053) by Patrik Dufresne).

### Removed

- Remove wsgi entrypoint ([bf2724c](https://gitlab.com/ikus-soft/rdiffweb/commit/bf2724c30c277fd0d2f6876bef3c2f695b894752) by Patrik Dufresne).
- Remove obsolete option `brand-default-theme` from the doc ([b2e0fe9](https://gitlab.com/ikus-soft/rdiffweb/commit/b2e0fe9ba75b16f157b983f59658a6bcf7c5cb62) by Patrik Dufresne).

### Merged

- Merge commit 'c226f6453048cbe8188ea94cc2562596e2dbee0b' ([687d574](https://gitlab.com/ikus-soft/rdiffweb/commit/687d574b9da4c3ffc9cc88a834373bc8adb036cf) by Patrik Dufresne).

### Misc

- Prepare release 2.10.4 ([fc0eb01](https://gitlab.com/ikus-soft/rdiffweb/commit/fc0eb01da9fce3ac0ea1d7b648f0d3056a725b87) by Patrik Dufresne).
- Update french translation ([eea69b3](https://gitlab.com/ikus-soft/rdiffweb/commit/eea69b3406657e63b2bc9b0591949b1f7f4f25fa) by Patrik Dufresne).
- Show/Hide animation in restore page #332 ([6189941](https://gitlab.com/ikus-soft/rdiffweb/commit/6189941ad18e4138bbcc7be45ce183ebb171130c) by Patrik Dufresne).
- File header and license cleanups ([715fbad](https://gitlab.com/ikus-soft/rdiffweb/commit/715fbad66c5a34c0a535af17d632d1021a0fe1a7) by Patrik Dufresne).
- Remove `# -*- coding: utf-8 -*-` header ([936b5e1](https://gitlab.com/ikus-soft/rdiffweb/commit/936b5e1d4d155af10aee0b7fab5ed0599cc14fe7) by Patrik Dufresne).
- Lookup `rdiff-backup` and `rdiff-backup-delete` in current executable path ([d74e8a5](https://gitlab.com/ikus-soft/rdiffweb/commit/d74e8a52baa7c4656a4326524e5afa950ce996fe) by Patrik Dufresne).
- Reorganize few api endpoint ([e6169d0](https://gitlab.com/ikus-soft/rdiffweb/commit/e6169d03e3f1c69a1359464c3ef0c51c165ae89c) by Patrik Dufresne).
- Return invalid fields has form errors ([fb5862f](https://gitlab.com/ikus-soft/rdiffweb/commit/fb5862f2a6cf4a3a3371c0f1a7bf495df2ccb43b) by Patrik Dufresne).
- Sort admin system logs by date ([8e1cfad](https://gitlab.com/ikus-soft/rdiffweb/commit/8e1cfadc6eb7d2ff900aebd9ce08df0c90a1969e) by Patrik Dufresne).
- Provide regexp implementation for sqlalchemy v1.3 ([2821a18](https://gitlab.com/ikus-soft/rdiffweb/commit/2821a18be6c42eb530f3cd2f8b589341636851b7) by Patrik Dufresne).
- Convert db into a plugin ([c4cae72](https://gitlab.com/ikus-soft/rdiffweb/commit/c4cae72002ddf5318fd2749e37e92246e12d0302) by Patrik Dufresne).
- Use Debian Bookworm as base for Docker ([c255617](https://gitlab.com/ikus-soft/rdiffweb/commit/c2556175ace51d642fab1a0c372b6d98e0548995) by Patrik Dufresne).
- Reffactor upgrade of DB schema ([d71ed22](https://gitlab.com/ikus-soft/rdiffweb/commit/d71ed2231ae086a93cc4ae31ff3db9d6a02cbe4a) by Patrik Dufresne).
- Reffactor current user repos API ([b9f3aa8](https://gitlab.com/ikus-soft/rdiffweb/commit/b9f3aa88633e5e9e05aa1a6eff3e1561ab8acd37) by Patrik Dufresne).
- Reffactor current user tokens API ([5545b7a](https://gitlab.com/ikus-soft/rdiffweb/commit/5545b7a9f0889aae95baff2a81eb12be4ae89ffe) by Patrik Dufresne).
- Externalize "required_scope" tools ([5a0a6aa](https://gitlab.com/ikus-soft/rdiffweb/commit/5a0a6aa79bc831d0e4903b447053a8e119b046fd) by Patrik Dufresne).
- Return API error as Json ([d2913a2](https://gitlab.com/ikus-soft/rdiffweb/commit/d2913a26cfff19a794098ae95ef1e72b8e9a75e1) by Patrik Dufresne).
- Update Openapi generator ([cb169c5](https://gitlab.com/ikus-soft/rdiffweb/commit/cb169c54c5b7abdec77d728c0986a9714226b248) by Patrik Dufresne).
- Update copyright ([e8fb906](https://gitlab.com/ikus-soft/rdiffweb/commit/e8fb906b0d34b40493ae3c1330ac9700fef3f3f4) by Patrik Dufresne).
- Update README changes ([7cba941](https://gitlab.com/ikus-soft/rdiffweb/commit/7cba94123c466d90699c5223bdc1743a8ac4d186) by Patrik Dufresne).
- Raise HTTP 405 when restapi method not defined ([65a218b](https://gitlab.com/ikus-soft/rdiffweb/commit/65a218bc90b1573cf9989a8cbcc42a16bd496ec1) by Patrik Dufresne).
- Generate openapi.json for not without doc string ([b70ee9b](https://gitlab.com/ikus-soft/rdiffweb/commit/b70ee9b750f1bad4ba4c6d5b7db8d5a471d7ef07) by Patrik Dufresne).
- Adjust quota settings to align with the nearest block size, preventing the 'Setting user's quota is not supported' error. ([d1d5ba4](https://gitlab.com/ikus-soft/rdiffweb/commit/d1d5ba4a7f592d0a3a66f085c47f077d672bb00c) by Patrik Dufresne).
- Fork process to restore files ([b6f461c](https://gitlab.com/ikus-soft/rdiffweb/commit/b6f461ccb0cb6486575631041aa382d209fe4e64) by Patrik Dufresne).
- Explicitly add "pytz" as dependencies ([15f365a](https://gitlab.com/ikus-soft/rdiffweb/commit/15f365ab7b8a7b696750369703931ab63137244a) by Patrik Dufresne).
- Drop Ubuntu Lunar ([fc74183](https://gitlab.com/ikus-soft/rdiffweb/commit/fc7418318896a11d8052d940745e54066b5abddb) by Patrik Dufresne).
- Migrate to pyproject.toml #281 ([b394ef6](https://gitlab.com/ikus-soft/rdiffweb/commit/b394ef64ba885a3212119cccbe204694b125c849) by Patrik Dufresne).
- Update Backup Log & Restore Log labels #316 ([c27d78e](https://gitlab.com/ikus-soft/rdiffweb/commit/c27d78e0f7d7a2f0082c3a7040b64d3093b78fc5) by Patrik Dufresne).
- Show keepdays, maxage in admin repos view #310 ([7928bed](https://gitlab.com/ikus-soft/rdiffweb/commit/7928bed7fd95039b9295dd79b1db46a6e34807da) by Patrik Dufresne).
- Adjust labels of buttons used to filter file statistics ([a11a266](https://gitlab.com/ikus-soft/rdiffweb/commit/a11a266837cbc67e906e315632927c99d4c08445) by Patrik Dufresne).
- Simplifying dh_auto_clean override. ([e701fc6](https://gitlab.com/ikus-soft/rdiffweb/commit/e701fc61eb37f2fd51d3bdc3cff2a53b167b78a1) by Daniel Baumann).
- Indenting comment for dh_auto_install override. ([d2e9b5c](https://gitlab.com/ikus-soft/rdiffweb/commit/d2e9b5c6e53a55480659989e53923477f43612f6) by Daniel Baumann).
- Removing trailing slash when creating manpage directory in rules. ([1ac5084](https://gitlab.com/ikus-soft/rdiffweb/commit/1ac508458f0b8717308a75a558aa483b10b53935) by Daniel Baumann).
- Updating indenting and grouping in maintainer scripts. ([017dcd7](https://gitlab.com/ikus-soft/rdiffweb/commit/017dcd77f173105493d88ee56b18e0d3e65f22ed) by Daniel Baumann).
- Updating year in copyright file for 2025. ([51095d8](https://gitlab.com/ikus-soft/rdiffweb/commit/51095d8372467bba46baa59b5199c39361678bcd) by Daniel Baumann).
- Updating source URL in copyright. ([89cf5e2](https://gitlab.com/ikus-soft/rdiffweb/commit/89cf5e2969c19c408674cdb4dbf128d8afb82a07) by Daniel Baumann).
- Removing trailing slash in url field. ([f4e76e9](https://gitlab.com/ikus-soft/rdiffweb/commit/f4e76e9d663cd2ecab382630eed33d5c698a24d9) by Daniel Baumann).
- Updating standards version to 4.7.0. ([2a46580](https://gitlab.com/ikus-soft/rdiffweb/commit/2a4658071b24ca69504e3537800f603a41ced282) by Daniel Baumann).
- Removing pre-bullseye versioned build-depends. ([1c53109](https://gitlab.com/ikus-soft/rdiffweb/commit/1c5310904a327b864ec427e8c7974c70744284b1) by Daniel Baumann).

## [6.0.5](https://gitlab.com/ikus-soft/rdiffweb/tags/6.0.5) - 2025-02-20

<small>[Compare with 6.0.4](https://gitlab.com/ikus-soft/rdiffweb/compare/6.0.4...6.0.5)</small>

### Misc

- Bump rdiffweb version to 2.9.7 to fix admin user creation minarca#293 ([7c86a1b](https://gitlab.com/ikus-soft/rdiffweb/commit/7c86a1be95c4458cc71400699dcdf257ca323ec7) by Patrik Dufresne).

## [2.9.7](https://gitlab.com/ikus-soft/rdiffweb/tags/2.9.7) - 2025-02-19

<small>[Compare with 2.9.6](https://gitlab.com/ikus-soft/rdiffweb/compare/2.9.6...2.9.7)</small>

### Misc

- Trigger creation of default user `admin` after plugin startup minarca#295 ([c226f64](https://gitlab.com/ikus-soft/rdiffweb/commit/c226f6453048cbe8188ea94cc2562596e2dbee0b) by Patrik Dufresne).

## [6.0.4](https://gitlab.com/ikus-soft/rdiffweb/tags/6.0.4) - 2025-01-08

<small>[Compare with 6.0.3](https://gitlab.com/ikus-soft/rdiffweb/compare/6.0.3...6.0.4)</small>

### Fixed

- Fix reported version and add test in CICD pipeline ([d1e8bba](https://gitlab.com/ikus-soft/rdiffweb/commit/d1e8bbaba0107750b6d1da0c34a210c9b3cae204) by Patrik Dufresne).

### Removed

- Remove zenity dependency introduced by mistake ([f0ff06d](https://gitlab.com/ikus-soft/rdiffweb/commit/f0ff06dfe67ccd42761041f7c4dd2938977eb286) by Patrik Dufresne).

### Misc

- Split repo ([659547f](https://gitlab.com/ikus-soft/rdiffweb/commit/659547fcdb223a7d94e287364f617fbc12172bba) by Patrik Dufresne).

## [2.9.6](https://gitlab.com/ikus-soft/rdiffweb/tags/2.9.6) - 2025-01-06

<small>[Compare with 2.9.5](https://gitlab.com/ikus-soft/rdiffweb/compare/2.9.5...2.9.6)</small>

### Misc

- Drop Ubuntu Lunar ([a37dec6](https://gitlab.com/ikus-soft/rdiffweb/commit/a37dec6acac827cb58a07d7357808210112e7285) by Patrik Dufresne).
- Explicitly add "pytz" as dependencies ([99da1b0](https://gitlab.com/ikus-soft/rdiffweb/commit/99da1b00718f84390fec03f1d68cb05f52b020fb) by Patrik Dufresne).
- Drop Ubuntu Mantic support ([fb9b10f](https://gitlab.com/ikus-soft/rdiffweb/commit/fb9b10fde29c125a7641a8daad96976bd2cf1307) by Patrik Dufresne).

## [6.0.3](https://gitlab.com/ikus-soft/rdiffweb/tags/6.0.3) - 2024-11-12

<small>[Compare with 6.0.0](https://gitlab.com/ikus-soft/rdiffweb/compare/6.0.0...6.0.3)</small>

### Added

- Add support for Ubuntu Noble 24.04 LTS & Oracular 24.10 ([73a4fbb](https://gitlab.com/ikus-soft/rdiffweb/commit/73a4fbbb303e64f638d8d181af828ed7b1f25609) by Patrik Dufresne).

## [2.9.5](https://gitlab.com/ikus-soft/rdiffweb/tags/2.9.5) - 2024-11-11

<small>[Compare with 2.9.4](https://gitlab.com/ikus-soft/rdiffweb/compare/2.9.4...2.9.5)</small>

### Added

- Add support for Ubuntu Oracular 24.10 ([9becf16](https://gitlab.com/ikus-soft/rdiffweb/commit/9becf16f0a96fad246021256de58a204318687b8) by Patrik Dufresne).
- Add support for Ubuntu Noble #317 ([3364f06](https://gitlab.com/ikus-soft/rdiffweb/commit/3364f0644d62590b65ad6610d74139edc8a1740f) by Patrik Dufresne).

## [6.0.0](https://gitlab.com/ikus-soft/rdiffweb/tags/6.0.0) - 2024-10-25

<small>[Compare with 5.0.5](https://gitlab.com/ikus-soft/rdiffweb/compare/5.0.5...6.0.0)</small>

### Added

- WIP: Add minarcaid authentication ([2cd679c](https://gitlab.com/ikus-soft/rdiffweb/commit/2cd679c723201f198d77d0847c885633d6b8a2ac) by Patrik Dufresne).

### Fixed

- Fix permissions error trying to regenerate identity ([cb6d012](https://gitlab.com/ikus-soft/rdiffweb/commit/cb6d0121dcdccfc0bf1afda02f6c712b9ebba3cc) by Patrik Dufresne).
- Fix postinst to get minarca's home #256 ([55b99b9](https://gitlab.com/ikus-soft/rdiffweb/commit/55b99b9f784afd7b41d0ddf4f6aa8f5b68e9785c) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-fix-keepdays' into 'master' ([05c79a7](https://gitlab.com/ikus-soft/rdiffweb/commit/05c79a768107eb6f8600ffb0e793494407702a73) by Patrik Dufresne).
- Merge branch 'patrik-multi-backup-kivy' into 'master' ([6e05249](https://gitlab.com/ikus-soft/rdiffweb/commit/6e05249b2745b443170559c33579db9b501297c0) by Patrik Dufresne).

### Misc

- Update french translation ([6024366](https://gitlab.com/ikus-soft/rdiffweb/commit/60243667f223e96c61775b4a2390ae9b10ec19a3) by Patrik Dufresne).
- Improve logging in minarca-shell ([f03d0da](https://gitlab.com/ikus-soft/rdiffweb/commit/f03d0da79a29df8ff817c83ccbde0bfc62bc378d) by Patrik Dufresne).
- Define distinct settings for minarca-home-dir and minarca-base-dir ([1fd4989](https://gitlab.com/ikus-soft/rdiffweb/commit/1fd4989ffa26374f8bcc4e35152462ebd8504fa2) by Patrik Dufresne).
- Update environment variable prefix to MINARCA_ ([e11002c](https://gitlab.com/ikus-soft/rdiffweb/commit/e11002ce2710f97246799858311b27cb57ad95e3) by Patrik Dufresne).
- Return the reason when minarcaid is invalid ([0734a3e](https://gitlab.com/ikus-soft/rdiffweb/commit/0734a3e05e092f3ee088937c8366edf4fbc39a67) by Patrik Dufresne).
- Increase minarcaid epoch validation to 5 minutes ([a30c030](https://gitlab.com/ikus-soft/rdiffweb/commit/a30c0307e4c7eaa6e64a51c3ebd8d09606040658) by Patrik Dufresne).
- Adjust colors in login screen ([b87fca2](https://gitlab.com/ikus-soft/rdiffweb/commit/b87fca284835f58cd7201d9c53c501c7c0ace357) by Patrik Dufresne).
- Bump rdiffweb to v2.9.3 ([af427f2](https://gitlab.com/ikus-soft/rdiffweb/commit/af427f2d8743c3444cdc2ec390084ed629467b9e) by Patrik Dufresne).
- Upgrade Rdiffweb to v2.9.2 ([11c9d7b](https://gitlab.com/ikus-soft/rdiffweb/commit/11c9d7b0a4e25e577bb2b01508261ab71b21ad85) by Patrik Dufresne).
- Set rdiffweb version to 2.9.1 ([b4f48bb](https://gitlab.com/ikus-soft/rdiffweb/commit/b4f48bbd5c4f5e6f8e6b51d41ccb71c5249b924a) by Patrik Dufresne).
- Update colors on minarca server ([d51c472](https://gitlab.com/ikus-soft/rdiffweb/commit/d51c4729f2cd042dc7c75b5c0825ea85ee237bb5) by Patrik Dufresne).
- Support multi-backup destination ([08f0404](https://gitlab.com/ikus-soft/rdiffweb/commit/08f04049809122e1069ee6dc607391f67b93e5d0) by Patrik Dufresne).

## [2.9.4](https://gitlab.com/ikus-soft/rdiffweb/tags/2.9.4) - 2024-10-24

<small>[Compare with 2.9.3](https://gitlab.com/ikus-soft/rdiffweb/compare/2.9.3...2.9.4)</small>

### Misc

- Enforce use of python:3.10-bullseye ([a96f583](https://gitlab.com/ikus-soft/rdiffweb/commit/a96f583797b65a8f68d3780c1ed470c7989a56dc) by Patrik Dufresne).
- Complete french translation #315 ([9fad72d](https://gitlab.com/ikus-soft/rdiffweb/commit/9fad72d2a19b78be1e5b9dcd4e880e3f7496dbd0) by Patrik Dufresne).

## [2.9.3](https://gitlab.com/ikus-soft/rdiffweb/tags/2.9.3) - 2024-08-02

<small>[Compare with 2.9.2](https://gitlab.com/ikus-soft/rdiffweb/compare/2.9.2...2.9.3)</small>

### Misc

- Provide default encoding value ([7d777ad](https://gitlab.com/ikus-soft/rdiffweb/commit/7d777ad45c132c55bbaf829bdc08c75bd24de035) by Patrik Dufresne).

## [2.9.2](https://gitlab.com/ikus-soft/rdiffweb/tags/2.9.2) - 2024-07-03

<small>[Compare with 2.9.1](https://gitlab.com/ikus-soft/rdiffweb/compare/2.9.1...2.9.2)</small>

### Merged

- Merge branch 'patrik-fix-translation' into 'master' ([0f5ebd9](https://gitlab.com/ikus-soft/rdiffweb/commit/0f5ebd9693ebe86f56b22869d97a3237e2b344c8) by Patrik Dufresne).

### Misc

- Use default language to send notification if user doesn't have a "Preferred Language" #306 ([0eb3cdc](https://gitlab.com/ikus-soft/rdiffweb/commit/0eb3cdc64ee3eca3e01452dd11313acf29c6435f) by Patrik Dufresne).

## [2.9.1](https://gitlab.com/ikus-soft/rdiffweb/tags/2.9.1) - 2024-06-11

<small>[Compare with 2.8.9](https://gitlab.com/ikus-soft/rdiffweb/compare/2.8.9...2.9.1)</small>

### Added

- Add prefered language to admin View ([9b59bf9](https://gitlab.com/ikus-soft/rdiffweb/commit/9b59bf96553681084616cc7fa70652046d29fb21) by Patrik Dufresne).

### Fixed

- Fix backward compatibility for database with empty repo's encoding ([1323c90](https://gitlab.com/ikus-soft/rdiffweb/commit/1323c90452ebf4cfe4f61b899c8ba1adbc01df09) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-admin-view-lang' into 'master' ([3ac0efd](https://gitlab.com/ikus-soft/rdiffweb/commit/3ac0efd4ffe27e4af24c864ca5e47c15d49e11dd) by Patrik Dufresne).
- Merge branch 'patrik-fix-repo-settings' into 'master' ([9299c2e](https://gitlab.com/ikus-soft/rdiffweb/commit/9299c2e9b74dc7deadf36f58b57b3587e3679043) by Patrik Dufresne).
- Merge branch 'fix-buster' into 'master' ([9bfabf8](https://gitlab.com/ikus-soft/rdiffweb/commit/9bfabf8cc5ca27b8dbbc6af427599715fdf8f0eb) by Patrik Dufresne).
- Merge branch 'patrik-restapi-scope' into 'master' ([edb1b12](https://gitlab.com/ikus-soft/rdiffweb/commit/edb1b12d0c51686e2cb7b74946fe508cb6e7a793) by Patrik Dufresne).

### Misc

- Improve DockerImage ([183c6a8](https://gitlab.com/ikus-soft/rdiffweb/commit/183c6a8cc3d3d822b40b2e540df0e06257991870) by Patrik Dufresne).
- Drop Debian Buster support ([6ed48b3](https://gitlab.com/ikus-soft/rdiffweb/commit/6ed48b340775a56fbf49323cfaa0aec6ba8dea6b) by Patrik Dufresne).
- little fix for columns ([f344095](https://gitlab.com/ikus-soft/rdiffweb/commit/f3440954d8f53926cbf0e028d405f614a177bd6b) by Patrik Dufresne).
- Improve REST api ([6ead98f](https://gitlab.com/ikus-soft/rdiffweb/commit/6ead98f44674350f276f2899d501fb559e35a5f6) by Patrik Dufresne).

## [5.0.5](https://gitlab.com/ikus-soft/rdiffweb/tags/5.0.5) - 2024-04-07

<small>[Compare with 5.0.3](https://gitlab.com/ikus-soft/rdiffweb/compare/5.0.3...5.0.5)</small>

### Fixed

- Fix compatibility issue with backupninja #237 ([e73c6be](https://gitlab.com/ikus-soft/rdiffweb/commit/e73c6bef98a2ccd397666481e6715fd520b3a7ba) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-fix-backup-ninja' into 'master' ([a2d4246](https://gitlab.com/ikus-soft/rdiffweb/commit/a2d4246456bf7a054394f94479b9e1ea8b01db73) by Patrik Dufresne).

## [5.0.3](https://gitlab.com/ikus-soft/rdiffweb/tags/5.0.3) - 2024-02-19

<small>[Compare with 5.0.2](https://gitlab.com/ikus-soft/rdiffweb/compare/5.0.2...5.0.3)</small>

### Merged

- Merge branch 'patrik-fix-page-settings' into 'master' ([5a3fa4c](https://gitlab.com/ikus-soft/rdiffweb/commit/5a3fa4c9b00eedd6ed103f3ad9facb1fa33871c7) by Patrik Dufresne).

### Misc

- Upgrade rdiffweb to version 2.8.9 ([c90f482](https://gitlab.com/ikus-soft/rdiffweb/commit/c90f482bb1375ec5c1c92147acd04827c7b9ce74) by Patrik Dufresne).

## [2.8.9](https://gitlab.com/ikus-soft/rdiffweb/tags/2.8.9) - 2024-02-19

<small>[Compare with 2.8.8](https://gitlab.com/ikus-soft/rdiffweb/compare/2.8.8...2.8.9)</small>

### Fixed

- Fix display of page settings minarca#235 ([27a12da](https://gitlab.com/ikus-soft/rdiffweb/commit/27a12da1d4e59608236b012b3b0c15a2dc5766e9) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-fix-page-settings' into 'master' ([03a7fd1](https://gitlab.com/ikus-soft/rdiffweb/commit/03a7fd1537300e70046671c46e3c56ba87b7eace) by Patrik Dufresne).
- Merge branch 'patrik-deb-src' into 'master' ([8a3a4d6](https://gitlab.com/ikus-soft/rdiffweb/commit/8a3a4d6bc1b82ea95c0161629753ee9e4b574f94) by Patrik Dufresne).

### Misc

- Build Debian source package ([14e4b17](https://gitlab.com/ikus-soft/rdiffweb/commit/14e4b170b2d7b7712ccd82b8af47b52770217fbd) by Patrik Dufresne).

## [5.0.2](https://gitlab.com/ikus-soft/rdiffweb/tags/5.0.2) - 2024-01-08

<small>[Compare with 5.0.1](https://gitlab.com/ikus-soft/rdiffweb/compare/5.0.1...5.0.2)</small>

### Merged

- Merge branch 'patrik-hot-fix' into 'master' ([0b7e31b](https://gitlab.com/ikus-soft/rdiffweb/commit/0b7e31b2fa8228cbccb95fc8a864a185f14f2da8) by Patrik Dufresne).

### Misc

- Upgrade rdiffweb to version 2.8.8 ([1176766](https://gitlab.com/ikus-soft/rdiffweb/commit/1176766d72740b6663de68f9dee945569a0fde11) by Patrik Dufresne).

## [2.8.8](https://gitlab.com/ikus-soft/rdiffweb/tags/2.8.8) - 2024-01-08

<small>[Compare with 2.8.7](https://gitlab.com/ikus-soft/rdiffweb/compare/2.8.7...2.8.8)</small>

### Fixed

- Fix usage of `session-idle-timeout` in config file #296 ([b9602ff](https://gitlab.com/ikus-soft/rdiffweb/commit/b9602ff7d26b20d4019364b8adae5efc907b5eac) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-fix-session-idle-timeout' into 'master' ([32677f4](https://gitlab.com/ikus-soft/rdiffweb/commit/32677f41e8d5d321107a3b8bd9a8939c5ce45b63) by Patrik Dufresne).
- Merge branch 'patrik-update-auth-mfa' into 'master' ([1d93327](https://gitlab.com/ikus-soft/rdiffweb/commit/1d933278d8d77cf98834ecde1bc842d339bbdb0a) by Patrik Dufresne).

### Misc

- Avoid uploading duplicate ".deb" files ([4409e70](https://gitlab.com/ikus-soft/rdiffweb/commit/4409e7019b42971fedd5b602f88473e5e170905c) by Patrik Dufresne).
- Update auth-mfa to support URI encoding ([ab3feae](https://gitlab.com/ikus-soft/rdiffweb/commit/ab3feaee09cfcb55b883971a9a14287a9767b581) by Patrik Dufresne).

## [2.8.7](https://gitlab.com/ikus-soft/rdiffweb/tags/2.8.7) - 2024-01-04

<small>[Compare with 2.8.6](https://gitlab.com/ikus-soft/rdiffweb/compare/2.8.6...2.8.7)</small>

### Fixed

- Fix date calculation when generating report #295 ([b2819ed](https://gitlab.com/ikus-soft/rdiffweb/commit/b2819ed8508149428e193096839c79daf918c440) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-fix-reporting' into 'master' ([f6d36d2](https://gitlab.com/ikus-soft/rdiffweb/commit/f6d36d2b49e34caa2a536b7150ff3a3b661b47b5) by Patrik Dufresne).
- Merge branch 'patrik-adjust-session-timeout' into 'master' ([b02b517](https://gitlab.com/ikus-soft/rdiffweb/commit/b02b5178952a9e42d48f11c5911e741fc49449ca) by Patrik Dufresne).

### Misc

- Adjust the session idle and absolute timeouts to 10 and 30 minutes, respectively. ([dc1575b](https://gitlab.com/ikus-soft/rdiffweb/commit/dc1575bd3840eac13db203b94a0e0112e124ef34) by Patrik Dufresne).

## [5.0.1](https://gitlab.com/ikus-soft/rdiffweb/tags/5.0.1) - 2023-11-24

<small>[Compare with 5.0.0](https://gitlab.com/ikus-soft/rdiffweb/compare/5.0.0...5.0.1)</small>

### Added

- Add German translation & update documentation ([519dff1](https://gitlab.com/ikus-soft/rdiffweb/commit/519dff13d11fbb1f65a0db524eae6b94d67211cc) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-update-locales' into 'master' ([8342b52](https://gitlab.com/ikus-soft/rdiffweb/commit/8342b5282bdcb6607308b490669ef97ea5be6791) by Patrik Dufresne).

### Misc

- Fix brokken link to https://www.ikus-soft.com ([60c8db2](https://gitlab.com/ikus-soft/rdiffweb/commit/60c8db208a21daff8d19e010b45b8d8184396d04) by Patrik Dufresne).

## [2.8.6](https://gitlab.com/ikus-soft/rdiffweb/tags/2.8.6) - 2023-11-24

<small>[Compare with 2.8.5](https://gitlab.com/ikus-soft/rdiffweb/compare/2.8.5...2.8.6)</small>

### Added

- Adding German translation ([24e64a5](https://gitlab.com/ikus-soft/rdiffweb/commit/24e64a56235845d486906f1c0e7d9c0622c80410) by Patrik Dufresne).

### Fixed

- Fix translation of report #291 ([d5120b8](https://gitlab.com/ikus-soft/rdiffweb/commit/d5120b8dbf87ffc4f44df8a9b9cdf81d42d11a76) by Patrik Dufresne).
- Fix broken links ([2665cdd](https://gitlab.com/ikus-soft/rdiffweb/commit/2665cdd5a161dbe6e10108d48ba1240dbae77a52) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-update-locales' into 'master' ([211d4cb](https://gitlab.com/ikus-soft/rdiffweb/commit/211d4cb8913a529df56af031bd149a745930a0fb) by Patrik Dufresne).
- Merge branch 'patrik-bug-fixes' into 'master' ([a3953e7](https://gitlab.com/ikus-soft/rdiffweb/commit/a3953e732873b6ddba37523df5a3b4650a7b033a) by Patrik Dufresne).
- Merge branch 'patrik-sponsor' into 'master' ([f5b4628](https://gitlab.com/ikus-soft/rdiffweb/commit/f5b4628474fd4b26f4e60d7c9d3aa4cec7aae5d5) by Patrik Dufresne).

### Misc

- Allow click on checkbox buttons #293 ([cd6a4fb](https://gitlab.com/ikus-soft/rdiffweb/commit/cd6a4fbb7ea44baeee946c5e3f7381287b291dc0) by Patrik Dufresne).
- Configure sponsor ([7a7e58c](https://gitlab.com/ikus-soft/rdiffweb/commit/7a7e58ce5968026e2cd894e98d5e1af087c0459f) by Patrik Dufresne).

## [5.0.0](https://gitlab.com/ikus-soft/rdiffweb/tags/5.0.0) - 2023-10-10

<small>[Compare with 4.5.3](https://gitlab.com/ikus-soft/rdiffweb/compare/4.5.3...5.0.0)</small>

### Added

- Add debian version to Debian package ([4c5279c](https://gitlab.com/ikus-soft/rdiffweb/commit/4c5279cf83bfc83cecbc171984ecffb6c8c03577) by Patrik Dufresne).
- Adding restore support on command line ([b0ef1d7](https://gitlab.com/ikus-soft/rdiffweb/commit/b0ef1d796d754abd1c61dba5456daf8981a41cd2) by Patrik Dufresne).
- Add support for rdiff-backup 2.2.x and Ubuntu Lunar #194 #203 ([edd54e4](https://gitlab.com/ikus-soft/rdiffweb/commit/edd54e46d77b5d8b9a171c882133480f829ae21f) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-upgrade-rdiffweb' into 'master' ([3cbe7c1](https://gitlab.com/ikus-soft/rdiffweb/commit/3cbe7c105297b4e9fb757683dafab1112c909297) by Patrik Dufresne).
- Merge branch 'patrik-release' into 'master' ([2d13db9](https://gitlab.com/ikus-soft/rdiffweb/commit/2d13db9d5a7a22c05b8b176d2782e94022effce3) by Patrik Dufresne).
- Merge branch 'patrik-restore-ui' into 'master' ([decfdfb](https://gitlab.com/ikus-soft/rdiffweb/commit/decfdfb07fd9406ba70e06a840662a166541235c) by Patrik Dufresne).
- Merge branch 'patrik-file-stats' into 'master' ([b69037b](https://gitlab.com/ikus-soft/rdiffweb/commit/b69037ba5a3701a2ef2d9ab80d5fe8bb5bd7395c) by Patrik Dufresne).
- Merge branch 'patrik-restore' into 'master' ([73b2890](https://gitlab.com/ikus-soft/rdiffweb/commit/73b28903a306fcd55951adcb4782933f66b726f8) by Patrik Dufresne).
- Merge branch 'patrik-upgrade' into 'master' ([7477f5e](https://gitlab.com/ikus-soft/rdiffweb/commit/7477f5ee2e0e5c4b148233edb2d1269683291bd9) by Patrik Dufresne).
- Merge branch 'patrik-2.2-and-lunar' into 'master' ([e4b9f17](https://gitlab.com/ikus-soft/rdiffweb/commit/e4b9f172a3646ab8b1029d7cc045bab63b4d6153) by Patrik Dufresne).
- Merge branch 'patrik-readme-contribution' into 'master' ([64c05da](https://gitlab.com/ikus-soft/rdiffweb/commit/64c05da26dc0286dcbe214c5f391dc5bf3f56a3c) by Patrik Dufresne).

### Misc

- Upgrade rdiffweb to v2.8.5 ([b637eb3](https://gitlab.com/ikus-soft/rdiffweb/commit/b637eb3a3200597bbac0b8486fc081b62d8874d9) by Patrik Dufresne).
- Update rdiffweb to v2.8.4 ([5461475](https://gitlab.com/ikus-soft/rdiffweb/commit/54614758b97342d5a4f0098c4beb484ee5167dd9) by Patrik Dufresne).
- patrik-fix-test-version ([54e189c](https://gitlab.com/ikus-soft/rdiffweb/commit/54e189ceece9b070bd9ed5ec665fbd134b780e53) by Patrik Dufresne).
- Upgrade rdiffweb to v2.8.2 ([48603be](https://gitlab.com/ikus-soft/rdiffweb/commit/48603bebbf46e94e94060678780f5a302fe471e0) by Patrik Dufresne).
- Upgrade rdiffweb v2.8.2a1 ([e0ec28a](https://gitlab.com/ikus-soft/rdiffweb/commit/e0ec28a6eb9dbfa7bd0b0201f0b9f72d5c639b13) by Patrik Dufresne).
- Upgrade rdiffweb to v2.8.1 ([c437d1b](https://gitlab.com/ikus-soft/rdiffweb/commit/c437d1bdabf5b6c6d7c4c855716be6a37dc650d7) by Patrik Dufresne).
- Upgrade rdiffweb to v2.8.0a9 ([ffe6fba](https://gitlab.com/ikus-soft/rdiffweb/commit/ffe6fba4969fecc1326ab9ffbc0fc07f3fb7dd30) by Patrik Dufresne).
- Deploy file stats - update rdiffweb 2.8.0a7 ([9fa14fa](https://gitlab.com/ikus-soft/rdiffweb/commit/9fa14fa7154bc8fa0b44c67437df2d1bfaf97669) by Patrik Dufresne).
- Upgrade rdiffweb to 2.8.0a5 - ignore weekend ([de99f85](https://gitlab.com/ikus-soft/rdiffweb/commit/de99f8509088dca07a0a1d21a8e2d3c98f3d9a74) by Patrik Dufresne).
- Upgrade rdiffweb to 2.8.0a4 ([3bf7981](https://gitlab.com/ikus-soft/rdiffweb/commit/3bf798129816b546a5c1c69dabcd9f34b5245664) by Patrik Dufresne).
- Upgrade rdiffweb to 2.8.0.a3 ([5b51b5d](https://gitlab.com/ikus-soft/rdiffweb/commit/5b51b5df3e6af2501262ba974267b8cbc268397b) by Patrik Dufresne).
- Upgrade rdiffweb to version 2.8.0a2 ([e429137](https://gitlab.com/ikus-soft/rdiffweb/commit/e429137b46bee18b2b59937d08af96f5dcc64164) by Patrik Dufresne).
- Log original ssh command or user agent on server side ([3aa5e15](https://gitlab.com/ikus-soft/rdiffweb/commit/3aa5e15243aca588c65faa10c8777494b1e51973) by Patrik Dufresne).
- Upgrade rdiffweb to v2.8.0a1 ([7d26380](https://gitlab.com/ikus-soft/rdiffweb/commit/7d26380399e3111421d45ca5b344ea17e16a1c74) by Patrik Dufresne).
- Update Copyright year ([dbcb5d8](https://gitlab.com/ikus-soft/rdiffweb/commit/dbcb5d8e45987b56c8bcac4004d5550511084d97) by Patrik Dufresne).

## [2.8.5](https://gitlab.com/ikus-soft/rdiffweb/tags/2.8.5) - 2023-10-10

<small>[Compare with 2.8.4](https://gitlab.com/ikus-soft/rdiffweb/compare/2.8.4...2.8.5)</small>

### Added

- Add last backup date to email notification #290 ([95d9128](https://gitlab.com/ikus-soft/rdiffweb/commit/95d9128120fd7306238774e8324fc1d6ec3ab0e6) by Patrik Dufresne).
- Add support for WTForm v3.1.0 ([ce52424](https://gitlab.com/ikus-soft/rdiffweb/commit/ce52424a1914e11b615bb854b89dc911d65dfbc3) by Patrik Dufresne).

### Fixed

- Fix Debian version #289 ([9bc08d0](https://gitlab.com/ikus-soft/rdiffweb/commit/9bc08d0b9ba4ff67c5319fa8c1dca81bfa096d95) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-fix-deb-version' into 'master' ([b7e8bf6](https://gitlab.com/ikus-soft/rdiffweb/commit/b7e8bf660d119879caa22f34b97d099151f8ae3a) by Patrik Dufresne).

### Misc

- Update README release note ([2199ad7](https://gitlab.com/ikus-soft/rdiffweb/commit/2199ad79fb0fbd5c76230e4c2006220a5f9619f5) by Patrik Dufresne).

## [2.8.4](https://gitlab.com/ikus-soft/rdiffweb/tags/2.8.4) - 2023-09-29

<small>[Compare with 2.8.3](https://gitlab.com/ikus-soft/rdiffweb/compare/2.8.3...2.8.4)</small>

### Added

- Add ratelimit to AccessToken, SSH Keys, User creation ([06f89b4](https://gitlab.com/ikus-soft/rdiffweb/commit/06f89b43469aae70e8833e55192721523f86c5a2) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-rate-limit' into 'master' ([a783916](https://gitlab.com/ikus-soft/rdiffweb/commit/a783916483d56fa3370bd892fc78bc1677bcae6b) by Patrik Dufresne).

## [2.8.3](https://gitlab.com/ikus-soft/rdiffweb/tags/2.8.3) - 2023-09-22

<small>[Compare with 2.8.2](https://gitlab.com/ikus-soft/rdiffweb/compare/2.8.2...2.8.3)</small>

### Removed

- Remove Ubuntu Kinetic ([c710540](https://gitlab.com/ikus-soft/rdiffweb/commit/c7105406b21661f4825cbd006602993221e6fd8a) by Patrik Dufresne).

## [2.8.2](https://gitlab.com/ikus-soft/rdiffweb/tags/2.8.2) - 2023-08-22

<small>[Compare with 2.8.1](https://gitlab.com/ikus-soft/rdiffweb/compare/2.8.1...2.8.2)</small>

### Added

- Add Ubuntu Mantic support ([1886346](https://gitlab.com/ikus-soft/rdiffweb/commit/188634607b35aaec79aaf652cc8bf403971ab8f0) by Patrik Dufresne).

### Fixed

- Fix Error 500 on Setting page #287 ([64f41e0](https://gitlab.com/ikus-soft/rdiffweb/commit/64f41e05865db1c2acd1f28b7470c00fcabddd21) by Patrik Dufresne).

### Changed

- Change layout of file statistics to display a single day #286 ([0a3af7d](https://gitlab.com/ikus-soft/rdiffweb/commit/0a3af7dc8f34100898c52c1fbe8b462887a7551f) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-disable-days' into 'master' ([994f98b](https://gitlab.com/ikus-soft/rdiffweb/commit/994f98bac4025e5e49ede587bbaebade028c3347) by Patrik Dufresne).
- Merge branch 'patrik-remove-older-exit-code' into 'master' ([4df28b1](https://gitlab.com/ikus-soft/rdiffweb/commit/4df28b12b36f2a1aee9ec4e200c3d01df1318d87) by Patrik Dufresne).
- Merge branch 'patrik-encoding-none' into 'master' ([8be93e6](https://gitlab.com/ikus-soft/rdiffweb/commit/8be93e674806ec92d2fd33eb2562555da3553cdf) by Patrik Dufresne).
- Merge branch 'patrik-split-stats' into 'master' ([a51e64c](https://gitlab.com/ikus-soft/rdiffweb/commit/a51e64ca01e3f936c85039fd1675cb4a77d06d18) by Patrik Dufresne).
- Merge branch 'patrik-selenium' into 'master' ([4bb9c60](https://gitlab.com/ikus-soft/rdiffweb/commit/4bb9c607232e88dba09862c1a5a72a638bbdccee) by Patrik Dufresne).

### Misc

- Use multi-stage to run test in docker image ([f3ffec9](https://gitlab.com/ikus-soft/rdiffweb/commit/f3ffec9ce43d4e6fa60da93a39e8b4905cba4abd) by Patrik Dufresne).
- Do not send notification during ignored days #284 ([085c92c](https://gitlab.com/ikus-soft/rdiffweb/commit/085c92c306f920b27ad02933637b8ee5323403f5) by Patrik Dufresne).
- Handle exit code 2 for rdiff-backup>=2.2.x #285 ([8609fb2](https://gitlab.com/ikus-soft/rdiffweb/commit/8609fb22a0e16424b2359f4dcfc8d5d1fbe0197b) by Patrik Dufresne).
- Unpin selenium version to support >= 4.11 ([31d348f](https://gitlab.com/ikus-soft/rdiffweb/commit/31d348f72a59696f110ec8318457e1ebfdfd8619) by Patrik Dufresne).

## [2.8.1](https://gitlab.com/ikus-soft/rdiffweb/tags/2.8.1) - 2023-08-01

<small>[Compare with 2.8.0](https://gitlab.com/ikus-soft/rdiffweb/compare/2.8.0...2.8.1)</small>

### Misc

- Pin selenium to 4.10 ([431832a](https://gitlab.com/ikus-soft/rdiffweb/commit/431832a9a16db8bb54f613b4ba43e3eabbfe9447) by Patrik Dufresne).

## [2.8.0](https://gitlab.com/ikus-soft/rdiffweb/tags/2.8.0) - 2023-07-31

<small>[Compare with 2.7.1](https://gitlab.com/ikus-soft/rdiffweb/compare/2.7.1...2.8.0)</small>

### Added

- Add increment size to file statistics #103 ([d2477b9](https://gitlab.com/ikus-soft/rdiffweb/commit/d2477b9a9fc116073bdb80f39682c0b38870d2c3) by Patrik Dufresne).
- Add file statistics view #103 ([d9fc924](https://gitlab.com/ikus-soft/rdiffweb/commit/d9fc9249a15666301a34de928fb4eea02fcdbfc8) by Patrik Dufresne).
- Add option to ignore some days of week #278 ([79decc5](https://gitlab.com/ikus-soft/rdiffweb/commit/79decc5688dcad059173bf0b62f48959f290ceb9) by Patrik Dufresne).
- Add fail2ban documentation ([8f3ab07](https://gitlab.com/ikus-soft/rdiffweb/commit/8f3ab074646879e86cbc278f530d7ef3a6564581) by Patrik Dufresne).
- Add ratelimit to "send me a status report" to avoid email flooding #272 ([f771b1b](https://gitlab.com/ikus-soft/rdiffweb/commit/f771b1b6c2a15649a9d37707a743c5d048e30246) by Patrik Dufresne).
- Add support for SQLAlchmey v2.0 #256 ([c01ed7c](https://gitlab.com/ikus-soft/rdiffweb/commit/c01ed7c94cf93e6be469f2313cd0bbe3f4cc2a01) by Patrik Dufresne).
- Add support for Ubuntu Lunar ([ea1c75f](https://gitlab.com/ikus-soft/rdiffweb/commit/ea1c75fb7499110bbad0a855c6bb29fa505eedb2) by Patrik Dufresne).
- Add error logging for restore failure ([91b6378](https://gitlab.com/ikus-soft/rdiffweb/commit/91b6378d63d94f34a611a9b71ffceecf61e3c39b) by Patrik Dufresne).

### Fixed

- Fix flake8 version ([444ed9e](https://gitlab.com/ikus-soft/rdiffweb/commit/444ed9e173c50bc9822b498a38dea72cee04ec18) by Patrik Dufresne).
- Fix file statistics menu ([bd01bc0](https://gitlab.com/ikus-soft/rdiffweb/commit/bd01bc03d539cac739f5c61ee6345482d6b42d49) by Patrik Dufresne).
- Fix presentation of quota in email report ([eea1db3](https://gitlab.com/ikus-soft/rdiffweb/commit/eea1db357bfb40b5ab9dcbd94f318dca22b69fe8) by Patrik Dufresne).
- Fix creation of access token with expiration time #277 ([b273c53](https://gitlab.com/ikus-soft/rdiffweb/commit/b273c5348298f83b17564ecb4dabe0935cf50ee5) by Patrik Dufresne).
- Fix presentation of quota in email notification ([43bf062](https://gitlab.com/ikus-soft/rdiffweb/commit/43bf06211ec5337fe5833b675d189822d5ff9b76) by Patrik Dufresne).

### Removed

- Remove "min" prefix from graphs #252 ([7c9f232](https://gitlab.com/ikus-soft/rdiffweb/commit/7c9f232bd46f1f54be9b713e25fe2685e6c2e061) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-release' into 'master' ([9b1a560](https://gitlab.com/ikus-soft/rdiffweb/commit/9b1a560342b1434dd8e700cfaa15bec291a56d0f) by Patrik Dufresne).
- Merge branch 'patrik-admin-repos-sorting' into 'master' ([dfb4f31](https://gitlab.com/ikus-soft/rdiffweb/commit/dfb4f314f1167620a1439136f4940cf3ec698467) by Patrik Dufresne).
- Merge branch 'patrik-default-login' into 'master' ([df12a09](https://gitlab.com/ikus-soft/rdiffweb/commit/df12a09c54c940123f925a24d886f4f6fc3d4950) by Patrik Dufresne).
- Merge branch 'patrik-graphs' into 'master' ([b7c92d3](https://gitlab.com/ikus-soft/rdiffweb/commit/b7c92d3dde4879e2f383b450fd6c52e85c45a023) by Patrik Dufresne).
- Merge branch 'patrik-trim-verification-code' into 'master' ([68f24db](https://gitlab.com/ikus-soft/rdiffweb/commit/68f24db1bfce037ecfa7908d2d9065917758bb32) by Patrik Dufresne).
- Merge branch 'patrik-view-file-statistics' into 'master' ([20efb24](https://gitlab.com/ikus-soft/rdiffweb/commit/20efb24acbf783151eb6fd7cb6033c5547b41b6c) by Patrik Dufresne).
- Merge branch 'patrik-ignore-weekend' into 'master' ([68c06bd](https://gitlab.com/ikus-soft/rdiffweb/commit/68c06bd4cd51792d4a0817e411eec1acebc3ad3b) by Patrik Dufresne).
- Merge branch 'patrik-email-report' into 'master' ([c530b1f](https://gitlab.com/ikus-soft/rdiffweb/commit/c530b1f9debe31c09e8861dec280821bac470a0c) by Patrik Dufresne).
- Merge branch 'patrik-doc-fail2ban' into 'master' ([7b9b3f2](https://gitlab.com/ikus-soft/rdiffweb/commit/7b9b3f2c984bad12ca150a7ba037dd53181a3866) by Patrik Dufresne).
- Merge branch 'patrik-fix-token-expiration' into 'master' ([d5c387c](https://gitlab.com/ikus-soft/rdiffweb/commit/d5c387caaefff1c568841a180f7e279cbffcda9d) by Patrik Dufresne).
- Merge branch 'patrik-fix-quota-report' into 'master' ([54435f9](https://gitlab.com/ikus-soft/rdiffweb/commit/54435f9448e46a71743daf2e4092a989d05b13a9) by Patrik Dufresne).
- Merge branch 'patrik-ratelimit-send-report' into 'master' ([feef0d7](https://gitlab.com/ikus-soft/rdiffweb/commit/feef0d7b11d86aed29bf98c21526088117964d85) by Patrik Dufresne).
- Merge branch 'patrik-quota-visibility' into 'master' ([e55e019](https://gitlab.com/ikus-soft/rdiffweb/commit/e55e01971164701fc2bb6b79d1944d81dd0bea19) by Patrik Dufresne).
- Merge branch 'patrik-sqlalchemy-2.0' into 'master' ([13383c9](https://gitlab.com/ikus-soft/rdiffweb/commit/13383c9b1db335bd8989e8055eee35606dc37a20) by Patrik Dufresne).
- Merge branch 'patrik-lunar' into 'master' ([bee4e4b](https://gitlab.com/ikus-soft/rdiffweb/commit/bee4e4bfbea9bc18a6e7148d62f63ffc3a5c8fc8) by Patrik Dufresne).
- Merge branch 'patrik-admin-users' into 'master' ([854e076](https://gitlab.com/ikus-soft/rdiffweb/commit/854e07670121d3c95da05eff6c7187503a225ac8) by Patrik Dufresne).

### Misc

- Update Release note ([21657c9](https://gitlab.com/ikus-soft/rdiffweb/commit/21657c9531500ae55fe0603a14454162dfb74991) by Patrik Dufresne).
- Sort repositories by last backup date #282 ([0285a36](https://gitlab.com/ikus-soft/rdiffweb/commit/0285a36851d48fb34ea04701099e455149fa9421) by Patrik Dufresne).
- Use username from redirect URL by default in login page #283 ([25c3a41](https://gitlab.com/ikus-soft/rdiffweb/commit/25c3a4182492860b1865329ef6b633b1ab84a652) by Patrik Dufresne).
- Trim extra space from verification code #279 ([46975f9](https://gitlab.com/ikus-soft/rdiffweb/commit/46975f92e79b9ab875397e1a79b936b85837667b) by Patrik Dufresne).
- Upgrade readme_renderer ([34e6be1](https://gitlab.com/ikus-soft/rdiffweb/commit/34e6be1b328c0a6779119114be265e12d22a79bb) by Patrik Dufresne).
- Update installation steps to include `arch=amd64` #254 ([5065b62](https://gitlab.com/ikus-soft/rdiffweb/commit/5065b62b755d708fa0a9dd51528bce5802a1e1db) by Patrik Dufresne).
- Freeze version of tzlocal in tox.ini ([e03f208](https://gitlab.com/ikus-soft/rdiffweb/commit/e03f20873d0b42621e13fbb1527b53e506a51726) by Patrik Dufresne).
- Update french translation ([e783885](https://gitlab.com/ikus-soft/rdiffweb/commit/e783885a37ff79cd37ceffc5e771da5949d2d522) by Patrik Dufresne).
- Send notification when user's quota reach 90% #46 ([a39e16b](https://gitlab.com/ikus-soft/rdiffweb/commit/a39e16b91491a08e8213c234e4301f64187892d8) by Patrik Dufresne).
- Update display of disk quota ([43124fb](https://gitlab.com/ikus-soft/rdiffweb/commit/43124fbcc76d09130c6287a4c0ea94a2a40e1200) by Patrik Dufresne).
- Update networking documentation to include certbot configuration ([0542897](https://gitlab.com/ikus-soft/rdiffweb/commit/054289730f8ae1963325856552c8f7fe12daafc7) by Patrik Dufresne).
- Update Banner ([93b0bd9](https://gitlab.com/ikus-soft/rdiffweb/commit/93b0bd9709ffe6a8df8165995afb6a40ad8cf8f6) by Patrik Dufresne).
- Allow admin to select report time range ([2bdae7a](https://gitlab.com/ikus-soft/rdiffweb/commit/2bdae7a032d24a7fbee852193e37c3a937ac473a) by Patrik Dufresne).
- Improve user management interface #237 ([8ff0766](https://gitlab.com/ikus-soft/rdiffweb/commit/8ff07665582555a7ea890cd484066dccf7db88e5) by Patrik Dufresne).

## [2.7.1](https://gitlab.com/ikus-soft/rdiffweb/tags/2.7.1) - 2023-04-29

<small>[Compare with 2.7.0](https://gitlab.com/ikus-soft/rdiffweb/compare/2.7.0...2.7.1)</small>

### Fixed

- Fix encoding problem with older Outlook 2007 client #273 ([2944cc4](https://gitlab.com/ikus-soft/rdiffweb/commit/2944cc4c0af8af99863c6f340075306e96f5238c) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-outlook-encoding' into 'master' ([5126aac](https://gitlab.com/ikus-soft/rdiffweb/commit/5126aac07e9f025156d2e64d6f1107120f2625d2) by Patrik Dufresne).
- Merge branch 'patrik-update-copyright-year' into 'master' ([928eba0](https://gitlab.com/ikus-soft/rdiffweb/commit/928eba08c1ec8022699256ba269cd59e11ee3c41) by Patrik Dufresne).

### Misc

- Update copyright year ([e9b134b](https://gitlab.com/ikus-soft/rdiffweb/commit/e9b134b0c757b25c773a682d76b3b199c3317afd) by Patrik Dufresne).

## [4.5.3](https://gitlab.com/ikus-soft/rdiffweb/tags/4.5.3) - 2023-04-24

<small>[Compare with 4.4.1](https://gitlab.com/ikus-soft/rdiffweb/compare/4.4.1...4.5.3)</small>

### Merged

- Merge branch 'patrik-update-rdiffweb' into 'master' ([f9b5d6d](https://gitlab.com/ikus-soft/rdiffweb/commit/f9b5d6db003ba8383833857a1a3cbd104d8c6b75) by Patrik Dufresne).

### Misc

- Update Rdiffweb ([86a6216](https://gitlab.com/ikus-soft/rdiffweb/commit/86a62160c9d8c2627a57b9b2a25d73b7f829a502) by Patrik Dufresne).

## [2.7.0](https://gitlab.com/ikus-soft/rdiffweb/tags/2.7.0) - 2023-04-20

<small>[Compare with 2.6.1](https://gitlab.com/ikus-soft/rdiffweb/compare/2.6.1...2.7.0)</small>

### Added

- Add test with invalid `default-lang` ([2bf5b5e](https://gitlab.com/ikus-soft/rdiffweb/commit/2bf5b5e66561a89dcdf1535e10311f1fed5e3a66) by Patrik Dufresne).

### Fixed

- Fix time calculation and timerange for reporting #71 ([0235d2b](https://gitlab.com/ikus-soft/rdiffweb/commit/0235d2b3a0d3fba3ac5fdd9117fb94a29dc4283c) by Patrik Dufresne).
- Fix translation of email_layout ([4240a79](https://gitlab.com/ikus-soft/rdiffweb/commit/4240a79fed389dad71e913c3725527952af66e09) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-prepare-release' into 'master' ([f028f7c](https://gitlab.com/ikus-soft/rdiffweb/commit/f028f7ce8395bb1c9c579bfc1c645412d41191e8) by Patrik Dufresne).
- Merge branch 'patrik-minor-changes' into 'master' ([d66d674](https://gitlab.com/ikus-soft/rdiffweb/commit/d66d6744db99315fd67bba0fb57fde47d04ebf70) by Patrik Dufresne).
- Merge branch 'patrik-fix-report' into 'master' ([4d6f4ce](https://gitlab.com/ikus-soft/rdiffweb/commit/4d6f4ce82a62032e78fd497c330c5bbf9069bb68) by Patrik Dufresne).
- Merge branch 'patrik-selenium-test' into 'master' ([e94d347](https://gitlab.com/ikus-soft/rdiffweb/commit/e94d347b85431673fa124a19845a8c7d17c37203) by Patrik Dufresne).
- Merge branch 'patrik-check-latest' into 'master' ([78739a0](https://gitlab.com/ikus-soft/rdiffweb/commit/78739a0a697367f431943731db4abb87ab75fe87) by Patrik Dufresne).
- Merge branch 'patrik-monthly-report' into 'master' ([324ac8d](https://gitlab.com/ikus-soft/rdiffweb/commit/324ac8d6865dbf5a2459d57ee77643144e89c78a) by Patrik Dufresne).
- Merge branch 'patrik-fix-notification-error' into 'master' ([83b672f](https://gitlab.com/ikus-soft/rdiffweb/commit/83b672f4c2a9bf755ffec604add8e198e7c67c2f) by Patrik Dufresne).
- Merge branch 'patrik-test-2.2' into 'master' ([6fa3cd8](https://gitlab.com/ikus-soft/rdiffweb/commit/6fa3cd8f2f6938fe352ff4a3df9c2b3698d174a5) by Patrik Dufresne).
- Merge branch 'patrik-test-invalid-default-lang' into 'master' ([d0cb705](https://gitlab.com/ikus-soft/rdiffweb/commit/d0cb70554720945aa05e933cc6ece454b1cab5cb) by Patrik Dufresne).

### Misc

- Prepare 2.7.0 release ([f5dcd6d](https://gitlab.com/ikus-soft/rdiffweb/commit/f5dcd6dc4c7e59d5dfc9a013c07e7b6064d4a345) by Patrik Dufresne).
- Do not validate user_root if empty ([6b38f5f](https://gitlab.com/ikus-soft/rdiffweb/commit/6b38f5f796df1cbf2906c85d202e2943e04faf72) by Patrik Dufresne).
- Update help mage to recommand png instead of SVG ([6fc578b](https://gitlab.com/ikus-soft/rdiffweb/commit/6fc578b8bbe572767e41277fe54d48dd9545c5f6) by Patrik Dufresne).
- Little adjustment for reporting ([b5c4374](https://gitlab.com/ikus-soft/rdiffweb/commit/b5c4374ebf48684c1bbfa373e0dd1aeffde212fb) by Patrik Dufresne).
- Improve testing of browse page using Selenium ([3c768d9](https://gitlab.com/ikus-soft/rdiffweb/commit/3c768d9deb98f52871249c099fef11e39ced5207) by Patrik Dufresne).
- Check new version availability #266 ([a93a389](https://gitlab.com/ikus-soft/rdiffweb/commit/a93a389f8d9e4498eca7b3b79b9b0ee574f951de) by Patrik Dufresne).
- Provide a Monthly, Weekly or Daily report #71 ([57f1e5b](https://gitlab.com/ikus-soft/rdiffweb/commit/57f1e5b3599795370d5b20093ad6acb7337a24f3) by Patrik Dufresne).
- Re-visit Post-redirect-get pattern ([2a2ad75](https://gitlab.com/ikus-soft/rdiffweb/commit/2a2ad75143cc32de3d8d7a1b2df5451f05890fe3) by Patrik Dufresne).
- Define subject for MFA Verification Code email #270 ([2982c4e](https://gitlab.com/ikus-soft/rdiffweb/commit/2982c4ebcf32cf17041ca11f89a0a24a1ead2c65) by Patrik Dufresne).
- Review testing matrix in CICD pipeline ([10ecd1b](https://gitlab.com/ikus-soft/rdiffweb/commit/10ecd1bd01830859b2389b23ae82de72166d28e7) by Patrik Dufresne).

## [4.4.1](https://gitlab.com/ikus-soft/rdiffweb/tags/4.4.1) - 2023-03-22

<small>[Compare with 4.4.0](https://gitlab.com/ikus-soft/rdiffweb/compare/4.4.0...4.4.1)</small>

### Fixed

- Fix `rdiff-backup` executable lookup ([faaa579](https://gitlab.com/ikus-soft/rdiffweb/commit/faaa579d1f32afc63bfbae5acdd813026d2b9287) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-bookworm' into 'master' ([d7db883](https://gitlab.com/ikus-soft/rdiffweb/commit/d7db883fad6cde3e6fd130a596f654b0b84049e7) by Patrik Dufresne).

## [2.6.1](https://gitlab.com/ikus-soft/rdiffweb/tags/2.6.1) - 2023-03-22

<small>[Compare with 2.6.0](https://gitlab.com/ikus-soft/rdiffweb/compare/2.6.0...2.6.1)</small>

### Merged

- Merge branch 'patrik-search-rdiff-backup' into 'master' ([58b8f56](https://gitlab.com/ikus-soft/rdiffweb/commit/58b8f56cf8c8d3bafd830b07f13a38e71f0fd534) by Patrik Dufresne).

### Misc

- Fail to start if rdiff-backup is not found #267 ([e68cca9](https://gitlab.com/ikus-soft/rdiffweb/commit/e68cca9743746ac113e489e044f70d6561f4daab) by Patrik Dufresne).
- Update README file ([e2ed8dc](https://gitlab.com/ikus-soft/rdiffweb/commit/e2ed8dc153ba9e7e168417c7a485943786b76261) by Patrik Dufresne).

## [4.4.0](https://gitlab.com/ikus-soft/rdiffweb/tags/4.4.0) - 2023-03-15

<small>[Compare with 4.3.0](https://gitlab.com/ikus-soft/rdiffweb/compare/4.3.0...4.4.0)</small>

### Merged

- Merge branch 'patrik-default-lang' into 'master' ([4fe0506](https://gitlab.com/ikus-soft/rdiffweb/commit/4fe050667b74e9a1c723269554ab72f5a4b1bd6a) by Patrik Dufresne).
- Merge branch 'patrik-reporting' into 'master' ([5b013cd](https://gitlab.com/ikus-soft/rdiffweb/commit/5b013cd23b0b0e0e7211b41fdadc7f31cdd68579) by Patrik Dufresne).
- Merge branch 'patrik-create-deb' into 'master' ([9e2a2a2](https://gitlab.com/ikus-soft/rdiffweb/commit/9e2a2a22061a349d7b57389fde8545bff50b0e18) by Patrik Dufresne).

### Misc

- Upgrade rdiffweb to 2.6.0 to include default-lang ([1992515](https://gitlab.com/ikus-soft/rdiffweb/commit/1992515322d69a5fe6cf8184b8c0fbcd2ea365ed) by Patrik Dufresne).
- Upgrade rdiffweb to include reporting ([11fffc1](https://gitlab.com/ikus-soft/rdiffweb/commit/11fffc1ebc1c1d03a0e183d4de71e0ee3fae205b) by Patrik Dufresne).
- Redistribute logos in PNG format for better compatibility ([c277a58](https://gitlab.com/ikus-soft/rdiffweb/commit/c277a587b7e40624720f5ae5ccbd960bbc254280) by Patrik Dufresne).
- Use debbuild to create DEB package for minarca-client ([26785d7](https://gitlab.com/ikus-soft/rdiffweb/commit/26785d7d239d5f6fc2f91a8d6e16684ddf0a330e) by Patrik Dufresne).

## [2.6.0](https://gitlab.com/ikus-soft/rdiffweb/tags/2.6.0) - 2023-03-15

<small>[Compare with 2.5.8](https://gitlab.com/ikus-soft/rdiffweb/compare/2.5.8...2.6.0)</small>

### Added

- Add test with selenium & validate HTML ([944ef7f](https://gitlab.com/ikus-soft/rdiffweb/commit/944ef7f58a5933b03b12d8672288be77f78a1e9d) by Patrik Dufresne).
- Add catch-all email for notification #258 ([c176bee](https://gitlab.com/ikus-soft/rdiffweb/commit/c176beee7b2ba96f9bb63391c98cc296075e37c3) by Patrik Dufresne).
- Add external_url configuration #257 ([29a9534](https://gitlab.com/ikus-soft/rdiffweb/commit/29a9534fd58ec81439a96e9829296c8693277e45) by Patrik Dufresne).

### Fixed

- Fix display of "* minutes ago" #264 ([069ccf6](https://gitlab.com/ikus-soft/rdiffweb/commit/069ccf64ab324053744a9405dca8568e9a4eb4dd) by Patrik Dufresne).
- Fix delete repository vs path deletion #250 ([991bbcf](https://gitlab.com/ikus-soft/rdiffweb/commit/991bbcffe99e8edbcf4e3270d00ad6c342c19801) by Patrik Dufresne).
- Fix deletion of repositories in subdirectory #250 ([0f62f32](https://gitlab.com/ikus-soft/rdiffweb/commit/0f62f32950e4436f3e5e9f335de0f9ac90cfe740) by Patrik Dufresne).

### Changed

- Change layout of repositories ([edee07d](https://gitlab.com/ikus-soft/rdiffweb/commit/edee07da99a141ccbc7f003779843b2632687eaf) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-upgrade-ldap' into 'master' ([cb5a74a](https://gitlab.com/ikus-soft/rdiffweb/commit/cb5a74aa9a4efa77b0076cb3df5852f9050f7ec3) by Patrik Dufresne).
- Merge branch 'patrik-selenium' into 'master' ([2333266](https://gitlab.com/ikus-soft/rdiffweb/commit/2333266d56a173515c1901067f86a9e534d32f6b) by Patrik Dufresne).
- Merge branch 'patrik-fix-send-mail-subject' into 'master' ([cf5d62e](https://gitlab.com/ikus-soft/rdiffweb/commit/cf5d62e7a57d9ac0c24a50291f4b56e0c6ba9e5b) by Patrik Dufresne).
- Merge branch 'patrik-update-translation' into 'master' ([87b257a](https://gitlab.com/ikus-soft/rdiffweb/commit/87b257a0d9c9b275f87ff3f758a0a6db64e51ff6) by Patrik Dufresne).
- Merge branch 'patrik-default-lang' into 'master' ([10c58dc](https://gitlab.com/ikus-soft/rdiffweb/commit/10c58dc726856bccf3bcbb853e98cb8bb746ce57) by Patrik Dufresne).
- Merge branch 'patrik-systemlog-rename-columns' into 'master' ([785f443](https://gitlab.com/ikus-soft/rdiffweb/commit/785f443ab0a27a6b293dc104e619d21f014ca50f) by Patrik Dufresne).
- Merge branch 'patrik-minute-ago' into 'master' ([5dafda6](https://gitlab.com/ikus-soft/rdiffweb/commit/5dafda6dbd56b653a70b589b850caba8ad653bbc) by Patrik Dufresne).
- Merge branch 'patrik-404-invalid-log' into 'master' ([b8ec822](https://gitlab.com/ikus-soft/rdiffweb/commit/b8ec822a84b617840841239e024103dba4a8c443) by Patrik Dufresne).
- Merge branch 'patrik-fix-remove-older' into 'master' ([19e55a6](https://gitlab.com/ikus-soft/rdiffweb/commit/19e55a68f27f4873063f90cdbf4037b9a1af3b8b) by Patrik Dufresne).
- Merge branch 'patrik-initial-backup' into 'master' ([5561980](https://gitlab.com/ikus-soft/rdiffweb/commit/5561980aaf3bb48f229a003b5b220293fc034233) by Patrik Dufresne).
- Merge branch 'master' into 'patrik-fix-remove-older' ([f97c0b9](https://gitlab.com/ikus-soft/rdiffweb/commit/f97c0b9722dfce35c3aa2ccef4cf68f365e9cdcf) by Patrik Dufresne).
- Merge branch 'patrik-admin-notification' into 'master' ([12c6fc2](https://gitlab.com/ikus-soft/rdiffweb/commit/12c6fc2f3f9117e620c23cc38a3ab074df36463d) by Patrik Dufresne).
- Merge branch 'patrik-event' into 'master' ([22c7807](https://gitlab.com/ikus-soft/rdiffweb/commit/22c78079a5abd67a95882473d7c09d42c42daf5c) by Patrik Dufresne).
- Merge branch 'rdiffweb-ldapfix-master' into 'master' ([ad5f397](https://gitlab.com/ikus-soft/rdiffweb/commit/ad5f3979d78e6e3f1d07c8b03ec5fc21645259e8) by Patrik Dufresne).
- Merge branch 'patrik-fixes' into 'master' ([a839aef](https://gitlab.com/ikus-soft/rdiffweb/commit/a839aef9ebbdd44e40622075a6a94d7aade50e62) by Patrik Dufresne).
- Merge branch 'patrik-status-view' into 'master' ([430d2c2](https://gitlab.com/ikus-soft/rdiffweb/commit/430d2c20950df8c1380043524a53f1e694f6d376) by Patrik Dufresne).
- Merge branch 'patrik-layout-repositories' into 'master' ([b435124](https://gitlab.com/ikus-soft/rdiffweb/commit/b4351243d4ceee6143770177865835481f9c67e6) by Patrik Dufresne).
- Merge branch 'patrik-external-url' into 'master' ([f214416](https://gitlab.com/ikus-soft/rdiffweb/commit/f2144165e2bc723e661555c27444945e2a5834db) by Patrik Dufresne).
- Merge branch 'patrik-quota-documentation' into 'master' ([238b4f5](https://gitlab.com/ikus-soft/rdiffweb/commit/238b4f5b6a09022623a713687d8f444905f14ed2) by Patrik Dufresne).
- Merge branch 'patrik-hotfix-sqlalchemy' into 'master' ([714478c](https://gitlab.com/ikus-soft/rdiffweb/commit/714478c761aee05fd71049836858811c7d572a32) by Patrik Dufresne).
- Merge branch 'master' into 'patrik-hotfix-sqlalchemy' ([68298e5](https://gitlab.com/ikus-soft/rdiffweb/commit/68298e5a7582d81ead10bec3498395b3f1a97f85) by Patrik Dufresne).
- Merge branch 'patrik-email-template' into 'master' ([b06acfb](https://gitlab.com/ikus-soft/rdiffweb/commit/b06acfbf894293098b710745fb38c37ca6b4da1a) by Patrik Dufresne).
- Merge branch 'patrik-notification-no-activity' into 'master' ([6cbe5a2](https://gitlab.com/ikus-soft/rdiffweb/commit/6cbe5a2c7c2a5e32e7a66db9d7eb23c5f78be21f) by Patrik Dufresne).
- Merge branch 'patrik-deletion' into 'master' ([b1f2a8a](https://gitlab.com/ikus-soft/rdiffweb/commit/b1f2a8abea8c5db1fa11ea6978f66fd88725b225) by Patrik Dufresne).

### Misc

- Update README for release ([ae47b01](https://gitlab.com/ikus-soft/rdiffweb/commit/ae47b017df94a6b95ca09a4de7394ef4e96195f3) by Patrik Dufresne).
- Update Quick Start documentation ([321a0cb](https://gitlab.com/ikus-soft/rdiffweb/commit/321a0cbbb9e14fdce774e3a1aacce23d21421d60) by Patrik Dufresne).
- Upgrade ldap module to support multiple required group ([ded48a4](https://gitlab.com/ikus-soft/rdiffweb/commit/ded48a40d352179932587e91a75b25af4de502c3) by Patrik Dufresne).
- Make sure email has a subject ([fa0c286](https://gitlab.com/ikus-soft/rdiffweb/commit/fa0c28640354616781177ff9c968a380546e7b5e) by Patrik Dufresne).
- Update french translation ([441cf73](https://gitlab.com/ikus-soft/rdiffweb/commit/441cf7343558c6b5405ce53c5b642d48a0772153) by Patrik Dufresne).
- Improve language control #263 ([0d4a7c4](https://gitlab.com/ikus-soft/rdiffweb/commit/0d4a7c424689c97d0dee709cd9a9d74baa8ada60) by Patrik Dufresne).
- Make sure to use json instead of simplejson ([43a0818](https://gitlab.com/ikus-soft/rdiffweb/commit/43a0818b1be435e8cfdf2d143f12ba5e6ee95b81) by Patrik Dufresne).
- Rename System Logs columns #265 ([52ddfab](https://gitlab.com/ikus-soft/rdiffweb/commit/52ddfab93895c829eb9948689a26877a98d20ef6) by Patrik Dufresne).
- Distinct between initial backup and interrupted ([57549df](https://gitlab.com/ikus-soft/rdiffweb/commit/57549df9be0c4fc16b5bf5ffc0e0f2076e4b8181) by Patrik Dufresne).
- Raise 404 error on invalid log file #259 ([eadf473](https://gitlab.com/ikus-soft/rdiffweb/commit/eadf473c5c601f21019d51e9aee377c28fa7b272) by Patrik Dufresne).
- Improve "remove-older" logging #262 ([d856554](https://gitlab.com/ikus-soft/rdiffweb/commit/d856554f2c9f43b0dac32cc96e64c99b4e8ea947) by Patrik Dufresne).
- Update ldap.py ([3d8507c](https://gitlab.com/ikus-soft/rdiffweb/commit/3d8507c4ab87406abc278d9cb496d67fb5fdb286) by Shane Robinson).
- Redesign timerange selection widget ([98568ce](https://gitlab.com/ikus-soft/rdiffweb/commit/98568ce3fcd7a1985c1a80ff97b40564b81cd3b9) by Patrik Dufresne).
- Update README ([33a8921](https://gitlab.com/ikus-soft/rdiffweb/commit/33a8921fe0813d6d2c787a48f254fe896e9d79fa) by Patrik Dufresne).
- Sort disk usage & Release session lock early for Ajax request ([c2e93c5](https://gitlab.com/ikus-soft/rdiffweb/commit/c2e93c5b2e0b9501bbbb3bba30244ba12388ebcb) by Patrik Dufresne).
- Improve System Logs view #62 ([e0a5399](https://gitlab.com/ikus-soft/rdiffweb/commit/e0a5399f050b91fa4b5fb3b46dad282cfaa10eb6) by Patrik Dufresne).
- Make use of timezone aware datetime ([d21e93a](https://gitlab.com/ikus-soft/rdiffweb/commit/d21e93aca770d48a89795eab5749e10e8418a573) by Patrik Dufresne).
- Support Setuptools v66 ([7d932d9](https://gitlab.com/ikus-soft/rdiffweb/commit/7d932d932e0cef4bb46c871ee90cbfa4acf2325b) by Patrik Dufresne).
- Adjust server log to include IP address and username for real request ([915f0a4](https://gitlab.com/ikus-soft/rdiffweb/commit/915f0a4579f01fd3b99954c4678a513f389794c3) by Patrik Dufresne).
- Only log server error ([63a9044](https://gitlab.com/ikus-soft/rdiffweb/commit/63a9044c36a11681652b6591ba60134be8fc57ff) by Patrik Dufresne).
- Update EXT4 quota documentation ([fc17d07](https://gitlab.com/ikus-soft/rdiffweb/commit/fc17d076aa6823b7d43be66a5ec9693200905dbc) by Patrik Dufresne).
- Make deletion test more stable ([6af8d27](https://gitlab.com/ikus-soft/rdiffweb/commit/6af8d27493d1701d096a1797c71cb159f41fc582) by Patrik Dufresne).
- Provide a better overview in Status view ([1dfebf3](https://gitlab.com/ikus-soft/rdiffweb/commit/1dfebf384f5c509c1d4a839cbe0c5339bfd0a227) by Patrik Dufresne).
- Redistribute logos in PNG format for better compatibility ([f2c3044](https://gitlab.com/ikus-soft/rdiffweb/commit/f2c304410a5ad28ed21d40d64c528840b48294ad) by Patrik Dufresne).
- Improve html2text implementation ([0d179f1](https://gitlab.com/ikus-soft/rdiffweb/commit/0d179f17c0eb144cffc74b7dee5e345b8568d783) by Patrik Dufresne).
- Use bootstrapemail to generate email template ([b066ada](https://gitlab.com/ikus-soft/rdiffweb/commit/b066ada9f9d191a2f3dda0144ddab57e3a0cc612) by Patrik Dufresne).
- Send notification for inactive backup based on statistics ([2f77b43](https://gitlab.com/ikus-soft/rdiffweb/commit/2f77b437c064635dbd186ed6174a974ff03ad1b0) by Patrik Dufresne).

## [2.5.8](https://gitlab.com/ikus-soft/rdiffweb/tags/2.5.8) - 2023-02-19

<small>[Compare with 2.5.7](https://gitlab.com/ikus-soft/rdiffweb/compare/2.5.7...2.5.8)</small>

### Fixed

- Fix execution of rdiffweb remove-older job to clean-up repository history #262 ([532dd2c](https://gitlab.com/ikus-soft/rdiffweb/commit/532dd2c1d1b9f937ac8a93607e006475933f0215) by Patrik Dufresne).

### Misc

- Support Setuptools v66 ([5e9d089](https://gitlab.com/ikus-soft/rdiffweb/commit/5e9d089046d40f220c2c609b5c5da99e353bfb8d) by Patrik Dufresne).

## [2.5.7](https://gitlab.com/ikus-soft/rdiffweb/tags/2.5.7) - 2023-01-27

<small>[Compare with 2.5.6](https://gitlab.com/ikus-soft/rdiffweb/compare/2.5.6...2.5.7)</small>

### Misc

- Enforce SQLAlchemy version between 1.2 or 1.4 ([5eb27cd](https://gitlab.com/ikus-soft/rdiffweb/commit/5eb27cd767831f6b8cfba4b06e6084e6dfbb57de) by Patrik Dufresne).

## [4.3.0](https://gitlab.com/ikus-soft/rdiffweb/tags/4.3.0) - 2023-01-16

<small>[Compare with 4.2.5](https://gitlab.com/ikus-soft/rdiffweb/compare/4.2.5...4.3.0)</small>

### Added

- Add man page to minarca-server ([905b19b](https://gitlab.com/ikus-soft/rdiffweb/commit/905b19bf84478b316d665dc20f8953dbf2f3706a) by Patrik Dufresne).
- Add test for SSH Key comments ([4790a8a](https://gitlab.com/ikus-soft/rdiffweb/commit/4790a8ae74dfe626cf167914a42b452653d7f038) by Patrik Dufresne).

### Fixed

- Fix flake8 config ([e625c22](https://gitlab.com/ikus-soft/rdiffweb/commit/e625c2236c770c648de2f4bde6d8f9d0624ab5c8) by Patrik Dufresne).
- Fix Rdiffweb version to 2.5.0 ([716af85](https://gitlab.com/ikus-soft/rdiffweb/commit/716af852846969afeba43268885700afca2f4ef6) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-final-changes' into 'master' ([496278b](https://gitlab.com/ikus-soft/rdiffweb/commit/496278b5201b191fe901403d7df52603e31e0e52) by Patrik Dufresne).
- Merge branch 'patrik-import-error-message' into 'master' ([1c96028](https://gitlab.com/ikus-soft/rdiffweb/commit/1c96028b677bad0cc1c95ce5d22e4e202fc14278) by Patrik Dufresne).
- Merge branch 'patrik-update-theme' into 'master' ([25e1813](https://gitlab.com/ikus-soft/rdiffweb/commit/25e181367ef27afb370c9169e57ccc675072aa37) by Patrik Dufresne).
- Merge branch 'patrik-upgrade-rdiffweb-2.5.2' into 'master' ([be67c0a](https://gitlab.com/ikus-soft/rdiffweb/commit/be67c0a8488677b7772619d2ee4373b40d11885d) by Patrik Dufresne).
- Merge branch 'patrik-background-task-update-attr-quota' into 'master' ([6dc3b1b](https://gitlab.com/ikus-soft/rdiffweb/commit/6dc3b1bfaf9c7ae93a68e7dc45c914f33ebfaa31) by Patrik Dufresne).
- Merge branch 'patrik-upgrade-rdiffweb' into 'master' ([bc2032a](https://gitlab.com/ikus-soft/rdiffweb/commit/bc2032a17e9e0cd99eae7880a6dd422a738f508b) by Patrik Dufresne).
- Merge branch 'patrik-upgrade-french-translation' into 'master' ([d6e7ef2](https://gitlab.com/ikus-soft/rdiffweb/commit/d6e7ef2dfcf3a96f037a27c521c18d07e7a11835) by Patrik Dufresne).

### Misc

- Cosmetic changes ([b6080f1](https://gitlab.com/ikus-soft/rdiffweb/commit/b6080f1666a7c755528f8a55ad459c4ef7c54be7) by Patrik Dufresne).
- Update server default theme ([8212023](https://gitlab.com/ikus-soft/rdiffweb/commit/8212023b65ea6de1b8cda7f6b87ca284ad1f7c17) by Patrik Dufresne).
- Upgrade rdiffweb to 2.5.3 ([9efcd6b](https://gitlab.com/ikus-soft/rdiffweb/commit/9efcd6ba9f52d7ea9acf742b572d03778f6d0aee) by Patrik Dufresne).
- Update documentation ([0e03c98](https://gitlab.com/ikus-soft/rdiffweb/commit/0e03c98a16839c3bfb9e816e7d0ee656f2ca246e) by Patrik Dufresne).
- Upgrade Rdiffweb to 2.5.2 ([9fdedf7](https://gitlab.com/ikus-soft/rdiffweb/commit/9fdedf76843a0510d87f209377b89320404633ce) by Patrik Dufresne).
- Upgrade rdiffweb to 2.5.1 ([5f14fe7](https://gitlab.com/ikus-soft/rdiffweb/commit/5f14fe7dd446b7686b14645e250e385599ee1f4c) by Patrik Dufresne).
- Run user's quota update in background task #186 ([d64487f](https://gitlab.com/ikus-soft/rdiffweb/commit/d64487f57aa4b2d4db3fcd8062f43c27e37cec8f) by Patrik Dufresne).
- Update website url to minarca.org ([94a1f38](https://gitlab.com/ikus-soft/rdiffweb/commit/94a1f3809a9e9849e463adbe79c3e2746ce05d52) by Patrik Dufresne).
- Upgrade to 2.5.0a9 ([e5a4780](https://gitlab.com/ikus-soft/rdiffweb/commit/e5a478098d31b0d43d74131dc8352d18c22ffa59) by Patrik Dufresne).
- Upgrade rdiffweb v2.5.0a6 ([f6c306d](https://gitlab.com/ikus-soft/rdiffweb/commit/f6c306d18bd9999dc68b8ff3176687a66ef2df43) by Patrik Dufresne).
- Replace deprecated references of `disutils.spawn.find_executable()` by `shutil.which()` ([3422a80](https://gitlab.com/ikus-soft/rdiffweb/commit/3422a807a971cb4c8ac0b1a286908985987a46d4) by Patrik Dufresne).
- Upgrade rdiffweb v2.5.0a1 include SQL Alchemy ORM ([d45c1f9](https://gitlab.com/ikus-soft/rdiffweb/commit/d45c1f9ee5a39c5a73a0ee0dd618ac41cc7bcbe6) by Patrik Dufresne).

## [2.5.6](https://gitlab.com/ikus-soft/rdiffweb/tags/2.5.6) - 2023-01-12

<small>[Compare with 2.5.5](https://gitlab.com/ikus-soft/rdiffweb/compare/2.5.5...2.5.6)</small>

### Fixed

- Fix Hamburger menu and change working minarca#192 ([b4add6d](https://gitlab.com/ikus-soft/rdiffweb/commit/b4add6db996813bebffa97082e9550ebf246f461) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-little-changes' into 'master' ([09425fe](https://gitlab.com/ikus-soft/rdiffweb/commit/09425fe5588f1f0c29951a6f2b0fe5d485cc0e33) by Patrik Dufresne).

## [2.5.5](https://gitlab.com/ikus-soft/rdiffweb/tags/2.5.5) - 2022-12-23

<small>[Compare with 2.5.4](https://gitlab.com/ikus-soft/rdiffweb/compare/2.5.4...2.5.5)</small>

### Fixed

- Fix loading of status graph ([26149ba](https://gitlab.com/ikus-soft/rdiffweb/commit/26149baa666e018b773b55da8eb82874e3650d0d) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-huntr' into 'master' ([70c1de6](https://gitlab.com/ikus-soft/rdiffweb/commit/70c1de694f1f93efa494f29115b33857aa496e8d) by Patrik Dufresne).
- Merge branch 'patrik-fix-status-graph' into 'master' ([b0c1422](https://gitlab.com/ikus-soft/rdiffweb/commit/b0c142251987302e04b2b1c35cf229b7bf93ff57) by Patrik Dufresne).

### Misc

- Disable translation caching ([fcffdb3](https://gitlab.com/ikus-soft/rdiffweb/commit/fcffdb3ac3164be44891e2a019a66b1f2739cd95) by Patrik Dufresne).
- Make sure that all ssh keys are unique, regardless of the user ([c4a19cf](https://gitlab.com/ikus-soft/rdiffweb/commit/c4a19cf67d575c4886171b8efcbf4675d51f3929) by Patrik Dufresne).
- Make username case-insensitive ([d1aaa96](https://gitlab.com/ikus-soft/rdiffweb/commit/d1aaa96b665a39fba9e98d6054a9de511ba0a837) by Patrik Dufresne).
- Ratelimit "Resend code to my email" in Two-Factor Authentication view ([6e9ee21](https://gitlab.com/ikus-soft/rdiffweb/commit/6e9ee210548f6d3210704cac302cfc7cdb239765) by Patrik Dufresne).
- Send notification on new SSH Key ([bc4bed8](https://gitlab.com/ikus-soft/rdiffweb/commit/bc4bed89affcba71251fe54ed10639da9d392c1d) by Patrik Dufresne).
- Disable automatic hyperlink in email template ([6afaae5](https://gitlab.com/ikus-soft/rdiffweb/commit/6afaae56a29536f0118b3380d296c416aa6d078d) by Patrik Dufresne).

## [2.5.4](https://gitlab.com/ikus-soft/rdiffweb/tags/2.5.4) - 2022-12-19

<small>[Compare with 2.5.3](https://gitlab.com/ikus-soft/rdiffweb/compare/2.5.3...2.5.4)</small>

### Added

- Add CSRF verification on `/logout` ([e6f0d80](https://gitlab.com/ikus-soft/rdiffweb/commit/e6f0d8002129be90fe82fa3e3ea0a6942caba398) by Patrik Dufresne).

### Fixed

- Fix graphs loading ([fffa013](https://gitlab.com/ikus-soft/rdiffweb/commit/fffa013fc7bfbae698547e66659236a672c1644c) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-graph' into 'master' ([4e4b4cd](https://gitlab.com/ikus-soft/rdiffweb/commit/4e4b4cd70001f2dc1c08c8e7bdaac0a9b8bf6ac0) by Patrik Dufresne).
- Merge branch 'patrik-branding' into 'master' ([0f07279](https://gitlab.com/ikus-soft/rdiffweb/commit/0f07279e64f6969afe17776a7fc94ca37ad91643) by Patrik Dufresne).
- Merge branch 'patrik-csrf-logout' into 'master' ([7c328ec](https://gitlab.com/ikus-soft/rdiffweb/commit/7c328ec9083f70232c0ff5d830cf6204b9b4299e) by Patrik Dufresne).
- Merge branch 'patrik-release-note' into 'master' ([4392987](https://gitlab.com/ikus-soft/rdiffweb/commit/43929875248842ee35cb039f257bef84ef5b67b1) by Patrik Dufresne).
- Merge branch 'patrik-fix-chartkick' into 'master' ([31876df](https://gitlab.com/ikus-soft/rdiffweb/commit/31876dfee583d333af5119c46e971c9789f1103d) by Patrik Dufresne).
- Merge branch 'patrik-discard-X-Forwarded-Host' into 'master' ([b1f509b](https://gitlab.com/ikus-soft/rdiffweb/commit/b1f509be9e28bfaca7c28c1553c62e5cf8f3b90d) by Patrik Dufresne).

### Misc

- Improve custom branding configuration ([ee3e351](https://gitlab.com/ikus-soft/rdiffweb/commit/ee3e3512a9b50bd3902b17ff145896ec27f5a6fe) by Patrik Dufresne).
- Update Release notes ([e800385](https://gitlab.com/ikus-soft/rdiffweb/commit/e800385e18f064b53bf4d04cdb79613ccdd95f55) by Patrik Dufresne).
- Create symbolic link for chartkick on Ubuntu Jammy ([6bedf38](https://gitlab.com/ikus-soft/rdiffweb/commit/6bedf3874587470983a063324d9594fe431e4e95) by Patrik Dufresne).
- Discard `X-Forwarded-Host` headers ([5f86167](https://gitlab.com/ikus-soft/rdiffweb/commit/5f861670ef8f38ca8eea52a98672d0e0fabb5368) by Patrik Dufresne).

## [2.5.3](https://gitlab.com/ikus-soft/rdiffweb/tags/2.5.3) - 2022-12-05

<small>[Compare with 2.5.2](https://gitlab.com/ikus-soft/rdiffweb/compare/2.5.2...2.5.3)</small>

### Fixed

- Fix strange behavior in access token management #247 ([2fe0094](https://gitlab.com/ikus-soft/rdiffweb/commit/2fe0094509e1255a88e9d4368728ae1854221e1f) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-update-config' into 'master' ([8e1a479](https://gitlab.com/ikus-soft/rdiffweb/commit/8e1a4790c09ca4dfed24825efe47f6825f4b0a4f) by Patrik Dufresne).
- Merge branch 'patrik-duplicate-ssh-key' into 'master' ([43b8a9b](https://gitlab.com/ikus-soft/rdiffweb/commit/43b8a9ba89331d51c55f16a7b1266dc3c8c4dc01) by Patrik Dufresne).
- Merge branch 'patrik-fix-revoke-access-token' into 'master' ([0c7a0e3](https://gitlab.com/ikus-soft/rdiffweb/commit/0c7a0e3b7fb2c89573277f9808b22fe5a480f2f0) by Patrik Dufresne).
- Merge branch 'patrik-bookworm' into 'master' ([08bb961](https://gitlab.com/ikus-soft/rdiffweb/commit/08bb96199161a24711029c1fdd602db3dbe20510) by Patrik Dufresne).

### Misc

- Improve handling of duplicate ssh keys added via api #248 ([8f9e1b3](https://gitlab.com/ikus-soft/rdiffweb/commit/8f9e1b353d121fc42fe459afb77959b589fe968e) by Patrik Dufresne).
- Update dependencies for Debian Bookworm ([86732db](https://gitlab.com/ikus-soft/rdiffweb/commit/86732dbb87a49ad2889718b48e1d989ea515a7aa) by Patrik Dufresne).
- Update configuration page ([c33ab14](https://gitlab.com/ikus-soft/rdiffweb/commit/c33ab14d7fedbc26134bb5f2ea6909dd9c036811) by Patrik Dufresne).

## [2.5.2](https://gitlab.com/ikus-soft/rdiffweb/tags/2.5.2) - 2022-11-28

<small>[Compare with 2.5.1](https://gitlab.com/ikus-soft/rdiffweb/compare/2.5.1...2.5.2)</small>

### Merged

- Merge branch 'patrik-release' into 'master' ([4383fad](https://gitlab.com/ikus-soft/rdiffweb/commit/4383fad9325d3a32b7550293289870491fb4f4a4) by Patrik Dufresne).
- Merge branch 'patrik-invalidate-cache' into 'master' ([9af577f](https://gitlab.com/ikus-soft/rdiffweb/commit/9af577f88eff4a551b45aa8da3c9bdceb14612ec) by Patrik Dufresne).
- Merge branch 'patrik-admin-password-reset' into 'master' ([112d517](https://gitlab.com/ikus-soft/rdiffweb/commit/112d5170ac1d3a7e758d1f22bb42004143d9d482) by Patrik Dufresne).
- Merge branch 'patrik-fix-empty-user-root' into 'master' ([25e325f](https://gitlab.com/ikus-soft/rdiffweb/commit/25e325f88650d924ea1e88799f07d46d34a5f4d8) by Patrik Dufresne).

### Misc

- Update release note 2.5.2 ([6abbfd0](https://gitlab.com/ikus-soft/rdiffweb/commit/6abbfd040de0d8020804d8b4cadd0e3d2a1765e2) by Patrik Dufresne).
- Define repo display_name to fix repository tree ([b79dba3](https://gitlab.com/ikus-soft/rdiffweb/commit/b79dba31cd87a87cc63cc2b84879de100af5f63d) by Patrik Dufresne).
- Improve test involving scheduled tasks ([766bbdd](https://gitlab.com/ikus-soft/rdiffweb/commit/766bbdd1b153f4a335ab641b495ca6ba232d99fd) by Patrik Dufresne).
- Invalidate browser cache for logo, headerlogo and favicon on restart #245 ([116c1a3](https://gitlab.com/ikus-soft/rdiffweb/commit/116c1a3a0e326d69ad78743482d5908b496952f8) by Patrik Dufresne).
- Replace admin password only when `--admin-password` option is provided ([56b374a](https://gitlab.com/ikus-soft/rdiffweb/commit/56b374ac89a6cd4f7b04f1cfdf5bc4732d0eb7fb) by Patrik Dufresne).
- Block repository access when user_root directory is empty or a relative path ([b2df367](https://gitlab.com/ikus-soft/rdiffweb/commit/b2df3679564d0daa2856213bb307d3e34bd89a25) by Patrik Dufresne).

## [2.5.1](https://gitlab.com/ikus-soft/rdiffweb/tags/2.5.1) - 2022-11-16

<small>[Compare with 2.5.0](https://gitlab.com/ikus-soft/rdiffweb/compare/2.5.0...2.5.1)</small>

### Added

- Add support for Ubuntu Kinetic #240 ([a762f47](https://gitlab.com/ikus-soft/rdiffweb/commit/a762f47138c60c6228e2062d4edc664a590e2974) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-release-lock-on-restore' into 'master' ([979ab34](https://gitlab.com/ikus-soft/rdiffweb/commit/979ab34bdb37b644a7d742323e3249f5db463354) by Patrik Dufresne).
- Merge branch 'patrik-filesize-for-deleted-files' into 'master' ([6013d6f](https://gitlab.com/ikus-soft/rdiffweb/commit/6013d6f053399ccb5730396bb08967cf1282c873) by Patrik Dufresne).
- Merge branch 'patrik-ru-translation' into 'master' ([68d86a9](https://gitlab.com/ikus-soft/rdiffweb/commit/68d86a993bf3a62cb69dd3c07ce0211e49722e69) by Patrik Dufresne).
- Merge branch 'patrik-ubuntu-kinetic' into 'master' ([519ffd9](https://gitlab.com/ikus-soft/rdiffweb/commit/519ffd9b980416e9e974967c044a354a69839f5a) by Patrik Dufresne).

### Misc

- Update Russian translation file ([e91bfe8](https://gitlab.com/ikus-soft/rdiffweb/commit/e91bfe85be6e887a5d9caf82e6480de552078312) by Patrik Dufresne).
- Release session lock on restore ([ba9aacd](https://gitlab.com/ikus-soft/rdiffweb/commit/ba9aacdb9b3f9b2acba2f2e1db17f4e3e6002b3e) by Patrik Dufresne).
- Disable filesize for deleted files to improve page loading #241 ([329362e](https://gitlab.com/ikus-soft/rdiffweb/commit/329362e2163d85c73f3e54d6325c721a6c73ecda) by Patrik Dufresne).

## [2.5.0](https://gitlab.com/ikus-soft/rdiffweb/tags/2.5.0) - 2022-11-09

<small>[Compare with 2.4.5](https://gitlab.com/ikus-soft/rdiffweb/compare/2.4.5...2.5.0)</small>

### Added

- Add rollback call where applicable ([5990d9d](https://gitlab.com/ikus-soft/rdiffweb/commit/5990d9d0dd9c802ac6735d64c3230ea20b76ba73) by Patrik Dufresne).
- Add OpenSSF Best Practices Badge ([b8e0c28](https://gitlab.com/ikus-soft/rdiffweb/commit/b8e0c2824368a4b728b063a12a27089421c9135c) by Patrik Dufresne).
- Add password score validation ([cdd73cd](https://gitlab.com/ikus-soft/rdiffweb/commit/cdd73cd05629383b47844abcbd77c1d64edd339a) by Patrik Dufresne).
- Add test to verify CSRF in user's settings #221 ([836e5a1](https://gitlab.com/ikus-soft/rdiffweb/commit/836e5a181f24b077452671a8a3094dd5046a1468) by Patrik Dufresne).
- Add REST API to manage sshkeys ([660795d](https://gitlab.com/ikus-soft/rdiffweb/commit/660795dfef9c56305599074d850c39a0622f784a) by Patrik Dufresne).
- Add artifacts expiration ([3e7911a](https://gitlab.com/ikus-soft/rdiffweb/commit/3e7911a1c3bd66f2de4cf1851fb3ad6ece6b718f) by Patrik Dufresne).
- Add Clickjacking Defense ([35caf48](https://gitlab.com/ikus-soft/rdiffweb/commit/35caf480cd8a7a62ab16c6a83d4993df478a0016) by Patrik Dufresne).
- Add Minarca User-Agent detection ([bf4e826](https://gitlab.com/ikus-soft/rdiffweb/commit/bf4e8263361893d7cfdf9932e4eaed5af30033bb) by Patrik Dufresne).
- Add Active Sessions management #203 ([0a2e045](https://gitlab.com/ikus-soft/rdiffweb/commit/0a2e0457e1a433e68e88f9a211e85b5e51a48867) by Patrik Dufresne).
- Add Ubuntu Jammy support ([a8719da](https://gitlab.com/ikus-soft/rdiffweb/commit/a8719da9d5bc3cf01fc7f36aad1cf16793bdf686) by Patrik Dufresne).
- Add unit test for remove-older ([2b3c0a8](https://gitlab.com/ikus-soft/rdiffweb/commit/2b3c0a81755523bba9cf111f57c3928d160cc528) by Patrik Dufresne).

### Fixed

- Fix race condition for deletion ([928b591](https://gitlab.com/ikus-soft/rdiffweb/commit/928b591b1d0b3205eb1a189c6df2a0771f95bb48) by Patrik Dufresne).
- Fix djlint formating ([586f69c](https://gitlab.com/ikus-soft/rdiffweb/commit/586f69cda2de95f968e039537b2a368f44aeade2) by Patrik Dufresne).
- Fix sessions clean-up ([924bbbe](https://gitlab.com/ikus-soft/rdiffweb/commit/924bbbe1c5d15224f038793367a58c09ea580eca) by Patrik Dufresne).
- Fix migration of old database #185 ([b06cd2e](https://gitlab.com/ikus-soft/rdiffweb/commit/b06cd2e018ab0211c7d892d45e49609ebe23576c) by Patrik Dufresne).
- Fix fullname column creation ([7778275](https://gitlab.com/ikus-soft/rdiffweb/commit/77782756d90a87577add67c9d18a85322683d82e) by Patrik Dufresne).
- Fix status page error handling ([797f6e6](https://gitlab.com/ikus-soft/rdiffweb/commit/797f6e66f0c89b31031ac7ec6d9905d27f2c2615) by Patrik Dufresne).

### Removed

- Remove reference to deprecated distutils #208 ([aea43cb](https://gitlab.com/ikus-soft/rdiffweb/commit/aea43cbf0170b0d87e37642b26afdaf1bc8c77c2) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-update-french-translation' into 'master' ([44a2b07](https://gitlab.com/ikus-soft/rdiffweb/commit/44a2b075c21fe0858a2087c2e19175738622e13d) by Patrik Dufresne).
- Merge branch 'patrik-adjust' into 'master' ([cc29583](https://gitlab.com/ikus-soft/rdiffweb/commit/cc29583e301efdebf57d1fd6fbdc1e2d2ddd59c3) by Patrik Dufresne).
- Merge branch 'patrik-password-reset' into 'master' ([e1d9e7e](https://gitlab.com/ikus-soft/rdiffweb/commit/e1d9e7e4b27e4cb7f31ad2459b5cb6a8324feda7) by Patrik Dufresne).
- Merge branch 'patrik-pipeline' into 'master' ([0757fda](https://gitlab.com/ikus-soft/rdiffweb/commit/0757fda8fe064e36c63c868e1a3e31f754806261) by Patrik Dufresne).
- Merge branch 'patrik-plugin-ordering' into 'master' ([57eabe7](https://gitlab.com/ikus-soft/rdiffweb/commit/57eabe7f8f1f98915feaddfa1d9629bf7f561b54) by Patrik Dufresne).
- Merge branch 'patrik-test-sql-upgrade' into 'master' ([3dabbcc](https://gitlab.com/ikus-soft/rdiffweb/commit/3dabbcc2183fe5a079e1faaf8cff0c3b264aa7d6) by Patrik Dufresne).
- Merge branch 'patrik-password-hash' into 'master' ([159335f](https://gitlab.com/ikus-soft/rdiffweb/commit/159335f87ae8c5ea14bb7d1dfd11a037143b95a4) by Patrik Dufresne).
- Merge branch 'patrik-mfa-notification' into 'master' ([de23b1c](https://gitlab.com/ikus-soft/rdiffweb/commit/de23b1c2ea51e2b1f05356b91b3ff0e80a4c3949) by Patrik Dufresne).
- Merge branch 'patrik-limit-session' into 'master' ([7287297](https://gitlab.com/ikus-soft/rdiffweb/commit/72872975fccf1676f09d231eabf13ab739eaa36b) by Patrik Dufresne).
- Merge branch 'patrik-badge' into 'master' ([fa4fd9d](https://gitlab.com/ikus-soft/rdiffweb/commit/fa4fd9daa651320d1aa0bc3aae57a1cea4126efa) by Patrik Dufresne).
- Merge branch 'patrik-validate-origin' into 'master' ([7b32404](https://gitlab.com/ikus-soft/rdiffweb/commit/7b3240425543fd5c859bb7472a614b73525a90cc) by Patrik Dufresne).
- Merge branch 'patrik-improve-ratelimit' into 'master' ([8becdaf](https://gitlab.com/ikus-soft/rdiffweb/commit/8becdaf734b11dc277f7b41151c00f12851085f5) by Patrik Dufresne).
- Merge branch 'patrik-new-old-password' into 'master' ([d49a255](https://gitlab.com/ikus-soft/rdiffweb/commit/d49a25513995b76d2a08b41199954404e686a01a) by Patrik Dufresne).
- Merge branch 'patrik-support-case-insensitive-column-name' into 'master' ([a5d0bca](https://gitlab.com/ikus-soft/rdiffweb/commit/a5d0bca218bd83c2e131767c061b0872969e9d23) by Patrik Dufresne).
- Merge branch 'patrik-fix-path-traversal' into 'master' ([3af8497](https://gitlab.com/ikus-soft/rdiffweb/commit/3af84978ef8b5d880604b6ae5cc6bf29c5567136) by Patrik Dufresne).
- Merge branch 'patrik-stable-test-packages' into 'master' ([7bdb1d6](https://gitlab.com/ikus-soft/rdiffweb/commit/7bdb1d6cf844dd9397ccb5b55fbc1216de8ec2f3) by Patrik Dufresne).
- Merge branch 'patrik-rate-limit-password-change' into 'master' ([9d18c38](https://gitlab.com/ikus-soft/rdiffweb/commit/9d18c38957434eb417b49022cbd5db9814897694) by Patrik Dufresne).
- Merge branch 'patrik-validate-fullname' into 'master' ([a92b4fa](https://gitlab.com/ikus-soft/rdiffweb/commit/a92b4fa441d50aee48ad257a0cad1e2aac77cb26) by Patrik Dufresne).
- Merge branch 'patrik-rdiff-backup-beta' into 'master' ([fc5bfa3](https://gitlab.com/ikus-soft/rdiffweb/commit/fc5bfa3be5fdd8951e3ecdd71ee0e39f837842d0) by Patrik Dufresne).
- Merge branch 'patrik-fix-permissions' into 'master' ([34f7007](https://gitlab.com/ikus-soft/rdiffweb/commit/34f7007ea0c10213d339097504a97acbfa338b2a) by Patrik Dufresne).
- Merge branch 'patrik-remove-older-session' into 'master' ([ac30bdb](https://gitlab.com/ikus-soft/rdiffweb/commit/ac30bdbdd6f22859d9fe89370d1d58df43c8ebf4) by Patrik Dufresne).
- Merge branch 'patrik-csrf-notification' into 'master' ([ba300f7](https://gitlab.com/ikus-soft/rdiffweb/commit/ba300f7de87ed78f7ca757ecb62622a0044e5034) by Patrik Dufresne).
- Merge commit '422791ea45713aaaa865bdca74addb9fffd93a71' ([87677b8](https://gitlab.com/ikus-soft/rdiffweb/commit/87677b87b6d0d9c9c04d2f700c98e1beab859371) by Patrik Dufresne).
- Merge commit '28258e5dd85e7c417918ed3bf481e19ed5eff91f' ([7030c18](https://gitlab.com/ikus-soft/rdiffweb/commit/7030c1886a9d1c3d04f603b2918d0ef861a42148) by Patrik Dufresne).
- Merge branch 'patrik-mfa' into 'master' ([7717a78](https://gitlab.com/ikus-soft/rdiffweb/commit/7717a78a464b85b0f9b30ee5606d23a241f81a34) by Patrik Dufresne).
- Merge commit '9125f5a2d918fed0f3fc1c86fa94cd1779ed9f73' ([4d1232c](https://gitlab.com/ikus-soft/rdiffweb/commit/4d1232cd0586eb79d1a921969f8f7a198a00d92b) by Patrik Dufresne).
- Merge commit '73a369a3f7ec7958106d395eb65dd511fca0d9c7' ([7e6918c](https://gitlab.com/ikus-soft/rdiffweb/commit/7e6918cd5203fa07779734202240d683bc79d8fa) by Patrik Dufresne).
- Merge branch 'patrik-clickjacking-defence' into 'master' ([45141ea](https://gitlab.com/ikus-soft/rdiffweb/commit/45141eaabd9b23eaf3e95ff51857d05b46aff95a) by Patrik Dufresne).
- Merge branch 'patrik-add-minarca-user-agent' into 'master' ([311f693](https://gitlab.com/ikus-soft/rdiffweb/commit/311f6932d63094cd036bc81df798102d1a3236ef) by Patrik Dufresne).
- Merge branch 'patrik-remove-distutils' into 'master' ([35d000f](https://gitlab.com/ikus-soft/rdiffweb/commit/35d000f0a25358c58b7ffda62b165d6ac5afb811) by Patrik Dufresne).
- Merge branch 'patrik-fix-db-migration' into 'master' ([ef6c368](https://gitlab.com/ikus-soft/rdiffweb/commit/ef6c368b0302689a9934c8b1bcbe515852873c34) by Patrik Dufresne).
- Merge branch 'patrik-active-session' into 'master' ([ab2ad9a](https://gitlab.com/ikus-soft/rdiffweb/commit/ab2ad9a905efc7313fb0193373c21210275b6160) by Patrik Dufresne).
- Merge branch 'patrik-fix-proxy' into 'master' ([5c4726e](https://gitlab.com/ikus-soft/rdiffweb/commit/5c4726e8c5256cdcf9c201dd43f4ea8d3578e4a8) by Patrik Dufresne).
- Merge branch 'patrik-session-clean-up' into 'master' ([184bd6a](https://gitlab.com/ikus-soft/rdiffweb/commit/184bd6aeabc1f7385f401e6e4fc032098fd81e97) by Patrik Dufresne).
- Merge branch 'patrik-datatables' into 'master' ([ecdf6cd](https://gitlab.com/ikus-soft/rdiffweb/commit/ecdf6cd3595ac17a6fbcd9b64242f270a602f552) by Patrik Dufresne).
- Merge branch 'patrik-adjust-events' into 'master' ([6d5090d](https://gitlab.com/ikus-soft/rdiffweb/commit/6d5090d22e3336c55a2dc62a514739c5547ecbe2) by Patrik Dufresne).
- Merge branch 'patrik-drop-eof-ubuntu' into 'master' ([a88e6af](https://gitlab.com/ikus-soft/rdiffweb/commit/a88e6af53693e4df76a184dbb0b00eba01199421) by Patrik Dufresne).
- Merge branch 'patrik-bootstrap-v4' into 'master' ([bf3acaf](https://gitlab.com/ikus-soft/rdiffweb/commit/bf3acaf6de0fb89d36214ec268ccf8330b78c767) by Patrik Dufresne).
- Merge branch 'patrik-fix-database-upgrade' into 'master' ([17b8157](https://gitlab.com/ikus-soft/rdiffweb/commit/17b8157f65672e0aaebfd3ec2fe6be4dd80df31f) by Patrik Dufresne).
- Merge branch 'patrik-ubuntu-jammy' into 'master' ([7f0d63f](https://gitlab.com/ikus-soft/rdiffweb/commit/7f0d63f0a5fd9297a4f9d2c646254bdf748278d8) by Patrik Dufresne).
- Merge branch 'patrik-remove-older-test' into 'master' ([cde5b9e](https://gitlab.com/ikus-soft/rdiffweb/commit/cde5b9eef3eae64fa80b6dc27b4492f4e3feefc2) by Patrik Dufresne).
- Merge branch 'patrik-refactor-sqlalchemy' into 'master' ([06230b0](https://gitlab.com/ikus-soft/rdiffweb/commit/06230b0af2607551c678d4b3addec4de696b9602) by Patrik Dufresne).
- Merge branch 'patrik-edit-release-date' into 'master' ([d10b485](https://gitlab.com/ikus-soft/rdiffweb/commit/d10b4853175be9db24f5aa20180744ad3c4c8393) by Patrik Dufresne).

### Misc

- Update french translation ([35f5968](https://gitlab.com/ikus-soft/rdiffweb/commit/35f5968624a2a3e97b9974456ba3713260b6ba5b) by Patrik Dufresne).
- Improve CSS branding configuration #239 ([ba6f387](https://gitlab.com/ikus-soft/rdiffweb/commit/ba6f387704b631d835183cf3121de8932b54d34b) by Patrik Dufresne).
- Handle duplicate token name ([f77eb8c](https://gitlab.com/ikus-soft/rdiffweb/commit/f77eb8c9a2b835eee253621b4f5c693e8b350316) by Patrik Dufresne).
- Raise `user_added` event before_insert ([516b3d8](https://gitlab.com/ikus-soft/rdiffweb/commit/516b3d8d7c34b1baff50ba3ea035d9c7ff96f1e5) by Patrik Dufresne).
- Identify persistent sessions with a badge ([b396bfb](https://gitlab.com/ikus-soft/rdiffweb/commit/b396bfb93ea01ef061ce6b6a4260bc0ba8d873fa) by Patrik Dufresne).
- Delete user's session on password change ([6efb995](https://gitlab.com/ikus-soft/rdiffweb/commit/6efb995bc32c8a8e9ad755eb813dec991dffb2b8) by Patrik Dufresne).
- Use python 3.10 to fix CICD pipeline ([a69d45c](https://gitlab.com/ikus-soft/rdiffweb/commit/a69d45c874d93fc73be353b3f556133191ec17ab) by Patrik Dufresne).
- Force plugins ordering on startup #232 ([36e3549](https://gitlab.com/ikus-soft/rdiffweb/commit/36e3549cef24cfe1c2d068a5d433430375bd3f2c) by Patrik Dufresne).
- Use argon2id to store password hash #231 ([397990b](https://gitlab.com/ikus-soft/rdiffweb/commit/397990b53dc5d28507f76e458aed915cdd97de57) by Patrik Dufresne).
- Improve testing of database upgrade ([7edc428](https://gitlab.com/ikus-soft/rdiffweb/commit/7edc4285e45066cfdb3a0f879cf5f29f422010cd) by Patrik Dufresne).
- Send email notification when enabling or disabling MFA ([c27c46b](https://gitlab.com/ikus-soft/rdiffweb/commit/c27c46bac656b1da74f28eac1b52dfa5df76e6f2) by Patrik Dufresne).
- Define idle and absolute session timeout with agressive default to protect usage on public computer ([f2a32f2](https://gitlab.com/ikus-soft/rdiffweb/commit/f2a32f2a9f3fb8be1a9432ac3d81d3aacdb13095) by Patrik Dufresne).
- Enforce 'Origin' validation ([afc1bdf](https://gitlab.com/ikus-soft/rdiffweb/commit/afc1bdfab5161c74012ff2590a6ec49cc0d8fde0) by Patrik Dufresne).
- Improve ratelimit implementation ([b78ec09](https://gitlab.com/ikus-soft/rdiffweb/commit/b78ec09f4582e363f6f449df6f987127e126c311) by Patrik Dufresne).
- Support case insensitive column name #228 ([be24bb6](https://gitlab.com/ikus-soft/rdiffweb/commit/be24bb6bbef0b380cb004955218719db6e89061b) by Patrik Dufresne).
- Mitigate path traversal vulnerability #227 ([79ff50f](https://gitlab.com/ikus-soft/rdiffweb/commit/79ff50f1bb1841b76964871e339aabb67630d652) by Patrik Dufresne).
- Enforce password policy new password cannot be set as new password ([2ffc2af](https://gitlab.com/ikus-soft/rdiffweb/commit/2ffc2af65c8f8113b06e0b89929c604bcdf844b9) by Patrik Dufresne).
- Make test-package more robust in CICD ([44bed43](https://gitlab.com/ikus-soft/rdiffweb/commit/44bed43eb3e2230eaed04cfd4a9e047cd23f88f7) by Patrik Dufresne).
- Limit incorrect attempts to change the user's password to prevent brute force attacks #225 ([b5e3bb0](https://gitlab.com/ikus-soft/rdiffweb/commit/b5e3bb0a98268d18ceead36ab9b2b7eaacd659a8) by Patrik Dufresne).
- Enforce validation on fullname, username and email for increase security #224 ([4d464b4](https://gitlab.com/ikus-soft/rdiffweb/commit/4d464b467f14b8eb9103d7f5f0774e49995527c7) by Patrik Dufresne).
- Enforce permissions on /etc/rdiffweb ([9aa7191](https://gitlab.com/ikus-soft/rdiffweb/commit/9aa7191c8b355df95682df23f645f7d573a52c50) by Patrik Dufresne).
- Configure proxy tools with `X-Real-IP` ([a98e965](https://gitlab.com/ikus-soft/rdiffweb/commit/a98e965d5651eb9d2fadd3eebee3dbcf0a2989cc) by Patrik Dufresne).
- Add more secure headers: Cache-control, Referrer-Policy, X-Content-Type-Options, X-XSS-Protection ([1027c20](https://gitlab.com/ikus-soft/rdiffweb/commit/1027c202e1d8f0162bc02913e6b51154925acb04) by Patrik Dufresne).
- Limit user's fullname and Token name field length ([b62c479](https://gitlab.com/ikus-soft/rdiffweb/commit/b62c479ff6979563c7c23e7182942bc4f460a2c7) by Patrik Dufresne).
- Timeout 15 min by default and 30 days for persistent session ([b2b1f18](https://gitlab.com/ikus-soft/rdiffweb/commit/b2b1f18472cd0855d6a2dd4123a3bac08a8727a3) by Patrik Dufresne).
- Define field limit for SSH Key title ([d1fb5ab](https://gitlab.com/ikus-soft/rdiffweb/commit/d1fb5abcd42b57c8274f6bba33573d524359fe42) by Patrik Dufresne).
- Define field limit for username, email and root directory #223 ([109e401](https://gitlab.com/ikus-soft/rdiffweb/commit/109e401ad74473ee5e59e7e6320d497eb1cfffdb) by Patrik Dufresne).
- Clean-up invalid path on error page ([5fbc544](https://gitlab.com/ikus-soft/rdiffweb/commit/5fbc544eede96333f22f08d6f92649a06e14a356) by Patrik Dufresne).
- Generate a new session on login and 2FA #220 ([102a92b](https://gitlab.com/ikus-soft/rdiffweb/commit/102a92b28e6ced74be50b8e08bd2916642affafe) by Patrik Dufresne).
- Use 'Secure' Attribute with Sensitive Cookie in HTTPS Session on HTTP Error #218 ([a7ca8e5](https://gitlab.com/ikus-soft/rdiffweb/commit/a7ca8e5fe1950e6011c75dbb7f22c660587c8503) by Patrik Dufresne).
- Mitigate CSRF on repository settings #217 ([585cd65](https://gitlab.com/ikus-soft/rdiffweb/commit/585cd65ecd2676de3597e76012bb2b214c08f0fd) by Patrik Dufresne).
- Support MarkupSafe<3 for Debian bookworm ([db8dc09](https://gitlab.com/ikus-soft/rdiffweb/commit/db8dc0929d86cf8266c6194145d61be37a732869) by Patrik Dufresne).
- Mitigate CSRF on notification #216 ([bfeb1d5](https://gitlab.com/ikus-soft/rdiffweb/commit/bfeb1d559c6953596eead6fd88573cc81e7fd566) by Patrik Dufresne).
- Update X-Real-IP documentation ([6b19e52](https://gitlab.com/ikus-soft/rdiffweb/commit/6b19e52904cb2279d4c5d25d7fb358e257ea645d) by Patrik Dufresne).
- Replace last warning message by flash ([da081da](https://gitlab.com/ikus-soft/rdiffweb/commit/da081da06d489dee2b55e89fae69d39488af5dc7) by Patrik Dufresne).
- Exclude dock/conf.py from sonar analysis ([5ce7777](https://gitlab.com/ikus-soft/rdiffweb/commit/5ce7777f59452f25ddae79eca30e0a4dca9e9b80) by Patrik Dufresne).
- Implement Access Token Authentication for /api ([9cd803f](https://gitlab.com/ikus-soft/rdiffweb/commit/9cd803fcdd2430cc137269aa69ca70df00ab414d) by Patrik Dufresne).
- Implement Multi-Factor Authentication #201 ([dade9a9](https://gitlab.com/ikus-soft/rdiffweb/commit/dade9a9e92fb50772dddf4629d565112b458bec4) by Patrik Dufresne).
- Defer loading of DEPRECATED users columns ([a04b95b](https://gitlab.com/ikus-soft/rdiffweb/commit/a04b95b0bd5b2e322fac5b7618622212d21b4466) by Patrik Dufresne).
- Update Security.md ([c8d69ce](https://gitlab.com/ikus-soft/rdiffweb/commit/c8d69ce2e46f6d9d2852d062e400934e32fe3ed1) by Patrik Dufresne).
- Test with beta version of rdiff-backup ([1269126](https://gitlab.com/ikus-soft/rdiffweb/commit/1269126ee29f2bd25cab3f8e221997fe3cb13b40) by Patrik Dufresne).
- Update release notes ([60a7742](https://gitlab.com/ikus-soft/rdiffweb/commit/60a77428ebbefa405a3c131e2ea79fe00c136bbb) by Patrik Dufresne).
- Support Reverse proxy with older CherryPy ([e562eed](https://gitlab.com/ikus-soft/rdiffweb/commit/e562eedec0e00f593d03dfed53330ded67d91a47) by Patrik Dufresne).
- Update user profile layout ([f10ead1](https://gitlab.com/ikus-soft/rdiffweb/commit/f10ead1b52a864aa5c7504e08838307e8e0f4562) by Patrik Dufresne).
- Adjust scheduler job name ([c5ff5b5](https://gitlab.com/ikus-soft/rdiffweb/commit/c5ff5b5d4f5b90960648a3c0515acb8f45504054) by Patrik Dufresne).
- Replace custom timsort by jquery DataTables #205 ([9f8dccb](https://gitlab.com/ikus-soft/rdiffweb/commit/9f8dccb4dbebb61538754ec1266cf6261fbc2839) by Patrik Dufresne).
- Improve user's events for minarca integration ([26de37d](https://gitlab.com/ikus-soft/rdiffweb/commit/26de37d311418e706405d61fe5e6f909ac6d6da4) by Patrik Dufresne).
- Drop Ubuntu hirsute & Impish ([ea5bde5](https://gitlab.com/ikus-soft/rdiffweb/commit/ea5bde5beaa96f33d4385ab08a73805264bac3a6) by Patrik Dufresne).
- Migrate to bootstrap v4.6 #204 ([147751a](https://gitlab.com/ikus-soft/rdiffweb/commit/147751a58279fdcf12cf230799d9ddd3c994c910) by Patrik Dufresne).
- Improve error handle when repo has failed status ([bc36739](https://gitlab.com/ikus-soft/rdiffweb/commit/bc36739e4429922a57b3906b3861cfa0f29e3505) by Patrik Dufresne).
- Adjust default SQL value to match previous version ([9a9ba57](https://gitlab.com/ikus-soft/rdiffweb/commit/9a9ba57440e0345a04d953380bc8d437160ab564) by Patrik Dufresne).
- Store user's session in database #202 ([6a47f1a](https://gitlab.com/ikus-soft/rdiffweb/commit/6a47f1a6604f9cb319b9abc63b39b7d96e1f62cc) by Patrik Dufresne).
- Reffactor to use SQLAlchemy ORM ([2333433](https://gitlab.com/ikus-soft/rdiffweb/commit/23334330328eda53e71a7a41758f7339aa3ee79b) by Patrik Dufresne).
- Update LDAP plugins ([e51972d](https://gitlab.com/ikus-soft/rdiffweb/commit/e51972ddca6d078a6b47acf1fbdb38412576c21f) by Patrik Dufresne).

## [4.2.5](https://gitlab.com/ikus-soft/rdiffweb/tags/4.2.5) - 2022-10-03

<small>[Compare with 4.2.4](https://gitlab.com/ikus-soft/rdiffweb/compare/4.2.4...4.2.5)</small>

### Merged

- Merge branch 'patrik-upgrade-2.4.10' into 'master' ([7917d53](https://gitlab.com/ikus-soft/rdiffweb/commit/7917d53c92ebfd1b0eda4b3aa97e13b0583d7eeb) by Patrik Dufresne).

### Misc

- Upgrade rdiffweb to 2.4.10 ([6956c6f](https://gitlab.com/ikus-soft/rdiffweb/commit/6956c6f21cee773efe4c8b8ee06edcacbbb8ec95) by Patrik Dufresne).

## [4.2.4](https://gitlab.com/ikus-soft/rdiffweb/tags/4.2.4) - 2022-09-29

<small>[Compare with 4.2.3](https://gitlab.com/ikus-soft/rdiffweb/compare/4.2.3...4.2.4)</small>

### Merged

- Merge branch 'patrik-upgrade-2.4.9' into 'master' ([cdece54](https://gitlab.com/ikus-soft/rdiffweb/commit/cdece54d5f5cae1f01ad7a16265aeb93f51b8956) by Patrik Dufresne).

### Misc

- Upgrade rdiffweb to 2.4.9 ([4fde7cb](https://gitlab.com/ikus-soft/rdiffweb/commit/4fde7cbc5c71c7f8ce5fb2766d4462f7ea78d78b) by Patrik Dufresne).

## [4.2.3](https://gitlab.com/ikus-soft/rdiffweb/tags/4.2.3) - 2022-09-26

<small>[Compare with 4.2.2](https://gitlab.com/ikus-soft/rdiffweb/compare/4.2.2...4.2.3)</small>

### Merged

- Merge branch 'patrik-upgrade-2.4.8' into 'master' ([5934756](https://gitlab.com/ikus-soft/rdiffweb/commit/59347568a195d99d8de09a80d705704cc455916a) by Patrik Dufresne).

### Misc

- Upgrade rdiffweb to 2.4.8 to fix vulnerabilities ([3260618](https://gitlab.com/ikus-soft/rdiffweb/commit/3260618259839643023a4cfa2defd752cb5d982d) by Patrik Dufresne).

## [4.2.2](https://gitlab.com/ikus-soft/rdiffweb/tags/4.2.2) - 2022-09-18

<small>[Compare with 4.2.1](https://gitlab.com/ikus-soft/rdiffweb/compare/4.2.1...4.2.2)</small>

### Merged

- Merge branch 'patrik-tidy-up' into 'master' ([1e114b8](https://gitlab.com/ikus-soft/rdiffweb/commit/1e114b8875b9a0009ca1e86d5006e28cf46f9209) by Patrik Dufresne).

### Misc

- Upgrade rdiffweb to 2.4.5 to vix vulnerabilities ([4ddcc59](https://gitlab.com/ikus-soft/rdiffweb/commit/4ddcc595479b57d06c0cc3f4621b520d353bb553) by Patrik Dufresne).
- Test minarca-server Debian package ([ddd1e95](https://gitlab.com/ikus-soft/rdiffweb/commit/ddd1e954c17546463bdb76cacb9a4772c76bac3a) by Patrik Dufresne).
- Update Minarca Logo ([857dfe4](https://gitlab.com/ikus-soft/rdiffweb/commit/857dfe4e897fbe195f4f42ab627f45bb7ee3e9a4) by Patrik Dufresne).

## [2.4.5](https://gitlab.com/ikus-soft/rdiffweb/tags/2.4.5) - 2022-09-16

<small>[Compare with 2.4.4](https://gitlab.com/ikus-soft/rdiffweb/compare/2.4.4...2.4.5)</small>

### Misc

- Mitigate CSRF on repository deletion and user deletion #214 #215 ([422791e](https://gitlab.com/ikus-soft/rdiffweb/commit/422791ea45713aaaa865bdca74addb9fffd93a71) by Patrik Dufresne).

## [2.4.4](https://gitlab.com/ikus-soft/rdiffweb/tags/2.4.4) - 2022-09-15

<small>[Compare with 2.4.3](https://gitlab.com/ikus-soft/rdiffweb/compare/2.4.3...2.4.4)</small>

### Misc

- Use X-Real-IP to identify clients #213 ([28258e5](https://gitlab.com/ikus-soft/rdiffweb/commit/28258e5dd85e7c417918ed3bf481e19ed5eff91f) by Patrik Dufresne).

## [2.4.3](https://gitlab.com/ikus-soft/rdiffweb/tags/2.4.3) - 2022-09-14

<small>[Compare with 2.4.2](https://gitlab.com/ikus-soft/rdiffweb/compare/2.4.2...2.4.3)</small>

### Misc

- Mitigate CSRF in profile's SSH Keys #212 ([9125f5a](https://gitlab.com/ikus-soft/rdiffweb/commit/9125f5a2d918fed0f3fc1c86fa94cd1779ed9f73) by Patrik Dufresne).

## [2.4.2](https://gitlab.com/ikus-soft/rdiffweb/tags/2.4.2) - 2022-09-12

<small>[Compare with 2.4.1](https://gitlab.com/ikus-soft/rdiffweb/compare/2.4.1...2.4.2)</small>

### Misc

- Update release version 2.4.2 ([73a369a](https://gitlab.com/ikus-soft/rdiffweb/commit/73a369a3f7ec7958106d395eb65dd511fca0d9c7) by Patrik Dufresne).
- Enforce minimum and maximum password length #211 ([233befc](https://gitlab.com/ikus-soft/rdiffweb/commit/233befc33bdc45d4838c773d5aed4408720504c5) by Patrik Dufresne).
- Avoid leakage of the stack trace in the default error page #210 ([e7828ca](https://gitlab.com/ikus-soft/rdiffweb/commit/e7828ca959a03582691679456a90b16903f98afe) by Patrik Dufresne).
- Use 'Secure' Attribute with Sensitive Cookie in HTTPS Session #209 ([f2de237](https://gitlab.com/ikus-soft/rdiffweb/commit/f2de2371c5e13ce1c6fd6f9a1ed3e5d46b93cd7e) by Patrik Dufresne).

## [2.4.1](https://gitlab.com/ikus-soft/rdiffweb/tags/2.4.1) - 2022-09-08

<small>[Compare with 2.4.0](https://gitlab.com/ikus-soft/rdiffweb/compare/2.4.0...2.4.1)</small>

### Added

- Add Clickjacking Defense ([7294bb7](https://gitlab.com/ikus-soft/rdiffweb/commit/7294bb7466532762c93d711211e5958940c1b428) by Patrik Dufresne).

### Misc

- Support Reverse proxy with older CherryPy ([d4dcb80](https://gitlab.com/ikus-soft/rdiffweb/commit/d4dcb80915c2a78eba43890a55d27b7efaa54519) by Patrik Dufresne).
- Drop Ubuntu hirsute & Impish ([0295c1c](https://gitlab.com/ikus-soft/rdiffweb/commit/0295c1c46600f5ccccfa48b83df726e4461ee70a) by Patrik Dufresne).
- Update 2.4.0 release date ([3c497da](https://gitlab.com/ikus-soft/rdiffweb/commit/3c497da4a8dcfc5ce967a8172b8da081b6e098fc) by Patrik Dufresne).

## [4.2.1](https://gitlab.com/ikus-soft/rdiffweb/tags/4.2.1) - 2022-07-15

<small>[Compare with 4.2.0](https://gitlab.com/ikus-soft/rdiffweb/compare/4.2.0...4.2.1)</small>

### Merged

- Merge branch 'patrik-fix-librsync-upgrade' into 'master' ([f4b810f](https://gitlab.com/ikus-soft/rdiffweb/commit/f4b810f911673b5a68f9ffcf30e006770e8b4e6a) by Patrik Dufresne).

### Misc

- Adjust `librsync` dependencies for release upgrade ([7fc487f](https://gitlab.com/ikus-soft/rdiffweb/commit/7fc487fe8755c033080ab425218e94310fed1f6d) by Patrik Dufresne).

## [4.2.0](https://gitlab.com/ikus-soft/rdiffweb/tags/4.2.0) - 2022-06-23

<small>[Compare with 4.1.1](https://gitlab.com/ikus-soft/rdiffweb/compare/4.1.1...4.2.0)</small>

### Added

- Add black and isort ([d75c1c0](https://gitlab.com/ikus-soft/rdiffweb/commit/d75c1c059c677d2258364ee101ffd4f007d81630) by Patrik Dufresne).

### Fixed

- Fix to support various version of setuptools-scm ([2393a8b](https://gitlab.com/ikus-soft/rdiffweb/commit/2393a8bc578286829fe130d80c5a6c7327d443da) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-bump-rdiffweb' into 'master' ([6111417](https://gitlab.com/ikus-soft/rdiffweb/commit/6111417725405e4982a41c1ca9d8262e52082a01) by Patrik Dufresne).
- Merge branch 'patrik-doc-theme' into 'master' ([24bd3a9](https://gitlab.com/ikus-soft/rdiffweb/commit/24bd3a97fa71532f81046ccf917078e1b23ff7e9) by Patrik Dufresne).
- Merge branch 'patrik-black-isort' into 'master' ([df8c4f3](https://gitlab.com/ikus-soft/rdiffweb/commit/df8c4f3c088976dc4d6a425d7898c1b477784319) by Patrik Dufresne).
- Merge branch 'patrik-upgrade-rdiffweb' into 'master' ([0eb304f](https://gitlab.com/ikus-soft/rdiffweb/commit/0eb304ff6285b5afa7d66e85b675cdf44becc795) by Patrik Dufresne).

### Misc

- Bump rdiffweb to 2.4.0 ([5d441be](https://gitlab.com/ikus-soft/rdiffweb/commit/5d441be04eef43750fa6c690cb135358af427ad0) by Patrik Dufresne).
- Bump rdiffweb to 2.4.0.a8 ([5d79aad](https://gitlab.com/ikus-soft/rdiffweb/commit/5d79aad8ff0db9e60fb810fd95348d1567bf22b6) by Patrik Dufresne).
- Bump rdiff-backup to 2.4.0a7 ([9438cfd](https://gitlab.com/ikus-soft/rdiffweb/commit/9438cfd248ebcbbea193d92f3df1a70fd88cde5d) by Patrik Dufresne).
- Bump rdiffweb to v2.4.0a6 ([4c590d2](https://gitlab.com/ikus-soft/rdiffweb/commit/4c590d2949a566c130191e2311f3a8daf139e1d0) by Patrik Dufresne).
- Bump rdiffweb to 2.4.0a5 ([c039fd3](https://gitlab.com/ikus-soft/rdiffweb/commit/c039fd3630fc7503283be46109f15da420cd9dbb) by Patrik Dufresne).
- Bump rdiffweb to v2.4.0a2 ([643ff10](https://gitlab.com/ikus-soft/rdiffweb/commit/643ff103c816dc1fadd5183dc47ccbcdb5c5f0f8) by IKUS Soft robot).
- Upgrade rdiffweb version to 2.4.0 ([c7b1fc2](https://gitlab.com/ikus-soft/rdiffweb/commit/c7b1fc2ce5dda190b753c6165ce2759aa3364d82) by Patrik Dufresne).
- Bump rdiffweb to v2.4.0a1 ([461e92a](https://gitlab.com/ikus-soft/rdiffweb/commit/461e92af9b4f187e39ec06c6aaf4034972f1a9fa) by IKUS Soft robot).

## [2.4.0](https://gitlab.com/ikus-soft/rdiffweb/tags/2.4.0) - 2022-06-16

<small>[Compare with 2.3.9](https://gitlab.com/ikus-soft/rdiffweb/compare/2.3.9...2.4.0)</small>

### Added

- Add HttpOnly flag to Set-Cookie #200 ([128ab8f](https://gitlab.com/ikus-soft/rdiffweb/commit/128ab8f7c89758a8d810a4aac69ce9c341d33497) by Patrik Dufresne).
- Add 2.4.0 release notes ([d486641](https://gitlab.com/ikus-soft/rdiffweb/commit/d48664140381fe98dc418a879230c1ae8333fb8e) by Patrik Dufresne).
- Add `cc` to smtp module ([12a8593](https://gitlab.com/ikus-soft/rdiffweb/commit/12a859336019c50031ebc1a787d6a18cf77777df) by Patrik Dufresne).
- Add unittest for out of repo browsing ([24bf9ad](https://gitlab.com/ikus-soft/rdiffweb/commit/24bf9ad0a5694cb2fb89ee2e5d0d66d18960b212) by Patrik Dufresne).
- Add black, isort and upgrade to pyproject.yml #184 #187 #181 ([87349f3](https://gitlab.com/ikus-soft/rdiffweb/commit/87349f3f3f266e46f3d2bdd876dd96c16b15c40b) by Patrik Dufresne).
- Add support for Debian Bookworm #180 ([a7d0925](https://gitlab.com/ikus-soft/rdiffweb/commit/a7d09257e7c0207722a505b98dbf35a7e18b4d53) by Patrik Dufresne).
- Add RateLimit to login page and API to mitigate robots attacks #167 ([de6112c](https://gitlab.com/ikus-soft/rdiffweb/commit/de6112c42da16d856ec9ea16b0e1f7c86f1f4380) by Patrik Dufresne).
- Add rdiff-backup version to Admin Page #152 ([fb0f78c](https://gitlab.com/ikus-soft/rdiffweb/commit/fb0f78c773323d7d9d6b77616a5826c1dc18d883) by Patrik Dufresne).

### Fixed

- Fix status page #191 ([c07cc40](https://gitlab.com/ikus-soft/rdiffweb/commit/c07cc40de384f957e4519eee215b7d2ed81ab13d) by Patrik Dufresne).
- Fix ratelimit #167 ([45613c3](https://gitlab.com/ikus-soft/rdiffweb/commit/45613c36da66ae56ba28853956090fcca0639375) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-http-only-cookie' into 'master' ([a193814](https://gitlab.com/ikus-soft/rdiffweb/commit/a1938147896e0421c86388e62171489219c6dc96) by Patrik Dufresne).
- Merge branch 'patrik-update-google-tag' into 'master' ([8a6bd45](https://gitlab.com/ikus-soft/rdiffweb/commit/8a6bd453e4218076b4f0477bfac5e1f96a41c6ec) by Patrik Dufresne).
- Merge branch 'patrik-use-compatible-timestamps' into 'master' ([00c05c5](https://gitlab.com/ikus-soft/rdiffweb/commit/00c05c53f8cdf5ad7e15514fcc9930bf2b83403d) by Patrik Dufresne).
- Merge branch 'patrik-browse-empty-folder' into 'master' ([03176ef](https://gitlab.com/ikus-soft/rdiffweb/commit/03176ef385bae02d0d30fcff7f2c6e55b2acdcc1) by Patrik Dufresne).
- Merge branch 'patrik-docker-hub' into 'master' ([5672198](https://gitlab.com/ikus-soft/rdiffweb/commit/56721985ab6c5b8abd76e74b1f5c317e27018cb4) by Patrik Dufresne).
- Merge branch 'patrik-final-fix' into 'master' ([0ee54ee](https://gitlab.com/ikus-soft/rdiffweb/commit/0ee54eeb7f723e385a6be110bfc42fedbbba4fbc) by Patrik Dufresne).
- Merge branch 'patrik-rdiff-index' into 'master' ([c7c5ade](https://gitlab.com/ikus-soft/rdiffweb/commit/c7c5adee00f94f2cacde65f375fee064fc43d837) by Patrik Dufresne).
- Merge branch 'patrik-update-smtp-plugin' into 'master' ([45bafc5](https://gitlab.com/ikus-soft/rdiffweb/commit/45bafc53765db00c5dcfe4e57dda6148577d304e) by Patrik Dufresne).
- Merge branch 'patrik-fix-status' into 'master' ([66df770](https://gitlab.com/ikus-soft/rdiffweb/commit/66df770f069fb9d17af7adcdb375d156c4308737) by Patrik Dufresne).
- Merge branch 'patrik-refresh-repo' into 'master' ([f3e49c2](https://gitlab.com/ikus-soft/rdiffweb/commit/f3e49c25ee7caa5d79b5d99cad2e81ab265d0d0b) by Patrik Dufresne).
- Merge branch 'patrik-run-test-debian' into 'master' ([5aa9049](https://gitlab.com/ikus-soft/rdiffweb/commit/5aa904903f08046adcca52370dd548a211615c68) by Patrik Dufresne).
- Merge branch 'patrik-update-minarca' into 'master' ([6d5f197](https://gitlab.com/ikus-soft/rdiffweb/commit/6d5f197e95a94788f982196cae6575d321743c9f) by Patrik Dufresne).
- Merge branch 'patrik-add-tooling' into 'master' ([b7f9343](https://gitlab.com/ikus-soft/rdiffweb/commit/b7f93433be5141241891df43707fcfd5d5d234f8) by Patrik Dufresne).
- Merge branch 'patrik-chartkick-jinja3' into 'master' ([9dfe9b6](https://gitlab.com/ikus-soft/rdiffweb/commit/9dfe9b62737017373646969fd2f4f33505dd500b) by Patrik Dufresne).
- Merge branch 'patrik-update-ldap-plugins' into 'master' ([a2b3f6e](https://gitlab.com/ikus-soft/rdiffweb/commit/a2b3f6e9375bd9ac00209c7c699b747dd6bf5dbe) by Patrik Dufresne).
- Merge branch 'patrik-ubuntu-impish' into 'master' ([780ebe8](https://gitlab.com/ikus-soft/rdiffweb/commit/780ebe8aae9d632268d945fc2e1bdda6bfb41a71) by Patrik Dufresne).
- Merge branch 'patrik-replace-user-quota-pub-sub' into 'master' ([3837069](https://gitlab.com/ikus-soft/rdiffweb/commit/3837069ae8b592cc51b2e3b9121e3113cada07d1) by Patrik Dufresne).
- Merge branch 'patrik-reffactoring' into 'master' ([16a8e66](https://gitlab.com/ikus-soft/rdiffweb/commit/16a8e6610b12008cabf92d82d63b7ecdf9dac065) by Patrik Dufresne).
- Merge branch 'patrik-ratelimit' into 'master' ([41fcb86](https://gitlab.com/ikus-soft/rdiffweb/commit/41fcb860cc579657ec122601141b4174a3ca86a5) by Patrik Dufresne).
- Merge branch 'patrik-fix-markupsafe' into 'master' ([db8528a](https://gitlab.com/ikus-soft/rdiffweb/commit/db8528afe548a97b0a7b057d170de2462cf76d12) by Patrik Dufresne).
- Merge branch 'patrik-rate-limit' into 'master' ([580902b](https://gitlab.com/ikus-soft/rdiffweb/commit/580902befef3b29c20db0c2f7b5ce135cc47e621) by Patrik Dufresne).
- Merge branch 'patrik-close-pipe' into 'master' ([0f395df](https://gitlab.com/ikus-soft/rdiffweb/commit/0f395dfef9f1441c211e93fea7c4bf5b743a6658) by Patrik Dufresne).
- Merge branch 'patrik-rdiff-backup-version' into 'master' ([dab5a76](https://gitlab.com/ikus-soft/rdiffweb/commit/dab5a764355a3e4f5f3bf2f752a87dad33941321) by Patrik Dufresne).
- Merge branch 'patrik-drop-centos-8' into 'master' ([ddfb11f](https://gitlab.com/ikus-soft/rdiffweb/commit/ddfb11f26217acd2e47aa266a9483f65af45222b) by Patrik Dufresne).
- Merge branch 'patrik-validate-email-sender' into 'master' ([0356248](https://gitlab.com/ikus-soft/rdiffweb/commit/035624870ad8c59eec6493e0fd6a35b003d87cfe) by Patrik Dufresne).

### Misc

- Install new google tag code ([4b83448](https://gitlab.com/ikus-soft/rdiffweb/commit/4b834488fe0aff32f869dbc2706cc89542232a91) by Patrik Dufresne).
- Support rdiff-backup with use-compatible-timestamps rdiffweb#197 ([5e1c087](https://gitlab.com/ikus-soft/rdiffweb/commit/5e1c087030284b89f50c4c3b5842875b9f9c0d97) by Patrik Dufresne).
- Allow browsing empty folder ([c89578e](https://gitlab.com/ikus-soft/rdiffweb/commit/c89578e0c3f9314824e4d074137f8bddacaea29a) by Patrik Dufresne).
- Allow sonar analisys failure ([257b971](https://gitlab.com/ikus-soft/rdiffweb/commit/257b97112f08f0e089f81e3cc6edc27adadd35af) by Patrik Dufresne).
- Wait for sonar analysis ([fb59712](https://gitlab.com/ikus-soft/rdiffweb/commit/fb5971243469d2919707aa83642880adf439446b) by Patrik Dufresne).
- Push docker image to DockerHub #144 ([6452ac8](https://gitlab.com/ikus-soft/rdiffweb/commit/6452ac8dd1f3eed948fae20fe6a6077707c5de73) by Patrik Dufresne).
- Improve repository browsing speed #192 ([2d0ddb0](https://gitlab.com/ikus-soft/rdiffweb/commit/2d0ddb04abf2ec94e2226b28d0c0b5934caed3e2) by Patrik Dufresne).
- Update smtp plugin ([1e6f19a](https://gitlab.com/ikus-soft/rdiffweb/commit/1e6f19a3ed4883376ef8581b5000490e53134378) by Patrik Dufresne).
- Refresh repo list when required and allow manual refresh #188 #189 ([a74c954](https://gitlab.com/ikus-soft/rdiffweb/commit/a74c954759213687b28fb8a9eb53cc6c77be7e84) by Patrik Dufresne).
- Run pytest within Debian build ([ffdafa8](https://gitlab.com/ikus-soft/rdiffweb/commit/ffdafa884022c0d0506e7690f1073714cf771e49) by Patrik Dufresne).
- Do not bump minarca version from pipeline ([54d0ba0](https://gitlab.com/ikus-soft/rdiffweb/commit/54d0ba061ab8b1262115f3b78819e1e17f68c482) by Patrik Dufresne).
- Minor refactoring to allow extending via plugins ([7528a8a](https://gitlab.com/ikus-soft/rdiffweb/commit/7528a8a7747a726963af7b7d60f9d875cd022f4d) by Patrik Dufresne).
- Upgrade ldap authentication to use ldap3 #186 ([fbac183](https://gitlab.com/ikus-soft/rdiffweb/commit/fbac183f24ca92964baa581d5eb2e962903bceab) by Patrik Dufresne).
- Upload rdiffweb package for Ubuntu impish #175 ([402b3e9](https://gitlab.com/ikus-soft/rdiffweb/commit/402b3e99e50ba702cf0b66b8c5b10996e43cdeb1) by Patrik Dufresne).
- Reffactor quota plugin #183 ([e2ab942](https://gitlab.com/ikus-soft/rdiffweb/commit/e2ab9426d31b52dbd26dad55eaa93125d270b35d) by Patrik Dufresne).
- Improve SMTP plugin to support addresses as tuple ([d24fd13](https://gitlab.com/ikus-soft/rdiffweb/commit/d24fd1395db3a6a8575786ce0b1c82ea6d32455a) by Patrik Dufresne).
- Complete changes to remove_older and notification plugins ([2526a0d](https://gitlab.com/ikus-soft/rdiffweb/commit/2526a0d6ce3573cca4914c34f61947398daf5ee8) by Patrik Dufresne).
- Extract smtp into a cherrypy plugin ([201655d](https://gitlab.com/ikus-soft/rdiffweb/commit/201655d2425fb6145382aa52b7b48933808d4a48) by Patrik Dufresne).
- Make scheduler a cherrypy plugin ([a1268d7](https://gitlab.com/ikus-soft/rdiffweb/commit/a1268d704a01b617d024b6b5732531249f267d71) by Patrik Dufresne).
- Make ldap module a cherrypy plugin ([f97ccaa](https://gitlab.com/ikus-soft/rdiffweb/commit/f97ccaa62da6bf23f96e0ea809acbe68c2cf8566) by Patrik Dufresne).
- Move i18n under tools package ([70e5f57](https://gitlab.com/ikus-soft/rdiffweb/commit/70e5f5798b60848aa2f7ac43ffd4502a9012ed10) by Patrik Dufresne).
- Update currentuser implementation ([e433511](https://gitlab.com/ikus-soft/rdiffweb/commit/e4335111847361a4b42084a255c1ed4b1b53bcdf) by Patrik Dufresne).
- Restrict MarkupSafe to <2.1 ([a0165d2](https://gitlab.com/ikus-soft/rdiffweb/commit/a0165d23a26932a021fd21b4e67ba0e9666b37f6) by Patrik Dufresne).
- Drop centos support ([ed7eb4a](https://gitlab.com/ikus-soft/rdiffweb/commit/ed7eb4ae6abe1df70cea9786d3c8d1386a213f5f) by Patrik Dufresne).
- Properly close rdiffweb-restore pipe #174 ([4742d02](https://gitlab.com/ikus-soft/rdiffweb/commit/4742d02288e0d569926e2e4748c5b4c3a5571c23) by Patrik Dufresne).
- Validate email-sender before sending emails #176 ([7a164ad](https://gitlab.com/ikus-soft/rdiffweb/commit/7a164ade4bf5993cba03df379e6320459d7edfc5) by Patrik Dufresne).

## [4.1.1](https://gitlab.com/ikus-soft/rdiffweb/tags/4.1.1) - 2022-01-18

<small>[Compare with 4.1.0](https://gitlab.com/ikus-soft/rdiffweb/compare/4.1.0...4.1.1)</small>

### Merged

- Merge branch 'patrik-fix-apt-repo-creation' into 'master' ([1474226](https://gitlab.com/ikus-soft/rdiffweb/commit/1474226c60000dae7c05562ca465230c47099343) by Patrik Dufresne).

### Misc

- Improve creation of apt configuration during installation ([65d36fd](https://gitlab.com/ikus-soft/rdiffweb/commit/65d36fd04257b94807e66c17b9d7002f66ab908e) by Patrik Dufresne).

## [4.1.0](https://gitlab.com/ikus-soft/rdiffweb/tags/4.1.0) - 2022-01-05

<small>[Compare with 4.0.6](https://gitlab.com/ikus-soft/rdiffweb/compare/4.0.6...4.1.0)</small>

### Added

- Add [arch=amd64] to apt repo #169 ([04128ea](https://gitlab.com/ikus-soft/rdiffweb/commit/04128ea7208a36917d36cacdb4b1712dfa84c4e4) by Patrik Dufresne).
- Adding APT Repo when installing deb packages #159 ([807b66c](https://gitlab.com/ikus-soft/rdiffweb/commit/807b66ce2cd91384d9e20c70425a4ab945253f1e) by Patrik Dufresne).

### Fixed

- Fix to support Rdiffweb v2.3.8 ([c3c2cc4](https://gitlab.com/ikus-soft/rdiffweb/commit/c3c2cc4ebd3194c311989cc1c95e11bfa120bd78) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-rdiffweb-238' into 'master' ([4e80107](https://gitlab.com/ikus-soft/rdiffweb/commit/4e80107211c6c79bbd9c0e626fff781814c36868) by Patrik Dufresne).
- Merge branch 'patrik-add-arch-to-deb-repo' into 'master' ([42aebdd](https://gitlab.com/ikus-soft/rdiffweb/commit/42aebdd6410ae87d1b74d5213ed2b66bf3e621f3) by Patrik Dufresne).
- Merge branch 'patrik-add-apt-repo' into 'master' ([6a5b0ad](https://gitlab.com/ikus-soft/rdiffweb/commit/6a5b0ad0a99dc5c2c2e79e47ce32801a6cdc36ac) by Patrik Dufresne).
- Merge branch 'patrik-sonar' into 'master' ([8f2ef3a](https://gitlab.com/ikus-soft/rdiffweb/commit/8f2ef3ad2877c8826e8d17b26787ba3267f6ed6d) by Patrik Dufresne).

### Misc

- Bump rdiffweb to v2.3.9 ([1fe5f12](https://gitlab.com/ikus-soft/rdiffweb/commit/1fe5f125b86af0e95024d0276e134201def97ce0) by IKUS Soft robot).
- Bump rdiffweb to v2.3.9rc1 ([edc8f60](https://gitlab.com/ikus-soft/rdiffweb/commit/edc8f6017a87aaa1e055dae64901428bafd969ee) by IKUS Soft robot).
- Bump rdiffweb to v2.3.9a2 ([4b00c90](https://gitlab.com/ikus-soft/rdiffweb/commit/4b00c902c3c33610fc9c7e8c3c53d45922da7d0e) by IKUS Soft robot).
- Bump rdiffweb to v2.3.9a1 ([0eab8a6](https://gitlab.com/ikus-soft/rdiffweb/commit/0eab8a673cf585d2e292a5d2f10d009373d09234) by IKUS Soft robot).
- Bump rdiffweb to v2.3.8 ([8e6c13a](https://gitlab.com/ikus-soft/rdiffweb/commit/8e6c13a4f0a68cd1ab156b74aeba3e422c511fb6) by IKUS Soft robot).
- Publish sonar repport #166 ([7b593c0](https://gitlab.com/ikus-soft/rdiffweb/commit/7b593c06438fd6e3fa198607bccd57289ea169c8) by Patrik Dufresne).

## [2.3.9](https://gitlab.com/ikus-soft/rdiffweb/tags/2.3.9) - 2022-01-05

<small>[Compare with 2.3.8](https://gitlab.com/ikus-soft/rdiffweb/compare/2.3.8...2.3.9)</small>

### Added

- Add flake8 to CICD pipeline ([6cc1f1c](https://gitlab.com/ikus-soft/rdiffweb/commit/6cc1f1c8ab84a34f06868a9ab57e827bd94b3a94) by Patrik Dufresne).

### Fixed

- Fix all flake8 issues ([deec016](https://gitlab.com/ikus-soft/rdiffweb/commit/deec0169431a9f7647f2124114582185aabae6cf) by Patrik Dufresne).
- Fix date parsing for backup.log #170 ([16b7837](https://gitlab.com/ikus-soft/rdiffweb/commit/16b7837e4c5264ecfa12c6f4dc8c65a502648e8e) by Patrik Dufresne).

### Removed

- Remove End-of-life Ubuntu Groovy ([b2ade30](https://gitlab.com/ikus-soft/rdiffweb/commit/b2ade306bce454522e3eacc22129699411296352) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-release-2.3.9' into 'master' ([53e3191](https://gitlab.com/ikus-soft/rdiffweb/commit/53e319169dbdbcf52cdc8bdb4f688ef8b1bec8f0) by Patrik Dufresne).
- Merge branch 'fix_decode' into 'master' ([b8c1d24](https://gitlab.com/ikus-soft/rdiffweb/commit/b8c1d24e1962b8af57ff8c730f495c72e7bcd3c1) by Patrik Dufresne).
- Merge branch 'patrik-ubuntu-end-of-life' into 'master' ([adb7ecc](https://gitlab.com/ikus-soft/rdiffweb/commit/adb7ecc0941734803960f6fbd6f942546e9d4e42) by Patrik Dufresne).
- Merge branch 'patrik-clear-warnings' into 'master' ([8855fbd](https://gitlab.com/ikus-soft/rdiffweb/commit/8855fbd23a2d4d6abd172b2f09382e2f252fa004) by Patrik Dufresne).
- Merge branch 'patrik-replace-storage-type' into 'master' ([15d8e92](https://gitlab.com/ikus-soft/rdiffweb/commit/15d8e92ef8a7f2f756f5e583c9c614298c5f735f) by Patrik Dufresne).
- Merge branch 'patrik-handle-null-last-backup-date' into 'master' ([cba2e47](https://gitlab.com/ikus-soft/rdiffweb/commit/cba2e47397de0ed35c7c7684e1dc33ed827ab324) by Patrik Dufresne).
- Merge branch 'patrik-handle-duplicate-user' into 'master' ([07db1a2](https://gitlab.com/ikus-soft/rdiffweb/commit/07db1a2c8985c24b8e7bf98532cc3065b295fcb1) by Patrik Dufresne).
- Merge branch 'patrik-fix-symlink-return-code' into 'master' ([aaad9b7](https://gitlab.com/ikus-soft/rdiffweb/commit/aaad9b7aa7aaff3ed71a7e0bfccb2bc8178ebad2) by Patrik Dufresne).
- Merge branch 'patrik-fix-date-parsing-error' into 'master' ([398f20e](https://gitlab.com/ikus-soft/rdiffweb/commit/398f20e3052207203a5b0aeff5f33216e8f6a9af) by Patrik Dufresne).

### Misc

- Update release note for v2.3.9 ([44cffe4](https://gitlab.com/ikus-soft/rdiffweb/commit/44cffe43aeb8a230862efc109c039bd7aaad7d31) by Patrik Dufresne).
- ldap_auth _try_decode was not decodng ([c6204de](https://gitlab.com/ikus-soft/rdiffweb/commit/c6204de494d7730b16d50266e5f2d1dc9a1ad839) by Shane Robinson).
- Clear a couple of deprecation warnings ([1f34c99](https://gitlab.com/ikus-soft/rdiffweb/commit/1f34c99494d46d18c75a61c92d957c34ab39b8d4) by Patrik Dufresne).
- Replace storage_type by storage_class ([8ded4ec](https://gitlab.com/ikus-soft/rdiffweb/commit/8ded4ec834efe1bf3d3cbd07fc35f8b8ae882b84) by Patrik Dufresne).
- Handle repo w/o last-backup-date in email #171 ([e5b4e4d](https://gitlab.com/ikus-soft/rdiffweb/commit/e5b4e4d2fd3630e6eaf3a78b56456cac5a13ccbf) by Patrik Dufresne).
- Return an error message for duplicate username #169 ([7410458](https://gitlab.com/ikus-soft/rdiffweb/commit/74104588f3b6bfca7dc58d56ac43ba043b4ffdc4) by Patrik Dufresne).
- Return 403 error for invalid symlink #168 ([766d1da](https://gitlab.com/ikus-soft/rdiffweb/commit/766d1da446572f2c0f636ccd04e93e13179b3cad) by Patrik Dufresne).

## [2.3.8](https://gitlab.com/ikus-soft/rdiffweb/tags/2.3.8) - 2021-12-01

<small>[Compare with 2.3.7](https://gitlab.com/ikus-soft/rdiffweb/compare/2.3.7...2.3.8)</small>

### Fixed

- Fix encoding of LDAP attribute for `ldap-add-user-default-userroot` ([4230497](https://gitlab.com/ikus-soft/rdiffweb/commit/4230497522475a175a59654d11f080c8b7dfe704) by Shane E. Robinson).

### Merged

- Merge branch 'patrik-release-note' into 'master' ([48487fa](https://gitlab.com/ikus-soft/rdiffweb/commit/48487fa2e39ce9f915e66c9a4e11b37c314e462c) by Patrik Dufresne).
- Merge branch 'patrik-fix-login-tools' into 'master' ([aa6d436](https://gitlab.com/ikus-soft/rdiffweb/commit/aa6d4363d025b8451b78472285c7ce1132df9ecd) by Patrik Dufresne).
- Merge commit '0864c9ea16027da2766d5856a6af04cc411c0641' into fix_default_userroot_for_ad ([1cc381e](https://gitlab.com/ikus-soft/rdiffweb/commit/1cc381e76b7114806aa33b1b09fb0ae62a27dbba) by Patrik Dufresne).
- Merge branch 'master' into 'master' ([0864c9e](https://gitlab.com/ikus-soft/rdiffweb/commit/0864c9ea16027da2766d5856a6af04cc411c0641) by Patrik Dufresne).
- Merge branch 'patrik-nexus' into 'master' ([34455ee](https://gitlab.com/ikus-soft/rdiffweb/commit/34455eeaeb491ff91911294b6bf1c3418586cd11) by Patrik Dufresne).
- Merge branch 'patrik-fix-chartjs' into 'master' ([3799dd4](https://gitlab.com/ikus-soft/rdiffweb/commit/3799dd42d7067fc949b8320e6c3b821af13e12c0) by Patrik Dufresne).
- Merge branch 'patrik-archive' into 'master' ([8dfe80b](https://gitlab.com/ikus-soft/rdiffweb/commit/8dfe80b8d0d05ad6d84c1ed710052d126ca523be) by Patrik Dufresne).

### Misc

- Update release note v2.3.8 ([d2faf39](https://gitlab.com/ikus-soft/rdiffweb/commit/d2faf39ec264e4b8a712713bc9ffdc1b78723227) by Patrik Dufresne).
- Improve authentication mechanics ([44f2398](https://gitlab.com/ikus-soft/rdiffweb/commit/44f23983fa9ee60a5c15e63b278b84d2206cba50) by Patrik Dufresne).
- Allow for a base DN of the entire directory. ([9b6fbae](https://gitlab.com/ikus-soft/rdiffweb/commit/9b6fbaecbb50e252f3446bcb83f9f82f41413266) by Shane Robinson).
- Publish doc to nexus server share#509 ([937874a](https://gitlab.com/ikus-soft/rdiffweb/commit/937874a8b1645c138d34cb49e1de3f6d811a1aa4) by Patrik Dufresne).
- Adjust formating of installation steps ([c86e797](https://gitlab.com/ikus-soft/rdiffweb/commit/c86e79779413d01aef0fc061508ae5d5f1dfbd73) by Patrik Dufresne).
- Use Chart.bundle on Debian #164 ([5e60362](https://gitlab.com/ikus-soft/rdiffweb/commit/5e60362ce0bfd4fe2a262b7d8acc829eb5278d85) by Patrik Dufresne).
- Publish doc to archive.ikus-soft.com ([8815732](https://gitlab.com/ikus-soft/rdiffweb/commit/8815732800a3219b8311d6e571ea24d3649f6c7c) by Patrik Dufresne).

## [4.0.6](https://gitlab.com/ikus-soft/rdiffweb/tags/4.0.6) - 2021-10-21

<small>[Compare with 4.0.0](https://gitlab.com/ikus-soft/rdiffweb/compare/4.0.0...4.0.6)</small>

### Merged

- Merge branch 'patrick-doc' into 'master' ([6f76fef](https://gitlab.com/ikus-soft/rdiffweb/commit/6f76fef06027e3fc7053982cd6c93cfe448a72b0) by Patrik Dufresne).

### Misc

- Bump rdiffweb to v2.3.7 ([d637f79](https://gitlab.com/ikus-soft/rdiffweb/commit/d637f7953ddfe437f7ea6ed102001de003c9768a) by IKUS Soft robot).
- Bump rdiffweb to v2.3.7rc1 ([9560210](https://gitlab.com/ikus-soft/rdiffweb/commit/95602109559cf12dfc5bd0ff7b83d4b04e364183) by IKUS Soft robot).
- Bump rdiffweb to v2.3.6 ([58adc77](https://gitlab.com/ikus-soft/rdiffweb/commit/58adc77d60650bf78e531c9b22d2036999208351) by IKUS Soft robot).
- Make call to minarca-server ([375d440](https://gitlab.com/ikus-soft/rdiffweb/commit/375d440855e419e706e02d8f2cea04e7c913ff0a) by Patrik Dufresne).

## [2.3.7](https://gitlab.com/ikus-soft/rdiffweb/tags/2.3.7) - 2021-10-21

<small>[Compare with 2.3.6](https://gitlab.com/ikus-soft/rdiffweb/compare/2.3.6...2.3.7)</small>

### Merged

- Merge branch 'patrik-fix-deb-version' into 'master' ([3720a4b](https://gitlab.com/ikus-soft/rdiffweb/commit/3720a4b939b7f18296b8d2b31b859d46cd239664) by Patrik Dufresne).

### Misc

- Update README with release note for 2.3.7 ([e44a8ab](https://gitlab.com/ikus-soft/rdiffweb/commit/e44a8abcb86c5436f3a87093dfab2fdf8cc5275c) by Patrik Dufresne).
- Skip SameSite=Lax is cookie is not defined ([42455b1](https://gitlab.com/ikus-soft/rdiffweb/commit/42455b19ff973db2728f9289cae3091c39d1f82d) by Patrik Dufresne).
- Use the right version in Debian package creation ([753533b](https://gitlab.com/ikus-soft/rdiffweb/commit/753533b28da1772db49d419cc426f5228a06166c) by Patrik Dufresne).

## [2.3.6](https://gitlab.com/ikus-soft/rdiffweb/tags/2.3.6) - 2021-10-20

<small>[Compare with 2.3.4](https://gitlab.com/ikus-soft/rdiffweb/compare/2.3.4...2.3.6)</small>

### Added

- Add CSRF protection ([c364cc1](https://gitlab.com/ikus-soft/rdiffweb/commit/c364cc1d806b3faf420425df78035dbbef4a1359) by Patrik Dufresne).
- Add users role documentation #101 ([57903a2](https://gitlab.com/ikus-soft/rdiffweb/commit/57903a2589626ace2f588f6d06da7ae5bf856476) by Patrik Dufresne).

### Fixed

- Fix issues with twine installation ([4faf4c7](https://gitlab.com/ikus-soft/rdiffweb/commit/4faf4c74f2ac6b9ada226bd67cbefb69b7b0463f) by Patrik Dufresne).

### Removed

- Remove obsolete import from i18n ([548bb78](https://gitlab.com/ikus-soft/rdiffweb/commit/548bb78ed48c6010056f090e68678c7e0777a825) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-fix-ubuntu-installation' into 'master' ([d5b43c8](https://gitlab.com/ikus-soft/rdiffweb/commit/d5b43c89e5529b1078d0b8a9fed07eefa86543b7) by Patrik Dufresne).
- Merge branch 'patrik-csrf-validate-origin' into 'master' ([16bcbd7](https://gitlab.com/ikus-soft/rdiffweb/commit/16bcbd788a37d31921a5c6f7e09a59d95e78dc87) by Patrik Dufresne).
- Merge branch 'patrik-doc' into 'master' ([1ec8118](https://gitlab.com/ikus-soft/rdiffweb/commit/1ec81187543e027502a5866b8ebc3adf1b72746e) by Patrik Dufresne).
- Merge branch 'patrik-fix-twine' into 'master' ([4792fa3](https://gitlab.com/ikus-soft/rdiffweb/commit/4792fa3653d5a01e6b7c130a6cf30985341a6183) by Patrik Dufresne).
- Merge pull request #74 from Fly7113/patch-1 ([4bf55ff](https://gitlab.com/ikus-soft/rdiffweb/commit/4bf55ffebaf8306687c59cc7cf06ec3e48ffe6a4) by Patrik Dufresne).

### Misc

- Update installation step #162 ([749c9e1](https://gitlab.com/ikus-soft/rdiffweb/commit/749c9e193b6b28ed4df16e9cf694aaa668bb6a49) by Patrik Dufresne).
- Build and publish Ubuntu debian packages ([06bc197](https://gitlab.com/ikus-soft/rdiffweb/commit/06bc1977259e4a893e6dcbe6e90228252e2485f2) by Patrik Dufresne).
- Improve wtforms usage and validation ([eac4f86](https://gitlab.com/ikus-soft/rdiffweb/commit/eac4f86b2a992c367c5a1b45fc62368f7a7d0987) by Patrik Dufresne).
- Improve unit test ([2662d16](https://gitlab.com/ikus-soft/rdiffweb/commit/2662d163f1ce92d5309fa9b0a976ac01a8d83b1f) by Patrik Dufresne).
- Minor fixes to dvelopement doc ([38a1723](https://gitlab.com/ikus-soft/rdiffweb/commit/38a17234853f8c42c2f294f4a3e0a8c4d86df2d2) by Patrik Dufresne).
- Update nginx configuration ([9d84294](https://gitlab.com/ikus-soft/rdiffweb/commit/9d8429441050cfe97508fe43b2b9e21f59a287ac) by Lorenzo Moscati).

## [4.0.0](https://gitlab.com/ikus-soft/rdiffweb/tags/4.0.0) - 2021-09-20

<small>[Compare with v3.9.0](https://gitlab.com/ikus-soft/rdiffweb/compare/v3.9.0...4.0.0)</small>

### Added

- Add symlink to rdiff-backup v2.0 ([03c4023](https://gitlab.com/ikus-soft/rdiffweb/commit/03c40230f4f6da1771bfcebae4b1b1599d2448a2) by Patrik Dufresne).

### Removed

- Remove mockldap from testing #155 #156 ([cbde330](https://gitlab.com/ikus-soft/rdiffweb/commit/cbde33045d4ed193f41e203913253be46bd2c8ec) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-favicon' into 'master' ([5b532c1](https://gitlab.com/ikus-soft/rdiffweb/commit/5b532c18139b3e49848b7034459086125a6fcb58) by Patrik Dufresne).
- Merge branch 'patrik-update-minarca-server-icon' into 'master' ([526b0b3](https://gitlab.com/ikus-soft/rdiffweb/commit/526b0b3ce27bf6cda9db0149a566010912d686c5) by Patrik Dufresne).

### Misc

- Update minarca favicon ([7286cde](https://gitlab.com/ikus-soft/rdiffweb/commit/7286cdeefc2e7d566ee29d13ab0d5e73f3dc9e35) by Patrik Dufresne).
- Bump rdiffweb to v2.3.4 ([a091dc6](https://gitlab.com/ikus-soft/rdiffweb/commit/a091dc66f9807c0bf8e2587f736794bbf9fe6a94) by IKUS Soft robot).
- Properly fallback to default quota #156 ([0c14337](https://gitlab.com/ikus-soft/rdiffweb/commit/0c14337da83abe6ce67f0e100e80cd6ace5d33f7) by Patrik Dufresne).
- Update minarca-server icon ([899e68e](https://gitlab.com/ikus-soft/rdiffweb/commit/899e68e49c6a439f3ce10f60bd2593fe1e2c28ca) by Patrik Dufresne).
- Replace nose test by pytest #155 ([7337996](https://gitlab.com/ikus-soft/rdiffweb/commit/7337996a49546485463ca0c7802a2ace753f49fa) by Patrik Dufresne).
- Define blue as default theme rdiffweb#158 ([e63bdb2](https://gitlab.com/ikus-soft/rdiffweb/commit/e63bdb21a436f2dd69c932aee81e854d5f211299) by Patrik Dufresne).
- Bump rdiffweb to v2.3.3 ([300c6f0](https://gitlab.com/ikus-soft/rdiffweb/commit/300c6f0c39b3bc126c96a753fe574052d20fd9a7) by IKUS Soft robot).
- Disable test in minarca server build ([ad373c4](https://gitlab.com/ikus-soft/rdiffweb/commit/ad373c4e1003c6cf82952fe53ba73e98712dc826) by Patrik Dufresne).
- Bump rdiffweb to v2.3.2 ([8aa3fc8](https://gitlab.com/ikus-soft/rdiffweb/commit/8aa3fc85d7fcab1f66c8d68737ce030e3340dae6) by IKUS Soft robot).
- Bump rdiffweb to v2.3.1 ([f1ac8a9](https://gitlab.com/ikus-soft/rdiffweb/commit/f1ac8a99b915f9b62eddd5615c23c82fc8f84cb1) by IKUS Soft robot).
- Replace `/var/run/minarca` by `/var/lib/minarca` rdiffweb#148 ([1da0001](https://gitlab.com/ikus-soft/rdiffweb/commit/1da0001a28d06e7ac5ceabb6436ea903c96a6d08) by Patrik Dufresne).
- Bump rdiffweb to v2.3.0 ([6d9e424](https://gitlab.com/ikus-soft/rdiffweb/commit/6d9e424dc03e40013acc8390ad641d33cf23ce05) by IKUS Soft robot).
- minarca-shell: Create /dev/null in chroot jail ([26e4565](https://gitlab.com/ikus-soft/rdiffweb/commit/26e45650d5d927b0f8fc3b6de3dcf576d0dd1b99) by Patrik Dufresne).
- Re-Implement Minarca Client in Python #87 ([911083f](https://gitlab.com/ikus-soft/rdiffweb/commit/911083f3250a94797a990c7524e9dfd9ed2cbd6f) by Patrik Dufresne).
- Bump Rdiffweb to include chartkick ([2ed3e22](https://gitlab.com/ikus-soft/rdiffweb/commit/2ed3e22d8c6ca3d196e079bfff114a28223640c7) by Patrik Dufresne).

## [2.3.4](https://gitlab.com/ikus-soft/rdiffweb/tags/2.3.4) - 2021-09-20

<small>[Compare with 2.3.3](https://gitlab.com/ikus-soft/rdiffweb/compare/2.3.3...2.3.4)</small>

### Merged

- Merge branch 'patrik-fix-notification' into 'master' ([ba3f6aa](https://gitlab.com/ikus-soft/rdiffweb/commit/ba3f6aa95c422cad497a1f0a8698225ad6320876) by Patrik Dufresne).
- Merge branch 'patrik-config-print-error' into 'master' ([3bcc6a8](https://gitlab.com/ikus-soft/rdiffweb/commit/3bcc6a8949d564f8e98010d06d7a3d96ab005ea4) by Patrik Dufresne).
- Merge branch 'patrik-pytest' into 'master' ([67a7ed7](https://gitlab.com/ikus-soft/rdiffweb/commit/67a7ed7e1a01da017deb6c68717e3c758bb3fccc) by Patrik Dufresne).
- Merge branch 'patrik-fix-email-notification' into 'master' ([0e76471](https://gitlab.com/ikus-soft/rdiffweb/commit/0e76471c26858957a6ee14c7372424d63e6e74d4) by Patrik Dufresne).

### Misc

- Update README change log ([0e45aac](https://gitlab.com/ikus-soft/rdiffweb/commit/0e45aaccc37337e853c5e58d38743d8aa58af46b) by Patrik Dufresne).
- Avoid sending email when nothing changed #159 ([6abb1a3](https://gitlab.com/ikus-soft/rdiffweb/commit/6abb1a3a2ce5facaf9f589e978a031176b5b7dd8) by Patrik Dufresne).
- Create SECURITY.md (#73) ([54c343c](https://gitlab.com/ikus-soft/rdiffweb/commit/54c343c72c19ab1261b3ffdd2bb26d458c3f207c) by Ziding Zhang).
- WIP: Print error when entrypoint fail to load ([1c4d7a3](https://gitlab.com/ikus-soft/rdiffweb/commit/1c4d7a3f5e0d313737a7c08118531ff3ac0357a4) by Patrik Dufresne).
- Define user's email from LDAP mail attr #156 ([c14cd87](https://gitlab.com/ikus-soft/rdiffweb/commit/c14cd87b870ff8cdd9cd06916ffa4e3b907172dc) by Patrik Dufresne).
- Migrate to pytest and fix mockldap dependencies #155 #160 ([5bd7896](https://gitlab.com/ikus-soft/rdiffweb/commit/5bd789606b4f616d27362efc2298fcf3496a731b) by Patrik Dufresne).
- Send email only if email-host is configured #157 ([c583771](https://gitlab.com/ikus-soft/rdiffweb/commit/c58377116d43e0f726b6ead5a008394dc6363396) by Patrik Dufresne).
- Update Copyright notice ([295f837](https://gitlab.com/ikus-soft/rdiffweb/commit/295f837efd94849c8e84ca98b6f91bf898521b19) by Patrik Dufresne).

## [2.3.3](https://gitlab.com/ikus-soft/rdiffweb/tags/2.3.3) - 2021-09-10

<small>[Compare with 2.3.2](https://gitlab.com/ikus-soft/rdiffweb/compare/2.3.2...2.3.3)</small>

### Added

- Add banner to README file ([452e07f](https://gitlab.com/ikus-soft/rdiffweb/commit/452e07fad8a195a61e598dff8bb02fd497f08a1c) by Patrik Dufresne).
- Add blue theme and automate theme validation #158 ([5431ad3](https://gitlab.com/ikus-soft/rdiffweb/commit/5431ad3095b7401d48f3c4a7aa33c52bdd7f96d9) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-add-banner' into 'master' ([c883d46](https://gitlab.com/ikus-soft/rdiffweb/commit/c883d468b03a73c7876e84fe9914fbd944af0b4f) by Patrik Dufresne).
- Merge branch 'patrik-add-theme' into 'master' ([12eb48d](https://gitlab.com/ikus-soft/rdiffweb/commit/12eb48d85f78bd0ad70dff8bf444005a6ca13853) by Patrik Dufresne).

## [2.3.2](https://gitlab.com/ikus-soft/rdiffweb/tags/2.3.2) - 2021-09-07

<small>[Compare with 2.3.1](https://gitlab.com/ikus-soft/rdiffweb/compare/2.3.1...2.3.2)</small>

### Merged

- Merge branch 'patrik-update-repos' into 'master' ([835862b](https://gitlab.com/ikus-soft/rdiffweb/commit/835862bd9959fdf3449930728dee1306e863b99b) by Patrik Dufresne).

### Misc

- Automatically update users repository on location view ([6e6239a](https://gitlab.com/ikus-soft/rdiffweb/commit/6e6239a40f1ed447bb2505359f1f1b5d2cdf8118) by Patrik Dufresne).

## [2.3.1](https://gitlab.com/ikus-soft/rdiffweb/tags/2.3.1) - 2021-07-14

<small>[Compare with 2.3.0](https://gitlab.com/ikus-soft/rdiffweb/compare/2.3.0...2.3.1)</small>

### Merged

- Merge branch 'patrik-fix-var-run' into 'master' ([01dce04](https://gitlab.com/ikus-soft/rdiffweb/commit/01dce0498ea1f3ee4356e7f4ecf21e3cd124a4c9) by Patrik Dufresne).

### Misc

- Update documentation for session-dir to avoid `/var/run` #148 ([59938c6](https://gitlab.com/ikus-soft/rdiffweb/commit/59938c6fdc6b1310ad6c96c3aa2291da13a06466) by Patrik Dufresne).

## [2.3.0](https://gitlab.com/ikus-soft/rdiffweb/tags/2.3.0) - 2021-07-07

<small>[Compare with 2.2.1](https://gitlab.com/ikus-soft/rdiffweb/compare/2.2.1...2.3.0)</small>

### Added

- Add release note v2.3.0 ([b34967b](https://gitlab.com/ikus-soft/rdiffweb/commit/b34967b4a0d1b6041ca8029268e9f01334a01d64) by Patrik Dufresne).

### Fixed

- Fix file and folder sorting in browser view #143 ([42b4687](https://gitlab.com/ikus-soft/rdiffweb/commit/42b468725266d0c0760673bb7bd9381baf945004) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-release-note-2.3.0' into 'master' ([ad98d73](https://gitlab.com/ikus-soft/rdiffweb/commit/ad98d73b6e968d3bc158e938582a7bf91993e6a9) by Patrik Dufresne).
- Merge branch 'patrik-fix-sorting' into 'master' ([e84f1a6](https://gitlab.com/ikus-soft/rdiffweb/commit/e84f1a6c5721ed7d4943a22a2f41272df50f569a) by Patrik Dufresne).
- Merge branch 'patrik-docker' into 'master' ([5564c6a](https://gitlab.com/ikus-soft/rdiffweb/commit/5564c6a0672c49db31427e4c7b6dfd166a379d8f) by Patrik Dufresne).
- Merge branch 'patrik-status' into 'master' ([2619c26](https://gitlab.com/ikus-soft/rdiffweb/commit/2619c2670537c068c78364a74efa573ff389c540) by Patrik Dufresne).
- Merge branch 'patrik-chartjs' into 'master' ([afa2fd1](https://gitlab.com/ikus-soft/rdiffweb/commit/afa2fd11214dbe5e66ab0beabb1f6488af246902) by Patrik Dufresne).
- Merge branch 'patrik-timezone' into 'master' ([de0f091](https://gitlab.com/ikus-soft/rdiffweb/commit/de0f0912f3b91505eb5b86aaa01d5bf637731b3b) by Patrik Dufresne).

### Documented

- Dockerize Rdiffweb #55 ([fd2066d](https://gitlab.com/ikus-soft/rdiffweb/commit/fd2066d5b34969d359d66575b961524de5fbd788) by Patrik Dufresne).

### Misc

- Replace d3js by chartkick #122 ([a45bfc3](https://gitlab.com/ikus-soft/rdiffweb/commit/a45bfc320d98cd946ef42fef3b4ca4eb95e3f3be) by Patrik Dufresne).
- Implement status view using chartjs #122 ([89f71f5](https://gitlab.com/ikus-soft/rdiffweb/commit/89f71f5f86aa5d52db651a9d4a1a5a5bff628749) by Patrik Dufresne).
- Display date with appropriate user's timezone #143 ([5e3f61e](https://gitlab.com/ikus-soft/rdiffweb/commit/5e3f61ec11b7d1670539b6dd87626fdf4f40c235) by Patrik Dufresne).

## [v3.9.0](https://gitlab.com/ikus-soft/rdiffweb/tags/v3.9.0) - 2021-05-11

<small>[Compare with v3.8.0](https://gitlab.com/ikus-soft/rdiffweb/compare/v3.8.0...v3.9.0)</small>

### Added

- minarca-shell: add timezone information in chroot jail ([9ee7936](https://gitlab.com/ikus-soft/rdiffweb/commit/9ee793627ecfee0305a7cb1f19ebf7d3731ec370) by Patrik Dufresne).
- Add support for bullseye ([a10d834](https://gitlab.com/ikus-soft/rdiffweb/commit/a10d8343c7af6f82839ffbd419dba3aa0497fc08) by Patrik Dufresne).
- Add rdiff-backup2 and rdiff-backup1 #134 ([2231333](https://gitlab.com/ikus-soft/rdiffweb/commit/223133316ca13a01d92f14972c65ee8ce78847b3) by Patrik Dufresne).

### Fixed

- Fix rdiff-backup-delete missing from PATH ([93060ed](https://gitlab.com/ikus-soft/rdiffweb/commit/93060edd4c02b4259bd8c03d0ff266dfca9caec6) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-compat-11' into 'master' ([e360392](https://gitlab.com/ikus-soft/rdiffweb/commit/e36039286ef37bf39479c852a00776f3590f3892) by Patrik Dufresne).
- Merge branch 'patrik-fix-pid-file' into 'master' ([69ab4a9](https://gitlab.com/ikus-soft/rdiffweb/commit/69ab4a90a354ea9793584138a3f3bb87214c58d8) by Patrik Dufresne).
- Merge branch 'patrik-rdiff-backup-2.0-from-deb' into 'master' ([e3e7a56](https://gitlab.com/ikus-soft/rdiffweb/commit/e3e7a562541a9faec41f0cf685c9dae6d194a39e) by Patrik Dufresne).
- Merge branch 'patrik-update-authorized-keys-on-startup' into 'master' ([bd463f3](https://gitlab.com/ikus-soft/rdiffweb/commit/bd463f336d34e050f0bcfc29cd7288691f30915f) by Patrik Dufresne).
- Merge branch 'patrik-rdiff-backup2' into 'master' ([5ce49dd](https://gitlab.com/ikus-soft/rdiffweb/commit/5ce49dddb2b47672335164411c66cf203247da6e) by Patrik Dufresne).
- Merge branch 'patrik-apt-repo' into 'master' ([f07cc5c](https://gitlab.com/ikus-soft/rdiffweb/commit/f07cc5c2af6e6b9b157ca412d0c20a8c5537204e) by Patrik Dufresne).
- Merge branch 'patrik-drop-debian-stretch' into 'master' ([af5c501](https://gitlab.com/ikus-soft/rdiffweb/commit/af5c501ad094d2d1b5f55c16513fe4db40c9641d) by Patrik Dufresne).
- Merge branch 'patrik-bump-rdiffweb' into 'master' ([2b9a6d9](https://gitlab.com/ikus-soft/rdiffweb/commit/2b9a6d9f99edea8f137365b10908c2c3354c4b3b) by Patrik Dufresne).

### Misc

- Bump rdiffweb to v2.2.1 ([6719054](https://gitlab.com/ikus-soft/rdiffweb/commit/67190542f4f5fa7cefb55e788b2fbd12ae616bea) by IKUS Soft robot).
- Bump rdiffweb to v2.2.0.dev1 ([e016ffb](https://gitlab.com/ikus-soft/rdiffweb/commit/e016ffbdf1cc2b8852e5dadcc1a06a064168fbd7) by IKUS Soft robot).
- Bump rdiffweb to v2.2.0a5 ([943a527](https://gitlab.com/ikus-soft/rdiffweb/commit/943a527074210c226641900e2ff602b5aeb98e6d) by IKUS Soft robot).
- Provide default `session-dir` folder ([4bc0bf3](https://gitlab.com/ikus-soft/rdiffweb/commit/4bc0bf320690499474ce3ddaa9e39a2e53546b1c) by Patrik Dufresne).
- Restore debian package systemd ([846da28](https://gitlab.com/ikus-soft/rdiffweb/commit/846da281c70c6c81b22fbcf237b4b69e7173b9f1) by Patrik Dufresne).
- Create debian pacakge with debhelper-compat (= 11) ([a731834](https://gitlab.com/ikus-soft/rdiffweb/commit/a73183409679f8589ca561eb971dbbd9549df17f) by Patrik Dufresne).
- Bump rdiffweb to v2.2.0a4 ([d434030](https://gitlab.com/ikus-soft/rdiffweb/commit/d434030c66dabf8200b090308d6cce1b41bd9cb8) by IKUS Soft robot).
- Install rdiff-backup 2.0.5 from Debian package ([b184974](https://gitlab.com/ikus-soft/rdiffweb/commit/b18497480c65c7939e10ce95062232b6defa4034) by Patrik Dufresne).
- Update authorization_keys files on startup ([bbd6c52](https://gitlab.com/ikus-soft/rdiffweb/commit/bbd6c521d3c5fb8ab80684a3d39fec1791f512c1) by Patrik Dufresne).
- Bump rdiffweb to v2.2.0a3 ([9581c49](https://gitlab.com/ikus-soft/rdiffweb/commit/9581c49da232b305be0caa403c3c3fda2623d06a) by IKUS Soft robot).
- Drop Debian stretch support ([30e67a6](https://gitlab.com/ikus-soft/rdiffweb/commit/30e67a689173fc0a43b029f1f4bd3c2f90ec2d55) by Patrik Dufresne).
- Bump rdiffweb to 2.1.1.dev78+g34f1634 with background job scheduler ([e10291b](https://gitlab.com/ikus-soft/rdiffweb/commit/e10291ba76af096a726197ce7d3880c091753ccc) by Patrik Dufresne).
- Replace call to assertEquals by assertEqual to avoid deprecation msg ([85a67b0](https://gitlab.com/ikus-soft/rdiffweb/commit/85a67b03d6a8013714f7e9f891c9f7e2a82e4668) by Patrik Dufresne).
- Replace call to warn() by warning() to avoid deprecation message ([eb2eac2](https://gitlab.com/ikus-soft/rdiffweb/commit/eb2eac2f81db206141ae1a112011c1b53ffafaa6) by Patrik Dufresne).
- Run minarca unit test in virtualenv ([ce3bcd6](https://gitlab.com/ikus-soft/rdiffweb/commit/ce3bcd6b38ea79440ea11566c4bd940c8fd8219f) by Patrik Dufresne).
- Upgrade rdiffweb to 2.1.1 ([4dbf0df](https://gitlab.com/ikus-soft/rdiffweb/commit/4dbf0df8efa0577c5ccd5f2d2f11c3d246212011) by Patrik Dufresne).

## [2.2.1](https://gitlab.com/ikus-soft/rdiffweb/tags/2.2.1) - 2021-05-11

<small>[Compare with 2.1.0](https://gitlab.com/ikus-soft/rdiffweb/compare/2.1.0...2.2.1)</small>

### Added

- Add google analytics to sphinx documentation ([26beae9](https://gitlab.com/ikus-soft/rdiffweb/commit/26beae9c1f7077be08353a42c753a274f9af3381) by Patrik Dufresne).
- Adding postrm to remove session directory on purge. ([d98d4ca](https://gitlab.com/ikus-soft/rdiffweb/commit/d98d4ca28a9ecef3c3dd31b9326274f0d35e5ed1) by Daniel Baumann).
- Add default limit to graph stats ([fd52736](https://gitlab.com/ikus-soft/rdiffweb/commit/fd5273659812d19bd8dc56c7f9e543b2c8de879f) by Patrik Dufresne).
- Add logs view #129 ([1d7b88e](https://gitlab.com/ikus-soft/rdiffweb/commit/1d7b88ef846b6a9b3466606a47acf4d7138f9076) by Patrik Dufresne).
- Add logging to rdiff-backup-delete job #128 ([3120fba](https://gitlab.com/ikus-soft/rdiffweb/commit/3120fba8b2289bc5b393f4fcfe1355e652e3e342) by Patrik Dufresne).
- Add test for storage-dir ([9853197](https://gitlab.com/ikus-soft/rdiffweb/commit/9853197ec6c3ffe27889f7ee35e792b6c9891ebd) by Patrik Dufresne).
- Add rdiff-backup to build depends ([98d6be2](https://gitlab.com/ikus-soft/rdiffweb/commit/98d6be2f2f87128900b56870429afdc9e89d577a) by Patrik Dufresne).
- Add default role and default userroot for LDAP user creation #125 ([fbf04a1](https://gitlab.com/ikus-soft/rdiffweb/commit/fbf04a1e18ccf48892ce309c81ddbdf3fc2d2343) by Patrik Dufresne).
- Add pipeline to build packages for Debian Buster ([536a0a1](https://gitlab.com/ikus-soft/rdiffweb/commit/536a0a1ddc800b6f520939de547130662912cfc8) by Patrik Dufresne).
- Add jquery-validation source code ([5b985e3](https://gitlab.com/ikus-soft/rdiffweb/commit/5b985e3493cda23f2f0a20107c669ab8a26bd649) by Patrik Dufresne).
- Add license header to timsort.js ([c08ea6a](https://gitlab.com/ikus-soft/rdiffweb/commit/c08ea6ae61c70be798c64c0940eb0ee407fc1f04) by Patrik Dufresne).
- Add license header to jquery.validate.ru.js ([9ab04ef](https://gitlab.com/ikus-soft/rdiffweb/commit/9ab04ef5b8ce3cef3931f31a3098d0c798ee2bd2) by Patrik Dufresne).
- Add license header to jquery.validate.fr.js ([a02ee63](https://gitlab.com/ikus-soft/rdiffweb/commit/a02ee63b0688a31e3fc18267b984d0a0aa4dd742) by Patrik Dufresne).
- Add license header to jquery.sortchildren.js ([0e3f11f](https://gitlab.com/ikus-soft/rdiffweb/commit/0e3f11fe69db906d161218612cbf5d48e6532a7d) by Patrik Dufresne).
- Adding bootstrap vendor source code ([140682d](https://gitlab.com/ikus-soft/rdiffweb/commit/140682de347dd4cfec514cef0af7b740e16645d9) by Patrik Dufresne).
- Add rdiff-backup as dependencies ([40f5d61](https://gitlab.com/ikus-soft/rdiffweb/commit/40f5d617eff5f01b1f516175cf0eca18d8480812) by Patrik Dufresne).
- Adding lintian override for intentionally broken gz file for the test suite. ([42b1aea](https://gitlab.com/ikus-soft/rdiffweb/commit/42b1aea2d4585b0340eb333a9238c82c3cb587fe) by Daniel Baumann).

### Fixed

- Fix missing return value in rdiffweb/core/quota.py ([3b470a6](https://gitlab.com/ikus-soft/rdiffweb/commit/3b470a661bf165fcd0b7c829073c0ea62fcd1112) by Niklas Bettgen).
- Fix PostgreSQL test flakiness ([268dc8b](https://gitlab.com/ikus-soft/rdiffweb/commit/268dc8b33d07814ef20ff0558d3dc75c904312c1) by Patrik Dufresne).
- Fix `APT_RELEASE_BUSTER` to publish release ([0b100ef](https://gitlab.com/ikus-soft/rdiffweb/commit/0b100efcbb916d77fcaf75c500ffeddba4c03131) by Patrik Dufresne).
- Fix unit test flakiness with postgresql ([e74f63b](https://gitlab.com/ikus-soft/rdiffweb/commit/e74f63b58bb93be9e3425fdf8ee4e460987eac23) by Patrik Dufresne).
- Fix flaky tests with postgresql #139 ([4609a10](https://gitlab.com/ikus-soft/rdiffweb/commit/4609a104edf87d9be11f1dcefcf79c06ce24f5ed) by Patrik Dufresne).
- Fix config file parsing ([0cb3ab9](https://gitlab.com/ikus-soft/rdiffweb/commit/0cb3ab91f0a851c5113ae7e45f708e6ddd64d649) by Patrik Dufresne).
- Fix setuptools_scm dependencies ([da194d6](https://gitlab.com/ikus-soft/rdiffweb/commit/da194d61c4e7ceec9a34d041d0346e8e95ba0717) by Patrik Dufresne).
- Fix to support SQLAlchemy 1.4.0 #136 ([ff7e160](https://gitlab.com/ikus-soft/rdiffweb/commit/ff7e1609258b1fe2b66332ac072d62ae5aa97c81) by Patrik Dufresne).
- Fix nexus push ([54995e8](https://gitlab.com/ikus-soft/rdiffweb/commit/54995e8e0877492d4cf124622a7e63273019ef42) by Patrik Dufresne).
- Fix copyright syntax error ([d1e080c](https://gitlab.com/ikus-soft/rdiffweb/commit/d1e080c4e3d337ac8f5091c7f7f3937fa7b6903e) by Patrik Dufresne).

### Removed

- Remove dead code ([e8e4f48](https://gitlab.com/ikus-soft/rdiffweb/commit/e8e4f48889263d603d841655d5d69152caa8cbe7) by Patrik Dufresne).
- Remove rdiff-backup-1.2 and rdiff-backup-2.0 dependencies ([0e3d27f](https://gitlab.com/ikus-soft/rdiffweb/commit/0e3d27f5a220007cb651f6e055350fa5f934e5a1) by Patrik Dufresne).
- Remove d3js files from debian source package ([1bf1ab2](https://gitlab.com/ikus-soft/rdiffweb/commit/1bf1ab2e752d3b4826fe2ac5fc45e44cbd1e434c) by Patrik Dufresne).

### Merged

- Merge branch 'bugfix/get-disk-quota' into 'master' ([a1dc60c](https://gitlab.com/ikus-soft/rdiffweb/commit/a1dc60ccfd4eeca0897d5a0924c3d1e0d9eb6b08) by Patrik Dufresne).
- Merge branch 'patrik-job-conditional' into 'master' ([484fba2](https://gitlab.com/ikus-soft/rdiffweb/commit/484fba270b01ed4672e63b5d93ec034c20318ee7) by Patrik Dufresne).
- Merge branch 'debian' into 'master' ([ea66652](https://gitlab.com/ikus-soft/rdiffweb/commit/ea66652d5a84205b5c4437a61c9a8e99a882f87e) by Patrik Dufresne).
- Merge branch 'patrik-sphinx' into 'master' ([23c7bdc](https://gitlab.com/ikus-soft/rdiffweb/commit/23c7bdcaae1b305898f8be9b769a5b3429476399) by Patrik Dufresne).
- Merge branch 'patrik-download-logs' into 'master' ([9f9e561](https://gitlab.com/ikus-soft/rdiffweb/commit/9f9e5617730e5a845d6d3684c5ce877db98a74db) by Patrik Dufresne).
- Merge branch 'patrik-status' into 'master' ([236607b](https://gitlab.com/ikus-soft/rdiffweb/commit/236607bfe2b5a70e90a50e062ba75612c30fdd48) by Patrik Dufresne).
- Merge branch 'patrik-add-logging-to-rdiff-backup-delete' into 'master' ([dbc7d22](https://gitlab.com/ikus-soft/rdiffweb/commit/dbc7d225dfbb9bfcab07b207e8d2e8ed83be1297) by Patrik Dufresne).
- Merge branch 'patrik-admin-password' into 'master' ([35305ae](https://gitlab.com/ikus-soft/rdiffweb/commit/35305ae3f451092e8143046e3da77f8165fd233a) by Patrik Dufresne).
- Merge branch 'patrik-session-dir' into 'master' ([8c1078a](https://gitlab.com/ikus-soft/rdiffweb/commit/8c1078aa0ad151f465555333bb7d0d246700cfdd) by Patrik Dufresne).
- Merge branch 'patrik-background-job' into 'master' ([34f1634](https://gitlab.com/ikus-soft/rdiffweb/commit/34f16341f51d838544bc97c6a176683fcd8dccff) by Patrik Dufresne).
- Merge branch 'patrik-debian-run-tests' into 'master' ([caa6de6](https://gitlab.com/ikus-soft/rdiffweb/commit/caa6de62110457dd5228f5ac1b30d22d623b09e0) by Patrik Dufresne).
- Merge branch 'patrik-fix-postgresql-testcases-flakiness' into 'master' ([8025c7e](https://gitlab.com/ikus-soft/rdiffweb/commit/8025c7e9d9b634946c6815d99019bf7e8ce0715a) by Patrik Dufresne).
- Merge branch 'patrik-drop-debian-stretch' into 'master' ([b2e718d](https://gitlab.com/ikus-soft/rdiffweb/commit/b2e718d993daf2156360e23a6ccd0ab63cda6ec4) by Patrik Dufresne).
- Merge branch 'patrik-split-browse-and-history' into 'master' ([b5f66cd](https://gitlab.com/ikus-soft/rdiffweb/commit/b5f66cd18601cbc2b054d51e807462c39fff9ff5) by Patrik Dufresne).
- Merge branch 'patrik-support-absolute-url' into 'master' ([8a7571e](https://gitlab.com/ikus-soft/rdiffweb/commit/8a7571ed2236298ead619c35572ea219d9b5cc32) by Patrik Dufresne).
- Merge branch 'patrik-fix-test' into 'master' ([b1bf97e](https://gitlab.com/ikus-soft/rdiffweb/commit/b1bf97e0b7e9d1a251fda9389c44884dae4a57b3) by Patrik Dufresne).
- Merge branch 'patrik-sonar' into 'master' ([420e79d](https://gitlab.com/ikus-soft/rdiffweb/commit/420e79d3d5645f2ae43beeba94f7501ae2f08e4f) by Patrik Dufresne).
- Merge branch 'patrik-sonar-version' into 'master' ([77302bc](https://gitlab.com/ikus-soft/rdiffweb/commit/77302bc2b82bf0f9f92ba905f0caf354e9f02397) by Patrik Dufresne).
- Merge branch 'patrik-quota' into 'master' ([40a3f15](https://gitlab.com/ikus-soft/rdiffweb/commit/40a3f1549826a6bfcf7b6b57ea8d8486f0231027) by Patrik Dufresne).
- Merge branch 'patrik-disable-sshkeys' into 'master' ([c8e7584](https://gitlab.com/ikus-soft/rdiffweb/commit/c8e75848d847c20cce9b6060011e52060ec97af2) by Patrik Dufresne).
- Merge branch 'patrik-fix-setuptools-scm' into 'master' ([ed19745](https://gitlab.com/ikus-soft/rdiffweb/commit/ed1974591cb7ba151a28b85a24b2a06d5ec637a0) by Patrik Dufresne).
- Merge branch 'patrik-get-disk-quota-for-dir' into 'master' ([6c57885](https://gitlab.com/ikus-soft/rdiffweb/commit/6c5788570db5d20533cc9fc21b2b14afd37c496f) by Patrik Dufresne).
- Merge branch 'patrik-sqlalchemy-1.4.0' into 'master' ([bbcf358](https://gitlab.com/ikus-soft/rdiffweb/commit/bbcf358c2b81e9352f3942475734f6d1cfdcbd20) by Patrik Dufresne).
- Merge branch 'patrik-add-arguments' into 'master' ([3ce3bf8](https://gitlab.com/ikus-soft/rdiffweb/commit/3ce3bf83618e0436c9145bea25fa1b61643e6be2) by Patrik Dufresne).
- Merge branch 'patrik-sqlalchemy' into 'master' ([0644444](https://gitlab.com/ikus-soft/rdiffweb/commit/0644444b9b3cd3ce8d9455e57d6d62c709f12ef5) by Patrik Dufresne).
- Merge branch 'patrik-default-role-and-root-directory-ldap' into 'master' ([37c8fd2](https://gitlab.com/ikus-soft/rdiffweb/commit/37c8fd2d4163f75b21f833d2e51aa408da397cb7) by Patrik Dufresne).
- Merge branch 'patrik-config-argparse' into 'master' ([5e7ce9e](https://gitlab.com/ikus-soft/rdiffweb/commit/5e7ce9ea3ca8be100e05e3598cb25ed41f46dcf4) by Patrik Dufresne).
- Merge branch 'patrik-fix-nexus-push' into 'master' ([d62a8c2](https://gitlab.com/ikus-soft/rdiffweb/commit/d62a8c2fff9310a29d7dfba2d1edd0f845be57ae) by Patrik Dufresne).
- Merge branch 'patrik-debian-systemd' into 'master' ([4f84360](https://gitlab.com/ikus-soft/rdiffweb/commit/4f84360f60d5cbe3e61c3d0ff0d22234c3134295) by Patrik Dufresne).
- Merge branch 'patrik-debian-manpages' into 'master' ([f7825d7](https://gitlab.com/ikus-soft/rdiffweb/commit/f7825d7d4218311bba8c27fe65d9ca10a850f2de) by Patrik Dufresne).
- Merge branch 'daniel.baumann-debian' into 'master' ([695fbfe](https://gitlab.com/ikus-soft/rdiffweb/commit/695fbfec16a52c72f1b02320b1028c6ed6afbdda) by Patrik Dufresne).

### Documented

- Fix publish:doc pipeline ([c5f05d4](https://gitlab.com/ikus-soft/rdiffweb/commit/c5f05d4e16574646b2d802957ae98cb81bfcd029) by Patrik Dufresne).

### Misc

- Update release note ([522a9ed](https://gitlab.com/ikus-soft/rdiffweb/commit/522a9ed41988d30643db703edfc8354e35e774bf) by Patrik Dufresne).
- Make a couple of job conditional to make pipeline run outside group ([01082f3](https://gitlab.com/ikus-soft/rdiffweb/commit/01082f3f0104027522a1389dceb8fdad99a51e97) by Patrik Dufresne).
- Adjust logging in error page ([e944c8f](https://gitlab.com/ikus-soft/rdiffweb/commit/e944c8f09b2e350323ab20a7c416239eceb5be8f) by Patrik Dufresne).
- Making postinst executable for cosmetical reasons within source tree. ([68eb57e](https://gitlab.com/ikus-soft/rdiffweb/commit/68eb57e85e90e19c3132f07d476f16475c05335e) by Daniel Baumann).
- Completing postinst structure. ([f3e2244](https://gitlab.com/ikus-soft/rdiffweb/commit/f3e2244bada7f1fc6be6d21326da234673d622ed) by Daniel Baumann).
- Enforce role of Admin user when setting admin-password #130 ([9c41b62](https://gitlab.com/ikus-soft/rdiffweb/commit/9c41b628e0b03737e5cc07a5b60ff792fb815115) by Patrik Dufresne).
- Complete logs view to allow downloading the full logs ([27771fc](https://gitlab.com/ikus-soft/rdiffweb/commit/27771fc18601d8426af2116a5d142e2ce86f3e8f) by Patrik Dufresne).
- Improve librdiff implementation ([a6db4b7](https://gitlab.com/ikus-soft/rdiffweb/commit/a6db4b723ec747ffd081dead0bbbacae4ddb1c89) by Patrik Dufresne).
- Allow to reset admin password #130 ([fcd9b63](https://gitlab.com/ikus-soft/rdiffweb/commit/fcd9b639d5ad394c454118a80f884d87dee527e0) by Patrik Dufresne).
- Create default `/var/run/rdiffweb/sessions` folder on Debian #131 ([7eb1cc3](https://gitlab.com/ikus-soft/rdiffweb/commit/7eb1cc3d219b512d4a4190cebd86f4d67d1fddc7) by Patrik Dufresne).
- Update configuration file example and fix comments parsing ([7c3ffc8](https://gitlab.com/ikus-soft/rdiffweb/commit/7c3ffc83f6e2e11a5e97940b7ee38fafd9e446e2) by Patrik Dufresne).
- Define `app.store` before creating plugins ([67fc5e4](https://gitlab.com/ikus-soft/rdiffweb/commit/67fc5e496cf600dcc2c150c51425ff8c6dd850f6) by Patrik Dufresne).
- Initial version of sphinx documentation #142 ([b6a53e2](https://gitlab.com/ikus-soft/rdiffweb/commit/b6a53e2b3e06c8bcf7841f83c2c036aef482624e) by Patrik Dufresne).
- Drop Debian Stretch support ([b5e9467](https://gitlab.com/ikus-soft/rdiffweb/commit/b5e946731ef2572aca1c00c184d6dc8d6f1ed307) by Patrik Dufresne).
- Split browser and history page ([6c01b45](https://gitlab.com/ikus-soft/rdiffweb/commit/6c01b4574b9ec9d66017dd0cd598ffeb36b9818a) by Patrik Dufresne).
- Allow deletion of files from history #128 ([a4fc4e6](https://gitlab.com/ikus-soft/rdiffweb/commit/a4fc4e6cc479a807ef8cb4fc9b90cb26af76ff83) by Patrik Dufresne).
- Use `needs` in gitlab CICD pipeline where applicable ([adcf6fb](https://gitlab.com/ikus-soft/rdiffweb/commit/adcf6fb6c97808805abb9e969d3c04355d337b61) by Patrik Dufresne).
- Upgrade docker image used for sonar ([5152df7](https://gitlab.com/ikus-soft/rdiffweb/commit/5152df730353d5c4f0c471cb69b762c2c361a21f) by Patrik Dufresne).
- Run repository deletion in background using apscheduler #48 ([7f2276b](https://gitlab.com/ikus-soft/rdiffweb/commit/7f2276be01ee20bbbe6bbeaa5c5c64ff841edde1) by Patrik Dufresne).
- Send email notification in background using apscheduler #47 ([e50b494](https://gitlab.com/ikus-soft/rdiffweb/commit/e50b4945b6a37f3f4f88fe5aedd9a21897be1cd4) by Patrik Dufresne).
- Ignore test_*.py in sonar analysis ([0b04c08](https://gitlab.com/ikus-soft/rdiffweb/commit/0b04c08b8997d2084a1572ace3662f9231ca3c32) by Patrik Dufresne).
- Provide version to sonar analysis ([e771e66](https://gitlab.com/ikus-soft/rdiffweb/commit/e771e665788ee4f91dc7fbe75461968a65747d2b) by Patrik Dufresne).
- Do not query quota if user_root is empty ([d55a5b6](https://gitlab.com/ikus-soft/rdiffweb/commit/d55a5b6a966f31cc32060486b3b5072f4941f2f3) by Patrik Dufresne).
- Use cherrypy.url() for url_for() template function ([3fc4f9e](https://gitlab.com/ikus-soft/rdiffweb/commit/3fc4f9e9ee67da5a3ab9b5b32e928902ec31d94c) by Patrik Dufresne).
- Split apache configuration into a separate section ([0096014](https://gitlab.com/ikus-soft/rdiffweb/commit/00960143861a838adeeba72553ba0bcb98b6dc51) by Patrik Dufresne).
- Schedule job in background using apscheduler #82 ([3f51af0](https://gitlab.com/ikus-soft/rdiffweb/commit/3f51af03b89cb14bff1d97f6a56716b362f586e9) by Patrik Dufresne).
- Allow disabling SSH Key management #127 ([58ebe84](https://gitlab.com/ikus-soft/rdiffweb/commit/58ebe842b435ed955bf7bc1d4839a7c85c3b3865) by Patrik Dufresne).
- Run tests in debian packages #137 ([685e3ce](https://gitlab.com/ikus-soft/rdiffweb/commit/685e3cecf6d2534c47e4bd7b953bc38d505994fd) by Patrik Dufresne).
- Get user quota only for valid user_root #135 ([3bed553](https://gitlab.com/ikus-soft/rdiffweb/commit/3bed553eb49d077ed1bca5211b8f22ae12a10407) by Patrik Dufresne).
- Replace setUpClass and tearDownClass by setup_class, teardown_class ([df9cdd9](https://gitlab.com/ikus-soft/rdiffweb/commit/df9cdd94db149bcea486f21eaa743fda7f48dd8c) by Patrik Dufresne).
- Load more arguments from entry_points ([244f67a](https://gitlab.com/ikus-soft/rdiffweb/commit/244f67a0bb11cf068ec41618d03f3800f94b794f) by Patrik Dufresne).
- Updating python debhelper sequence. ([f80dc0b](https://gitlab.com/ikus-soft/rdiffweb/commit/f80dc0b854152e9bcf2f014ac037bcd2896c57b6) by Daniel Baumann).
- Support PostgreSQL by using Use SQLAlchemy in our persistence layer #126 ([3552275](https://gitlab.com/ikus-soft/rdiffweb/commit/35522756583980afd997cdf84b24aacd036f680f) by Patrik Dufresne).
- Enhance i18n module to keep track of locales in cache ([3350ea7](https://gitlab.com/ikus-soft/rdiffweb/commit/3350ea7b2317e18e9f4d02945aa8cb6a536eab88) by Patrik Dufresne).
- Complete implementation of configArgParse for localized options ([4806fe9](https://gitlab.com/ikus-soft/rdiffweb/commit/4806fe9535b2dcb4381b2cafb02f94246ea381f8) by Patrik Dufresne).
- Use debhelper-compat (= 13) for buster build ([587d131](https://gitlab.com/ikus-soft/rdiffweb/commit/587d131fcb78ede8b1e37420d86153ea5e310b51) by Patrik Dufresne).
- Allow building packages for bullseye with debhelper-compat (= 12) ([1643b7c](https://gitlab.com/ikus-soft/rdiffweb/commit/1643b7c057b296eadad9fd0dde3b4cacab2ec27e) by Patrik Dufresne).
- Ignore files and rdiffweb.postrm.debhelper ([c7fe443](https://gitlab.com/ikus-soft/rdiffweb/commit/c7fe44367daa3e8ad460c1fb7ba6b466e29f3562) by Patrik Dufresne).
- Generate the man page for debian package #121 ([bf981d9](https://gitlab.com/ikus-soft/rdiffweb/commit/bf981d93a99b7a21d3bbfc97ef79b14b2083c440) by Patrik Dufresne).
- Dropping venv for now as it seems broken, needs fixing later on. ([f3e06ae](https://gitlab.com/ikus-soft/rdiffweb/commit/f3e06ae82e6deca7da039d5722bb5ce2e69a0165) by Daniel Baumann).
- Updating to standards version 4.5.1. ([64cb73b](https://gitlab.com/ikus-soft/rdiffweb/commit/64cb73b78436fbe0ae0adfe1aec24dfe734a49a1) by Daniel Baumann).
- Removing trailing slash in debhelper install file. ([00f5a1c](https://gitlab.com/ikus-soft/rdiffweb/commit/00f5a1c16416e187e7b0acdf633ea895c82f1e04) by Daniel Baumann).
- Updating year in copyright file. ([8794271](https://gitlab.com/ikus-soft/rdiffweb/commit/8794271fa55d92881238ec493123635a64cca954) by Daniel Baumann).
- Running wrap-and-sort over debian directory. ([44d1426](https://gitlab.com/ikus-soft/rdiffweb/commit/44d142649a46000be230712274f7df246d79f9c8) by Daniel Baumann).
- Updating date in changelog. ([cdbb4f3](https://gitlab.com/ikus-soft/rdiffweb/commit/cdbb4f32d8df6491e06dbf2691fae98f256f3812) by Daniel Baumann).
- Updating version number in changelog. ([677f618](https://gitlab.com/ikus-soft/rdiffweb/commit/677f618ae35b7d30c918cd6a08aab6d7db9763d7) by Daniel Baumann).
- Use ConfigArgParse for configuration #114 ([97945a1](https://gitlab.com/ikus-soft/rdiffweb/commit/97945a13f9c030a22575f4fe5baa642ad55783be) by Patrik Dufresne).

## [v3.8.0](https://gitlab.com/ikus-soft/rdiffweb/tags/v3.8.0) - 2021-02-17

<small>[Compare with v3.7.0](https://gitlab.com/ikus-soft/rdiffweb/compare/v3.7.0...v3.8.0)</small>

### Added

- Add minarca-shell and minarca quota logs #126 ([ba1ada0](https://gitlab.com/ikus-soft/rdiffweb/commit/ba1ada06db471f05982bd63dce9d40169a0fcfdf) by Patrik Dufresne).

### Removed

- Remove obsolete sudoers.d file ([92afad0](https://gitlab.com/ikus-soft/rdiffweb/commit/92afad0dd36e41ffa52a00b9e13e640d9a4c7bd7) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-chroot' into 'master' ([04be60f](https://gitlab.com/ikus-soft/rdiffweb/commit/04be60f6e2ab99b999a9e3faaedb3bd1da170154) by Patrik Dufresne).
- Merge branch 'patrik-fix-log-format' into 'master' ([afe2306](https://gitlab.com/ikus-soft/rdiffweb/commit/afe2306530ce75e9679cd377effb67874d71d4c3) by Patrik Dufresne).
- Merge branch 'patrik-fix-minarca-shell-migration' into 'master' ([4014b38](https://gitlab.com/ikus-soft/rdiffweb/commit/4014b38ba84ba07d779e49185557b6c9dcd7a658) by Patrik Dufresne).
- Merge branch 'patrik-zfs-project-quota' into 'master' ([9546dcf](https://gitlab.com/ikus-soft/rdiffweb/commit/9546dcf7d0b8292a2b5d41a261e25bf94d2e2c10) by Patrik Dufresne).
- Merge branch 'patrik-tidy-up' into 'master' ([24d6d59](https://gitlab.com/ikus-soft/rdiffweb/commit/24d6d595fc9fd719f5a79b4c2284272dd254b829) by Patrik Dufresne).
- Merge branch 'patrik-reuse-docker-images' into 'master' ([24b6514](https://gitlab.com/ikus-soft/rdiffweb/commit/24b6514bfd14e8734b36edf14ee27830eab8a282) by Patrik Dufresne).

### Misc

- Declare $HOME in user namespace Fix #132 ([c3d0baa](https://gitlab.com/ikus-soft/rdiffweb/commit/c3d0baa2b358ddc6e44db740c7aaf0f14608bdd6) by Patrik Dufresne).
- Implement chroot jail using user namespace #121 ([1dea7b2](https://gitlab.com/ikus-soft/rdiffweb/commit/1dea7b2b8a4af35392ab672213dc5b24a357b96e) by Patrik Dufresne).
- Verify if log file as accessible ([e343510](https://gitlab.com/ikus-soft/rdiffweb/commit/e343510d160ce90224b6c0fc8b8ca80cf305c9f5) by Patrik Dufresne).
- Bump rdiffweb to v2.1.0 ([d7b2f52](https://gitlab.com/ikus-soft/rdiffweb/commit/d7b2f5256c53901f5dc76f32e1ef09505812a931) by IKUS Soft robot).
- Bump rdiffweb to v2.0.3a7 ([113a055](https://gitlab.com/ikus-soft/rdiffweb/commit/113a05564a357f3c6767004280e70206d5c5a18e) by IKUS Soft robot).
- Bump rdiffweb to v2.0.3a6 ([ba7c849](https://gitlab.com/ikus-soft/rdiffweb/commit/ba7c84954faa3f3caa5f8abed339bc8ec24ff98d) by IKUS Soft robot).
- Bump rdiffweb to 2.0.3a6.dev11+g16addfa ([aa29a20](https://gitlab.com/ikus-soft/rdiffweb/commit/aa29a201b6ef820ef6c8a0010e9a782d200afce0) by Patrik Dufresne).
- Adjust logging format for minarca-shell minarca#124 ([d47d997](https://gitlab.com/ikus-soft/rdiffweb/commit/d47d9975085d5df35ce02040044e49da048ad7e9) by Patrik Dufresne).
- Bump rdiffweb to 2.0.3a6.dev2+g2431245 ([767ddaa](https://gitlab.com/ikus-soft/rdiffweb/commit/767ddaa495020e11eea71d6dc8a73d2615470aa7) by Patrik Dufresne).
- Support new location of minarca-shell #127 ([3106896](https://gitlab.com/ikus-soft/rdiffweb/commit/3106896457c865d48b7a0ecd9b3f463c090b7882) by Patrik Dufresne).
- Bump rdiffweb to v2.0.3a5 ([10b5bc3](https://gitlab.com/ikus-soft/rdiffweb/commit/10b5bc33a1a1c46411badf42b3955a14ccf73f37) by IKUS Soft robot).
- Improve ZFS quota management ([eaa70dd](https://gitlab.com/ikus-soft/rdiffweb/commit/eaa70dd586206e472dc794d539b2be9cb73a4fa6) by IKUS Soft robot).
- Implement minarca-shell in python #118 ([7598769](https://gitlab.com/ikus-soft/rdiffweb/commit/7598769156240a5c56f738083f2569f4141669ba) by Patrik Dufresne).
- Drops support for python2.7 ([e42f8ed](https://gitlab.com/ikus-soft/rdiffweb/commit/e42f8edc712935b84096046a73a453d8da49a3aa) by Patrik Dufresne).
- Bump rdiffweb to v1.6.0b1 ([22ce61e](https://gitlab.com/ikus-soft/rdiffweb/commit/22ce61ed7978344661cb6c2897e91a110e80f4c2) by IKUS Soft robot).
- Replace `test-bdist` target by integration-tests using docker-compose ([1541c74](https://gitlab.com/ikus-soft/rdiffweb/commit/1541c745fc753688a8bdcec0449b8d3f417587e0) by Patrik Dufresne).
- Improve Makefile - `clean` target to delete files owned by root to delete files - run docker with interactive mode to allow interupt - make use of `--no-install-recommends` to reduce compile time ([b4a6a35](https://gitlab.com/ikus-soft/rdiffweb/commit/b4a6a35e699f79ea08955603aee16f7f8525a5e8) by Patrik Dufresne).
- Split Makefile into subdirectories ([9198c9c](https://gitlab.com/ikus-soft/rdiffweb/commit/9198c9c7460d0f95a51e8b939993c91ae6d9b7cc) by Patrik Dufresne).
- Update CICD ([96012c1](https://gitlab.com/ikus-soft/rdiffweb/commit/96012c116cee65ca76393840e714c2fc83755723) by Patrik Dufresne).
- Bump rdiffweb to v1.5.1b2 ([0981640](https://gitlab.com/ikus-soft/rdiffweb/commit/098164092a5c0e246071abd591e6ec902e4bd396) by IKUS Soft robot).
- Bump rdiffweb to v1.5.1b1 ([6244d59](https://gitlab.com/ikus-soft/rdiffweb/commit/6244d59e8cfe3a69463c75bb1ca4d082d7cc159a) by IKUS Soft robot).

## [2.1.0](https://gitlab.com/ikus-soft/rdiffweb/tags/2.1.0) - 2021-01-15

<small>[Compare with 2.0.2](https://gitlab.com/ikus-soft/rdiffweb/compare/2.0.2...2.1.0)</small>

### Added

- Add userid in Admin view ([5ea0ca9](https://gitlab.com/ikus-soft/rdiffweb/commit/5ea0ca91d57c2ecc54af885ffd81bc1b77226aef) by Patrik Dufresne).

### Fixed

- Fix logic to support absolute path for logfiles ([61b8cef](https://gitlab.com/ikus-soft/rdiffweb/commit/61b8cef260d6091800da16db17f1efa2a60645d2) by Patrik Dufresne).
- Fix human size parsing in admin view to be more permissive ([d685ce8](https://gitlab.com/ikus-soft/rdiffweb/commit/d685ce88255e69bf44e36218db30402ec6b733f4) by Patrik Dufresne).
- Fix access_log username formatting #116 ([4cbf267](https://gitlab.com/ikus-soft/rdiffweb/commit/4cbf267f16f8568a30e24ad9f6cdfbd3396a42fb) by Patrik Dufresne).

### Changed

- Change API used for UserQuota ([5420dde](https://gitlab.com/ikus-soft/rdiffweb/commit/5420ddefd906509bf9b3480e7a0b5110811ccc2c) by Patrik Dufresne).

### Removed

- Remove dh-systemd from Debian build dependencies ([2bd1a00](https://gitlab.com/ikus-soft/rdiffweb/commit/2bd1a0037f4f338b572e7cfff947b51582c66eee) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-release' into 'master' ([24a567d](https://gitlab.com/ikus-soft/rdiffweb/commit/24a567d867d072c0194d8eb2006799787fd324ac) by Patrik Dufresne).
- Merge branch 'patrik-fix-disk-usage' into 'master' ([716fcbd](https://gitlab.com/ikus-soft/rdiffweb/commit/716fcbd818e4de260a1d8d79b41efedf18e47c83) by Patrik Dufresne).
- Merge branch 'patrik-logfile-view' into 'master' ([6a3fca5](https://gitlab.com/ikus-soft/rdiffweb/commit/6a3fca5aaff9c3b72f4e9c16bae4a5975e64e2a9) by Patrik Dufresne).
- Merge branch 'patrik-logging' into 'master' ([c227985](https://gitlab.com/ikus-soft/rdiffweb/commit/c227985ae1b5e09f9c442d7b7b4bb696bf14c28c) by Patrik Dufresne).
- Merge branch 'patrik-human-size' into 'master' ([04198cf](https://gitlab.com/ikus-soft/rdiffweb/commit/04198cf2d244dddeb402b08447abfe424fce31d1) by Patrik Dufresne).
- Merge branch 'patrik-fix-access-log' into 'master' ([05faf73](https://gitlab.com/ikus-soft/rdiffweb/commit/05faf7369576671c0c48a884113b128ccc858571) by Patrik Dufresne).
- Merge branch 'patrik-quota-human-readable' into 'master' ([8fe8489](https://gitlab.com/ikus-soft/rdiffweb/commit/8fe8489871b69f9c250a0b0d119172aa928626f4) by Patrik Dufresne).
- Merge branch 'patrik-fix-status' into 'master' ([2431245](https://gitlab.com/ikus-soft/rdiffweb/commit/2431245876702912a7a08d14fd7cedd7cdb54c42) by Patrik Dufresne).
- Merge branch 'patrik-improve-startup-error-handling' into 'master' ([05b285b](https://gitlab.com/ikus-soft/rdiffweb/commit/05b285bf183df7a055f3b523e6ab7ced98fb9502) by Patrik Dufresne).
- Merge branch 'patrik-quota' into 'master' ([187af28](https://gitlab.com/ikus-soft/rdiffweb/commit/187af287ee667ae165339d25b6feebeba1f01eba) by Patrik Dufresne).
- Merge branch 'patrik-allow-failure-debian-package' into 'master' ([bf780ba](https://gitlab.com/ikus-soft/rdiffweb/commit/bf780ba333328b659db60202530a68282d1a303b) by Patrik Dufresne).

### Misc

- Prepare documentation and release note for 2.1.0 ([e3ba07e](https://gitlab.com/ikus-soft/rdiffweb/commit/e3ba07ee1ed34966b2d2ef5909f412bb7a854007) by Patrik Dufresne).
- Report disk usage from user's root directory instead of '/' #120 ([02f2762](https://gitlab.com/ikus-soft/rdiffweb/commit/02f2762fb59c02a7db0e62ef70b332a1883de61f) by Patrik Dufresne).
- Simplify the logic to allow monkey patching of the log files list. ([a115895](https://gitlab.com/ikus-soft/rdiffweb/commit/a115895ff0b6c3a1bc42e0483a38093b30ffbd0d) by Patrik Dufresne).
- Use humanfriendly in templates ([ccd9b3f](https://gitlab.com/ikus-soft/rdiffweb/commit/ccd9b3fffb3c84576b838d789e169ab628cab8b0) by Patrik Dufresne).
- Adjust rdiffweb log format minarca#124 ([16addfa](https://gitlab.com/ikus-soft/rdiffweb/commit/16addfac4114228a79ca0ba12d50e381e55fd000) by Patrik Dufresne).
- Adjust the users quota progress bar ([8b140e3](https://gitlab.com/ikus-soft/rdiffweb/commit/8b140e3cbcd2f9a2f726d31d34228f6f295f9dda) by Patrik Dufresne).
- Allow setting user's quota with human readable value ([19a8926](https://gitlab.com/ikus-soft/rdiffweb/commit/19a89262e9ee9db5957eb160353be66bed8c9f43) by Patrik Dufresne).
- Improve repo status detection #117 ([c67b2ba](https://gitlab.com/ikus-soft/rdiffweb/commit/c67b2baeaa06be4d3a44f3c3edd30cb21334c0ba) by Patrik Dufresne).
- Improve web interface to report user's quota and usage in Admin view ([7b2c987](https://gitlab.com/ikus-soft/rdiffweb/commit/7b2c9870acce4f5a6c22c9d8a8fcaec1d29230f2) by Patrik Dufresne).
- Improve logging of quota error ([a27d2ff](https://gitlab.com/ikus-soft/rdiffweb/commit/a27d2ff8ee1c55ce54de709723daf00064771597) by Patrik Dufresne).
- Print exception in log if service fail to start ([49262d2](https://gitlab.com/ikus-soft/rdiffweb/commit/49262d23a8342a3f7c7946ab4c794a40c313e7ac) by Patrik Dufresne).
- Combine tox testing and package creation ([abce4f2](https://gitlab.com/ikus-soft/rdiffweb/commit/abce4f28c9c7705a2cdcd06154c311d83d8de772) by Patrik Dufresne).
- Allow failure for debian packages ([33d2b9c](https://gitlab.com/ikus-soft/rdiffweb/commit/33d2b9c7718d27f99797487882a1af4a466d1d64) by Patrik Dufresne).
- Replace cherrypy 8 by 9 for debian bullsyeye to mitigate a bug ([c0fa531](https://gitlab.com/ikus-soft/rdiffweb/commit/c0fa531ac8a38df7a9219be83cf5a3b7ecd01eb2) by Patrik Dufresne).
- Improve quota management ([a5517f8](https://gitlab.com/ikus-soft/rdiffweb/commit/a5517f8073b1c3d5aba893512f65e925d8338f64) by Patrik Dufresne).

## [2.0.2](https://gitlab.com/ikus-soft/rdiffweb/tags/2.0.2) - 2020-12-04

<small>[Compare with 2.0.1](https://gitlab.com/ikus-soft/rdiffweb/compare/2.0.1...2.0.2)</small>

### Added

- Add `readme_render` to check README.md formatting ([ff1e8cc](https://gitlab.com/ikus-soft/rdiffweb/commit/ff1e8ccbd0bf24daaaa1e6ed77c0de46ce8c592c) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-publish-deb-nexus' into 'master' ([d77ed1d](https://gitlab.com/ikus-soft/rdiffweb/commit/d77ed1df57b3a1dc8bba84f675389275669630cb) by Patrik Dufresne).

### Misc

- Try to fix pypi upload ([3cb0df3](https://gitlab.com/ikus-soft/rdiffweb/commit/3cb0df37ea5ba39b82d276482a15032e6b3e258b) by Patrik Dufresne).

## [2.0.1](https://gitlab.com/ikus-soft/rdiffweb/tags/2.0.1) - 2020-12-04

<small>[Compare with 2.0.0](https://gitlab.com/ikus-soft/rdiffweb/compare/2.0.0...2.0.1)</small>

### Fixed

- Fix test version ([a565285](https://gitlab.com/ikus-soft/rdiffweb/commit/a5652850adc92e61f6959c5968fb80419970ca1d) by Patrik Dufresne).

### Removed

- Remove allow failure on centos7-py3 ([445b139](https://gitlab.com/ikus-soft/rdiffweb/commit/445b139117ff0d7e1e21443bfbdc45dabb93cb4d) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-publish-deb-nexus' into 'master' ([a718f2a](https://gitlab.com/ikus-soft/rdiffweb/commit/a718f2a0d5adada9c4e3087cb7c9bb0da570cc71) by Patrik Dufresne).

## [2.0.0](https://gitlab.com/ikus-soft/rdiffweb/tags/2.0.0) - 2020-12-04

<small>[Compare with 1.5.0](https://gitlab.com/ikus-soft/rdiffweb/compare/1.5.0...2.0.0)</small>

### Added

- Add dependencies on python3-distutils for distutil.spawn ([bfc6a41](https://gitlab.com/ikus-soft/rdiffweb/commit/bfc6a41982e6be2d7c15d622f7dc8f5938da95b6) by Patrik Dufresne).
- Add debian package test in CICD pipeline ([4ca8ea5](https://gitlab.com/ikus-soft/rdiffweb/commit/4ca8ea5040b9b46fcd6bb2e00b28ebd7f87cff1f) by Patrik Dufresne).
- Add service unit for rdiffweb ([7259715](https://gitlab.com/ikus-soft/rdiffweb/commit/72597154878239696a0ffab6669eb247c6fed669) by Patrik Dufresne).
- Adding r3 field in control. ([e5aa8f2](https://gitlab.com/ikus-soft/rdiffweb/commit/e5aa8f2b00bd12f9f32ee10fbffe2bbdcee9fd0c) by Daniel Baumann).
- Adding todo file. ([94152f1](https://gitlab.com/ikus-soft/rdiffweb/commit/94152f109cf54094455e9a7e67911c0d6a42e59c) by Daniel Baumann).
- Add debian folder #87 ([2d2d68e](https://gitlab.com/ikus-soft/rdiffweb/commit/2d2d68ec215323ea13e0caf3ab0ae7f6e48f79f5) by Patrik Dufresne).

### Fixed

- Fix WTForms dependency version <3.0.0 ([9f7ad75](https://gitlab.com/ikus-soft/rdiffweb/commit/9f7ad756589a181316f4b59eb3352e2247c76482) by Patrik Dufresne).
- Fix CICD artifact location for debian package ([885d6d5](https://gitlab.com/ikus-soft/rdiffweb/commit/885d6d5689bb1755f72d22f7864ea104f4781afd) by Patrik Dufresne).
- Fix rdiffweb get version ([79ca468](https://gitlab.com/ikus-soft/rdiffweb/commit/79ca4688dcbe84b0e62f58f223e74a25fdd08f87) by Patrik Dufresne).
- Fix curl command line to follow redirection (-L) #109 ([dd39b3f](https://gitlab.com/ikus-soft/rdiffweb/commit/dd39b3ff503b39081c91eee82fe36a51fb5e2501) by Patrik Dufresne).
- Fix Update repos #107 ([5c6fa6c](https://gitlab.com/ikus-soft/rdiffweb/commit/5c6fa6c2c822732cfad76862349a9a99608be372) by Patrik Dufresne).

### Removed

- Remove reference to fonts.googleapis.com ([95aa166](https://gitlab.com/ikus-soft/rdiffweb/commit/95aa1661ee30d49544426eb39ede67fef6796673) by Patrik Dufresne).
- Remove python3-setuptools from Recommends ([d03d136](https://gitlab.com/ikus-soft/rdiffweb/commit/d03d136dee969b3ba920ab6b420aecbd093f0994) by Patrik Dufresne).
- Remove TODO related to python-ldap ([b9ab2ba](https://gitlab.com/ikus-soft/rdiffweb/commit/b9ab2baa432098b8de33d22b8e6f7848208a9cf9) by Patrik Dufresne).
- Remove deprecated logrotate configuration ([13e0d06](https://gitlab.com/ikus-soft/rdiffweb/commit/13e0d06bd8d67f8284604a472de3735e21b3c46a) by Patrik Dufresne).
- Remove .less files from final binary package ([9b3970b](https://gitlab.com/ikus-soft/rdiffweb/commit/9b3970bf00118c49a68d6d41578475d91903f6fb) by Patrik Dufresne).
- Remove python2 from tox.ini ([6f3a52a](https://gitlab.com/ikus-soft/rdiffweb/commit/6f3a52a777decfa2ddef15341f7fe65d8df0da11) by Patrik Dufresne).
- Remove executable bit from files ([3f3b341](https://gitlab.com/ikus-soft/rdiffweb/commit/3f3b3413ee5928210594d4afbb47e06721b8bad9) by Patrik Dufresne).
- Remove python shebang ([75bccda](https://gitlab.com/ikus-soft/rdiffweb/commit/75bccda86689152ab1cdd6e51925abe89696927a) by Patrik Dufresne).
- Remove minify dependencies ([60323b6](https://gitlab.com/ikus-soft/rdiffweb/commit/60323b60d54ca0840b30ba89ad648915502db15c) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-publish-deb-nexus' into 'master' ([8177289](https://gitlab.com/ikus-soft/rdiffweb/commit/8177289156c75cb17bf7abe8c59e07ffb5d7a831) by Patrik Dufresne).
- Merge branch 'patrik-debian' into 'master' ([de75cd1](https://gitlab.com/ikus-soft/rdiffweb/commit/de75cd165a0c7afd30ef89d29e160669b24eec6e) by Patrik Dufresne).
- Merge branch 'patrik-fix-centos-encoding' into 'master' ([f623d01](https://gitlab.com/ikus-soft/rdiffweb/commit/f623d01f9d1b5dfd50d1363ca3e6949ee7b579c8) by Patrik Dufresne).
- Merge branch 'patrik-drop-python2' into 'master' ([31ea302](https://gitlab.com/ikus-soft/rdiffweb/commit/31ea302ac1f62da323ebd2cf35ef9e1309339789) by Patrik Dufresne).
- Merge branch 'patrik-fix-mo' into 'master' ([035b0e3](https://gitlab.com/ikus-soft/rdiffweb/commit/035b0e38ea0579e1e397d85be9e25922650e4987) by Patrik Dufresne).
- Merge branch 'patrik-tidy-up-code' into 'master' ([833185f](https://gitlab.com/ikus-soft/rdiffweb/commit/833185fef6d1f27a35f4cbaa6f8ad2c52b91043b) by Patrik Dufresne).
- Merge branch 'patrik-fix-version' into 'master' ([7a41e7d](https://gitlab.com/ikus-soft/rdiffweb/commit/7a41e7db7c0316251c6f652c720ea1f7a0a2c239) by Patrik Dufresne).
- Merge branch 'patrik-fix-curl' into 'master' ([477d6fc](https://gitlab.com/ikus-soft/rdiffweb/commit/477d6fc3eacf3a32cf5fad7fbbd7d8ecc3ffb85b) by Patrik Dufresne).
- Merge branch 'patrik-docker-images' into 'master' ([6a70bf3](https://gitlab.com/ikus-soft/rdiffweb/commit/6a70bf3e80ade0a1a8889ee4c6c304dc60e89fbf) by Patrik Dufresne).
- Merge branch 'patrik-replace-git-references' into 'master' ([bd6b76b](https://gitlab.com/ikus-soft/rdiffweb/commit/bd6b76b1b534949577f00448171fcac3314a2c09) by Patrik Dufresne).
- Merge branch 'Eeems-patch-1' into 'master' ([dbf22da](https://gitlab.com/ikus-soft/rdiffweb/commit/dbf22da0a97b3608cd57012016de5d9e230b3b4d) by Patrik Dufresne).
- Merge branch 'patrik-fix-update-repos' into 'master' ([4ad9f8e](https://gitlab.com/ikus-soft/rdiffweb/commit/4ad9f8e7e7295687ed8580fec1943dda9745e462) by Patrik Dufresne).

### Misc

- Update Documentation to install using APT for bullseye ([91e6264](https://gitlab.com/ikus-soft/rdiffweb/commit/91e6264a4f753a9267b063c9bcac5b1c57fba5d0) by Patrik Dufresne).
- Push deb to nexus server ([0c155c6](https://gitlab.com/ikus-soft/rdiffweb/commit/0c155c6a9b65409842926e968023c2a01550ff2f) by Patrik Dufresne).
- Test debian package with debian:buster ([4268944](https://gitlab.com/ikus-soft/rdiffweb/commit/4268944bb822bbd225987795664e3eede19205e3) by Patrik Dufresne).
- Update copyright info for jquery, bootstrap, d3 ([64a3e6a](https://gitlab.com/ikus-soft/rdiffweb/commit/64a3e6a25e3972d242e21e7c5475193f75b9da10) by Patrik Dufresne).
- Symlink to libjs-bootstrap, libjs-jquery, libjs-d3, libjs-d3-tip ([767e146](https://gitlab.com/ikus-soft/rdiffweb/commit/767e146e09e58f77635e6d7564bf35a6378ef350) by Patrik Dufresne).
- Provide default configuration file /etc/rdiffweb/rdw.conf ([a11548d](https://gitlab.com/ikus-soft/rdiffweb/commit/a11548dc5bcc45f6b498a8ef6b36efce0cee9fe2) by Patrik Dufresne).
- Updating copyright information for Bootstrap .less ([312e5f8](https://gitlab.com/ikus-soft/rdiffweb/commit/312e5f8842b2ea72a17bd3ce632bc45dde052771) by Patrik Dufresne).
- Install dependencies using `apt build-dep -y .` ([52518ce](https://gitlab.com/ikus-soft/rdiffweb/commit/52518ce4a0e0a70006c859019902af07ce4f0b87) by Patrik Dufresne).
- Import bootstrap.min.js and jquery.min.js independently ([056ee14](https://gitlab.com/ikus-soft/rdiffweb/commit/056ee14ddc2687af14f638150f02b9a69c4e5a87) by Patrik Dufresne).
- Use Debian bullseye for debian packages and only build binary package ([eb3de0a](https://gitlab.com/ikus-soft/rdiffweb/commit/eb3de0ade79f1f23701e503d52d71c9366cc8df2) by Patrik Dufresne).
- Running wrap-and-sort. ([e8f172f](https://gitlab.com/ikus-soft/rdiffweb/commit/e8f172f825c506707f71be4c047dee915aeaa2e7) by Daniel Baumann).
- Improving package short description. ([b3893d5](https://gitlab.com/ikus-soft/rdiffweb/commit/b3893d519bffaeadf889ef30a45e23bd5ff86d14) by Daniel Baumann).
- Removing pre-buster version from python3 depends. ([85ee669](https://gitlab.com/ikus-soft/rdiffweb/commit/85ee669323711f00a8bb231c2d86cedbd0e2680d) by Daniel Baumann).
- Switching package to architecture all. ([21a0e95](https://gitlab.com/ikus-soft/rdiffweb/commit/21a0e952acfe15d493179fd623f71049c7feff49) by Daniel Baumann).
- Removing tests from the final package. ([80f5061](https://gitlab.com/ikus-soft/rdiffweb/commit/80f506157426d9f879383a24f674b225843ff7c9) by Daniel Baumann).
- Updating copyright file for GPL-3+ to match license terms used for upstream source, rathern than GPL-3 only. ([37fdc89](https://gitlab.com/ikus-soft/rdiffweb/commit/37fdc893c97c6cb82513d0c6f8c49622a0fede44) by Daniel Baumann).
- Including rdw.conf as example. ([269cbe5](https://gitlab.com/ikus-soft/rdiffweb/commit/269cbe5bf5cd2540918ec7b649f014633b989752) by Daniel Baumann).
- Correcting years in copyright file. ([9355e45](https://gitlab.com/ikus-soft/rdiffweb/commit/9355e45c66ae65ada567ba9d4c5a48ddbc6f2e43) by Daniel Baumann).
- Including upstream documentation. ([74b982b](https://gitlab.com/ikus-soft/rdiffweb/commit/74b982b03575abe56c62906ac517fa2a568779dd) by Daniel Baumann).
- Replacing dh_installman override with a execute-before statement. ([a5c0c34](https://gitlab.com/ikus-soft/rdiffweb/commit/a5c0c345c4bccee076520b03dfcd7d5ba27f68d2) by Daniel Baumann).
- Extending dh_auto_clean to also remove generated manpages. ([9143fd0](https://gitlab.com/ikus-soft/rdiffweb/commit/9143fd05d19cf04ffb5dd9753b012b0428dbe557) by Daniel Baumann).
- Moving mktemp handling for dh_installman to the top of the rules file. ([019943e](https://gitlab.com/ikus-soft/rdiffweb/commit/019943eef514ca4e16d07685010f209acd59895b) by Daniel Baumann).
- Prefixing manpages debhelper file explicitly with package name. ([18953c2](https://gitlab.com/ikus-soft/rdiffweb/commit/18953c2873b3a0f64cb896970d0012330caaf2f5) by Daniel Baumann).
- Correcting license stanza in copyright file. ([e1dbad0](https://gitlab.com/ikus-soft/rdiffweb/commit/e1dbad0c969814efd4ab9bc9d52296ce3ae43e6c) by Daniel Baumann).
- Removing deduplication of license stanzas in copyright file. ([8e39701](https://gitlab.com/ikus-soft/rdiffweb/commit/8e3970198dec6f11d8938dd7333a2266cd22f01c) by Daniel Baumann).
- Correcting upstream contact in copyright file. ([0341318](https://gitlab.com/ikus-soft/rdiffweb/commit/0341318ac657ec0778c1d620445819377495382d) by Daniel Baumann).
- Correcting upstream name in copyright file. ([5db2571](https://gitlab.com/ikus-soft/rdiffweb/commit/5db2571ba7902123fc960b8a09aa0376e9e25d0f) by Daniel Baumann).
- Updating source section to web. ([81bb29d](https://gitlab.com/ikus-soft/rdiffweb/commit/81bb29d78fd0b3fd49360f2c1c53f7cce82ac766) by Daniel Baumann).
- Updating to standards-version 4.5.0. ([8cb1f39](https://gitlab.com/ikus-soft/rdiffweb/commit/8cb1f39427fe6e06786d7fa8d933ee6e14a4cab5) by Daniel Baumann).
- Using debhelper-compat instead of debian/compat. ([84c2ac1](https://gitlab.com/ikus-soft/rdiffweb/commit/84c2ac19c1ea507ad63a53718618b595335773ae) by Daniel Baumann).
- Updating to debhelper 13. ([449ce4d](https://gitlab.com/ikus-soft/rdiffweb/commit/449ce4d89df85c3e728d90f0cce181e363eae3b0) by Daniel Baumann).
- Improving changelog message about initial upload. ([773eacd](https://gitlab.com/ikus-soft/rdiffweb/commit/773eacd688c1c23d107ab344a0bbeae7dd45576a) by Daniel Baumann).
- Updating source format to 3.0 (quilt). ([e19d526](https://gitlab.com/ikus-soft/rdiffweb/commit/e19d5265beb5598d8aeb99b4d1aa4601799d28fd) by Daniel Baumann).
- Pass a LANG environment variable to rdiff-backup restore process #112 ([6e9d62a](https://gitlab.com/ikus-soft/rdiffweb/commit/6e9d62aaeb6d927550d4eb40dda70110099a9514) by Patrik Dufresne).
- Build deb packages ([aec042a](https://gitlab.com/ikus-soft/rdiffweb/commit/aec042a20e57684bcafdd54507bda78d636f4757) by Patrik Dufresne).
- Provide null translation if the catalogues are not found ([7004195](https://gitlab.com/ikus-soft/rdiffweb/commit/7004195c53f43d0d48ffb2ba928f1651d6e93eca) by Patrik Dufresne).
- Do not update *.mo files during build ([87357be](https://gitlab.com/ikus-soft/rdiffweb/commit/87357bebbb4b39372861d9e14f43628351a5e4ea) by Patrik Dufresne).
- Improve cherrypy version detection ([29b53f9](https://gitlab.com/ikus-soft/rdiffweb/commit/29b53f9c0c1b81212f36a99a3046d8fc8ed39987) by Patrik Dufresne).
- Drop Support of Python 2 ([207cf99](https://gitlab.com/ikus-soft/rdiffweb/commit/207cf994e1abae5813ff706c985c92c175caf593) by Patrik Dufresne).
- Provide --help and --version ([4feaa50](https://gitlab.com/ikus-soft/rdiffweb/commit/4feaa50ac78d4afa26992bd56af0494610dff2ad) by Patrik Dufresne).
- Update rdiffweb installation doc ([063f9f4](https://gitlab.com/ikus-soft/rdiffweb/commit/063f9f4c46926ebec76dafbe04a483076c57bdb4) by Patrik Dufresne).
- Reuse ikus060/python docker images ([e161019](https://gitlab.com/ikus-soft/rdiffweb/commit/e161019b9f84648abb92ca3f418889b40e892ec5) by Patrik Dufresne).
- Replace patrikdufresne.com reference and github references ([2239ff5](https://gitlab.com/ikus-soft/rdiffweb/commit/2239ff5712e04b073c5e6db3ace655494ea9fbb4) by Patrik Dufresne).
- Handle elapsed time of days in the graph. ([cc1468f](https://gitlab.com/ikus-soft/rdiffweb/commit/cc1468ff1410695d07d579ce4d15816545f5739b) by Nathaniel van Diepen).

## [v3.7.0](https://gitlab.com/ikus-soft/rdiffweb/tags/v3.7.0) - 2020-07-01

<small>[Compare with v3.6.0](https://gitlab.com/ikus-soft/rdiffweb/compare/v3.6.0...v3.7.0)</small>

### Removed

- Remove "+stretch" from the debian version ([ecbfcdb](https://gitlab.com/ikus-soft/rdiffweb/commit/ecbfcdbdd935c2e5ac92d8971ccbac1301e70512) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-get-minarca-script' into 'master' ([e5f2b57](https://gitlab.com/ikus-soft/rdiffweb/commit/e5f2b57c88700d7bfb2cd46464a21fb106f7b364) by Patrik Dufresne).

### Misc

- Bump rdiffweb to v1.5.0 ([060783d](https://gitlab.com/ikus-soft/rdiffweb/commit/060783d66cb7f136a47366e426824e9207f0ef45) by IKUS Soft robot).
- Bump rdiffweb to v1.4.1b3 ([8d75f5c](https://gitlab.com/ikus-soft/rdiffweb/commit/8d75f5ce04cc933aee59aa2ec6754f92dc2b40fe) by IKUS Soft robot).
- Bump rdiffweb to v1.4.1b2 ([ab1d7b1](https://gitlab.com/ikus-soft/rdiffweb/commit/ab1d7b18e99be575a1c4b733a4f20befed039d4a) by IKUS Soft robot).
- Replace PDSL inc reference by IKUS Software inc. ([5363e83](https://gitlab.com/ikus-soft/rdiffweb/commit/5363e8369dfe940866d5de6fd24f89aa3c95d98e) by Patrik Dufresne).

## [1.5.0](https://gitlab.com/ikus-soft/rdiffweb/tags/1.5.0) - 2020-07-01

<small>[Compare with 1.4.0](https://gitlab.com/ikus-soft/rdiffweb/compare/1.4.0...1.5.0)</small>

### Added

- Add release note v1.5.0 ([7702291](https://gitlab.com/ikus-soft/rdiffweb/commit/77022912c1f4fbc20384b44bb62bb25147e8c943) by Patrik Dufresne).
- Add warning is user's root directory is not valid #30 ([d0705d4](https://gitlab.com/ikus-soft/rdiffweb/commit/d0705d4bf585dfce93c77fbae9c5fa176ba6fcc8) by Patrik Dufresne).
- Add option to control spider depthness #1 ([90dab67](https://gitlab.com/ikus-soft/rdiffweb/commit/90dab676432b4924287cf58bc2f5668814d22ac0) by Patrik Dufresne).
- Add build test for Debian Bullseye and python3.8 #104 ([c44dc34](https://gitlab.com/ikus-soft/rdiffweb/commit/c44dc34c9715df0ec00f7c70d2033bc111ea0fac) by Patrik Dufresne).

### Fixed

- Fix Last Update format for minutes and adding unit test #83 ([78cc266](https://gitlab.com/ikus-soft/rdiffweb/commit/78cc2668888f4504408322b464fd77117c3bf366) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-release' into 'master' ([582b3ac](https://gitlab.com/ikus-soft/rdiffweb/commit/582b3ac3fd1de2a8d790d6f2fa3fdd882bfeeb23) by Patrik Dufresne).
- Merge branch 'patrik-validate-default-theme' into 'master' ([c4fc991](https://gitlab.com/ikus-soft/rdiffweb/commit/c4fc991344a9aa36f926c5ac39e8dc28b6d6cfda) by Patrik Dufresne).
- Merge branch 'patrik-max-depth-option' into 'master' ([d280cbb](https://gitlab.com/ikus-soft/rdiffweb/commit/d280cbb517e0781a4b885b9baa0e893a67acc7a8) by Patrik Dufresne).
- Merge branch 'patrik-display-warning' into 'master' ([d0f4c96](https://gitlab.com/ikus-soft/rdiffweb/commit/d0f4c9636d61d3d3540523ed5b04d708dde7948c) by Patrik Dufresne).
- Merge branch 'patrik-add-debian-bullseye' into 'master' ([3265c91](https://gitlab.com/ikus-soft/rdiffweb/commit/3265c919be41425b1e35b3b544c32b8311ac0d63) by Patrik Dufresne).
- Merge branch 'patrik-date-last-updated' into 'master' ([54780fb](https://gitlab.com/ikus-soft/rdiffweb/commit/54780fbe519a8e6ec10ea2b008b79812a32c3c6a) by Patrik Dufresne).
- Merge branch 'patrik-replace-demo-url' into 'master' ([3866909](https://gitlab.com/ikus-soft/rdiffweb/commit/38669099fc2d5f136a4efe60b0d9c87fa2ae441b) by Patrik Dufresne).
- Merge branch 'patrik-automate-minarca-bump' into 'master' ([e5a99ae](https://gitlab.com/ikus-soft/rdiffweb/commit/e5a99ae6d41f7f3a403405fca75fae29abcb664a) by Patrik Dufresne).
- Merge branch 'patrik-release-note-1.4.0' into 'master' ([b96c8c9](https://gitlab.com/ikus-soft/rdiffweb/commit/b96c8c96c0addb1085dd7eb85641c5211f2d404f) by Patrik Dufresne).

### Misc

- Replace platform.dist() by distro package #104 ([49c3805](https://gitlab.com/ikus-soft/rdiffweb/commit/49c3805d1f59f5667ae1b6c8e86fade50f60f1ec) by Patrik Dufresne).
- Reformat date to be displayed as "Updated ... ago" #83 ([dc92ba9](https://gitlab.com/ikus-soft/rdiffweb/commit/dc92ba96e3bf7e4a6ba403940a38708045bd4c3f) by Patrik Dufresne).
- Replace demo url by https://rdiffweb-demo.ikus-soft.com/ share#160 ([eff34b6](https://gitlab.com/ikus-soft/rdiffweb/commit/eff34b68aaae6ed945b9050a2de01bfafd71d310) by Patrik Dufresne).
- Upgrade downstream version #102 ([9eb563d](https://gitlab.com/ikus-soft/rdiffweb/commit/9eb563dd111dfcfeb74210dc36aa60645f4f4606) by Patrik Dufresne).
- Release note v1.4.0 ([e524cfa](https://gitlab.com/ikus-soft/rdiffweb/commit/e524cfad3fc4b4f464e75402dbec692086dcf45c) by Patrik Dufresne).
- Validate DefaultTheme value. Fix #90 ([c3f281c](https://gitlab.com/ikus-soft/rdiffweb/commit/c3f281c52403386419339bb70c10c73eba6fe5cf) by Patrik Dufresne).

## [v3.6.0](https://gitlab.com/ikus-soft/rdiffweb/tags/v3.6.0) - 2020-05-20

<small>[Compare with v3.5.2](https://gitlab.com/ikus-soft/rdiffweb/compare/v3.5.2...v3.6.0)</small>

### Fixed

- Fix recursiveness during installation ([d975405](https://gitlab.com/ikus-soft/rdiffweb/commit/d975405bd69d2b049403adc793899a56f07aadc1) by Patrik Dufresne).

### Changed

- Change the help URL to allow redirection #105 ([ff01c76](https://gitlab.com/ikus-soft/rdiffweb/commit/ff01c765959936e060a6f3b683fe6c47664f4284) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-bump-release' into 'master' ([0aa320c](https://gitlab.com/ikus-soft/rdiffweb/commit/0aa320c9d33395e10b9a7a96ea4de48a02bd4945) by Patrik Dufresne).
- Merge branch 'patrik-publish-to-apt' into 'master' ([482ccea](https://gitlab.com/ikus-soft/rdiffweb/commit/482cceae68be1653cf08fe71f24ea312feade519) by Patrik Dufresne).

### Misc

- Bump to v1.4.0 ([67fc912](https://gitlab.com/ikus-soft/rdiffweb/commit/67fc912f9a713484abd0e203919d9cebf985539b) by Patrik Dufresne).
- Bump to 1.4.0b5 ([372d447](https://gitlab.com/ikus-soft/rdiffweb/commit/372d447d0966d41c091fbb7176d646cac7444136) by Patrik Dufresne).
- Bump to 1.4.0b4 ([0663dc0](https://gitlab.com/ikus-soft/rdiffweb/commit/0663dc0f2838daaddcfe86ef5354ed7b82337c08) by Patrik Dufresne).
- Powered by Minarca footer #99 ([11f45a6](https://gitlab.com/ikus-soft/rdiffweb/commit/11f45a67e2164ab5347512bacbe2ac95a0b391e5) by Patrik Dufresne).
- Bump rdiffweb to 1.4.0b3 ([5d1158e](https://gitlab.com/ikus-soft/rdiffweb/commit/5d1158e38fcfb7e8536a796c15215e791e24d782) by Patrik Dufresne).
- Bump to v1.3.2 ([1bc0f01](https://gitlab.com/ikus-soft/rdiffweb/commit/1bc0f01f4a45eafe0662d96125bd14c8560e8549) by Patrik Dufresne).

## [1.4.0](https://gitlab.com/ikus-soft/rdiffweb/tags/1.4.0) - 2020-05-20

<small>[Compare with 1.3.2](https://gitlab.com/ikus-soft/rdiffweb/compare/1.3.2...1.4.0)</small>

### Added

- Add wtforms and flash for admin/users #96 #97 ([debbe13](https://gitlab.com/ikus-soft/rdiffweb/commit/debbe13d5da1c77d4fede4f02b5d0679ddcb664b) by Patrik Dufresne).
- Add "Powered by" footer #91 ([e995d1c](https://gitlab.com/ikus-soft/rdiffweb/commit/e995d1ca4ae52768f6600f4acb032c1400122a70) by Patrik Dufresne).

### Fixed

- Fix pipeline for gitlab.com ([e168b64](https://gitlab.com/ikus-soft/rdiffweb/commit/e168b648e3a0ca208a12387df439a2551613b252) by Patrik Dufresne).
- Fix users roles #94 ([9b78407](https://gitlab.com/ikus-soft/rdiffweb/commit/9b784078d21b44422019146146c5638a8a5bd87d) by Patrik Dufresne).
- Fix single repo discovery ([6411960](https://gitlab.com/ikus-soft/rdiffweb/commit/641196053f527a52fb89ca0d67b648e94fa41a2e) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-users-ssh-keys' into 'master' ([2c3adb7](https://gitlab.com/ikus-soft/rdiffweb/commit/2c3adb7478d47d9ad4d15ebb34a1b2235b25df52) by Patrik Dufresne).
- Merge branch 'patrik-wtforms-flash' into 'master' ([26f0576](https://gitlab.com/ikus-soft/rdiffweb/commit/26f0576ac31e5ef71a5ed94a031c28cb950ffcfe) by Patrik Dufresne).
- Merge branch 'patrik-fix-pipeline' into 'master' ([9dc38fb](https://gitlab.com/ikus-soft/rdiffweb/commit/9dc38fb02b54d38f8060c5e42d3266ba7cdf302b) by Patrik Dufresne).
- Merge branch 'patrik-delete-admin' into 'master' ([246bc24](https://gitlab.com/ikus-soft/rdiffweb/commit/246bc24952f6efeb7d170f4d7b9918fa042d4f2b) by Patrik Dufresne).
- Merge branch 'patrik-footer' into 'master' ([55a04d6](https://gitlab.com/ikus-soft/rdiffweb/commit/55a04d669a4a0fa7f6ab628a1ede5a63830921d2) by Patrik Dufresne).
- Merge branch 'patrik-user-roles' into 'master' ([dfcf451](https://gitlab.com/ikus-soft/rdiffweb/commit/dfcf45126bab5deb6db3e68e194d1afb1077acb7) by Patrik Dufresne).
- Merge branch 'patrik-fix-single-repo' into 'master' ([324426f](https://gitlab.com/ikus-soft/rdiffweb/commit/324426f06cc69489de12be0c804f8eb013604ba4) by Patrik Dufresne).
- Merge branch 'patrik-release-notes' into 'master' ([5b51155](https://gitlab.com/ikus-soft/rdiffweb/commit/5b511556f42a8548b5e6bd9b1434a242c2ccce58) by Patrik Dufresne).

### Misc

- Update french translation ([27da3e6](https://gitlab.com/ikus-soft/rdiffweb/commit/27da3e63487707c5755abc7226b3bd2bd5736716) by Patrik Dufresne).
- Block "Users" from deleting SSH Keys. #100 ([f50cccf](https://gitlab.com/ikus-soft/rdiffweb/commit/f50cccf832ea34dbadf9df59451023fa46017b64) by Patrik Dufresne).
- Call trigger to deploy rdiffweb ([2f99ac0](https://gitlab.com/ikus-soft/rdiffweb/commit/2f99ac0a616d2037e3d92804006649c9bb973a53) by Patrik Dufresne).
- Properly handle deletion of admin user #93 ([3494d51](https://gitlab.com/ikus-soft/rdiffweb/commit/3494d51cfca595017bbdae4e60064ebb436fbc04) by Patrik Dufresne).
- [SPONSORED] Add new user roles to fine tune permissions #104 ([2bef10a](https://gitlab.com/ikus-soft/rdiffweb/commit/2bef10a3361f9b96ce2d46eac10e19dd80ce2925) by Patrik Dufresne).
- Update change log with v1.3.2 ([5d86d0d](https://gitlab.com/ikus-soft/rdiffweb/commit/5d86d0d0fe09b4562d6aa53f22b3802e82fa459a) by Patrik Dufresne).

## [1.3.2](https://gitlab.com/ikus-soft/rdiffweb/tags/1.3.2) - 2020-04-23

<small>[Compare with 1.3.1](https://gitlab.com/ikus-soft/rdiffweb/compare/1.3.1...1.3.2)</small>

### Fixed

- Fix repo tree when path are conflicting ([a32c4ab](https://gitlab.com/ikus-soft/rdiffweb/commit/a32c4ab066f7d00e55c75df5fe9453e7a8953047) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-fix-repo-tree' into 'master' ([6901cb4](https://gitlab.com/ikus-soft/rdiffweb/commit/6901cb4d1ac38dcbc2f118dfd150b80f823d8686) by Patrik Dufresne).
- Merge branch 'patrik-fix-virtualenv' into 'master' ([ddf2217](https://gitlab.com/ikus-soft/rdiffweb/commit/ddf2217911bed5391c213027ddd7656ac1dcf789) by Patrik Dufresne).

### Misc

- Decode stderr from rdiffweb-restore subprocess ([64de4dd](https://gitlab.com/ikus-soft/rdiffweb/commit/64de4dd1aa69cbcfb7cd6b412faf5efe0c633696) by Patrik Dufresne).
- Handle special case when the repo doesn't has rdiff-backup-data ([bbbb821](https://gitlab.com/ikus-soft/rdiffweb/commit/bbbb821560efe8c0227cd126ece29a5996408d6a) by Patrik Dufresne).
- Lookup executable in virtualenv #92 ([b1be69b](https://gitlab.com/ikus-soft/rdiffweb/commit/b1be69bc12b557030d46a66acc43a765d31cbc0d) by Patrik Dufresne).
- Update Changelog for v1.3.0 and v1.3.1 ([9bed1ba](https://gitlab.com/ikus-soft/rdiffweb/commit/9bed1bac51a997261950e3c106a2d2dda98d7e1d) by Patrik Dufresne).

## [v3.5.2](https://gitlab.com/ikus-soft/rdiffweb/tags/v3.5.2) - 2020-04-12

<small>[Compare with v3.5.0](https://gitlab.com/ikus-soft/rdiffweb/compare/v3.5.0...v3.5.2)</small>

### Merged

- Merge branch 'develop/patrik/release' into 'master' ([0574a7d](https://gitlab.com/ikus-soft/rdiffweb/commit/0574a7d26df5bebb0ae0ba21caa198d8de745d0a) by Patrik Dufresne).

### Misc

- Bump to rdiffweb 1.3.1 ([293d644](https://gitlab.com/ikus-soft/rdiffweb/commit/293d6445e4df92d48bcb2cf73eb99bfe7d72316c) by Patrik Dufresne).

## [1.3.1](https://gitlab.com/ikus-soft/rdiffweb/tags/1.3.1) - 2020-04-10

<small>[Compare with 1.3.0](https://gitlab.com/ikus-soft/rdiffweb/compare/1.3.0...1.3.1)</small>

### Added

- Add change log entries for release v1.3.0 ([5cabeb4](https://gitlab.com/ikus-soft/rdiffweb/commit/5cabeb40861dcd5c358071113be8ff0cabb41520) by Patrik Dufresne).

### Merged

- Merge branch 'patrik-ssha-password' into 'master' ([02cac4f](https://gitlab.com/ikus-soft/rdiffweb/commit/02cac4f7e6192c123625df55e1b2c55b9b67c6f8) by Patrik Dufresne).
- Merge branch 'develop/patrik/prepare-release' into 'master' ([ccd31b1](https://gitlab.com/ikus-soft/rdiffweb/commit/ccd31b17f6d7b6726a5359aa0a988781a749ad89) by Patrik Dufresne).

### Misc

- Enforce password encryption by using SSHA scheme #88 ([8bb83e1](https://gitlab.com/ikus-soft/rdiffweb/commit/8bb83e120155efb97753e053e0a95292847e912a) by Patrik Dufresne).

## [v3.5.0](https://gitlab.com/ikus-soft/rdiffweb/tags/v3.5.0) - 2020-04-08

<small>[Compare with v3.4.3](https://gitlab.com/ikus-soft/rdiffweb/compare/v3.4.3...v3.5.0)</small>

### Added

- Add #DEBHELPER# to postinitscript ([c0ce9dc](https://gitlab.com/ikus-soft/rdiffweb/commit/c0ce9dcbda82aca6af4fa49218e03273dd69ad89) by Patrik Dufresne).

### Changed

- Change permissions recursively ([bf7a7fd](https://gitlab.com/ikus-soft/rdiffweb/commit/bf7a7fd6e8844c2d8c3aaca0eff6eb1899a4526e) by Patrik Dufresne).

### Merged

- Merge branch 'develop/patrik/release' into 'master' ([98dbaef](https://gitlab.com/ikus-soft/rdiffweb/commit/98dbaef3c147860ce52bdffc187565c10290ef8a) by Patrik Dufresne).
- Merge branch 'develop/patrik/makefile' into 'master' ([2c238bf](https://gitlab.com/ikus-soft/rdiffweb/commit/2c238bf2cf1d6f96eb4329f257c083b4470cea9f) by Patrik Dufresne).
- Merge branch 'develop/patrik/deb-build' into 'master' ([7023ce4](https://gitlab.com/ikus-soft/rdiffweb/commit/7023ce40797bdef5dccf4591e296622776a269af) by Patrik Dufresne).

### Misc

- Bump rdiffweb to v1.3.0 ([342de31](https://gitlab.com/ikus-soft/rdiffweb/commit/342de311a1d3437e695f366e90dafb89a157e150) by Patrik Dufresne).
- Create a Makefile for test & build ([1d97a38](https://gitlab.com/ikus-soft/rdiffweb/commit/1d97a386bad6cd27c18fc17011b2bf876871c778) by Patrik Dufresne).
- Test deb pacakge on buster ([7771349](https://gitlab.com/ikus-soft/rdiffweb/commit/777134996339c658b433d64365b6fb248e4bf8e7) by Patrik Dufresne).

## [1.3.0](https://gitlab.com/ikus-soft/rdiffweb/tags/1.3.0) - 2020-03-27

<small>[Compare with 1.2.2](https://gitlab.com/ikus-soft/rdiffweb/compare/1.2.2...1.3.0)</small>

### Fixed

- Fix to prevent duplicate repository in database #85 ([ad01729](https://gitlab.com/ikus-soft/rdiffweb/commit/ad017296c03e65647a57b7e061d71a8dd53c524c) by Patrik Dufresne).

### Removed

- Remove obsolete dependencies to pysqlite2 ([121411c](https://gitlab.com/ikus-soft/rdiffweb/commit/121411cd5bbfd7641afda09143301f228e1946e2) by Patrik Dufresne).

### Merged

- Merge branch 'develop/patrik/fix-duplicate-repos' into 'master' ([885b907](https://gitlab.com/ikus-soft/rdiffweb/commit/885b9077df150d3aae7d37209cf38927779e2520) by Patrik Dufresne).
- Merge branch 'develop/patrik/cicd' into 'master' ([da66138](https://gitlab.com/ikus-soft/rdiffweb/commit/da66138b195e017d919c8b9d526358a9b3ca8efc) by Patrik Dufresne).
- Merge branch 'develop/patrik/restore-stream' into 'master' ([4e10583](https://gitlab.com/ikus-soft/rdiffweb/commit/4e105837b38c1fc958389a40d4672fdd3152c6b9) by Patrik Dufresne).

### Misc

- Pre-build docker images for each target ([fc7bce7](https://gitlab.com/ikus-soft/rdiffweb/commit/fc7bce7bfdab90b5f058d15163b009f453441616) by Patrik Dufresne).
- Restore files and folder using a subprocess #72 #39 ([48e0fb2](https://gitlab.com/ikus-soft/rdiffweb/commit/48e0fb24ed8a3f10a0aca6720162e0bf449c15ba) by Patrik Dufresne).

## [v3.4.3](https://gitlab.com/ikus-soft/rdiffweb/tags/v3.4.3) - 2020-03-08

<small>[Compare with v3.4.2](https://gitlab.com/ikus-soft/rdiffweb/compare/v3.4.2...v3.4.3)</small>

### Merged

- Merge branch 'develop/patrik/release-3.4.3' into 'master' ([c8dae9a](https://gitlab.com/ikus-soft/rdiffweb/commit/c8dae9abb7b0d39219893d4fca02a866159bf104) by Patrik Dufresne).

### Misc

- Bump rdiffweb to v1.2.2 ([1e9a39a](https://gitlab.com/ikus-soft/rdiffweb/commit/1e9a39a64bbad745ae78822f206375adc5480b56) by Patrik Dufresne).

## [1.2.2](https://gitlab.com/ikus-soft/rdiffweb/tags/1.2.2) - 2020-03-05

<small>[Compare with 1.2.1](https://gitlab.com/ikus-soft/rdiffweb/compare/1.2.1...1.2.2)</small>

### Added

- Add CentOS 7 & 8 target ([3a5b892](https://gitlab.com/ikus-soft/rdiffweb/commit/3a5b8926d06223ad6e125ad0d5cfdf179cb13722) by Patrik Dufresne).
- Add installation step for CentOS and RedHat ([4462d6a](https://gitlab.com/ikus-soft/rdiffweb/commit/4462d6ab71a89a5b24b4b0e1bf15aa7dd0bd4b91) by Patrik Dufresne).
- Add reference to refresh when repo view is empty rdiffweb/#77 ([a3e91c0](https://gitlab.com/ikus-soft/rdiffweb/commit/a3e91c0acec7efb3bfc2a1592071e5854a4e7e56) by Patrik Dufresne).
- Add rdiff-backup2 from pypi ([f78ef7a](https://gitlab.com/ikus-soft/rdiffweb/commit/f78ef7adc32294ecadca4fd66d1ae100526d85cf) by Patrik Dufresne).

### Removed

- Remove some target from gitlab pipeline. ([a7b545e](https://gitlab.com/ikus-soft/rdiffweb/commit/a7b545e6a72bc5bc34e56bff70f8d5cba7c38fbb) by Patrik Dufresne).
- Remove use of LIMIT to stay compatible with CentOS7 ([07c6a75](https://gitlab.com/ikus-soft/rdiffweb/commit/07c6a7522dc9f7356971086aabe38367c0fba4e2) by Patrik Dufresne).

### Merged

- Merge branch 'develop/patrik/release-1.2.2' into 'master' ([d70bc53](https://gitlab.com/ikus-soft/rdiffweb/commit/d70bc539a558f2138ee8bf3c3d3432d4ad73e3d3) by Patrik Dufresne).
- Merge branch 'develop/patrik/centos7' into 'master' ([056514c](https://gitlab.com/ikus-soft/rdiffweb/commit/056514c009efec2594c61038399584f10d8ae157) by Patrik Dufresne).
- Merge branch 'develop/patrik/add-rdiff-backup2' into 'master' ([54af9f0](https://gitlab.com/ikus-soft/rdiffweb/commit/54af9f0e3112328e3f55764a3953b604a2c85a10) by Patrik Dufresne).
- Merge branch 'develop/patrik/cache-repo-status' into 'master' ([9b79984](https://gitlab.com/ikus-soft/rdiffweb/commit/9b79984c1baf7e4cea464c4a850b06857fcda6fc) by Patrik Dufresne).
- Merge branch 'develop/patrik/reduce-build' into 'master' ([c3a5996](https://gitlab.com/ikus-soft/rdiffweb/commit/c3a59962d529c72af61fa42dc062015fcedd2d2d) by Patrik Dufresne).
- Merge branch 'develop/patrik/fix-path' into 'master' ([78da790](https://gitlab.com/ikus-soft/rdiffweb/commit/78da79016d91ca792c1002e131fa3797c33258d7) by Patrik Dufresne).
- Merge branch 'develop/patrik/improve-ui-refresh' into 'master' ([237196b](https://gitlab.com/ikus-soft/rdiffweb/commit/237196b7b2bd739a9d52125ae1aba858becd5d83) by Patrik Dufresne).

### Misc

- Test with rdiff-backup pre-release ([7b92457](https://gitlab.com/ikus-soft/rdiffweb/commit/7b9245739210af36b8006216621eda74dbb7a9d2) by Patrik Dufresne).
- Use tar to extract archive (to avoid encoding issue) ([8fc51c3](https://gitlab.com/ikus-soft/rdiffweb/commit/8fc51c35e5c1dfffe4353e4197d1137c74095a91) by Patrik Dufresne).
- Release v1.2.2 ([118f49f](https://gitlab.com/ikus-soft/rdiffweb/commit/118f49f545f0ad9e7fd4851b2a58087b28449e5f) by Patrik Dufresne).
- Cache entries ([7a9bba6](https://gitlab.com/ikus-soft/rdiffweb/commit/7a9bba67087c6521a4bb2e4415c2dc648d0eac58) by Patrik Dufresne).
- Cache the repository status ([988662c](https://gitlab.com/ikus-soft/rdiffweb/commit/988662c8738ff5b10d3f37c80d5a45b0168f0166) by Patrik Dufresne).
- Use full path to call rdiff-backup executable #68 ([139af61](https://gitlab.com/ikus-soft/rdiffweb/commit/139af610fe80d8bf493f44625c3ba9ed905a1fa6) by Patrik Dufresne).
- Reduce the number of build ([041393f](https://gitlab.com/ikus-soft/rdiffweb/commit/041393f6a5f3341dbbc65563c2f53fd7172f015d) by Patrik Dufresne).

## [v3.4.2](https://gitlab.com/ikus-soft/rdiffweb/tags/v3.4.2) - 2020-02-09

<small>[Compare with v3.4.0](https://gitlab.com/ikus-soft/rdiffweb/compare/v3.4.0...v3.4.2)</small>

### Fixed

- Fix default permissions on folders #51 ([0e47632](https://gitlab.com/ikus-soft/rdiffweb/commit/0e47632c6c10e3e5a7044f0def9420a7f76ed653) by Patrik Dufresne).

### Merged

- Merge branch 'develop/patrik/release-3.4.1' into 'master' ([6d4367d](https://gitlab.com/ikus-soft/rdiffweb/commit/6d4367d8426e14b08c0457775a9f7a09652983c8) by Patrik Dufresne).
- Merge branch 'develop/patrik/fix-permissions' into 'master' ([2ae1c8f](https://gitlab.com/ikus-soft/rdiffweb/commit/2ae1c8ffd5cac49ec2aa71254fe31caef02ebea6) by Patrik Dufresne).

### Misc

- Prepare release v3.4.1 ([bb688e5](https://gitlab.com/ikus-soft/rdiffweb/commit/bb688e5b428d9f549c20ba36004de55be817f078) by Patrik Dufresne).

## [1.2.1](https://gitlab.com/ikus-soft/rdiffweb/tags/1.2.1) - 2020-02-08

<small>[Compare with 1.2.0](https://gitlab.com/ikus-soft/rdiffweb/compare/1.2.0...1.2.1)</small>

### Added

- Add cache for apt, pip and tox ([b3096ea](https://gitlab.com/ikus-soft/rdiffweb/commit/b3096eae5c9c33ea6a899b4c6031f6b0f5b39c71) by Patrik Dufresne).
- Add file rotation #75 ([f56b10f](https://gitlab.com/ikus-soft/rdiffweb/commit/f56b10f0eee577dc9a169deb9dfc26d7d1976b9b) by Patrik Dufresne).

### Fixed

- Fix access to other user repo #76 ([ad01c5d](https://gitlab.com/ikus-soft/rdiffweb/commit/ad01c5dd06cdee1b58f5a819f1fbdd855ad9b155) by Patrik Dufresne).
- Fix minarca plugins exception when creating admin user minarca/#47 ([d53d3f4](https://gitlab.com/ikus-soft/rdiffweb/commit/d53d3f497451e5e1c2cddb6c7a74c8ad4c39a411) by Patrik Dufresne).

### Merged

- Merge branch 'develop/patrik/log-rotating' into 'master' ([40d9462](https://gitlab.com/ikus-soft/rdiffweb/commit/40d9462594741a74214ea6b8d056a9f96a7e24a9) by Patrik Dufresne).
- Merge branch 'develop/patrik/cicd-cache' into 'master' ([3b1d04f](https://gitlab.com/ikus-soft/rdiffweb/commit/3b1d04fcda3b892ca54b7a2c39125bb88c49283f) by Patrik Dufresne).
- Merge branch 'develop/patrik/fix-admin-user-creation' into 'master' ([017b108](https://gitlab.com/ikus-soft/rdiffweb/commit/017b1086e9460ff95818edaf2db0d1eb5b8e2671) by Patrik Dufresne).
- Merge branch 'develop/patrik/fix-repo-access-for-admin' into 'master' ([599b3ef](https://gitlab.com/ikus-soft/rdiffweb/commit/599b3ef7bcb7223d0917d0e17e7e9b10bfa58e22) by Patrik Dufresne).

### Misc

- Update README for v1.2.1 ([d0ac1f6](https://gitlab.com/ikus-soft/rdiffweb/commit/d0ac1f6f421a417715471614ead5b479f8fa06c3) by Patrik Dufresne).

## [v3.4.0](https://gitlab.com/ikus-soft/rdiffweb/tags/v3.4.0) - 2020-01-30

<small>[Compare with v3.3.0](https://gitlab.com/ikus-soft/rdiffweb/compare/v3.3.0...v3.4.0)</small>

### Added

- Add port to EmailHost ([e445d47](https://gitlab.com/ikus-soft/rdiffweb/commit/e445d4710278b2167837042bd712d9243796ac50) by Patrik Dufresne).

### Merged

- Merge branch 'develop/patrik/bump-rdiffweb' into 'master' ([faefed5](https://gitlab.com/ikus-soft/rdiffweb/commit/faefed5b8e8f0b079c4232a00d3138cd27cd7de6) by Patrik Dufresne).
- Merge branch 'develop/patrik/fix-cicd-wine' into 'master' ([042327d](https://gitlab.com/ikus-soft/rdiffweb/commit/042327d7ef0cce4fea096ea73a5c294c68e44868) by Patrik Dufresne).
- Merge branch 'develop/patrik/fix-EmailHost' into 'master' ([92187e1](https://gitlab.com/ikus-soft/rdiffweb/commit/92187e144e15dec3465dc4b3393cc495368dfc58) by Patrik Dufresne).

### Misc

- Move all test script to /tests and add scripts to test Windows ([9710940](https://gitlab.com/ikus-soft/rdiffweb/commit/9710940f158961c7c27ffff7610e2fd5208b69c2) by Patrik Dufresne).
- Bump rdiffweb to 1.2.0 ([0110dc5](https://gitlab.com/ikus-soft/rdiffweb/commit/0110dc5ef61a96f08b223e7102f241d0e9cd9c2c) by Patrik Dufresne).

## [1.2.0](https://gitlab.com/ikus-soft/rdiffweb/tags/1.2.0) - 2020-01-30

<small>[Compare with 1.1.0](https://gitlab.com/ikus-soft/rdiffweb/compare/1.1.0...1.2.0)</small>

### Added

- Add explicit pipeline for buster and stretch ([1bc7b3c](https://gitlab.com/ikus-soft/rdiffweb/commit/1bc7b3c9f50c3e377353d8a92c275beca857d4f4) by Patrik Dufresne).

### Fixed

- Fix persistence for SQLite 3.16 ([2625f48](https://gitlab.com/ikus-soft/rdiffweb/commit/2625f48d62204eaa704db984641b4bec0cced168) by Patrik Dufresne).

### Merged

- Merge branch 'develop/patrik/release-1.2.0' into 'master' ([9e5ed79](https://gitlab.com/ikus-soft/rdiffweb/commit/9e5ed7937c1154749743b3cc0cad72651ff48165) by Patrik Dufresne).
- Merge branch 'develop/patrik/reffactor-db' into 'master' ([3c2e041](https://gitlab.com/ikus-soft/rdiffweb/commit/3c2e0413a32c4a662d54cb42af47d70190e7c280) by Patrik Dufresne).
- Merge branch 'develop/patrik/add-pipeline-buster' into 'master' ([1757fd8](https://gitlab.com/ikus-soft/rdiffweb/commit/1757fd86f94bf21862c07e2a4ea4f04f080b30c8) by Patrik Dufresne).
- Merge branch 'develop/patrik/pypi-proxy' into 'master' ([a712cde](https://gitlab.com/ikus-soft/rdiffweb/commit/a712cdea843fa363832d03656567caffd8ae7a0a) by Patrik Dufresne).
- Merge branch 'develop/patrik/update-doc' into 'master' ([7edced1](https://gitlab.com/ikus-soft/rdiffweb/commit/7edced1e2beaf33cc5950965fcbfd4427420069e) by Patrik Dufresne).

### Misc

- Update README for release 1.2.0 ([939e84b](https://gitlab.com/ikus-soft/rdiffweb/commit/939e84b23f25cc8bd7e20303910c15d640d5906e) by Patrik Dufresne).
- Reduce duplicate code in sqlite backend ([48c14f6](https://gitlab.com/ikus-soft/rdiffweb/commit/48c14f66e47234574b72b213ac60e2eb7c717d54) by Patrik Dufresne).
- Mose delete_user() into UserObject pdsl/rdiffweb#70 ([4607991](https://gitlab.com/ikus-soft/rdiffweb/commit/460799152b01105d512efdb664e0eac318f8fa73) by Patrik Dufresne).
- Move `set_password` into UserObject pdsl/rdiffweb#70 ([d0ac179](https://gitlab.com/ikus-soft/rdiffweb/commit/d0ac1792a2a6b52e5d0f9c7f3cd4fe26ee13dacb) by Patrik Dufresne).
- Huge modification to the persistence layer pdsl/rdiffweb#70 ([af063d5](https://gitlab.com/ikus-soft/rdiffweb/commit/af063d55e6e6fe413c5f5b6da1662877c1cbffb8) by Patrik Dufresne).
- Update Documentation ([ed1d729](https://gitlab.com/ikus-soft/rdiffweb/commit/ed1d729b67cc3de5c86d9ac79bd82cc2f722745c) by Patrik Dufresne).
- Define alternative pip index url to reduce network issues ([130fc3f](https://gitlab.com/ikus-soft/rdiffweb/commit/130fc3f03f53f62198e9ddac30b4411ff1e66cf0) by Patrik Dufresne).

## [v3.3.0](https://gitlab.com/ikus-soft/rdiffweb/tags/v3.3.0) - 2019-11-06

<small>[Compare with v3.0.1](https://gitlab.com/ikus-soft/rdiffweb/compare/v3.0.1...v3.3.0)</small>

### Added

- Add dependencies for `tail` command line pdsl/rdiffweb#5 ([2270a4e](https://gitlab.com/ikus-soft/rdiffweb/commit/2270a4e8fbee8f437a13477f5dd772fe4150b2fe) by Patrik Dufresne).

### Merged

- Merge branch 'develop/patrik/bump' into 'master' ([65c3ae2](https://gitlab.com/ikus-soft/rdiffweb/commit/65c3ae2e2338b111cbbe7067e6ccc8e40cd48184) by Patrik Dufresne).
- Merge branch 'develop/patrik/tes' into 'master' ([88e7348](https://gitlab.com/ikus-soft/rdiffweb/commit/88e73485bc56cbc929c09e2647e718853efc076e) by Patrik Dufresne).
- Merge branch 'develop/patrik/bump-rdiffweb-version' into 'master' ([c5dea03](https://gitlab.com/ikus-soft/rdiffweb/commit/c5dea032978f07a764a4372abfb76edbddfd5324) by Patrik Dufresne).
- Merge branch 'develo/patrik/headline' into 'master' ([4cfcd54](https://gitlab.com/ikus-soft/rdiffweb/commit/4cfcd54222505a01a5f8de0da5123bcd8ee0ff2c) by Patrik Dufresne).

### Misc

- Support backup over non default SSH port ([ef44ff3](https://gitlab.com/ikus-soft/rdiffweb/commit/ef44ff374256a40a6b8b1ecd2c37a881e7696f53) by Patrik Dufresne).
- Bump to rdiffweb to 1.0.4.dev50+gd85dd88 ([4ec5156](https://gitlab.com/ikus-soft/rdiffweb/commit/4ec5156b072dfc55a2fee8f0aa03ed17e113353c) by Patrik Dufresne).
- Bump to 1.0.4.dev50+g162651f ([c27dd30](https://gitlab.com/ikus-soft/rdiffweb/commit/c27dd308040acebd45085fa59cb8386785e90f8a) by Patrik Dufresne).
- Bump to 1.0.4.dev48+g774d120 ([54941f9](https://gitlab.com/ikus-soft/rdiffweb/commit/54941f93d80ff7ac96eac7575a3fcfb0356f13a3) by Patrik Dufresne).
- Update setup.py 1.0.4.dev47+g0770b7f ([43243b4](https://gitlab.com/ikus-soft/rdiffweb/commit/43243b45716ca20529efcbbe14b7239fede5c809) by Patrik Dufresne).
- Bump to 1.0.4.dev45+ga56c816 ([5b4addb](https://gitlab.com/ikus-soft/rdiffweb/commit/5b4addb54b81751df0cf668e23263676dbd51caa) by Patrik Dufresne).
- Provide default minarca headline pdsl/share#25 ([5e8ec69](https://gitlab.com/ikus-soft/rdiffweb/commit/5e8ec69a778b322e3f9ebb76bc6c13c8245026c2) by Patrik Dufresne).
- Download only if file doesn't exists ([0892629](https://gitlab.com/ikus-soft/rdiffweb/commit/0892629de6f11ebb4e15f6cca99e8b1c17799076) by Patrik Dufresne).

## [1.1.0](https://gitlab.com/ikus-soft/rdiffweb/tags/1.1.0) - 2019-10-31

<small>[Compare with 1.0.3](https://gitlab.com/ikus-soft/rdiffweb/compare/1.0.3...1.1.0)</small>

### Added

- Add test to update notifications ([21dd20f](https://gitlab.com/ikus-soft/rdiffweb/commit/21dd20f567c00b5fcfc0442cc95acb9c946725c8) by Patrik Dufresne).
- Add test to query users with invalid criteria ([84e3a7a](https://gitlab.com/ikus-soft/rdiffweb/commit/84e3a7acd267464f1c40c6fb5d1acd8385501093) by Patrik Dufresne).
- Add test to set repository max age ([2293ed5](https://gitlab.com/ikus-soft/rdiffweb/commit/2293ed5e0820074837a7cd1362fb511a12450a51) by Patrik Dufresne).
- Add more test to validate access to invalid repository ([4036775](https://gitlab.com/ikus-soft/rdiffweb/commit/4036775177e74c516616e5151258da7195463f2b) by Patrik Dufresne).
- Add rdiffweb & plugins version to sysinfo pdsl/rdiffweb#51 ([653b22a](https://gitlab.com/ikus-soft/rdiffweb/commit/653b22ad65ec3a8a4a7e249c23cd1305e9ae92e6) by Patrik Dufresne).
- Add repository view in Admin Area pdsl/rdiffweb#40 ([573785d](https://gitlab.com/ikus-soft/rdiffweb/commit/573785de3deac21cd39263faf935ec41cc6e35f2) by Patrik Dufresne).
- Add jinja2 version into tox matrix ([21e35f4](https://gitlab.com/ikus-soft/rdiffweb/commit/21e35f43fb10879bcf068874edd53478498782fe) by Patrik Dufresne).
- Add System Info view in Admin Area pdsl/rdiffweb#6 pdsl/rdiffweb#59 ([684efa3](https://gitlab.com/ikus-soft/rdiffweb/commit/684efa3c81d2da24d2b046fbf3135e00252cb20f) by Patrik Dufresne).

### Fixed

- Fix deletion of repo when repo_path starts with "/" pdsl/rdiffweb#66 ([d85dd88](https://gitlab.com/ikus-soft/rdiffweb/commit/d85dd88e597425a93e70adb98996048a7a50794e) by Patrik Dufresne).
- Fix issue with status page errors ([f8def69](https://gitlab.com/ikus-soft/rdiffweb/commit/f8def691ec1ed429e3bb81809ab0266ce83389d0) by Patrik Dufresne).
- Fix google font import css ([c0ad318](https://gitlab.com/ikus-soft/rdiffweb/commit/c0ad3181ce0e19a074412685c0f5bc25904cbf8d) by Patrik Dufresne).
- Fix database persistence with repository name starting with a / ([5ff27fc](https://gitlab.com/ikus-soft/rdiffweb/commit/5ff27fcefa387e12a29dda80a5924c8ff9147602) by Patrik Dufresne).
- Fix issue with capital case encoding name ([a56c816](https://gitlab.com/ikus-soft/rdiffweb/commit/a56c816a15497500dd2570d2c0eaf90c2fc7bdfb) by Patrik Dufresne).
- Fix compilation of .less files ([a46b695](https://gitlab.com/ikus-soft/rdiffweb/commit/a46b6953619f4152b026cf8ec484401879ff3a6d) by Patrik Dufresne).
- Fix for admin logs ([6d5a9a2](https://gitlab.com/ikus-soft/rdiffweb/commit/6d5a9a29652fbc50fa38402eb6130403a0d66889) by Patrik Dufresne).
- Fix code smells ([bf611af](https://gitlab.com/ikus-soft/rdiffweb/commit/bf611afeb474e531c29ddb2bfcc96eb9714489a5) by Patrik Dufresne).

### Removed

- Remove unused rdw_templating.add_templatesdir & get_template functions ([50b3b97](https://gitlab.com/ikus-soft/rdiffweb/commit/50b3b976fea2f8d00f90637a6a03fafae86d7521) by Patrik Dufresne).
- Remove obsolete try catch from page_settings._remove_older() ([098debc](https://gitlab.com/ikus-soft/rdiffweb/commit/098debc99c42e2f938dae1e8100ad79eda510a53) by Patrik Dufresne).
- Remove unused RepoObject.__repr__() function ([6a74b45](https://gitlab.com/ikus-soft/rdiffweb/commit/6a74b4551d4da7157c9a5f8bae56c46d8b4f0e91) by Patrik Dufresne).
- Remove useless condition from `split_path` ([14494d8](https://gitlab.com/ikus-soft/rdiffweb/commit/14494d82b4651c727997dc2857f37b88f73667f8) by Patrik Dufresne).
- Remove obsolete `admin_repo_edit` entry point ([562a83d](https://gitlab.com/ikus-soft/rdiffweb/commit/562a83d4d11701a557e07c388927357f752817f9) by Patrik Dufresne).

### Merged

- Merge branch 'develop/patrik/bug-fixes' into 'master' ([570becb](https://gitlab.com/ikus-soft/rdiffweb/commit/570becbdc25271f6a952952faff0e17c54e84111) by Patrik Dufresne).
- Merge branch 'develop/patrik/improve-coverage' into 'master' ([466bc98](https://gitlab.com/ikus-soft/rdiffweb/commit/466bc989cece5b93b5e85e3f67ddc1508c308812) by Patrik Dufresne).
- Merge branch 'develop/patrik/admin-repos' into 'master' ([817e7fe](https://gitlab.com/ikus-soft/rdiffweb/commit/817e7fe984e00cf5216ccad83412dafebb043b67) by Patrik Dufresne).
- Merge branch 'develop/patrik/more-sysinfo' into 'master' ([abc1cb9](https://gitlab.com/ikus-soft/rdiffweb/commit/abc1cb97950c929eb8a4fff6c290cab3c69090f6) by Patrik Dufresne).
- Merge branch 'develop/patrik/repo-url' into 'master' ([640cb49](https://gitlab.com/ikus-soft/rdiffweb/commit/640cb49c37d97507fe6c848348794d8825ec9ce9) by Patrik Dufresne).
- Merge branch 'develop/patrik/admin-users' into 'master' ([3b2ea9e](https://gitlab.com/ikus-soft/rdiffweb/commit/3b2ea9ec4d403e0587b48a57e96235b320c9aedc) by Patrik Dufresne).
- Merge branch 'develop/patrik/confirm' into 'master' ([5e7fac1](https://gitlab.com/ikus-soft/rdiffweb/commit/5e7fac1e525327f8d295c4ce0da10758745ad68b) by Patrik Dufresne).
- Merge branch 'develop/patrik/admin-sysinfo' into 'master' ([fc829c6](https://gitlab.com/ikus-soft/rdiffweb/commit/fc829c6c105fa68869a94d3e8b203bd3ecef3f56) by Patrik Dufresne).
- Merge branch 'develop/patrik/reffactoring' into 'master' ([29fecf3](https://gitlab.com/ikus-soft/rdiffweb/commit/29fecf300a80fdf85c8265b1303c2f0436a32ede) by Patrik Dufresne).
- Merge branch 'develop/patrik/show-logs' into 'master' ([03bf891](https://gitlab.com/ikus-soft/rdiffweb/commit/03bf891fd32c8bb3fac7ea3cb981eb154d1e98cc) by Patrik Dufresne).
- Merge branch 'develop/patrik/upgrade-jinja2' into 'master' ([2e8b946](https://gitlab.com/ikus-soft/rdiffweb/commit/2e8b9467ee06825e8809e310d78540343c74641e) by Patrik Dufresne).
- Merge branch 'develop/patrik/cache' into 'master' ([622d69c](https://gitlab.com/ikus-soft/rdiffweb/commit/622d69c9206a2f6f89f66843c7f762835fa9257a) by Patrik Dufresne).
- Merge branch 'develop/patrik/improve-admin-tool' into 'master' ([590919d](https://gitlab.com/ikus-soft/rdiffweb/commit/590919de7e1fa2930467b9d141583b56cec79d94) by Patrik Dufresne).
- Merge branch 'develop/patrik/update-doc' into 'master' ([d3ec752](https://gitlab.com/ikus-soft/rdiffweb/commit/d3ec752c55464637578847be5d12954ae9b624db) by Patrik Dufresne).

### Misc

- Update changelog ([e02d468](https://gitlab.com/ikus-soft/rdiffweb/commit/e02d468a5dfbe5fe6bf8db0dd6062b37dc9087b1) by Patrik Dufresne).
- Check if /admin/ is redirect to login page ([0d24244](https://gitlab.com/ikus-soft/rdiffweb/commit/0d24244d5dc175c4de8953b6bc0553bd1b0ad726) by Patrik Dufresne).
- Rename some test modules ([0a88f66](https://gitlab.com/ikus-soft/rdiffweb/commit/0a88f666ffd2fbe475ce5b1a04c80a2012d5b90e) by Patrik Dufresne).
- Check access to invalid log file ([26a875a](https://gitlab.com/ikus-soft/rdiffweb/commit/26a875a67c170abc6c04f83fb9bf2672e571a151) by Patrik Dufresne).
- Define repository URL as <username>/repopath ([15c6576](https://gitlab.com/ikus-soft/rdiffweb/commit/15c657617d3bce9130279f897e0ef779ff08f1fc) by Patrik Dufresne).
- Use cherrypy tools to check permissions ([78ed352](https://gitlab.com/ikus-soft/rdiffweb/commit/78ed352b51deba050d5172abc5bddc50b453e93d) by Patrik Dufresne).
- Enhance admin user view search bar ([e46fb19](https://gitlab.com/ikus-soft/rdiffweb/commit/e46fb19cdc45ac55611a41d8efb17b65581550b6) by Patrik Dufresne).
- Check local database login before LDAP ([1b7f784](https://gitlab.com/ikus-soft/rdiffweb/commit/1b7f784feeba229dd166a5fd0bf4d1b33484b206) by Patrik Dufresne).
- Reorganize the confirm modals ([25424e3](https://gitlab.com/ikus-soft/rdiffweb/commit/25424e3be5c11d96bf2faa2e085cc75216b1091f) by Patrik Dufresne).
- Reorganising macros ([69977a9](https://gitlab.com/ikus-soft/rdiffweb/commit/69977a9ff1d88f5e6afe3ec917e3f8c205d1b4c2) by Patrik Dufresne).
- Show logs in Admin View pdsl/rdiffweb#5 ([c58c171](https://gitlab.com/ikus-soft/rdiffweb/commit/c58c171d5e8ecb8f8e05da5fa8ba6c1461c5f5f9) by Patrik Dufresne).
- Define pip cache ([42e2ca0](https://gitlab.com/ikus-soft/rdiffweb/commit/42e2ca06f8ac5036fa56c9cd6656f240ab476c42) by Patrik Dufresne).
- Bump jinja2 version pdsl/rdiffweb#61 ([7442cea](https://gitlab.com/ikus-soft/rdiffweb/commit/7442cea320e5f134bd9d14e65cbafb8372a5eab7) by Patrik Dufresne).
- Improve the login page headline pdsl/share#25 ([0ccca7c](https://gitlab.com/ikus-soft/rdiffweb/commit/0ccca7c8a7dcbebd3487073a3bd1a95ab783295d) by Patrik Dufresne).
- Improve menu structure pdsl/rdiffweb#52 ([599ce29](https://gitlab.com/ikus-soft/rdiffweb/commit/599ce2916b535183f91e3ee5f4608311516cb147) by Patrik Dufresne).
- Update change log with release date ([a1fea23](https://gitlab.com/ikus-soft/rdiffweb/commit/a1fea23e11abfb4da5411340152d47408b9c5e57) by Patrik Dufresne).
- Update doc from pdsl website ([4912ff3](https://gitlab.com/ikus-soft/rdiffweb/commit/4912ff3c323da01666bf08d1f9b7856288be11b7) by Patrik Dufresne).

## [v3.0.1](https://gitlab.com/ikus-soft/rdiffweb/tags/v3.0.1) - 2019-10-04

<small>[Compare with v3.0.0](https://gitlab.com/ikus-soft/rdiffweb/compare/v3.0.0...v3.0.1)</small>

### Added

- Add integration test to link client to server ([76092b9](https://gitlab.com/ikus-soft/rdiffweb/commit/76092b935b0eae80e6d63946f931ece08ee42fb1) by Patrik Dufresne).

### Fixed

- Fix minarca-shell to support quota management ([e094b0d](https://gitlab.com/ikus-soft/rdiffweb/commit/e094b0d1ad9be1e4e50d6c955bb5052b3c82703d) by Patrik Dufresne).
- Fix user exists verification for sudo ([6e3490d](https://gitlab.com/ikus-soft/rdiffweb/commit/6e3490d4e07039d7db3ab8938e0eda27a2add76f) by Patrik Dufresne).
- Fix repository validation ([5fd33af](https://gitlab.com/ikus-soft/rdiffweb/commit/5fd33afef76407af506c4eed995d08d7bf0286d6) by Patrik Dufresne).

### Changed

- Change user's home permissions ([7ad3262](https://gitlab.com/ikus-soft/rdiffweb/commit/7ad3262803d870eb1bf95f2ae1f99c4024d889ca) by Patrik Dufresne).

### Merged

- Merge branch 'develop/patrik/bump-version' into 'master' ([d2f984a](https://gitlab.com/ikus-soft/rdiffweb/commit/d2f984aa2d19657e6b4709bad20e815e297b7c22) by Patrik Dufresne).
- Merge branch 'develop/patrik/fix-quota-management' into 'master' ([82e5f9b](https://gitlab.com/ikus-soft/rdiffweb/commit/82e5f9b25858f8e98ad5e4bb21188d0197678b3e) by Patrik Dufresne).
- Merge branch 'develop/patrik/extra-fix' into 'master' ([45a9658](https://gitlab.com/ikus-soft/rdiffweb/commit/45a9658cc077d977b45486735ea1c05167dbc273) by Patrik Dufresne).

### Misc

- Bump rdiffweb to v1.0.3 ([4515f1a](https://gitlab.com/ikus-soft/rdiffweb/commit/4515f1a0e455ba165f389e3e9ebc14eaf602f6c7) by Patrik Dufresne).
- Update the authorized_keys when user's home directory get updated ([616857e](https://gitlab.com/ikus-soft/rdiffweb/commit/616857ecd7d9988ffc8f3b96356d486aa59a48ec) by Patrik Dufresne).
- Bump rdiffweb version to v1.0.2 ([930f120](https://gitlab.com/ikus-soft/rdiffweb/commit/930f120c8186f35e5b6a70af9d6a944c6130d9ae) by Patrik Dufresne).

## [1.0.3](https://gitlab.com/ikus-soft/rdiffweb/tags/1.0.3) - 2019-10-04

<small>[Compare with 1.0.2](https://gitlab.com/ikus-soft/rdiffweb/compare/1.0.2...1.0.3)</small>

### Merged

- Merge branch 'develop/patrik/remove-auto-update' into 'master' ([e0389da](https://gitlab.com/ikus-soft/rdiffweb/commit/e0389da671239fdb4fd70cda9989b65d1e34d3f4) by Patrik Dufresne).

### Misc

- Removing the auto update repos ([bfecba1](https://gitlab.com/ikus-soft/rdiffweb/commit/bfecba17fc4eaef739fd781c5c8b34b079106529) by Patrik Dufresne).

## [1.0.2](https://gitlab.com/ikus-soft/rdiffweb/tags/1.0.2) - 2019-10-01

<small>[Compare with 1.0.1](https://gitlab.com/ikus-soft/rdiffweb/compare/1.0.1...1.0.2)</small>

### Merged

- Merge branch 'develop/patrik/fix-admin-user-creation' into 'master' ([f6056f6](https://gitlab.com/ikus-soft/rdiffweb/commit/f6056f64f95e276779a24db48963d4afa5183889) by Patrik Dufresne).

### Misc

- Update change logs ([a55a383](https://gitlab.com/ikus-soft/rdiffweb/commit/a55a383105ddcfc067304de2dba347cfbc6ae44d) by Patrik Dufresne).
- Update french translation ([f7cef74](https://gitlab.com/ikus-soft/rdiffweb/commit/f7cef7473646b0625ca16dd35ac0b89244e8db19) by Patrik Dufresne).
- Update translation documentation ([a59129e](https://gitlab.com/ikus-soft/rdiffweb/commit/a59129e539eb9fddc8f0db53f467748e3d277b86) by Patrik Dufresne).
- Create admin user if missing ([7a5f67e](https://gitlab.com/ikus-soft/rdiffweb/commit/7a5f67e48e69b00f34d9a1e8b430768a5bcbffd8) by Patrik Dufresne).
- Update README ([47eb075](https://gitlab.com/ikus-soft/rdiffweb/commit/47eb07515bf71d4824df5dbc3d6b3432ce097d74) by Patrik Dufresne).

## [1.0.1](https://gitlab.com/ikus-soft/rdiffweb/tags/1.0.1) - 2019-09-22

<small>[Compare with 1.0.0](https://gitlab.com/ikus-soft/rdiffweb/compare/1.0.0...1.0.1)</small>

### Added

- Add python-dev and build-essential to installation step ([85cfaeb](https://gitlab.com/ikus-soft/rdiffweb/commit/85cfaeb7a08a6227064034f4f56e1806621744e3) by Patrik Dufresne).

### Fixed

- Fix ssh duplicate key pdsl/rdiffweb#57 ([2ce7fb7](https://gitlab.com/ikus-soft/rdiffweb/commit/2ce7fb74e19d1e798ffd9574fa11f998c894c79f) by Patrik Dufresne).
- Fix removal of SSH Key pdsl/rdiffweb#58 ([d6a6ab1](https://gitlab.com/ikus-soft/rdiffweb/commit/d6a6ab1e4ecfd39a8fb2cd288b2a749716704a80) by Patrik Dufresne).

### Merged

- Merge branch 'develop/patrik/fix-ssh-key' into 'master' ([5c464b9](https://gitlab.com/ikus-soft/rdiffweb/commit/5c464b9c8d2d37e8c947c4559976b73bfb60952d) by Patrik Dufresne).

### Misc

- Keep only installation step from pypi ([9491503](https://gitlab.com/ikus-soft/rdiffweb/commit/9491503f7bd80b1b6289ceccb8e349c96a5716db) by Patrik Dufresne).
- Update README link to canonical link ([d95f71c](https://gitlab.com/ikus-soft/rdiffweb/commit/d95f71c014e1ee7bdc4dbedc5416520c0265cbf3) by Patrik Dufresne).

## [v3.0.0](https://gitlab.com/ikus-soft/rdiffweb/tags/v3.0.0) - 2019-09-14

<small>[Compare with first commit](https://gitlab.com/ikus-soft/rdiffweb/compare/e025e8db48e813ab8b8ee842e1b83690999f478d...v3.0.0)</small>

### Added

- Add support for backupninja ([34f4e96](https://gitlab.com/ikus-soft/rdiffweb/commit/34f4e96e16d6cedb3ce7b30bbca643549e144a32) by Patrik Dufresne).
- Add notice about SUDO_OWNERSHIP ([ef062a6](https://gitlab.com/ikus-soft/rdiffweb/commit/ef062a6a1b86049a8a32fa37da62c64da36d09ee) by Patrik Dufresne).
- Add sudo rules for minarca-shell ([4bc0479](https://gitlab.com/ikus-soft/rdiffweb/commit/4bc047976e990a100fd5e8970b3051403e483440) by Patrik Dufresne).
- Add log when updating the authorized_keys file ([5d0c65b](https://gitlab.com/ikus-soft/rdiffweb/commit/5d0c65b328597458d65226f745a1bd21eee5786f) by Patrik Dufresne).
- Add AGPL license ([e411cc5](https://gitlab.com/ikus-soft/rdiffweb/commit/e411cc5be4808a571d82d0abfe883a9a30a7ebd7) by Patrik Dufresne).
- Add /api/minarca to return remotehost & identity ([4fa5a69](https://gitlab.com/ikus-soft/rdiffweb/commit/4fa5a6950317f6c6d33c55c50aa572cf455c5f1d) by Patrik Dufresne).

### Fixed

- Fix Typo in minarca-shell ([49b74e6](https://gitlab.com/ikus-soft/rdiffweb/commit/49b74e6742de364ef05296c3bf597b4b8e555105) by Patrik Dufresne).
- Fix quota api bytes vs str ([06a6335](https://gitlab.com/ikus-soft/rdiffweb/commit/06a633593c502f129bfdaa2ec71e07608d93204c) by Patrik Dufresne).
- Fix user creation - bump to 1.0.0a5.dev10+gf359d1b ([189249e](https://gitlab.com/ikus-soft/rdiffweb/commit/189249e3d718277733477dbc4107d3d440bbb557) by Patrik Dufresne).

### Removed

- Remove user's ssh key when user get deleted pdsl/minarca-server#13 ([599508e](https://gitlab.com/ikus-soft/rdiffweb/commit/599508e2d4f408a13e996c45af0a478a41ee1153) by Patrik Dufresne).

### Merged

- Merge branch 'develop/patrik/fix-backupninja' into 'master' ([b98ece9](https://gitlab.com/ikus-soft/rdiffweb/commit/b98ece942de4d3310fb537193459085e4df1a73c) by Patrik Dufresne).
- Merge branch 'develop/patrik/fix-sudo' into 'master' ([ae907e2](https://gitlab.com/ikus-soft/rdiffweb/commit/ae907e260cbc49d6a06dee6d50395184a14f60cc) by Patrik Dufresne).

### Misc

- Move all files under /data ([6876da9](https://gitlab.com/ikus-soft/rdiffweb/commit/6876da939561d1ac7ca3f35dffc1075aa575a68c) by Patrik Dufresne).
- Move default storages to /backups/ ([6fd0032](https://gitlab.com/ikus-soft/rdiffweb/commit/6fd0032fc915f575554aabd89c10190f4d0e01d5) by Patrik Dufresne).
- Support reverse proxy pdsl/minarca-server#12 ([b7c21a5](https://gitlab.com/ikus-soft/rdiffweb/commit/b7c21a59103f1d490a087d7b823d7cedc7062f33) by Patrik Dufresne).
- Improve error handling when adding a new user ([640d9fb](https://gitlab.com/ikus-soft/rdiffweb/commit/640d9fb9d9109f40c65fe659887258f65b48c0e6) by Patrik Dufresne).
- Support bytes or unicode for mail attributes pdsl/minarca-server#11 ([bd2452e](https://gitlab.com/ikus-soft/rdiffweb/commit/bd2452e91f83583ee5845daf227ab6c8cc670d53) by Patrik Dufresne).
- Update disk usage testcases ([4f2dabe](https://gitlab.com/ikus-soft/rdiffweb/commit/4f2dabe97c120ba4fd5df36a61fafe64fd86f502) by Patrik Dufresne).
- Bump to 1.0.0a5.dev14+g1903616 ([7648e4b](https://gitlab.com/ikus-soft/rdiffweb/commit/7648e4b526c6f4a87a4d038a3c21af5d4f3d701c) by Patrik Dufresne).
- Rename webserver.log to server.log ([6bb2cb1](https://gitlab.com/ikus-soft/rdiffweb/commit/6bb2cb1902da4ca8a284defa592958c678b8c0b0) by Patrik Dufresne).
- Bump rdiffweb to 1.0.0a5.dev8+gdd5ed94 ([3f82b2f](https://gitlab.com/ikus-soft/rdiffweb/commit/3f82b2fb719f808519f0ebac7d6be873a5d4f823) by Patrik Dufresne).
- Allow minarca-shell to be configured ([a3287d0](https://gitlab.com/ikus-soft/rdiffweb/commit/a3287d09ab25cc8d26562a07cb1fd109c5da82ea) by Patrik Dufresne).
- Update minarca icon ([8e15e09](https://gitlab.com/ikus-soft/rdiffweb/commit/8e15e094bbad98ba0877b7c8f2b7f6bab4a0917f) by Patrik Dufresne).
- Enforce restart after upgrade ([f0e2a7f](https://gitlab.com/ikus-soft/rdiffweb/commit/f0e2a7ffe6d9e1b531a56780d069f63f258708df) by Patrik Dufresne).
- Bump rdiffweb version ([91b2c4b](https://gitlab.com/ikus-soft/rdiffweb/commit/91b2c4b2fb69cb4ef7f18f3eb3601f8f4fe33d13) by Patrik Dufresne).
- Provide minarca-shell script ([e0612d3](https://gitlab.com/ikus-soft/rdiffweb/commit/e0612d3346ec536ff240bca9f2713156066a094f) by Patrik Dufresne).
- Manage SSH keys ([1751cc9](https://gitlab.com/ikus-soft/rdiffweb/commit/1751cc9b22d999aafec985f7ca2e7f1eaa544d46) by Patrik Dufresne).
- TASK-1079 Create deb packages ([e025e8d](https://gitlab.com/ikus-soft/rdiffweb/commit/e025e8db48e813ab8b8ee842e1b83690999f478d) by Patrik Dufresne).

## [1.0.0](https://gitlab.com/ikus-soft/rdiffweb/tags/1.0.0) - 2019-09-11

<small>[Compare with 0.10.9](https://gitlab.com/ikus-soft/rdiffweb/compare/0.10.9...1.0.0)</small>

### Added

- Add mailing list to README ([dd5ed94](https://gitlab.com/ikus-soft/rdiffweb/commit/dd5ed941279bbb07cf7c1bc945853c53d114deeb) by Patrik Dufresne).
- Add error handler on repository delete ([66c0c74](https://gitlab.com/ikus-soft/rdiffweb/commit/66c0c740dba71e4ed9a0f1779626bc2713252392) by Patrik Dufresne).
- Add test for default theme ([6d32b61](https://gitlab.com/ikus-soft/rdiffweb/commit/6d32b6161cb42c208822fbca9848e388d8705cbb) by Patrik Dufresne).
- Add Build status badges ([5cb666d](https://gitlab.com/ikus-soft/rdiffweb/commit/5cb666d00b3038064c096313803276df827970b5) by Patrik Dufresne).
- Add new api to return list of repos. ([641a1cb](https://gitlab.com/ikus-soft/rdiffweb/commit/641a1cb6b91a28fdf4dd076b63381542a19dbe4b) by Patrik Dufresne).
- Add branche name for sonar analysis ([f2e51ef](https://gitlab.com/ikus-soft/rdiffweb/commit/f2e51ef20cf92ecb90f031a38e688d9da0525387) by Patrik Dufresne).
- Add missing "python-ldap" dependencies ([08c4581](https://gitlab.com/ikus-soft/rdiffweb/commit/08c4581b4b25f76867f2ecf05972bb00fc4c8ff7) by Patrik Dufresne).
- Add support for custom theme ([0fade69](https://gitlab.com/ikus-soft/rdiffweb/commit/0fade690e01a2620c627a39c6e0595964b8e85ea) by Patrik Dufresne).
- Add test for set_password() with empty value ([5b96da3](https://gitlab.com/ikus-soft/rdiffweb/commit/5b96da3615dc41c5cbdfa7780ad2e8ae2d1f2ab8) by Patrik Dufresne).
- Add sonar runner ([ca66dae](https://gitlab.com/ikus-soft/rdiffweb/commit/ca66daeb38b3b3722c853e4d3eb044c51434031d) by Patrik Dufresne).
- Add wsgi entry point ([8ca21df](https://gitlab.com/ikus-soft/rdiffweb/commit/8ca21df893efc74b7705abc51bc580a8dec761a7) by Patrik Dufresne).

### Fixed

- Fix page status ([001114c](https://gitlab.com/ikus-soft/rdiffweb/commit/001114c492b2313ebf757645c7c7c29fc334ea9b) by Patrik Dufresne).
- Fix publish & package pipeline ([1a2abba](https://gitlab.com/ikus-soft/rdiffweb/commit/1a2abba1110b31dd1517a7afcdf8a83c52d6e2e4) by Patrik Dufresne).
- Fix pipeline publish step ([5729ef3](https://gitlab.com/ikus-soft/rdiffweb/commit/5729ef3128957bac92da193037b9e33859956f3d) by Patrik Dufresne).
- Fix a performance issue with huge repositories ([76a6ec3](https://gitlab.com/ikus-soft/rdiffweb/commit/76a6ec31379ecb99ff6065124501efe159c24918) by Patrik Dufresne).
- Fix build dependencies for py27 ([397570c](https://gitlab.com/ikus-soft/rdiffweb/commit/397570cc06418c0128660023f6fc4cd8ef1491d5) by Patrik Dufresne).
- Fix HTTP 401 vs 403 ([8035e40](https://gitlab.com/ikus-soft/rdiffweb/commit/8035e40ca43071f398c90c002a183b44519e330e) by Patrik Dufresne).
- Fix bug introduce by upgrade to Jinja2 + python3 ([6d45c2b](https://gitlab.com/ikus-soft/rdiffweb/commit/6d45c2b9e94d48eb76a9ebf84dc0d2f286e2af24) by Patrik Dufresne).
- Fix IUserQuota execution ([8199e1e](https://gitlab.com/ikus-soft/rdiffweb/commit/8199e1ea0d50d773bcbc4538bbfc00e2174256e0) by Patrik Dufresne).
- Fix handling of serverhost option encoding ([69a776c](https://gitlab.com/ikus-soft/rdiffweb/commit/69a776c6fc68799ea9c006fe26d829ad5c24ffcc) by Patrik Dufresne).
- Fixes around user & ldap auth ([ae44bb8](https://gitlab.com/ikus-soft/rdiffweb/commit/ae44bb80f51c9994a2aaa18db4e7e52fd25c13db) by Patrik Dufresne).
- Fix notification plugin ([890a816](https://gitlab.com/ikus-soft/rdiffweb/commit/890a816c10359045634a326b75238abf6f8f202a) by Patrik Dufresne).
- Fix warning for MANIFEST.in ([f9f4630](https://gitlab.com/ikus-soft/rdiffweb/commit/f9f463024760cf58bfe19e0402173562b367e536) by Patrik Dufresne).

### Changed

- Change SSH Keys persistence and uniqueness ([d653038](https://gitlab.com/ikus-soft/rdiffweb/commit/d65303874f6a8a2ecba2392827b51d2dc4689544) by Patrik Dufresne).

### Removed

- Remove prod deployment from pipeline ([272e481](https://gitlab.com/ikus-soft/rdiffweb/commit/272e4814e51b6f311d4153383cbc8d94d14986a0) by Patrik Dufresne).
- Remove profiling ([6402e46](https://gitlab.com/ikus-soft/rdiffweb/commit/6402e468d72e22b65956a5adb0b78f777d3657e6) by Patrik Dufresne).
- Remove obsolete plugins code ([f8923d8](https://gitlab.com/ikus-soft/rdiffweb/commit/f8923d8f4ea1fee40a82b761f15c3521200b4b0b) by Patrik Dufresne).
- Remove reference to `rssLink` ([1124d80](https://gitlab.com/ikus-soft/rdiffweb/commit/1124d806f632d32cbda105ccfbadc3fb53d80aba) by Patrik Dufresne).
- Remove reference to `extra_head_templates` ([f5b00d0](https://gitlab.com/ikus-soft/rdiffweb/commit/f5b00d0ef88eab036e724ca0d11522bdf24fb450) by Patrik Dufresne).
- Remove remaining plugins ([d727adc](https://gitlab.com/ikus-soft/rdiffweb/commit/d727adc83a965a3c58240b8486405d0241c566e5) by Patrik Dufresne).
- Remove ldap_auth plugin ([448b989](https://gitlab.com/ikus-soft/rdiffweb/commit/448b9895973b8e8beb5421afc98cd5bc0127db83) by Patrik Dufresne).
- Remove db_sqlite ([615cc10](https://gitlab.com/ikus-soft/rdiffweb/commit/615cc106edbd8bdd9600a0248402556abd821250) by Patrik Dufresne).
- Remove graphs plugins ([3a2bf90](https://gitlab.com/ikus-soft/rdiffweb/commit/3a2bf9005404e849eadca3ec16e168663c7763e6) by Patrik Dufresne).
- Remove delete_repo plugins ([a654c7d](https://gitlab.com/ikus-soft/rdiffweb/commit/a654c7dba0f59bf57dfa1f371c99549fb0315ec9) by Patrik Dufresne).
- Remove update_repos plugin ([c8316a5](https://gitlab.com/ikus-soft/rdiffweb/commit/c8316a5d41c2e998df2a80a887df2996b5b7fda3) by Patrik Dufresne).
- Remove remove_older plugin ([57b5e44](https://gitlab.com/ikus-soft/rdiffweb/commit/57b5e44e5c820b43a64098f4409dab4a2eaaed64) by Patrik Dufresne).
- Remove set_encoding plugin ([d9b107d](https://gitlab.com/ikus-soft/rdiffweb/commit/d9b107dc17ef90356927e244f17bb120c89b1894) by Patrik Dufresne).

### Merged

- Merge branch 'develop/patrik/remove-plugins' into 'master' ([fbb2d52](https://gitlab.com/ikus-soft/rdiffweb/commit/fbb2d524dcac20648acfffb0ae77c3fad251a754) by Patrik Dufresne).
- Merge branch 'develop/patrik/remove-plugins' ([fbd2e79](https://gitlab.com/ikus-soft/rdiffweb/commit/fbd2e79b154b10df0362cfc47d296afaa59f881b) by Patrik Dufresne).
- Merge branch 'develop/patrik/fix-performance-issue' into 'master' ([83ef11f](https://gitlab.com/ikus-soft/rdiffweb/commit/83ef11fc32fd1dafca041b7681267cdfddaa533f) by Patrik Dufresne).
- Merge remote-tracking branch 'origin/master' into develop/patrik/remove-plugins ([0dea6f9](https://gitlab.com/ikus-soft/rdiffweb/commit/0dea6f92e336ceb44916d767f5ca1695162a0a3e) by Patrik Dufresne).

### Misc

- Enable tools.proxy at application level pdsl/minarca-server#12 ([e08d314](https://gitlab.com/ikus-soft/rdiffweb/commit/e08d314789a95dc768a7ba10c71a9563d1a092d1) by Patrik Dufresne).
- Replace InvalidUserError by assertion ([1903616](https://gitlab.com/ikus-soft/rdiffweb/commit/1903616f52160a50d09d6b4f871797c61f4c2c7a) by Patrik Dufresne).
- Handle exception when plugins fail to load ([f6cb078](https://gitlab.com/ikus-soft/rdiffweb/commit/f6cb078c2eb00ed035bff4570bed0bb028faf366) by Patrik Dufresne).
- Do not send mail to user without email address rdiffweb/#53 ([8ed3c42](https://gitlab.com/ikus-soft/rdiffweb/commit/8ed3c42a065941b6aabd09ae60e155d1229cd747) by Patrik Dufresne).
- Pick only the first entry point for IUserQuota ([1bf2576](https://gitlab.com/ikus-soft/rdiffweb/commit/1bf25768de50452c3c98c7cf65e45d2591b23847) by Patrik Dufresne).
- Call user_attr_changed with userobj ([f359d1b](https://gitlab.com/ikus-soft/rdiffweb/commit/f359d1b36f8603c2af12e6792eae37258242460b) by Patrik Dufresne).
- Allow users creation without email, password and user_home ([e444d63](https://gitlab.com/ikus-soft/rdiffweb/commit/e444d63c89cd80407419aac583586475a5f82e93) by Patrik Dufresne).
- Reorganize the documentation ([c36c51d](https://gitlab.com/ikus-soft/rdiffweb/commit/c36c51d7c8718deb68fc03f2c80897073aad2994) by Patrik Dufresne).
- Automate deployment to demo server ([fa22652](https://gitlab.com/ikus-soft/rdiffweb/commit/fa226523f57760130e1d9242c19fe2d0bb06bca2) by Patrik Dufresne).
- Replace CHANGES by README ([8bde669](https://gitlab.com/ikus-soft/rdiffweb/commit/8bde669958b06e8d10e44cd3b792ea529c9400fc) by Patrik Dufresne).
- Update README ([153e697](https://gitlab.com/ikus-soft/rdiffweb/commit/153e697836a29d750bc46d0df7b1c79409ca5314) by Patrik Dufresne).
- Update default css ([7f9bcf4](https://gitlab.com/ikus-soft/rdiffweb/commit/7f9bcf4675667b4b4ce9e841cb1f78672d0cc33b) by Patrik Dufresne).
- Move the documentation back to here ([e81befb](https://gitlab.com/ikus-soft/rdiffweb/commit/e81befb6e2255746ca3a1063ba72ae222b549526) by Patrik Dufresne).
- Improve performance of librdiff ([3090413](https://gitlab.com/ikus-soft/rdiffweb/commit/3090413a51619896a82e064f8fa0c62e47dc1dbc) by Patrik Dufresne).
- Try to use Nexus proxy ([c9b3284](https://gitlab.com/ikus-soft/rdiffweb/commit/c9b32841e99ac7d03344249d7802bb940a99dc34) by Patrik Dufresne).
- Migrate ssh key management to UserObj ([e329d6e](https://gitlab.com/ikus-soft/rdiffweb/commit/e329d6e0b96cac83c22f701a95369261ee691523) by Patrik Dufresne).
- Register Notification as a deamon ([d4553f2](https://gitlab.com/ikus-soft/rdiffweb/commit/d4553f2207b8235ee3dd32960cd8679f6b46ad8c) by Patrik Dufresne).
- Update config file to remove plugins related options ([d8fe379](https://gitlab.com/ikus-soft/rdiffweb/commit/d8fe379105a2944a161d85e04d6bad289e8c56af) by Patrik Dufresne).
- Upload wheel package for py2 & py3 ([9983b25](https://gitlab.com/ikus-soft/rdiffweb/commit/9983b25fa421eef5909e9c1a0359a50997b113d7) by Patrik Dufresne).
- Replace `validate_user_path()` by UserObject.get_repo_path() ([a4b114a](https://gitlab.com/ikus-soft/rdiffweb/commit/a4b114a9dec6f917ffe2d79f85353bcd583c144c) by Patrik Dufresne).
- user_sqlite: Make use of boolean mapping ([f394f3a](https://gitlab.com/ikus-soft/rdiffweb/commit/f394f3acfaa86ec960a6f10c64b0d84dae0383df) by Patrik Dufresne).
- Rename variable to follow Python convention in user_sqlite ([76ece9e](https://gitlab.com/ikus-soft/rdiffweb/commit/76ece9ef1bc30ff2cd6f677670ce562c49a263be) by Patrik Dufresne).
- Migrate minarca disk usage to rdiffweb core ([9e521ae](https://gitlab.com/ikus-soft/rdiffweb/commit/9e521aedc1042ac218a57d8912ddae40ea836427) by Patrik Dufresne).
- Simplify get_version method ([bc6aac8](https://gitlab.com/ikus-soft/rdiffweb/commit/bc6aac862feaf432c41c8c92eed65ebe541c6192) by Patrik Dufresne).
- Drop support of cherrypy v3.2.2 add support of cherrypy v18 ([df38d1f](https://gitlab.com/ikus-soft/rdiffweb/commit/df38d1f13eb7646c11d06dfb4205f76a9938624d) by Patrik Dufresne).
- Reffactor config ([afc116d](https://gitlab.com/ikus-soft/rdiffweb/commit/afc116db5eded8d0de2aef66e77e06caf21b230f) by Patrik Dufresne).
- Create Controller for LoginPage ([f8deff9](https://gitlab.com/ikus-soft/rdiffweb/commit/f8deff951de8379688a130521427323a9c27ba6e) by Patrik Dufresne).
- Replace PageMain by Controller class ([6cfaeef](https://gitlab.com/ikus-soft/rdiffweb/commit/6cfaeef930d72ba6547559ea160bea282bd9b6db) by Patrik Dufresne).
- Move validate_user_path() to Controller class ([7f6df06](https://gitlab.com/ikus-soft/rdiffweb/commit/7f6df067f3b7e7cda18190438d0bccedc746b797) by Patrik Dufresne).
- Move validation to controller module ([79cfca8](https://gitlab.com/ikus-soft/rdiffweb/commit/79cfca82067a8f63d21d2b2c18783e61a5c725f6) by Patrik Dufresne).
- Rename Component to Controller ([8e15a24](https://gitlab.com/ikus-soft/rdiffweb/commit/8e15a24ad4f3b540d2eecce9ec35a4c532f3ae26) by Patrik Dufresne).
- Reorganize the packages ([749516f](https://gitlab.com/ikus-soft/rdiffweb/commit/749516f282c0c2f1eba4c180e22fa1c9214ae971) by Patrik Dufresne).

## [0.10.9](https://gitlab.com/ikus-soft/rdiffweb/tags/0.10.9) - 2019-05-22

<small>[Compare with 0.10.8](https://gitlab.com/ikus-soft/rdiffweb/compare/0.10.8...0.10.9)</small>

### Changed

- Change config loading ([1442ee5](https://gitlab.com/ikus-soft/rdiffweb/commit/1442ee50dd5935ecda29667a602b3ea237feb6e7) by Patrik Dufresne).
- Change log level around authentication ([d85528a](https://gitlab.com/ikus-soft/rdiffweb/commit/d85528aa64641d9bfb08e582cba204646a6f03fa) by Patrik Dufresne).

### Removed

- Remove travis-ci / Replace by gitlab CICD ([3baec5f](https://gitlab.com/ikus-soft/rdiffweb/commit/3baec5f1b78e9c931fa920383b69fb97957c4972) by Patrik Dufresne).

### Merged

- Merge branch 'develop/patrik/fix-error-log' into 'master' ([d41ca64](https://gitlab.com/ikus-soft/rdiffweb/commit/d41ca646a53745b3ccd50069776c301c023f7539) by Patrik Dufresne).
- Merge branch 'develop/patrik/change-log-level' into 'master' ([c6a481e](https://gitlab.com/ikus-soft/rdiffweb/commit/c6a481e3152dde4ee3dce2cf221e32653e94a730) by Patrik Dufresne).
- Merge branch 'develop/patrik/cicd-docker-image' into 'master' ([67fc7d5](https://gitlab.com/ikus-soft/rdiffweb/commit/67fc7d5011882054d7a96406f76b8913ac07b96d) by Patrik Dufresne).

### Misc

- Improve error handling around error.log ([d702aa8](https://gitlab.com/ikus-soft/rdiffweb/commit/d702aa82a109be7721b08f11fb6201684822a7e4) by Patrik Dufresne).
- CICD rdiffweb deployment ([a78156e](https://gitlab.com/ikus-soft/rdiffweb/commit/a78156ed155737b3609639d8a9413dbc61fcdc74) by Patrik Dufresne).
- CICD prebuild image ([060bac9](https://gitlab.com/ikus-soft/rdiffweb/commit/060bac9c92e467aaaf05155801f8b5b367ddb127) by Patrik Dufresne).

## [0.10.8](https://gitlab.com/ikus-soft/rdiffweb/tags/0.10.8) - 2018-07-14

<small>[Compare with 0.10.7](https://gitlab.com/ikus-soft/rdiffweb/compare/0.10.7...0.10.8)</small>

### Added

- Add support for cherrypy 16 ([48d00fc](https://gitlab.com/ikus-soft/rdiffweb/commit/48d00fcca845c2cd1de79cdcced5579991988706) by Patrik Dufresne).

### Fixed

- Fix background thread execution. TASK-1001 ([88947f6](https://gitlab.com/ikus-soft/rdiffweb/commit/88947f64652777141451516e888e5fa566765ca6) by Patrik Dufresne).

### Removed

- Remove pages and coverage step from CICD ([552a9dc](https://gitlab.com/ikus-soft/rdiffweb/commit/552a9dc297e1798e30ecb0fc33dea1fe62e85a51) by Patrik Dufresne).

### Merged

- Merge branch 'develop/cherrypy16' into 'master' ([1527dc0](https://gitlab.com/ikus-soft/rdiffweb/commit/1527dc07d6c3c5f29a929b33214775ccea911c5b) by Patrik Dufresne).
- Merge branch 'develop/demon-task-1027' into 'master' ([a15b36b](https://gitlab.com/ikus-soft/rdiffweb/commit/a15b36b8c4d0179843788740bb70c1fc10d0c9c0) by Patrik Dufresne).

### Misc

- TASK-1027 Fix bug in deamon plugin scheduler ([4203cf8](https://gitlab.com/ikus-soft/rdiffweb/commit/4203cf87fcaaa63e22a5e1bf2cfba2e7ba000df1) by Patrik Dufresne).
- Only push branches to github ([b21e524](https://gitlab.com/ikus-soft/rdiffweb/commit/b21e524a85b6d2d908c649dde40845d10309efb6) by Patrik Dufresne).

## [0.10.7](https://gitlab.com/ikus-soft/rdiffweb/tags/0.10.7) - 2018-04-12

<small>[Compare with 0.10.6](https://gitlab.com/ikus-soft/rdiffweb/compare/0.10.6...0.10.7)</small>

### Misc

- Make the DeamonPlugin more robust ([33d5f2f](https://gitlab.com/ikus-soft/rdiffweb/commit/33d5f2fc44ed7d9c20171e6f199ca496186bc80b) by Patrik Dufresne).
- Compile each tox environment in parallel. ([2e08e2e](https://gitlab.com/ikus-soft/rdiffweb/commit/2e08e2e7fba33f11da02a33d49e040c60ccfa641) by Patrik Dufresne).
- Update copyright year to 2018 ([430ea16](https://gitlab.com/ikus-soft/rdiffweb/commit/430ea16826cab31353c616a59c89cd79828c32bc) by Patrik Dufresne).
- Adjust logging level in filter_authentication. ([1eb2269](https://gitlab.com/ikus-soft/rdiffweb/commit/1eb2269a5ecc49df7909dd21aa886b82c91ee85b) by Patrik Dufresne).

## [0.10.6](https://gitlab.com/ikus-soft/rdiffweb/tags/0.10.6) - 2018-04-04

<small>[Compare with 0.10.5](https://gitlab.com/ikus-soft/rdiffweb/compare/0.10.5...0.10.6)</small>

### Added

- Add .mo file to git. ([6ad7c2e](https://gitlab.com/ikus-soft/rdiffweb/commit/6ad7c2ebacc3b30c1c18a9912ce54433a46a3a12) by Patrik Dufresne).
- Add gitlab-ci.yml config ([0921680](https://gitlab.com/ikus-soft/rdiffweb/commit/09216807e35994a16b0da547feefc793ef897afc) by Patrik Dufresne).

### Fixed

- Fix the Content-Type when restoring file. TASK-972 ([1f5616d](https://gitlab.com/ikus-soft/rdiffweb/commit/1f5616d1b06ebec2e2111695e33fb5338ad53c33) by Patrik Dufresne).
- Fix timezone issue. ([bef8327](https://gitlab.com/ikus-soft/rdiffweb/commit/bef8327982931f66cae9ac2c46e1a0774627e69f) by Patrik Dufresne).
- Fix related to missing _read_gzip_header in python 3.5. ([216d668](https://gitlab.com/ikus-soft/rdiffweb/commit/216d6687c041411c0bbeb1050ef5fe63bb5ca563) by Patrik Dufresne).

### Changed

- Change translation layer ([37d7b1c](https://gitlab.com/ikus-soft/rdiffweb/commit/37d7b1ca07db25c1e1b4d278178255c9834ea572) by Patrik Dufresne).

### Removed

- Remove .pydevproject from git ([f142a83](https://gitlab.com/ikus-soft/rdiffweb/commit/f142a83d29db81ca8dfa5ecc0279a151e6fe523a) by Patrik Dufresne).
- Remove CHANGELOG. Was never maintained ([f391ebe](https://gitlab.com/ikus-soft/rdiffweb/commit/f391ebed72b8943553f9468c32d1a3f4a3bf7d7b) by Patrik Dufresne).
- Remove tox command line from setup.py ([0f798d1](https://gitlab.com/ikus-soft/rdiffweb/commit/0f798d1ac7facf9b16a8c39ea66407dd86174876) by Patrik Dufresne).
- Remove `filltmpl` from setup.py ([98e23cf](https://gitlab.com/ikus-soft/rdiffweb/commit/98e23cff8eb32265c841f0dfe8679459c40fb53a) by Patrik Dufresne).

### Misc

- Publish to pypi only for tags ([54e661f](https://gitlab.com/ikus-soft/rdiffweb/commit/54e661f06a84d6aa1977ea8867d46e189efd86df) by Patrik Dufresne).
- Migrate rdwTime to librdiff.RdiffTime. ([61da3a3](https://gitlab.com/ikus-soft/rdiffweb/commit/61da3a318ee3117042bdaf1fc448fbd540270cf1) by Patrik Dufresne).
- Constraint Jinja2 version to avoid a bug ([b35ebbd](https://gitlab.com/ikus-soft/rdiffweb/commit/b35ebbd45bae6764eca1df02c6f5dc42a8d150af) by Patrik Dufresne).
- Define the tar.gz encoding. ([1154321](https://gitlab.com/ikus-soft/rdiffweb/commit/1154321bb387a348b36473f9d446ac211a9ab594) by Patrik Dufresne).
- Create a Jenkinsfile ([85447a3](https://gitlab.com/ikus-soft/rdiffweb/commit/85447a35565e9c75497ff817169c5ba689e7bd9e) by Patrik Dufresne).
- Prepare next development version ([e582a5c](https://gitlab.com/ikus-soft/rdiffweb/commit/e582a5c46b3f79b679a386f4c495529bccbeb1a6) by Jenkins).

## [0.10.5](https://gitlab.com/ikus-soft/rdiffweb/tags/0.10.5) - 2018-01-31

<small>[Compare with 0.10.4](https://gitlab.com/ikus-soft/rdiffweb/compare/0.10.4...0.10.5)</small>

### Added

- Add Catalan and spanish translation. ([999d171](https://gitlab.com/ikus-soft/rdiffweb/commit/999d171e87f3f3ef997e60f665f82e3c6aedb655) by Patrik Dufresne).
- Add travis badge to README.md file ([4a8e90f](https://gitlab.com/ikus-soft/rdiffweb/commit/4a8e90f48a99e3979f53381d4226e0562fe12f8d) by ikus060).

### Changed

- Change assertTrue(isinstance()) into assertIsInstance() ([5fc0485](https://gitlab.com/ikus-soft/rdiffweb/commit/5fc0485e8dfea37d1abc8071d4b18cc013dddc57) by ikus060).

### Misc

- Release 0.10.5 ([dfcce6b](https://gitlab.com/ikus-soft/rdiffweb/commit/dfcce6b507b5d9aba22cb69832596d6e4a1b112e) by Jenkins).
- Update french translation. ([9f8908b](https://gitlab.com/ikus-soft/rdiffweb/commit/9f8908b2b75a6613c4ab4cb5f2d93d11420d730d) by Patrik Dufresne).
- Do not disable file restore when status is not ok. ([36fb1dc](https://gitlab.com/ikus-soft/rdiffweb/commit/36fb1dc65ddf0c0ae0c2762187fa33032345468a) by Patrik Dufresne).
- Rework basic and form authentication to collaborate. ([c2f36e3](https://gitlab.com/ikus-soft/rdiffweb/commit/c2f36e3ff8477bb328fddce5729706b8e3d97cb9) by Patrik Dufresne).
- Reconfigure travis matrix to use tox. Add cherrypy 11. TASK-902 ([909e864](https://gitlab.com/ikus-soft/rdiffweb/commit/909e86418cd8adc9be7afb3a7aee43718ccb37b4) by ikus060).
- Make sure to compile the catalogs before running the test. ([9d18441](https://gitlab.com/ikus-soft/rdiffweb/commit/9d18441042ca4ad1b2a37fb69d37aeee5965089c) by ikus060).
- Force timezone in travis. ([0074516](https://gitlab.com/ikus-soft/rdiffweb/commit/00745162152b9d047ba94521964c52e848d83941) by ikus060).
- Declare TMPDIR as /var/tmp. ([5f76533](https://gitlab.com/ikus-soft/rdiffweb/commit/5f76533fc20f0b23b428517255b4858db598e187) by ikus060).
- Prepare next development version ([d0c0e38](https://gitlab.com/ikus-soft/rdiffweb/commit/d0c0e387c0167782a59c73d3c1b2bec7a6e873e7) by Jenkins).
- Install python-pysqlite2 and rdiff-backup in Travis ([4dcff94](https://gitlab.com/ikus-soft/rdiffweb/commit/4dcff94da2d304dc6e08018545228678879350cc) by ikus060).
- Provide travis config file ([d564c73](https://gitlab.com/ikus-soft/rdiffweb/commit/d564c73ac179111ac1b14f8ee16f2f72db03d51a) by ikus060).
- Start implementation of a RESTful API for Rdiffweb. ([e0d4ebb](https://gitlab.com/ikus-soft/rdiffweb/commit/e0d4ebb6f442690f41429d3f97cf51ac7df90214) by Patrik Dufresne).

## [0.10.4](https://gitlab.com/ikus-soft/rdiffweb/tags/0.10.4) - 2017-10-16

<small>[Compare with 0.10.2](https://gitlab.com/ikus-soft/rdiffweb/compare/0.10.2...0.10.4)</small>

### Added

- Add a new function to limit the login based on ldap group. ([4e31e1b](https://gitlab.com/ikus-soft/rdiffweb/commit/4e31e1b97cbeb3cac2a4f2f473d76a080314f90d) by Patrik Dufresne).

### Misc

- Release 0.10.4 ([3259592](https://gitlab.com/ikus-soft/rdiffweb/commit/3259592621bdbbfc29f555d4c73e046d68c4f9a0) by Jenkins).
- Convert keepdays into int() in _remove_older plugins. ([632a93b](https://gitlab.com/ikus-soft/rdiffweb/commit/632a93b054dfd1d2137b718fe75ec98d87fbe2eb) by ikus060).
- Move away documentation to www.patrikdufresne.com ([e03a513](https://gitlab.com/ikus-soft/rdiffweb/commit/e03a5136a69198891e6b1adb57a7cc5d90d014a2) by ikus060).
- Prepare next development version ([4b85b12](https://gitlab.com/ikus-soft/rdiffweb/commit/4b85b12ddb1247a281e47a9289e87f37bd13728c) by Jenkins).

## [0.10.2](https://gitlab.com/ikus-soft/rdiffweb/tags/0.10.2) - 2017-05-25

<small>[Compare with 0.10.0](https://gitlab.com/ikus-soft/rdiffweb/compare/0.10.0...0.10.2)</small>

### Added

- Add pytest as dependencies for cherrypy10 ([fabcd06](https://gitlab.com/ikus-soft/rdiffweb/commit/fabcd06ee40b4656b006ee98d69608736e34cf67) by Patrik Dufresne).
- Add sub_filter rule to nginx config to support d3js graphs. ([d047eec](https://gitlab.com/ikus-soft/rdiffweb/commit/d047eecb59419444e2bd9d688bcf9e391b9b82f7) by Patrik Dufresne).

### Fixed

- Fix locations to properly display a single repository. ([e2ec847](https://gitlab.com/ikus-soft/rdiffweb/commit/e2ec84799ceecb28b1507dbfacaabcb3f0391b5b) by Patrik Dufresne).
- Fix to properly support cherrypy>=10 ([77421fa](https://gitlab.com/ikus-soft/rdiffweb/commit/77421fadf21be8811932fb58fb0f8234af9f0e2d) by Patrik Dufresne).
- Fix imports _ ([ee1f182](https://gitlab.com/ikus-soft/rdiffweb/commit/ee1f1829a704a0150a77302fbfd87c081df9c69a) by Patrik Dufresne).

### Changed

- Change config to generate multiple junit report file. ([3c4fe52](https://gitlab.com/ikus-soft/rdiffweb/commit/3c4fe528999259e519f372733ad1eedf692c876c) by Patrik Dufresne).

### Misc

- Release 0.10.2 ([bd46726](https://gitlab.com/ikus-soft/rdiffweb/commit/bd46726b02427344967c62352cb065ca070d5302) by Jenkins).
- Prepare next development version ([46e7109](https://gitlab.com/ikus-soft/rdiffweb/commit/46e710988260de1c3fd4a2b6adffb27433b4c828) by Jenkins).

## [0.10.0](https://gitlab.com/ikus-soft/rdiffweb/tags/0.10.0) - 2017-05-17

<small>[Compare with 0.9.5](https://gitlab.com/ikus-soft/rdiffweb/compare/0.9.5...0.10.0)</small>

### Added

- Add a robots.txt #37 ([a984fa6](https://gitlab.com/ikus-soft/rdiffweb/commit/a984fa63aaab933e15b86583801a160dfc839364) by Patrik Dufresne).
- Add more cherrypy version to tox config file ([2f0ded7](https://gitlab.com/ikus-soft/rdiffweb/commit/2f0ded790f5937536269f232b3b6099050843a90) by Patrik Dufresne).
- Add systemd configuration file ([e4c462e](https://gitlab.com/ikus-soft/rdiffweb/commit/e4c462e99eaf6a2f3c571fd00aa09651fcbb7182) by Patrik Dufresne).
- Add FAQ page ([424c509](https://gitlab.com/ikus-soft/rdiffweb/commit/424c5092ae3af3b1879d941de3ce81acce60ef4d) by Patrik Dufresne).

### Fixed

- Fix creation of email template to support non ascii. pdsl/minarca#225 ([5589827](https://gitlab.com/ikus-soft/rdiffweb/commit/5589827bca724cc5784ca91d94aad2084824e9fe) by Patrik Dufresne).
- Fix display when repo is interrupt during progress. #34 ([30a4021](https://gitlab.com/ikus-soft/rdiffweb/commit/30a40219c8ea17ce1e7f208d4121e95ee57ea4e2) by Patrik Dufresne).
- Fix date parsing with quoted chars. #36 ([21f4ced](https://gitlab.com/ikus-soft/rdiffweb/commit/21f4cede03802c3a8608ecb1fee37287d26bfdcf) by Patrik Dufresne).
- Fix the layout to properly display on smaller screen. pdsl/minarca#197 ([a7abe65](https://gitlab.com/ikus-soft/rdiffweb/commit/a7abe65568745dbcfa292cbbc1f8ec817269697d) by Patrik Dufresne).
- Fix bug for py3. ([6875c7e](https://gitlab.com/ikus-soft/rdiffweb/commit/6875c7e5fd178a5e81495d96f199f494272e702f) by Patrik Dufresne).
- Fix validation of RdiffRepo. Fix pdsl/minarca#191 ([f1b32ec](https://gitlab.com/ikus-soft/rdiffweb/commit/f1b32ecfdc2a5f91fe500509282047db7a0d2fef) by Patrik Dufresne).
- Fix problem with unprintable FileError exception. ([52b336e](https://gitlab.com/ikus-soft/rdiffweb/commit/52b336e3a749d1fb3f77983f74e4a38fa2a7bbf2) by Patrik Dufresne).
- Fix validation for simlink. pdsl/minarca#190 ([6c60300](https://gitlab.com/ikus-soft/rdiffweb/commit/6c60300a619ae116241582717f3037d997f4520b) by Patrik Dufresne).
- Fix ajax path in set_encoding plugin. ([a5b6a1e](https://gitlab.com/ikus-soft/rdiffweb/commit/a5b6a1e8ee38a38baad56bbf312d39f86259359c) by Patrik Dufresne).
- Fix logging in filter_authentication ([6931533](https://gitlab.com/ikus-soft/rdiffweb/commit/6931533f9eb92b4e5dae8759334c08852b12d225) by Patrik Dufresne).
- Fix HistoryEntry#errors to return something. ([7e27c7a](https://gitlab.com/ikus-soft/rdiffweb/commit/7e27c7a074c766296594dfad87e266827dd3d42e) by Patrik Dufresne).

### Changed

- Change status validation to detect previous backup failure. ([2590750](https://gitlab.com/ikus-soft/rdiffweb/commit/2590750e9ebaf727625c861823b5ed1c63730e96) by Patrik Dufresne).
- Change title of history page. pdsl/minarca#224 ([b57c4e5](https://gitlab.com/ikus-soft/rdiffweb/commit/b57c4e54432ca64a0330fb7724c5cb5941548de7) by Patrik Dufresne).
- Change repositories layout for multi-disk windows server #33 ([7a80bb7](https://gitlab.com/ikus-soft/rdiffweb/commit/7a80bb71b3619b0f67d4e70a48194851221e6881) by Patrik Dufresne).
- Change the logging level in filter_authentication ([a7fbe4d](https://gitlab.com/ikus-soft/rdiffweb/commit/a7fbe4dd65f7081ad392b0aaafeb8a68b0997202) by Patrik Dufresne).

### Removed

- Remove old and obsolete email_notification file. ([8d06895](https://gitlab.com/ikus-soft/rdiffweb/commit/8d06895ba76e9f32c6e4edb35a31f97f2e84437d) by Patrik Dufresne).
- Remove babel from installation requirements ([d456356](https://gitlab.com/ikus-soft/rdiffweb/commit/d456356f41bdac40d7ab8c8a78ce922f3ec04f5a) by Patrik Dufresne).
- Remove obsolete import from page_settings ([a975dec](https://gitlab.com/ikus-soft/rdiffweb/commit/a975dec1662a3ae854b0c4ece70ef2896ac5843d) by Patrik Dufresne).

### Merged

- Merge RdiffPath and DirEntry. ([489f3cd](https://gitlab.com/ikus-soft/rdiffweb/commit/489f3cdfc261d3fc90dfe74faa7a49ac9560cd0e) by Patrik Dufresne).

### Misc

- Release 0.10.0 ([bd8c27b](https://gitlab.com/ikus-soft/rdiffweb/commit/bd8c27b039808b3d281dbd8fb8f0fcbf011ce2d3) by Jenkins).
- Include the full path in browse and history view. ([15c6526](https://gitlab.com/ikus-soft/rdiffweb/commit/15c652600bfe44dc923f4493877bf2158669304b) by Patrik Dufresne).
- Check if process is running using psutil ([255ce35](https://gitlab.com/ikus-soft/rdiffweb/commit/255ce35389b6669bc2ed705a10179003621ca533) by Patrik Dufresne).
- Register a default error handler to convert exception into HTTP error ([e2bed47](https://gitlab.com/ikus-soft/rdiffweb/commit/e2bed47877c00c0331734c5d3587f54aff1c8862) by Patrik Dufresne).
- Update french translation pdsl/minarca#222 pdsl/minarca#223 ([45f1741](https://gitlab.com/ikus-soft/rdiffweb/commit/45f17411338862e1cc00c50d3f1ed37932028b88) by Patrik Dufresne).
- Touch implementation of find_repos ([024648a](https://gitlab.com/ikus-soft/rdiffweb/commit/024648ae2cc171cafe3cc48501d8ddaa29ccb67c) by Patrik Dufresne).
- Rdiffweb should not be index by robot. ([4ea021b](https://gitlab.com/ikus-soft/rdiffweb/commit/4ea021bdda27be66c37a5d7aba2223a5b7141460) by Patrik Dufresne).
- Export TMPDIR environment variable when executing rdiff-backup. ([5033318](https://gitlab.com/ikus-soft/rdiffweb/commit/5033318a344fd2fae88ca6dcda2f13bd73b8ae17) by Patrik Dufresne).
- Notify user by mail when password changes. pdsl/minarca#151 ([5cf60e4](https://gitlab.com/ikus-soft/rdiffweb/commit/5cf60e48315f42b6733e5aabd642dede4bb21597) by Patrik Dufresne).
- Avoid updating email fields if it didn't changed. pdsl/minarca#187 ([7b2219b](https://gitlab.com/ikus-soft/rdiffweb/commit/7b2219b0ee8373f8e0009274692fb1f89712faf1) by Patrik Dufresne).
- Make the repo_name bold. See pdsl/minarca#199 ([a7ad8d3](https://gitlab.com/ikus-soft/rdiffweb/commit/a7ad8d3723ca8d04606e9ec02a9d71ca09e8e029) by Patrik Dufresne).
- Review usage of repo_name vs repo_path. ([a66fd2d](https://gitlab.com/ikus-soft/rdiffweb/commit/a66fd2d1d4299b57a1977c37178b416372ca9b7d) by Patrik Dufresne).
- Allow restore() with DirEntry. ([3226dd4](https://gitlab.com/ikus-soft/rdiffweb/commit/3226dd4f79288eb2689c65bf670cd67929062df2) by Patrik Dufresne).
- Replace usage of logging by logger. ([c981f6f](https://gitlab.com/ikus-soft/rdiffweb/commit/c981f6f1be35b28f7025c69fb4f430f80dace112) by Patrik Dufresne).
- Use change_dates instead of restore_dates. ([5d79c40](https://gitlab.com/ikus-soft/rdiffweb/commit/5d79c403cf26374002a1337066eb92c28d1a3ecc) by Patrik Dufresne).
- Update nginx config ([2d83068](https://gitlab.com/ikus-soft/rdiffweb/commit/2d8306865002464e6a5aa5edb45a774cdaa501ae) by Patrik Dufresne).
- Update install/config doc ([df5d71e](https://gitlab.com/ikus-soft/rdiffweb/commit/df5d71ea04f53c517b4c26ff7db9f01fccead38a) by Patrik Dufresne).
- Relayout the browser and restore GUI. pdsl/minarca#125 ([2ef7d03](https://gitlab.com/ikus-soft/rdiffweb/commit/2ef7d03cb5d72a12beb42ab84ba3be7b5c54e714) by Patrik Dufresne).
- Reorganize static file. pdsl/rdiffweb#31 ([892ccd6](https://gitlab.com/ikus-soft/rdiffweb/commit/892ccd6e76d82158c986ce8ec028b41127a6abc4) by Patrik Dufresne).
- Prepare next development version ([df6b0dd](https://gitlab.com/ikus-soft/rdiffweb/commit/df6b0dd32db5cce98e487a5690cd1f7e4daeb474) by Jenkins).

## [0.9.5](https://gitlab.com/ikus-soft/rdiffweb/tags/0.9.5) - 2016-10-11

<small>[Compare with 0.9.3](https://gitlab.com/ikus-soft/rdiffweb/compare/0.9.3...0.9.5)</small>

### Misc

- Release 0.9.5 ([12da803](https://gitlab.com/ikus-soft/rdiffweb/commit/12da80344af29469a5eff6225523723b17c3f002) by Jenkins).
- Include d3.js as static ressources ([61cf8a6](https://gitlab.com/ikus-soft/rdiffweb/commit/61cf8a650e2e068a88c59ee9f5bf83653b96c89f) by Patrik Dufresne).
- Prepare next development version ([3b716a1](https://gitlab.com/ikus-soft/rdiffweb/commit/3b716a176ba3ba9494e5694d8a8588acfa77e035) by Jenkins).

## [0.9.3](https://gitlab.com/ikus-soft/rdiffweb/tags/0.9.3) - 2016-10-08

<small>[Compare with 0.9.2](https://gitlab.com/ikus-soft/rdiffweb/compare/0.9.2...0.9.3)</small>

### Misc

- Release 0.9.3 ([dd72b73](https://gitlab.com/ikus-soft/rdiffweb/commit/dd72b73bdd535edc25f8743f94d9bd03c1c4ca87) by Jenkins).
- Prepare next development version ([1514ac1](https://gitlab.com/ikus-soft/rdiffweb/commit/1514ac1029bd93f9006745eca6a45079106b37f8) by Jenkins).

## [0.9.2](https://gitlab.com/ikus-soft/rdiffweb/tags/0.9.2) - 2016-10-07

<small>[Compare with 0.9.1](https://gitlab.com/ikus-soft/rdiffweb/compare/0.9.1...0.9.2)</small>

### Added

- Add missing 'rdw.conf' and 'babel.cfg' to source package. ([e278e9a](https://gitlab.com/ikus-soft/rdiffweb/commit/e278e9a2223f3b2bbcb8e7a06681e8d7815ad525) by Patrik Dufresne).

### Fixed

- Fix source package to include extras folder. ([cebb518](https://gitlab.com/ikus-soft/rdiffweb/commit/cebb5183de8831b10cd17050ba206bd5dcd52740) by Patrik Dufresne).
- Fix loading of jquery validation locales. ([f7fb7af](https://gitlab.com/ikus-soft/rdiffweb/commit/f7fb7afc2126800cdbac0be5aeea1660d21df4fa) by Patrik Dufresne).

### Removed

- Remove filltmpl from default build. ([db7585a](https://gitlab.com/ikus-soft/rdiffweb/commit/db7585a6818888371e026a097b12cdb68ebed2d2) by Patrik Dufresne).

### Misc

- Release 0.9.2 ([1a492a8](https://gitlab.com/ikus-soft/rdiffweb/commit/1a492a8b5eb2f0eff40e920f34933a546ffc9dda) by Jenkins).
- Update installation steps. ([a2b58ef](https://gitlab.com/ikus-soft/rdiffweb/commit/a2b58ef99eaf6398c13a578b8b8fc037723352d3) by Patrik Dufresne).
- Downgrade Babel requirement for 0.9.6. ([c8de3a3](https://gitlab.com/ikus-soft/rdiffweb/commit/c8de3a3cc7ee024bfc3c7f76e6514170b5bc0eb1) by Patrik Dufresne).
- Don't include *.plugin in source package. ([222d23e](https://gitlab.com/ikus-soft/rdiffweb/commit/222d23eb58ee929bbd19bf5d9da4c7b86879f654) by Patrik Dufresne).
- Swallow exception in status page. ([ff15d1b](https://gitlab.com/ikus-soft/rdiffweb/commit/ff15d1b8b13e8cf2afd93349b4aa08fadda57836) by Patrik Dufresne).
- Prepare next development version ([87ef8c9](https://gitlab.com/ikus-soft/rdiffweb/commit/87ef8c9429a81a1c36b2cf398d58d6142e8f55d7) by Jenkins).

## [0.9.1](https://gitlab.com/ikus-soft/rdiffweb/tags/0.9.1) - 2016-10-07

<small>[Compare with 0.8.1](https://gitlab.com/ikus-soft/rdiffweb/compare/0.8.1...0.9.1)</small>

### Added

- Add option in LdapAuth Plugin to verify the ShadownExpire. See #23 ([c3b9af8](https://gitlab.com/ikus-soft/rdiffweb/commit/c3b9af83e3c68f987993f753238ee196de7f2c81) by Patrik Dufresne).
- Adding new Option class to access config. ([fa110dc](https://gitlab.com/ikus-soft/rdiffweb/commit/fa110dc8d7223cdb9de284eeb8ccdbe9e4a8b8a1) by Patrik Dufresne).
- Add delete repo form validation. pdsl/minarca#135 ([1c2f538](https://gitlab.com/ikus-soft/rdiffweb/commit/1c2f538eb897920f4329a5840756795f8fd6aa90) by Patrik Dufresne).
- Add form validation to password change form. ([0d8c491](https://gitlab.com/ikus-soft/rdiffweb/commit/0d8c491643f7085533c4803adeb468ad081d31a9) by Patrik Dufresne).
- Add JQueryValidation with translation ([078aad3](https://gitlab.com/ikus-soft/rdiffweb/commit/078aad320ac9b2031af98ec0381bbe51185b1f46) by Patrik Dufresne).
- Add show more button to restore page. See #7 ([bf8f66e](https://gitlab.com/ikus-soft/rdiffweb/commit/bf8f66e7b7c3ae0fd63b12f745662cb90c286406) by Patrik Dufresne).
- Add CHANGE log file. ([0ff46db](https://gitlab.com/ikus-soft/rdiffweb/commit/0ff46db8e0d8004f24f0882cdb79c1ecc7d3a8d0) by Patrik Dufresne).
- Add a limit parameter to history. #7 ([6cec6e3](https://gitlab.com/ikus-soft/rdiffweb/commit/6cec6e36cf8cc93603b61b940fa9d57a7a929608) by Patrik Dufresne).
- Add email notification when mail is changed. pdsl/minarca#98 ([58e1d59](https://gitlab.com/ikus-soft/rdiffweb/commit/58e1d5968e95d5cc07dd85c5e1659987d8e2a0ee) by Patrik Dufresne).
- Add path to librdiff exception. ([9c582c6](https://gitlab.com/ikus-soft/rdiffweb/commit/9c582c6173dce330439ce5384213b0e43fb29cb8) by Patrik Dufresne).
- Add error handling to Ajax form submit ([9d5ef58](https://gitlab.com/ikus-soft/rdiffweb/commit/9d5ef5875fcb28bacb334d664e3bfb7fc7b2c21c) by Patrik Dufresne).
- Add right margin to d3js layout. Fix #26 ([ddc6fd7](https://gitlab.com/ikus-soft/rdiffweb/commit/ddc6fd7b405ae905f4ff3a7aa97dc5605a8383ec) by Patrik Dufresne).
- Add subtract to rdwTime. ([18388c4](https://gitlab.com/ikus-soft/rdiffweb/commit/18388c476972dec1bd8f7cec577b3b593571522c) by Patrik Dufresne).
- Add nginx config file to extras ([2c30fa7](https://gitlab.com/ikus-soft/rdiffweb/commit/2c30fa7ed900aa7cf88f43f4c759a765e63abcb7) by Vladimir Berezhnoy).
- Add icons & colors to ajax form submit. ([0ffe936](https://gitlab.com/ikus-soft/rdiffweb/commit/0ffe936dc51751c5785190995bafcbdc3d7c9aaa) by Patrik Dufresne).
- Add `ok` icon to fontello. ([55d8e56](https://gitlab.com/ikus-soft/rdiffweb/commit/55d8e56c1bdfbab3e6a642753f339463c9c8b128) by Patrik Dufresne).
- Add RemoveOlder plugin. ([74ab1ac](https://gitlab.com/ikus-soft/rdiffweb/commit/74ab1ac7ad8851440e11b244492b873fdb767350) by Patrik Dufresne).
- Add `set_attr` and `get_attr` for repos. ([6f4a550](https://gitlab.com/ikus-soft/rdiffweb/commit/6f4a5505a72afb40ece505120f25455cd691fbb7) by Patrik Dufresne).
- Add `attention` icons to fontello.less ([52529de](https://gitlab.com/ikus-soft/rdiffweb/commit/52529de22a965471014ca0170dfe63bee45fd6cf) by Patrik Dufresne).
- Add documentation about authentication. ([b724157](https://gitlab.com/ikus-soft/rdiffweb/commit/b7241576cfc8c1fd109f6e9874aea884df430619) by Patrik Dufresne).
- Add id attrib to container. ([74fc890](https://gitlab.com/ikus-soft/rdiffweb/commit/74fc8904f551c070c3fd7aa4027aca79b312d138) by Patrik Dufresne).
- Add text to static() assertion. ([5c2c0ff](https://gitlab.com/ikus-soft/rdiffweb/commit/5c2c0ffb09540c1a6bff3a4f24573d31301e53f4) by Patrik Dufresne).
- Add Graphs plugin. See #11 ([dd86215](https://gitlab.com/ikus-soft/rdiffweb/commit/dd862156c8925bc93d4347c1c08c7ee065b65e0e) by Patrik Dufresne).
- Add some icon to fontello ([d42f3a3](https://gitlab.com/ikus-soft/rdiffweb/commit/d42f3a32195919010f2489f36d38077a6c4c1279) by Patrik Dufresne).
- Add test coverage to page_restore. ([9fa16de](https://gitlab.com/ikus-soft/rdiffweb/commit/9fa16de1980d0eb0a32ea49f562f0bfb9a643619) by Patrik Dufresne).
- Add Test coverage for page_prefs. ([a985e29](https://gitlab.com/ikus-soft/rdiffweb/commit/a985e29e915f80383eee8cec384800c4ad924a11) by Patrik Dufresne).
- Add test coverage for settings page. ([039aa2f](https://gitlab.com/ikus-soft/rdiffweb/commit/039aa2fe573b577faf7c3247eb75f9c61ae4a240) by Patrik Dufresne).
- Add .pydevproject to gitignore ([814be31](https://gitlab.com/ikus-soft/rdiffweb/commit/814be314f8005f8c0f1626fb4e48239b564f0e7a) by Patrik Dufresne).
- Add mock as requirements. ([b4565fb](https://gitlab.com/ikus-soft/rdiffweb/commit/b4565fbdb876073be59285cb9ae2451eb8d1dab8) by Patrik Dufresne).
- Add mail notification. see #3 ([e635c07](https://gitlab.com/ikus-soft/rdiffweb/commit/e635c07863f921043c1462b3a8884d0706a2c004) by Patrik Dufresne).
- Add debug signal to dump thread. ([eeebbe7](https://gitlab.com/ikus-soft/rdiffweb/commit/eeebbe73df23d5bf0cb2001dbb46edce254e4c95) by Patrik Dufresne).
- Add profiling option `--profile` ([ca52a7d](https://gitlab.com/ikus-soft/rdiffweb/commit/ca52a7d75ecbad7552efd1d02b2924925c250f90) by Patrik Dufresne).
- Add logging to know how long it take to restore a file. ([6e4cdc9](https://gitlab.com/ikus-soft/rdiffweb/commit/6e4cdc9d3073950af096def6eb886140d9fe6e15) by Patrik Dufresne).
- Add directory in Zip archive. ([138dbee](https://gitlab.com/ikus-soft/rdiffweb/commit/138dbee511ac25783ea49c60acfa0d55b9503e9c) by Patrik Dufresne).
- Add file recursively to tar.gz. ([8d1c000](https://gitlab.com/ikus-soft/rdiffweb/commit/8d1c0002f70f969435c99d541044b4fb2261dd43) by Patrik Dufresne).
- Add new {% attrib %} See pdsl/rdiffweb#12 ([a19d9ef](https://gitlab.com/ikus-soft/rdiffweb/commit/a19d9efec020fb9afb4b2968c0f9251262ea3619) by Patrik Dufresne).
- Add log to page_admin (for debugging) ([5311fef](https://gitlab.com/ikus-soft/rdiffweb/commit/5311fefbcb11b5fcdb40a1b591da033b4a7d130b) by Patrik Dufresne).
- Add tox configuration file to automate test running on py2 and py3 ([b639eef](https://gitlab.com/ikus-soft/rdiffweb/commit/b639eef2f91739ef35d8cfa8608a6587c6ba6aac) by Patrik Dufresne).
- Add integration test and make it work in py2 and py3 ([4db4e44](https://gitlab.com/ikus-soft/rdiffweb/commit/4db4e441178452cd7a5fee071b02a400b118bff5) by Patrik Dufresne).
- Add new command filltmpl for sonar properties. ([799b1a2](https://gitlab.com/ikus-soft/rdiffweb/commit/799b1a20e974a26857badf41e5e89abefc27ef88) by Patrik Dufresne).

### Fixed

- Fix display when repo is broken. pdsl/minarca#159 ([c08f52a](https://gitlab.com/ikus-soft/rdiffweb/commit/c08f52a93a119c42082275d9ff622bfabdf8c76f) by Patrik Dufresne).
- Fix english wording and update French translation. ([aa096aa](https://gitlab.com/ikus-soft/rdiffweb/commit/aa096aa7c6b7dc10e9fffbb49c4cf32cfd4b353a) by Patrik Dufresne).
- Fix bug github/#65 in status.xml reported by bahamut45. ([c5f6eb6](https://gitlab.com/ikus-soft/rdiffweb/commit/c5f6eb6d5aab6c410fc2bc9c0f0aa1ee1ca00909) by Patrik Dufresne).
- Fix package name python2 > python ([f1479e9](https://gitlab.com/ikus-soft/rdiffweb/commit/f1479e9cd8008a176ecb66e783c953aeadcb9908) by Patrik Dufresne).
- Fix repo.get_attr() default value. ([f922579](https://gitlab.com/ikus-soft/rdiffweb/commit/f9225790b2c3ba161e3dbd565463bceed63ddbe7) by Patrik Dufresne).
- Fix notifications plugins to set max age. Fix #28 ([d74a986](https://gitlab.com/ikus-soft/rdiffweb/commit/d74a98660f022e1430a8559768632d259eaa3545) by Patrik Dufresne).
- Fix remove_older execution to avoid concat bytes for py3. ([21e97f8](https://gitlab.com/ikus-soft/rdiffweb/commit/21e97f8aed9d38ec8f87577a230eae095ee2ce5d) by Patrik Dufresne).
- Fix admin page testcases. ([f7132ea](https://gitlab.com/ikus-soft/rdiffweb/commit/f7132ea651e3d4db7df6dd23c45ae2c775bab1e9) by Patrik Dufresne).
- Fix locations templates to show all `templates_before_content` ([c585c50](https://gitlab.com/ikus-soft/rdiffweb/commit/c585c50790b7707ff4efd90457fe02bfd387372f) by Patrik Dufresne).
- Fix graphs browsing to `data` for python 3. ([861af74](https://gitlab.com/ikus-soft/rdiffweb/commit/861af7495e14377aa0242639e43814120dc27479) by Patrik Dufresne).
- Fix typo in default configuration comments. ([fafb30b](https://gitlab.com/ikus-soft/rdiffweb/commit/fafb30ba39cd8bc5838e2868f0e662271a7a4f33) by Patrik Dufresne).
- Fix Graphs plugin to receive poppath are bytes. ([d176fe5](https://gitlab.com/ikus-soft/rdiffweb/commit/d176fe527fe44b51c21d33246a6d7dc07f099de1) by Patrik Dufresne).
- Fix poppath to read args using unquote. ([2e1e6f7](https://gitlab.com/ikus-soft/rdiffweb/commit/2e1e6f7a37ac18356e75ccccd9ff851d7d7e5178) by Patrik Dufresne).
- Fix pages title in layout_repo.html ([f77215e](https://gitlab.com/ikus-soft/rdiffweb/commit/f77215efed90b702162da6f2c405f1eaffb5e8be) by Patrik Dufresne).
- Fix attrib to support True ([0444f1f](https://gitlab.com/ikus-soft/rdiffweb/commit/0444f1f0201123df8c3bdb607c422c2d34daf91b) by Patrik Dufresne).
- Fix archive encoding. See pdsl/minarca#121 ([03897c9](https://gitlab.com/ikus-soft/rdiffweb/commit/03897c94e1f3d554989508001fb8a53005e77688) by Patrik Dufresne).
- Fix content-disposition for file and archive. See pdsl/minarca#120 ([4cf99b5](https://gitlab.com/ikus-soft/rdiffweb/commit/4cf99b5bea0c8468d13c51d0c7d205fd5bd7c1c9) by Patrik Dufresne).
- Fix small encoding issue with authform redirection. ([ec2b172](https://gitlab.com/ikus-soft/rdiffweb/commit/ec2b17201d625ed0840a81a2b20bfe9a89e8426c) by Patrik Dufresne).
- Fix Admin plugin title ([7c57bc6](https://gitlab.com/ikus-soft/rdiffweb/commit/7c57bc6fae646f10d19e2c8204b317ed8cfe3095) by Patrik Dufresne).
- Fix plugin filter ([ca1371b](https://gitlab.com/ikus-soft/rdiffweb/commit/ca1371bb1a3de789a24934d643e7aaeeb5024933) by Patrik Dufresne).
- Fix archiver to support python < 2.7.3 ([5e08972](https://gitlab.com/ikus-soft/rdiffweb/commit/5e08972bd277ee4505e203deb2a30d77b87f9c42) by Patrik Dufresne).
- Fix FavIcon and HeaderLogo support. ([a559684](https://gitlab.com/ikus-soft/rdiffweb/commit/a5596845971b0d84defba829cf0d57f2e17a40ea) by Patrik Dufresne).
- Fix regression - support single repository browsing ([c7ea4b3](https://gitlab.com/ikus-soft/rdiffweb/commit/c7ea4b36ff67d236ccc929f8af09208d45209a56) by Patrik Dufresne).
- Fix str vs bytes for spider repo. ([56740b5](https://gitlab.com/ikus-soft/rdiffweb/commit/56740b5bad35625a07006750e2f04104e5fe15ad) by Patrik Dufresne).
- Fix notify logging ([924e541](https://gitlab.com/ikus-soft/rdiffweb/commit/924e541e8aa6dd1c196744320962d65d9536c3b8) by Patrik Dufresne).
- Fix attrib testcases (for py3) ([a9cbec0](https://gitlab.com/ikus-soft/rdiffweb/commit/a9cbec0e636b7ccd543702f49e69a7ae97e65525) by Patrik Dufresne).
- Fix setup.py to make it work using native string. ([901de8a](https://gitlab.com/ikus-soft/rdiffweb/commit/901de8a316ab1e9f79ec271916c648dbfdbd95e9) by Patrik Dufresne).
- Fix setup.py ([7e1d150](https://gitlab.com/ikus-soft/rdiffweb/commit/7e1d1505290627242a0d6253d2fd356558c3ee13) by Patrik Dufresne).

### Changed

- Change help message for remove_older #171 ([a2958fe](https://gitlab.com/ikus-soft/rdiffweb/commit/a2958fe2befa29faf653d67f786a50e0a4c6c5a6) by Patrik Dufresne).
- Change Folder icon. pdsl/minarca#171 ([ee34d2e](https://gitlab.com/ikus-soft/rdiffweb/commit/ee34d2e483ebe886fa86c936d93364a5efe4c597) by Patrik Dufresne).
- Change nosetests verbosity ([078180b](https://gitlab.com/ikus-soft/rdiffweb/commit/078180b7f31fbdb81643e1b0b273774cc6aa1487) by Patrik Dufresne).
- Change requirement to babel >= 1.3 ([caebd3e](https://gitlab.com/ikus-soft/rdiffweb/commit/caebd3edc7dc0ba240ee1c2d676eace9f3a2b8f1) by Patrik Dufresne).
- Change a bit the restore url to allow multiple kind ([557e0d1](https://gitlab.com/ikus-soft/rdiffweb/commit/557e0d1b22f993f65cce9c89aad3854c3d498a6e) by Patrik Dufresne).
- Change location of execute() function to RdiffRepo. ([b31b85f](https://gitlab.com/ikus-soft/rdiffweb/commit/b31b85fb944dc6e2c7f95540037b79410d7854a3) by Patrik Dufresne).
- Change style of remove_older template. ([84ed3d7](https://gitlab.com/ikus-soft/rdiffweb/commit/84ed3d741de5c34f58ee6f32c3474599c980ce07) by Patrik Dufresne).
- Change location of javascripts. Add ajax form submit. ([2f5aece](https://gitlab.com/ikus-soft/rdiffweb/commit/2f5aeceb8420a98ecf2d9dc4398cde9f49f528d3) by Patrik Dufresne).
- Change error handling in locations page. see #17 ([08c6dc9](https://gitlab.com/ikus-soft/rdiffweb/commit/08c6dc9b70682081a750cb73218be907ef3dd335) by Patrik Dufresne).

### Removed

- Remove JobPlugin from SetEncoding plugin ([d8e6ff3](https://gitlab.com/ikus-soft/rdiffweb/commit/d8e6ff339ad48c834874d77367f308b17ba617a5) by Patrik Dufresne).
- Remove funcsigs from dependencies ([3031759](https://gitlab.com/ikus-soft/rdiffweb/commit/30317595d714e407c28d32fd921205669e064abd) by Patrik Dufresne).
- Remove trailing slash (/) from restore URLs ([38a1f38](https://gitlab.com/ikus-soft/rdiffweb/commit/38a1f38eefc40ca0bd528ff7842e2bb3ea42c28e) by Patrik Dufresne).
- Remove useless border-bottom-right-* from login widget. ([ee2c72f](https://gitlab.com/ikus-soft/rdiffweb/commit/ee2c72f09dfd06de13837806592cacf5cf79698a) by Patrik Dufresne).
- Remove testcases from test_page_setings. ([efcd332](https://gitlab.com/ikus-soft/rdiffweb/commit/efcd33213f5975e8d9f8469dfe5d5d7dba16014a) by Patrik Dufresne).
- Remove obsolete import from librdiff. ([7fd8cc9](https://gitlab.com/ikus-soft/rdiffweb/commit/7fd8cc9a4432ebedab769abb30b02772d62a45f7) by Patrik Dufresne).
- Remove obsolete `from builtins import object` from rdw_app ([52011c9](https://gitlab.com/ikus-soft/rdiffweb/commit/52011c9261b93b58783321a3e79e7d5de675d87a) by Patrik Dufresne).
- Remove debug flag when restoring files. ([df48173](https://gitlab.com/ikus-soft/rdiffweb/commit/df481737d296e9253c39232d84c8ac2539b4931a) by Patrik Dufresne).
- Remove obsolete line from MANIFEST to avoid warning when installing. ([a049018](https://gitlab.com/ikus-soft/rdiffweb/commit/a049018b784712a7d631698691039f162098f80d) by Patrik Dufresne).
- Remove tox.ini since it doesn't work with Jenkins. ([3680988](https://gitlab.com/ikus-soft/rdiffweb/commit/3680988089600ab74711e1a5d9b788b2d36f4099) by Patrik Dufresne).
- Remove any encode_s and decode_s. ([ebbcae2](https://gitlab.com/ikus-soft/rdiffweb/commit/ebbcae2f71806439fd6667fa8b72364082403c44) by Patrik Dufresne).

### Misc

- Release 0.9.1 ([4f8dbac](https://gitlab.com/ikus-soft/rdiffweb/commit/4f8dbac02dc0c2560e46e7a403061d5eedf9c14e) by Jenkins).
- Update french translation. See pdsl/minarca#152 ([e348554](https://gitlab.com/ikus-soft/rdiffweb/commit/e3485544a242855dec9b220595a4708191ac5df8) by Patrik Dufresne).
- Try to build a nice error page with branding. pdsl/minarca#147 ([92b3467](https://gitlab.com/ikus-soft/rdiffweb/commit/92b34675026e3deaa723cf49abbb71a12c1b38c3) by Patrik Dufresne).
- Enhance browsing Folder/Files. pdsl/minarca#125 ([4d1a9a4](https://gitlab.com/ikus-soft/rdiffweb/commit/4d1a9a4a6a869126d614d53a90c4de5609dad12b) by Patrik Dufresne).
- Make use of Option in Ldap Auth plugin. ([ba918ed](https://gitlab.com/ikus-soft/rdiffweb/commit/ba918ed2b47bcb3e5b1b16238c44e443254682b4) by Patrik Dufresne).
- Allow to update user attribute without notification. ([72bdfae](https://gitlab.com/ikus-soft/rdiffweb/commit/72bdfae5d3cabf0c35ef49c760fb91f7a48ce86e) by Patrik Dufresne).
- Update french translation. ([52d49d7](https://gitlab.com/ikus-soft/rdiffweb/commit/52d49d72d3b7bec6a9638b2f85cc1d85b9ee27e0) by Patrik Dufresne).
- Handle exception when SSH key is invalid. pdsl/minarca#137 ([c521839](https://gitlab.com/ikus-soft/rdiffweb/commit/c521839ff1a4fffcebc8c774c885e0a4095630fa) by Patrik Dufresne).
- Refactor usage of Exceptions. pdsl/minarca#136 ([6850d71](https://gitlab.com/ikus-soft/rdiffweb/commit/6850d71ca43a87b605adb8c5952c844ad6a5697a) by Patrik Dufresne).
- Skip loading of JobPLugin. ([871bec3](https://gitlab.com/ikus-soft/rdiffweb/commit/871bec3c04319a19346eaa24142f35c1fd87875f) by Patrik Dufresne).
- Use minify to compile all javascript files. ([58ec5a4](https://gitlab.com/ikus-soft/rdiffweb/commit/58ec5a4eb495c9332fdb244867cdf64075463f22) by Patrik Dufresne).
- Rename the "Download ZIP" button to "Download". See pdsl/minarca#134 ([5d745b2](https://gitlab.com/ikus-soft/rdiffweb/commit/5d745b2c3486204ccd6e1381856968b1fb3530a4) by Patrik Dufresne).
- Implement notification for user attribute change. ([7f67949](https://gitlab.com/ikus-soft/rdiffweb/commit/7f679494591b590265cbaf8cd1d66650979a71f0) by Patrik Dufresne).
- Force URL encoding ISO-8859-1 in py3 and cherrypy >= 5.5.0 ([b9ba71c](https://gitlab.com/ikus-soft/rdiffweb/commit/b9ba71cb3ba79b059adf8d1a8cc8b8cdfbde39fb) by Patrik Dufresne).
- Provide a tox configuration. ([0f69915](https://gitlab.com/ikus-soft/rdiffweb/commit/0f699156eb866b76fa1be4bb574b8a5dd4ab179d) by Patrik Dufresne).
- Upgrade cherrypy version to 3.5.0 to run around a bug. ([b3074d9](https://gitlab.com/ikus-soft/rdiffweb/commit/b3074d9324b62c91faea88e643a986429859afc9) by Patrik Dufresne).
- Update docs with nginx config. ([e8771df](https://gitlab.com/ikus-soft/rdiffweb/commit/e8771df500f1f13d6541f5abf739c77c8e524a03) by Patrik Dufresne).
- Enable profiling when any --profile-* arguments is used. ([3c4a9ca](https://gitlab.com/ikus-soft/rdiffweb/commit/3c4a9ca9eb867731e4f464be31e1c882a40b06c3) by Patrik Dufresne).
- Replace login/logout page with a cherrypy tool. ([d6f6490](https://gitlab.com/ikus-soft/rdiffweb/commit/d6f6490ddf90c82d7fdf68bf63044c17e887fb4f) by Patrik Dufresne).
- Allow plugin to add extra head. ([f320b8a](https://gitlab.com/ikus-soft/rdiffweb/commit/f320b8aafd7bffdc194e1f8f8f38ac94a15a1fab) by Patrik Dufresne).
- Convert some assert statement into function call. ([5cc2b67](https://gitlab.com/ikus-soft/rdiffweb/commit/5cc2b6736fcbdff6fa8c763d9b578a30c5cbfd33) by Patrik Dufresne).
- Move jquery form submit under /ajax/ path. ([c8bc62f](https://gitlab.com/ikus-soft/rdiffweb/commit/c8bc62fdc6afd585fd05f8acea57ab6c7ea8b4db) by Patrik Dufresne).
- Make a plugin from encoding settings. ([95b0c68](https://gitlab.com/ikus-soft/rdiffweb/commit/95b0c68788be6f94e0ab17c6abba1409416e9a9e) by Patrik Dufresne).
- Make alerts messages dismissible. ([2363ae4](https://gitlab.com/ikus-soft/rdiffweb/commit/2363ae47b220448b38fb1d0781fd982306399fcd) by Patrik Dufresne).
- Sort attribute generated by attrib(). ([9f4ba14](https://gitlab.com/ikus-soft/rdiffweb/commit/9f4ba142b0f53c41176dd4282227b8b9f52a5321) by Patrik Dufresne).
- Enhance user testcases to make use of get_repo() function. ([7360109](https://gitlab.com/ikus-soft/rdiffweb/commit/736010976407a29678bb24ef41c01f30c3cf28ed) by Patrik Dufresne).
- Use get_repo() instead of repo_list in notifications testcases. ([79f57da](https://gitlab.com/ikus-soft/rdiffweb/commit/79f57da7375c8a0ea76d76fcb5887b5cc041432e) by Patrik Dufresne).
- Refactor delete_repo to be more accurate. ([2413711](https://gitlab.com/ikus-soft/rdiffweb/commit/2413711f5fe37512abc9b2fd1f3d77d0058ff411) by Patrik Dufresne).
- Replace repo_dict by get_repo(). ([9b677e7](https://gitlab.com/ikus-soft/rdiffweb/commit/9b677e735f6a187468a293eb6b2c730d6783840b) by Patrik Dufresne).
- Support remove_older by executing rdiff-backup command line. ([02fed95](https://gitlab.com/ikus-soft/rdiffweb/commit/02fed9561e599b96162fbaaecbd705d479391be9) by Patrik Dufresne).
- Raise Exception is execute() fail. ([cb162a9](https://gitlab.com/ikus-soft/rdiffweb/commit/cb162a94fa703198e02a23b649d171e3986690df) by Patrik Dufresne).
- Reverse ordering of activate and add templates. ([f569f40](https://gitlab.com/ikus-soft/rdiffweb/commit/f569f402280f939273e34645d7140091228952e7) by Patrik Dufresne).
- Create a new JobPlugin to centralize code for fixed time execution. ([2459a7c](https://gitlab.com/ikus-soft/rdiffweb/commit/2459a7c184498b83919d48854889b78fc4253bd2) by Patrik Dufresne).
- Make sure to add all `templates_content` to settings page. ([3a8a159](https://gitlab.com/ikus-soft/rdiffweb/commit/3a8a159e0a2f365f32e312ec5d7d641e1f8dc1a9) by Patrik Dufresne).
- Refactor user library again to remove get_* and set_*. ([e0be084](https://gitlab.com/ikus-soft/rdiffweb/commit/e0be08402dc728115e15512dd8b38e3281a49d15) by Patrik Dufresne).
- Update templates to set the right activate page. ([2761255](https://gitlab.com/ikus-soft/rdiffweb/commit/2761255988c47df15ef1894bf9e8a65f448bd8b4) by Patrik Dufresne).
- Use navbar-inverse instead of default. ([d3aa3e1](https://gitlab.com/ikus-soft/rdiffweb/commit/d3aa3e1c7aec0d834f7187e631df4dbdeaf4733c) by Patrik Dufresne).
- Make 'build_less' optional. ([1cd134f](https://gitlab.com/ikus-soft/rdiffweb/commit/1cd134f8ea19572685c6791b40423a8836538aca) by Patrik Dufresne).
- Return false if resource_filename doesn't exists. ([ca10884](https://gitlab.com/ikus-soft/rdiffweb/commit/ca10884c4a927bea0a1bba136213d749b66c2315) by Patrik Dufresne).
- Include all static files. ([ea7a9b5](https://gitlab.com/ikus-soft/rdiffweb/commit/ea7a9b56351cd0ad42364b4e50db70eeba159fe0) by Patrik Dufresne).
- Relayout the download button in restore folder page. ([84996d3](https://gitlab.com/ikus-soft/rdiffweb/commit/84996d36f2980bcf4672af3f74193e33b0b6fd36) by Patrik Dufresne).
- Minor cosmetic changes. ([5a32079](https://gitlab.com/ikus-soft/rdiffweb/commit/5a32079db7abba714f1122ab36f7bfbb10c6738a) by Patrik Dufresne).
- Upgrade to basic Bootstrap 3.3.6 (default theme). ([7f22e53](https://gitlab.com/ikus-soft/rdiffweb/commit/7f22e5370c0b6992f46c2846f024d406a29e4a2a) by Patrik Dufresne).
- Replace Grunt by lessc. Relocated main.css. ([c12fee9](https://gitlab.com/ikus-soft/rdiffweb/commit/c12fee9d016f0fa556d7c9002cf47c88c267b129) by Patrik Dufresne).
- Replace header_logo by a static page handler. ([c696828](https://gitlab.com/ikus-soft/rdiffweb/commit/c6968281d91b5a1f19187288f38c19512dbcaf0e) by Patrik Dufresne).
- Force content-type for static file. ([7189e67](https://gitlab.com/ikus-soft/rdiffweb/commit/7189e679bd2655b8d842eb6e360a01ce05c9a080) by Patrik Dufresne).
- Replace static by page handler. ([b2364ba](https://gitlab.com/ikus-soft/rdiffweb/commit/b2364ba31c2d30bb2699433ca2a8eebde1463d09) by Patrik Dufresne).
- Serve favicon.ico using a page handler. ([4f71186](https://gitlab.com/ikus-soft/rdiffweb/commit/4f7118623c79921f5205efb199ede569162e6040) by Patrik Dufresne).
- Replace configuration by decorator for login page. ([70979a6](https://gitlab.com/ikus-soft/rdiffweb/commit/70979a619efed9f71eb40bd015d464bf830eb170) by Patrik Dufresne).
- Move delete repo into a plugins. ([85f0681](https://gitlab.com/ikus-soft/rdiffweb/commit/85f06819276883dae78bf8a828c9fdda81fa6f64) by Patrik Dufresne).
- Replace _cp_dispatch by class decorators. ([93142b7](https://gitlab.com/ikus-soft/rdiffweb/commit/93142b72b6b2d02b877a21fe948ec7fc6d9d3882) by Patrik Dufresne).
- Enable Graphs plugin by default. ([38b8592](https://gitlab.com/ikus-soft/rdiffweb/commit/38b85925521167a681d05b769b048a14c429271f) by Patrik Dufresne).
- Minor modification to doc.md ([a302c9a](https://gitlab.com/ikus-soft/rdiffweb/commit/a302c9a04489453d09c2b4d5e2fa86b4b50c7854) by Patrik Dufresne).
- Create a markdown file to hold all documentation. See pdsl-www/#63 ([50543b2](https://gitlab.com/ikus-soft/rdiffweb/commit/50543b21a30c268b766c7da7fc76631fa7162a6e) by Patrik Dufresne).
- Compute next execution time once notifications are sent. see #3 ([0456a1d](https://gitlab.com/ikus-soft/rdiffweb/commit/0456a1dc8248c7cd04f238c6406522924ce38a2d) by Patrik Dufresne).
- Improve librdiff file statistics ([c0fa092](https://gitlab.com/ikus-soft/rdiffweb/commit/c0fa09268b1794bb6da5744e8b62ed627193ba93) by Patrik Dufresne).
- Update layouts to support configurable nav bar. ([dca3a63](https://gitlab.com/ikus-soft/rdiffweb/commit/dca3a63d746e40c9070523aa79a15e3443ea6d96) by Patrik Dufresne).
- Make sure to log the exception shown using default error page. ([fe635a1](https://gitlab.com/ikus-soft/rdiffweb/commit/fe635a1c1905412d2056af3d9f01bed0050462f0) by Patrik Dufresne).
- Continue updating error handling to avoid using ValueError. ([972b8bd](https://gitlab.com/ikus-soft/rdiffweb/commit/972b8bddf81e5e801fa5273b5ebe76c48604967f) by Patrik Dufresne).
- Replace any call to _compile_error_template by an HTTPError ([8fbbbc8](https://gitlab.com/ikus-soft/rdiffweb/commit/8fbbbc844dc1ac53e9b64c221f2a5b55011e5542) by Patrik Dufresne).
- Alway show header name in title ([ce65a3f](https://gitlab.com/ikus-soft/rdiffweb/commit/ce65a3f610f42088e15d1c063e022c3524b7b5e9) by Patrik Dufresne).
- Replace default error page by a nice one. see #17 ([935790f](https://gitlab.com/ikus-soft/rdiffweb/commit/935790f960557eb697551c0ebc087e90691fe82b) by Patrik Dufresne).
- Enhance the logging configuration. see #24 ([d7adfe6](https://gitlab.com/ikus-soft/rdiffweb/commit/d7adfe618b628ee0bc5fa0199225f0f0706b65f3) by Patrik Dufresne).
- Use UserObject as current user. Add RepoObject. ([050e11d](https://gitlab.com/ikus-soft/rdiffweb/commit/050e11d323e8d61f72ba1f7eea6d7fd535a3573e) by Patrik Dufresne).
- Replace non-breaking space (\xC2\xA0) by space. ([1de1ded](https://gitlab.com/ikus-soft/rdiffweb/commit/1de1dedb21af45768ad99d780f7893214223da6b) by Patrik Dufresne).
- Support repo without backup date. ([606f16a](https://gitlab.com/ikus-soft/rdiffweb/commit/606f16a76eb6a4674780f34845b2c1af859a4720) by Patrik Dufresne).
- Continue to enhance content-disposition. see pdsl/minarca#120 ([3fd29c9](https://gitlab.com/ikus-soft/rdiffweb/commit/3fd29c922e47a4cdee9ab7779c786fddb14937e1) by Patrik Dufresne).
- Reorganize import in filter_authentication ([4866db3](https://gitlab.com/ikus-soft/rdiffweb/commit/4866db3732a913d726d7a7f267651f043f933e13) by Patrik Dufresne).
- Set useful thread name for deamon thread ([2856a18](https://gitlab.com/ikus-soft/rdiffweb/commit/2856a18c6c2831767bd382c6cc5fa3af7e2d037d) by Patrik Dufresne).
- Improve rdwTime() ([66202c4](https://gitlab.com/ikus-soft/rdiffweb/commit/66202c4fc5942cd86bedd9e49b532fbe351f6760) by Patrik Dufresne).
- Quick implementation of UserObject. ([30f8c72](https://gitlab.com/ikus-soft/rdiffweb/commit/30f8c7246d071340c60d3261a24a370646d63b67) by Patrik Dufresne).
- Recover plugin description. Lost when migrating plugin. ([6f5b32d](https://gitlab.com/ikus-soft/rdiffweb/commit/6f5b32d285059e549710a09bb849d10ac10ee336) by Patrik Dufresne).
- Pipe archive creation. see #8 ([7d1457e](https://gitlab.com/ikus-soft/rdiffweb/commit/7d1457e7f0bc4db3e3a8cca96e2f94f2c69d2230) by Patrik Dufresne).
- Disable test_gc (because it randomly fail). ([9ebe4ff](https://gitlab.com/ikus-soft/rdiffweb/commit/9ebe4ff2322069233a971324254f0c153c574fe6) by Patrik Dufresne).
- Reorganize jinja2 template to use extends ([9c69523](https://gitlab.com/ikus-soft/rdiffweb/commit/9c695234cab99eab7f71564f266df2eef6d965b8) by Patrik Dufresne).
- Convert Yapsy plugin into entry_point plugins. ([3027007](https://gitlab.com/ikus-soft/rdiffweb/commit/3027007c38595ba8bd7fdb9cc02e2b0e663bcbbe) by Patrik Dufresne).
- Re-organize i18n ([4245771](https://gitlab.com/ikus-soft/rdiffweb/commit/4245771ecba3035292529e2919899a1849dedbfe) by Patrik Dufresne).
- Increase log level for "active/deactive" plugin. ([fc834b6](https://gitlab.com/ikus-soft/rdiffweb/commit/fc834b610e273ad669d20dfb2d87f4ed1ca08111) by Patrik Dufresne).
- Search plugin recursively. ([63798fd](https://gitlab.com/ikus-soft/rdiffweb/commit/63798fd37affcf7ae40ab9deec1220863a9f3693) by Patrik Dufresne).
- Always show templates in locations ([6702453](https://gitlab.com/ikus-soft/rdiffweb/commit/670245324efe6cbc13804c3242f6f12f643d3d5b) by Patrik Dufresne).
- Repalce deprecated warn() by warning() ([a02cf52](https://gitlab.com/ikus-soft/rdiffweb/commit/a02cf529733042516738155e052b33f68fe7d7f1) by Patrik Dufresne).
- Ignore encoding problem in spider repos ([eeb0807](https://gitlab.com/ikus-soft/rdiffweb/commit/eeb0807768cc2214b883adb3f7ac53b7219cdac1) by Patrik Dufresne).
- Update testcases.tar.gz to include a sub directory with encoding. ([364b52d](https://gitlab.com/ikus-soft/rdiffweb/commit/364b52d41130fe230185710b17be772e2d4d3544) by Patrik Dufresne).
- Exclude "static" folder from sonar analysis. ([56559f6](https://gitlab.com/ikus-soft/rdiffweb/commit/56559f60b8b517940b1c303a936a348c997b58ce) by Patrik Dufresne).
- IN PROGRESS - add {% attrib %} ([6e21d77](https://gitlab.com/ikus-soft/rdiffweb/commit/6e21d77b1e9a98ab611db75e5cbdda54082fe9fc) by Patrik Dufresne).
- Review all logger modulo (%) formatting. See #9 ([dc222b5](https://gitlab.com/ikus-soft/rdiffweb/commit/dc222b558b1928c74480840ceda5f820fa2ab8ec) by Patrik Dufresne).
- workaround babel requirement (for Tox) ([1b08521](https://gitlab.com/ikus-soft/rdiffweb/commit/1b085216df7d4ba805d67e0e46444e1022060804) by Patrik Dufresne).
- Complete review or str() and bytes() ([57ab669](https://gitlab.com/ikus-soft/rdiffweb/commit/57ab669a563047896f5cf199e8983f1524664142) by Patrik Dufresne).
- Third step to support python3. ([173eb60](https://gitlab.com/ikus-soft/rdiffweb/commit/173eb6039da3b60f0e3d63388969e46fbf03daed) by Patrik Dufresne).
- Second step to support py3 ([bd59335](https://gitlab.com/ikus-soft/rdiffweb/commit/bd59335ec221ebd26fc7cd10515bd2bf6f2ddfaa) by Patrik Dufresne).
- First step to support py3 ([1ca110e](https://gitlab.com/ikus-soft/rdiffweb/commit/1ca110ec2e84b865f2ac11c0d133d31ff1748539) by Patrik Dufresne).
- Refactor plugin ILocationsPagePlugin into ITemplateFilterPlugin. ([101b7c7](https://gitlab.com/ikus-soft/rdiffweb/commit/101b7c7367ffb67d88891ad2f1f9ffef7fd846af) by Patrik Dufresne).
- Convert update repos into core plugin. ([a706347](https://gitlab.com/ikus-soft/rdiffweb/commit/a706347e4987e579e5c402d7793b61a00b9b549f) by Patrik Dufresne).
- Start fixing spider repo auto refresh ([f1cda72](https://gitlab.com/ikus-soft/rdiffweb/commit/f1cda72f9ff8ced040867bb92508891878fc12c9) by Patrik Dufresne).
- Enhance repository header. ([892bf78](https://gitlab.com/ikus-soft/rdiffweb/commit/892bf78306e4204a8135bc0bfbc1027210821f07) by Patrik Dufresne).
- Prepare next development version ([c6015ea](https://gitlab.com/ikus-soft/rdiffweb/commit/c6015eaf531cca2cd6654695919f3e0459a09b7d) by Jenkins).
- Update russian translation. ([ca148f0](https://gitlab.com/ikus-soft/rdiffweb/commit/ca148f07aeccc9e02ce9a0e230b843585fdd046b) by Patrik Dufresne).
- Update french translation ([0161a04](https://gitlab.com/ikus-soft/rdiffweb/commit/0161a048aa45f1b155c6c9ab6a1c4a0065c83b81) by Patrik Dufresne).
- Review some loglevel. ([5abdc59](https://gitlab.com/ikus-soft/rdiffweb/commit/5abdc595eeebd0eb1451963f80b8a073547f0167) by Patrik Dufresne).

## [0.8.1](https://gitlab.com/ikus-soft/rdiffweb/tags/0.8.1) - 2015-12-21

<small>[Compare with v0.7.0](https://gitlab.com/ikus-soft/rdiffweb/compare/v0.7.0...0.8.1)</small>

### Added

- Add setup.py.bak and .eggs/ to git ignore. ([edbe6c1](https://gitlab.com/ikus-soft/rdiffweb/commit/edbe6c1b43c6ecfa008f445f5e086c38d3f48206) by Patrik Dufresne).
- Add logined notification. ([ab11ccd](https://gitlab.com/ikus-soft/rdiffweb/commit/ab11ccdb668d1bc09a3ca8eb52ee47c07b0f762f) by Patrik Dufresne).
- Add msapplication meta tag (for Win8 pinning) see #57 ([3acc49a](https://gitlab.com/ikus-soft/rdiffweb/commit/3acc49a276f638f0588d50f051aa2079340744bc) by Patrik Dufresne).
- Add some testcases for user.py. ([f2b7e26](https://gitlab.com/ikus-soft/rdiffweb/commit/f2b7e269dcec56f3383804440eeb0b31b40217aa) by Patrik Dufresne).
- Add a bit of logging into page_settings. ([6f6d001](https://gitlab.com/ikus-soft/rdiffweb/commit/6f6d0013f3956c04a50d7316b819becd9b866145) by Patrik Dufresne).
- Add assertion in user.py ([9816d94](https://gitlab.com/ikus-soft/rdiffweb/commit/9816d9439827ed9bebd72fa889e32c7aab686fc2) by Patrik Dufresne).
- Add nosetests config to setup.cfg ([183b069](https://gitlab.com/ikus-soft/rdiffweb/commit/183b06993bfdfb1565529d609d00b5c58ba9f0f3) by Patrik Dufresne).
- Add log line when login failed. ([e414f59](https://gitlab.com/ikus-soft/rdiffweb/commit/e414f597b9d86401e82889171c8056564ba89e76) by Patrik Dufresne).
- Add ip and username in log. ([25923f5](https://gitlab.com/ikus-soft/rdiffweb/commit/25923f5ac922d7c3a092ec03a91c0c4e46f0fd64) by Patrik Dufresne).
- Add '+' to create authorized_keys if missing. ([fdd2773](https://gitlab.com/ikus-soft/rdiffweb/commit/fdd277365b0b8649040138b144351a80ed57bbf4) by Patrik Dufresne).
- Add new "settings" tabs to change encoding. Ref #52 ([280c616](https://gitlab.com/ikus-soft/rdiffweb/commit/280c6168d5891ad872cfe9855e1ece7f42d90a3e) by Patrik Dufresne).
- Add item prop to repositories. ([291903f](https://gitlab.com/ikus-soft/rdiffweb/commit/291903f1bf3ed391c02e9cc544f1ebcec53dafcd) by Patrik Dufresne).
- Add ru translation received by Евгений Максимов <me@vragam.net> ([a10af25](https://gitlab.com/ikus-soft/rdiffweb/commit/a10af255008c606203f94f132b78514693ccf2bb) by Patrik Dufresne).
- Add RLock to SQLite user db. ([a0f1c0d](https://gitlab.com/ikus-soft/rdiffweb/commit/a0f1c0d47d981ff0460bb2bba1404be205ad25e4) by Patrik Dufresne).
- Add options to customize the welcome message. ([e2cb502](https://gitlab.com/ikus-soft/rdiffweb/commit/e2cb5024eb7211b1bb7a5defebb6375c0b65f927) by Patrik Dufresne).
- Add default config for UserPrefs plugins. ([c6dad1b](https://gitlab.com/ikus-soft/rdiffweb/commit/c6dad1b15d636aabd600612add50c3044cea422d) by Patrik Dufresne).
- Add threadname to logging line. ([264d792](https://gitlab.com/ikus-soft/rdiffweb/commit/264d792e39915187fc07fb78c78c1e39547973cc) by Patrik Dufresne).
- Add itemprop=id for sshkeys. ([509542b](https://gitlab.com/ikus-soft/rdiffweb/commit/509542bcebdef1a40f59df45f9b7e25296976b9e) by Patrik Dufresne).
- Add email validation ([f8f43aa](https://gitlab.com/ikus-soft/rdiffweb/commit/f8f43aac3909edb0e0311e14c6cb663c4797a866) by Patrik Dufresne).
- Add SSH Keys plugin to manage authorized_keys ([4a50e5d](https://gitlab.com/ikus-soft/rdiffweb/commit/4a50e5dafe6ff5d7b5ec6a7e1266c1c6f201d251) by Patrik Dufresne).
- Add 'START' and 'STOP' log line to clearly identify startup. ([5c99831](https://gitlab.com/ikus-soft/rdiffweb/commit/5c99831c43a8e58f7e8943ed767cd98fd4ac5c33) by Patrik Dufresne).
- Add english mo file for default translation. ([55f8374](https://gitlab.com/ikus-soft/rdiffweb/commit/55f837475d4eb14cf0560e8ce7db078bb0baa73a) by Patrik Dufresne).
- Add babel to requirements.txt ([5199c61](https://gitlab.com/ikus-soft/rdiffweb/commit/5199c614c624496e6acd58a98c65a4b299e9eda1) by Patrik Dufresne).
- Add requirements.txt ([a57c1be](https://gitlab.com/ikus-soft/rdiffweb/commit/a57c1be32493364c76c8fb08104efae2688b6095) by Patrik Dufresne).
- Add microdata to plugin page. ([951a6f2](https://gitlab.com/ikus-soft/rdiffweb/commit/951a6f26a870e80ee693f4fdcdd295cd39d1d0aa) by Patrik Dufresne).
- Add comments to encode_s() ([4df1cfc](https://gitlab.com/ikus-soft/rdiffweb/commit/4df1cfc7d322449e44f51612dbf06f7908789b90) by Patrik Dufresne).

### Fixed

- Fix change_dates ordering. see pdsl/minarca#97 ([fab4726](https://gitlab.com/ikus-soft/rdiffweb/commit/fab4726ba81fe5a534e201c240e654cb49b78192) by Patrik Dufresne).
- Fix password change validation. ([c7b75f0](https://gitlab.com/ikus-soft/rdiffweb/commit/c7b75f0b8aad144200575e0d5259d96d669b7520) by Patrik Dufresne).
- Fix support for 'LdapAllowPasswordChange' option. ([03e1b34](https://gitlab.com/ikus-soft/rdiffweb/commit/03e1b3443592ff042a357c9fd704206eb494ba63) by Patrik Dufresne).
- Fix ldap testcases. ([cccde6e](https://gitlab.com/ikus-soft/rdiffweb/commit/cccde6eea255984866944df99992e721844e004a) by Patrik Dufresne).
- Fix exists() vs has_password() / db vs store. ([9badfcf](https://gitlab.com/ikus-soft/rdiffweb/commit/9badfcff2ccedb9eac9f97a828a4236b678cd5dc) by Patrik Dufresne).
- Fix creation of admin user when creating database. ([a9a6cea](https://gitlab.com/ikus-soft/rdiffweb/commit/a9a6cea3b0aeb37e615a139d3f887a19807900cb) by Patrik Dufresne).
- Fix password check unicode. ([1871c32](https://gitlab.com/ikus-soft/rdiffweb/commit/1871c32b00c9742cb70b4219300292e5da9ba467) by Patrik Dufresne).
- Fix set_info() call in admin page. ([3c76417](https://gitlab.com/ikus-soft/rdiffweb/commit/3c76417409bfbe4252839b5c247e4e28078d7701) by Patrik Dufresne).
- Fix Ldap get user attribute ([db38c5b](https://gitlab.com/ikus-soft/rdiffweb/commit/db38c5b7dc4e88967c226e766ed0860bd0700ad0) by Patrik Dufresne).
- Fix duplicate get_user_root method ([426d8dd](https://gitlab.com/ikus-soft/rdiffweb/commit/426d8dd7c141bb6f012859bbbd8b45857864db08) by Patrik Dufresne).
- Fix change email. ([cde996e](https://gitlab.com/ikus-soft/rdiffweb/commit/cde996ec3e96cd304051b47fee750a48ce0a7888) by Patrik Dufresne).
- Fix allow add user if missing. ([06c642b](https://gitlab.com/ikus-soft/rdiffweb/commit/06c642bf8e43d1fa8da3957b04d2d1e16d28ba52) by Patrik Dufresne).
- Fix ldap unicode vs str. ([1d3d14e](https://gitlab.com/ikus-soft/rdiffweb/commit/1d3d14ed4045e802a7d1d12e6eefff4013e52ca2) by Patrik Dufresne).
- Fix test_ldap ([bcb9d04](https://gitlab.com/ikus-soft/rdiffweb/commit/bcb9d041a16cded20aa2614d64aa00466947a20b) by Patrik Dufresne).
- Fix tests_require ([925fc0a](https://gitlab.com/ikus-soft/rdiffweb/commit/925fc0a91800b77e6598fbd4f24e3e5850602233) by Patrik Dufresne).
- Fix ssh keys plugin to create file and directory. ([cb946e0](https://gitlab.com/ikus-soft/rdiffweb/commit/cb946e0cac9068229e5a6d76811c372daa51df2c) by Patrik Dufresne).
- Fix issue related to SSH Prefs page not being available. ([312ce00](https://gitlab.com/ikus-soft/rdiffweb/commit/312ce0002925fa6ca95dd1f26fcdfb060b7e7640) by Patrik Dufresne).
- Fix path validation. ([449da47](https://gitlab.com/ikus-soft/rdiffweb/commit/449da478105cb3c6dfcc5529bc65ef8aa69bc982) by Patrik Dufresne).
- Fix ZIP operation to use ISO-8859-1 encoding for filenames. Fix #55 ([f2703c3](https://gitlab.com/ikus-soft/rdiffweb/commit/f2703c3e4967a3bf4b44f5b5dcf85bacff5da7cb) by Patrik Dufresne).
- Fix _ import in db_sqlite ([e66df94](https://gitlab.com/ikus-soft/rdiffweb/commit/e66df9490a67b737d0139f5530fc071840b84357) by Patrik Dufresne).
- Fix get_config_bool to support true and True. ([09fbfc1](https://gitlab.com/ikus-soft/rdiffweb/commit/09fbfc1f574ceec01bf79fb0d6c8ba27c9c32f69) by Patrik Dufresne).
- Fix some "major" issues repported by Sonarqube. ([8cd0c6d](https://gitlab.com/ikus-soft/rdiffweb/commit/8cd0c6df54b110ce772c38aa50e455794b0f4f46) by Patrik Dufresne).
- Fix assert statement. ([3caab95](https://gitlab.com/ikus-soft/rdiffweb/commit/3caab959162a9283120ed44ebcec4c815b4e0e37) by Patrik Dufresne).

### Changed

- Change log level for "user not logged in" ([0626ee5](https://gitlab.com/ikus-soft/rdiffweb/commit/0626ee5bf7a510ca1fa05674729ee12ea655cdc7) by Patrik Dufresne).
- Change default filesize format to use GiB and not GB ([e1ed4f8](https://gitlab.com/ikus-soft/rdiffweb/commit/e1ed4f8940cf9d5e28c8edb66cf5deb39db1c47d) by Patrik Dufresne).
- Change import to "from rdiffweb import ..." ([df37e7e](https://gitlab.com/ikus-soft/rdiffweb/commit/df37e7e0490fcb9d2072c2d986842ef186f5102d) by Patrik Dufresne).

### Removed

- Remove initscript, default config and logrotate from setup.py. ([86e6b10](https://gitlab.com/ikus-soft/rdiffweb/commit/86e6b10096a647bc397773ee2673ddb094f915f9) by Patrik Dufresne).
- Remove olbolete import from librdiff. ([4452fb7](https://gitlab.com/ikus-soft/rdiffweb/commit/4452fb7fa54d08ee84dab6542817a1ccfa16f858) by Patrik Dufresne).
- Remove setup page and auto configure rdiffweb when required. ([fb60c0e](https://gitlab.com/ikus-soft/rdiffweb/commit/fb60c0ee85015e5b3cd06ce63a74ae28422d37df) by Patrik Dufresne).
- Remove file_statistics cache replace by pure python implementation. ([dcabc05](https://gitlab.com/ikus-soft/rdiffweb/commit/dcabc05e960c29aa77b6949bbce097abbbdb5803) by Patrik Dufresne).
- Remove obsolete TODO related to password validation. ([662dc2f](https://gitlab.com/ikus-soft/rdiffweb/commit/662dc2f5548ce61fffc54149a758a40d872e217d) by Patrik Dufresne).
- Remove unused import from db_ldap plugin. ([28e055f](https://gitlab.com/ikus-soft/rdiffweb/commit/28e055f96d202cf894f7a5c86af7a650b134fd02) by Patrik Dufresne).
- Remove obsolete rdw_config import. ([76287a2](https://gitlab.com/ikus-soft/rdiffweb/commit/76287a2780f6e10583a9884eab1cfa6ae6de455f) by Patrik Dufresne).
- Remove obsolete https filter. ([a0a334e](https://gitlab.com/ikus-soft/rdiffweb/commit/a0a334e58f42ff39a15b4fb6fd059ce340ca12ba) by Patrik Dufresne).
- Remove hardcoded version. Get it from package info. ([745ab2a](https://gitlab.com/ikus-soft/rdiffweb/commit/745ab2a237269ade98e562bfb2e3e378413a5884) by Patrik Dufresne).
- Remove ref url from readme file. ([ac81832](https://gitlab.com/ikus-soft/rdiffweb/commit/ac81832835c1181f51ad79898ba8fdde61a95d4a) by Patrik Dufresne).

### Misc

- Release 0.8.1 ([0dadf52](https://gitlab.com/ikus-soft/rdiffweb/commit/0dadf52b2babb3b6925c4d1738766c7b4dcfdc74) by Jenkins).
- Set owner for authorized_keys. pdsl/minarca#100 ([d9e8662](https://gitlab.com/ikus-soft/rdiffweb/commit/d9e866234a0a300bbe103c21bba861c4b3c6907b) by Patrik Dufresne).
- refactor some code to use list comprehension syntax in librdiff ([d901028](https://gitlab.com/ikus-soft/rdiffweb/commit/d90102871bf2aa7a3a5028b8e0a4752963ca70fa) by Patrik Dufresne).
- Reffactore abit arround restore_dates. ([6759ef2](https://gitlab.com/ikus-soft/rdiffweb/commit/6759ef25247d27d8502ccde9eb0b512d5870bbdf) by Patrik Dufresne).
- Send logined notification at the right time. ([d6b0f62](https://gitlab.com/ikus-soft/rdiffweb/commit/d6b0f62d864cb2206b8a52f633de54716f03a74a) by Patrik Dufresne).
- Move test.py to make it accessible to plugins tests. ([b6c7cd8](https://gitlab.com/ikus-soft/rdiffweb/commit/b6c7cd8c3ed8eb21344815f6d669ec1aac799494) by Patrik Dufresne).
- Improve in_progress detection -- verify if PID is running ([4f71a21](https://gitlab.com/ikus-soft/rdiffweb/commit/4f71a21663e78050492796d1cc4dcc15f777143f) by Patrik Dufresne).
- Ignore nosetests.xml and coverage.xml ([974ab7e](https://gitlab.com/ikus-soft/rdiffweb/commit/974ab7ea611892ca21ea7f867f5d5ff78750b652) by Patrik Dufresne).
- Support translated Welcome message. ([cee1f9a](https://gitlab.com/ikus-soft/rdiffweb/commit/cee1f9a7b326eac98781c78453e25c530344550d) by Patrik Dufresne).
- Minor formating fix in page_main. ([e9d3f16](https://gitlab.com/ikus-soft/rdiffweb/commit/e9d3f16877f5cc49138c0972b6fe9aebdd606811) by Patrik Dufresne).
- Make sure to return a single home directory value if multipel value are return by LDAP. ([1c8160f](https://gitlab.com/ikus-soft/rdiffweb/commit/1c8160fe455719c577b4d9537c6a08a70b495a21) by Patrik Dufresne).
- Reffactor getter / setter related to database. ([596a4b3](https://gitlab.com/ikus-soft/rdiffweb/commit/596a4b37cbee58ff42ae72050f3329b7b5d8429b) by Patrik Dufresne).
- Update default configuration. Remove obsolete UserDB option. ([dc06884](https://gitlab.com/ikus-soft/rdiffweb/commit/dc06884bc6663909a571a358c58f0a2ab0b3cbad) by Patrik Dufresne).
- Reffactor RdiffApp to implement Application directly. ([4e98308](https://gitlab.com/ikus-soft/rdiffweb/commit/4e983088adfbf8aa394ce8183418acd7b4727458) by Patrik Dufresne).
- Refactor rdw_spider_repos. ([b8b7341](https://gitlab.com/ikus-soft/rdiffweb/commit/b8b73415f66feadb855e226bee09a88b937eb776) by Patrik Dufresne).
- Refactor user & password system ([933c3b0](https://gitlab.com/ikus-soft/rdiffweb/commit/933c3b03235ca8aeb83e2e0afb708ea4147c3b08) by Patrik Dufresne).
- Corrigé orthographe ligne 597 ([3342834](https://gitlab.com/ikus-soft/rdiffweb/commit/33428344932da1035437146dc84f75249c88733c) by Annik Dufresne).
- Try to support 'X-Forwarded-For' header. ([745ec5c](https://gitlab.com/ikus-soft/rdiffweb/commit/745ec5c6745ee80f0454a10b6ea52ab0acb5cdf5) by Patrik Dufresne).
- Update french translation. ([a7a7a23](https://gitlab.com/ikus-soft/rdiffweb/commit/a7a7a239885a231f99c48bfd9658dbb0bb124ba7) by Patrik Dufresne).
- Try to fix encoding normalization. ([0c117e4](https://gitlab.com/ikus-soft/rdiffweb/commit/0c117e41f93b118edb632e5870509b22628443cf) by Patrik Dufresne).
- Allow HTML in "WelcomeMsg". Ref #76 ([49eb8cc](https://gitlab.com/ikus-soft/rdiffweb/commit/49eb8cc5426debd6f392e17fd09d298ad4d2945f) by Patrik Dufresne).
- Minor appearance fixes. ([017f469](https://gitlab.com/ikus-soft/rdiffweb/commit/017f46935647258366b370a27e7bc13607185466) by Patrik Dufresne).
- Allow user to delete repository. ([276451d](https://gitlab.com/ikus-soft/rdiffweb/commit/276451d2ca85ae8defd022dc907fba5efaacea8c) by Patrik Dufresne).
- Minor apperance modification. ([d7f9802](https://gitlab.com/ikus-soft/rdiffweb/commit/d7f98028962dfdff8c7a0a2da2ee3572b83cb523) by Patrik Dufresne).
- Enhance loglevel for some low level logs. ([176e8bc](https://gitlab.com/ikus-soft/rdiffweb/commit/176e8bcd21e06caa032213195053a7ed32da6262) by Patrik Dufresne).
- Reffactor browsing view a bit (to introduce Settings) Ref #52 #57 ([ef6958b](https://gitlab.com/ikus-soft/rdiffweb/commit/ef6958b1c83235a2ec7002585e595b1735fae1b3) by Patrik Dufresne).
- Update translations. ([f226ad6](https://gitlab.com/ikus-soft/rdiffweb/commit/f226ad6a61e8add3a9e7effa5bf7d1f6bed85446) by Patrik Dufresne).
- Update translations ([3c46884](https://gitlab.com/ikus-soft/rdiffweb/commit/3c46884b7344841bd1f92ec07bad8cfb40b0318c) by Patrik Dufresne).
- Provide a default info message if userprefs are not availables. ([d27d5b2](https://gitlab.com/ikus-soft/rdiffweb/commit/d27d5b29c7cf09cb505b3a783f2054daf840c3f9) by Patrik Dufresne).
- Use SQLite UserDB by default. Fix default configuration file. ([03bed4b](https://gitlab.com/ikus-soft/rdiffweb/commit/03bed4b629d4bf0ca63ca0fc9918634e1cc5b810) by Patrik Dufresne).
- Minor reffactoring arround _recursive_tar() and _recursive_zip() ([541fbc0](https://gitlab.com/ikus-soft/rdiffweb/commit/541fbc00c3a991ceb4ce14c38cf1aae23bbb38b7) by Patrik Dufresne).
- Reffactoring replace remove_dir() by shutil.rmtree() ([0919901](https://gitlab.com/ikus-soft/rdiffweb/commit/091990105ee039da3422a71ead2b7b4235dff977) by Patrik Dufresne).
- Minor reffactoring in librdiff: pre-sort the increments in reverse order. Simplify some if .. then .. else ([917de45](https://gitlab.com/ikus-soft/rdiffweb/commit/917de454f1ba890d774275c66f1b17b9bb1facf8) by Patrik Dufresne).
- Set a error page to workarround encoding in error in cherrypy. ([53a90e3](https://gitlab.com/ikus-soft/rdiffweb/commit/53a90e318560a3a79dd68a296a71fa98c8a7d850) by Patrik Dufresne).
- Correct typo in log message. ([6b6954c](https://gitlab.com/ikus-soft/rdiffweb/commit/6b6954cd006d184ca57fc2f22f9f03eb663f93a1) by Patrik Dufresne).
- Correction to the temp file name generate to use a prefix. ([66eb912](https://gitlab.com/ikus-soft/rdiffweb/commit/66eb9121284e8f138df6220982219c3982a77bc3) by Patrik Dufresne).
- Use weakref in librdiff in attempt to fix memoryleak. refs #52 ([dce8282](https://gitlab.com/ikus-soft/rdiffweb/commit/dce82820dd32366b2930140f0f13c922e04f2bcb) by Patrik Dufresne).
- Correct som PEP8 warnings in librdiff. ([0038b92](https://gitlab.com/ikus-soft/rdiffweb/commit/0038b92b34d8440782c588cdf937f4869e0c3b40) by Patrik Dufresne).
- Prefix temp directory with rdiffweb. ([a8037e0](https://gitlab.com/ikus-soft/rdiffweb/commit/a8037e0f079294d4d61137cff71041427323edf3) by Patrik Dufresne).
- Update MANIFEST.in ([2be6eed](https://gitlab.com/ikus-soft/rdiffweb/commit/2be6eed3aed59ff485d90fbca33ac51cb62f64e2) by Patrik Dufresne).
- Replace usage of package_data by MANIFEST.in ([bc473e4](https://gitlab.com/ikus-soft/rdiffweb/commit/bc473e46abde35907bb8c55d6aca6ffd3fcec1eb) by Patrik Dufresne).
- Localize some string related to password validation. ([19c3edd](https://gitlab.com/ikus-soft/rdiffweb/commit/19c3eddde003a4c9cfe1923f54ce9e93e6f6ebdc) by Patrik Dufresne).
- Correct multiple PEP8 warning. ([8ba9101](https://gitlab.com/ikus-soft/rdiffweb/commit/8ba91014040f88de0fb32355c72c9c5174bda360) by Patrik Dufresne).
- Don't check SSH key length in autorizedkeys. Use Crypto to get key length. Correct field name in template: comment -> title. ([9653a5f](https://gitlab.com/ikus-soft/rdiffweb/commit/9653a5fe3826bcbcf91b824749fe35c7d5271437) by Patrik Dufresne).
- Rename macro form_confirm to delete_confirm() ([ae7c188](https://gitlab.com/ikus-soft/rdiffweb/commit/ae7c188a174bf2e0ee6db4661ec051de7997920b) by Patrik Dufresne).
- Minor modifications to modal dialog. ([6149ee7](https://gitlab.com/ikus-soft/rdiffweb/commit/6149ee703f9c8d18fd69f854261d8b3237b2d6fd) by Patrik Dufresne).
- Set cherrypy max_request_body_size to 2MiB to increase security. ([4da6223](https://gitlab.com/ikus-soft/rdiffweb/commit/4da622316fc106ddf3480644a983e0d995d29a11) by Patrik Dufresne).
- Generalize the delete button with confirmation. ([ca17413](https://gitlab.com/ikus-soft/rdiffweb/commit/ca174138c41806cf235d81560b031b15ed831491) by Patrik Dufresne).
- Rename `model_dialog` to `model_dialog`. ([0bacaa9](https://gitlab.com/ikus-soft/rdiffweb/commit/0bacaa91e9144481969b9479ba2228beb327af91) by Patrik Dufresne).
- Create a CurrentUser object to lazy load data about current user. Refactor the preferences page to use plugins architecture. ([898c522](https://gitlab.com/ikus-soft/rdiffweb/commit/898c5223df9e520209736f01840913c438520206) by Patrik Dufresne).
- Again, try to handle the case when no UserDB plugin is available. ([2beee62](https://gitlab.com/ikus-soft/rdiffweb/commit/2beee6214645cf2a1c19eef770aed8263aee0007) by Patrik Dufresne).
- Update rdw_plugins to add more logging. Also avoid to activate the plugins twice. ([12c6788](https://gitlab.com/ikus-soft/rdiffweb/commit/12c67886673163dc6bc614a33784827f6917b6ff) by Patrik Dufresne).
- Enhance the error message when UserDB is miss configured. ([29ae2e3](https://gitlab.com/ikus-soft/rdiffweb/commit/29ae2e340a6fff0b2afab748ffcbdc5531a31261) by Patrik Dufresne).
- Dump memory when receiving SIGUSR2. ([6e8ff70](https://gitlab.com/ikus-soft/rdiffweb/commit/6e8ff7084247c6016c6b4d2da21bc00242248d61) by Patrik Dufresne).
- Make sure to send bytes to yapsy. ([207c3f8](https://gitlab.com/ikus-soft/rdiffweb/commit/207c3f8ae742898a1887d5c508d7e06d7ad0f0ac) by Patrik Dufresne).
- Handle plugin loading when one plugin is invalid. ([b24fa92](https://gitlab.com/ikus-soft/rdiffweb/commit/b24fa92448516bb98318add061d8d1f249fc84c5) by Patrik Dufresne).
- For plugin architecture, change the translation loading to load plugins translation too. ([6376534](https://gitlab.com/ikus-soft/rdiffweb/commit/637653484edcf880b6cf51a5aa691e80d044e060) by Patrik Dufresne).
- Reformat the setup.py ([f5065d9](https://gitlab.com/ikus-soft/rdiffweb/commit/f5065d9aed2a017e2436906ec9d53b58c1bd28fe) by Patrik Dufresne).
- Set plugin version to 0.8.0 (not 8.0) ([94f0169](https://gitlab.com/ikus-soft/rdiffweb/commit/94f016971502f610148dfc0a98b7215e37303387) by Patrik Dufresne).
- Correct english word in .conf ([7d0c087](https://gitlab.com/ikus-soft/rdiffweb/commit/7d0c0871669b619b163ca3817435d42227a18f59) by Patrik Dufresne).
- Bump version to 0.8.0 ([624fb9a](https://gitlab.com/ikus-soft/rdiffweb/commit/624fb9aabcf1f16418b07fdf338617011999048d) by Patrik Dufresne).
- Move forward a plugin architecture. First implementation include UserDB plugins: LDAP and SQLite. MySQL is on the way. ([f667ef6](https://gitlab.com/ikus-soft/rdiffweb/commit/f667ef6eab2564ccf697aec6c9ad86d3df352a80) by Patrik Dufresne).
- Correct librdiff to avoid encoding problem during logging. ([78a32f7](https://gitlab.com/ikus-soft/rdiffweb/commit/78a32f7f059084cc7788018f2560745a5eaae9f8) by Patrik Dufresne).
- Correct i18n to fallback when translation is not available to current resquest/response. ([aceaae0](https://gitlab.com/ikus-soft/rdiffweb/commit/aceaae09c0b6015599ee97f3625abf032510da8e) by Patrik Dufresne).
- Correct basic auth (for RSS feed). ([0c0d0ba](https://gitlab.com/ikus-soft/rdiffweb/commit/0c0d0ba6ef344cc4fb03c4b7961cb7e69ce5a2ca) by Patrik Dufresne).
- Update README.md - add update-rc command line ([37dc6f6](https://gitlab.com/ikus-soft/rdiffweb/commit/37dc6f699a5067ef381fcc2498a267a04e836421) by Patrik Dufresne).
- Update README.md - add rdiff-backup to apt-get ([679c49a](https://gitlab.com/ikus-soft/rdiffweb/commit/679c49a0e595b9b261f5f1987101139d71eb8076) by Patrik Dufresne).
- Cache configuration setting. Use unicode string in every module. ([07e0230](https://gitlab.com/ikus-soft/rdiffweb/commit/07e02309738a98a199f0c183d37ecde7db36b4a7) by Patrik Dufresne).

## [v0.7.0](https://gitlab.com/ikus-soft/rdiffweb/tags/v0.7.0) - 2015-03-31

<small>[Compare with v0.6.5](https://gitlab.com/ikus-soft/rdiffweb/compare/v0.6.5...v0.7.0)</small>

### Added

- Add new string to translation. ([d100256](https://gitlab.com/ikus-soft/rdiffweb/commit/d10025654f19059874a72ac04911889b929f9369) by Patrik Dufresne).
- Add python-babel to list of dependencies to compile the translation. ([d423ef9](https://gitlab.com/ikus-soft/rdiffweb/commit/d423ef970101c67cfd5b9208718682651b9ccc39) by Patrik Dufresne).
- Add annotations to avoid error in eclipse. ([44a86e6](https://gitlab.com/ikus-soft/rdiffweb/commit/44a86e68bd21770ca44393e82be2d4666193899a) by Patrik Dufresne).
- setup.py: Add french translation file to package data ([cae68cf](https://gitlab.com/ikus-soft/rdiffweb/commit/cae68cf8ebed31bb1cf4fe0aa1eb3014d76e5a41) by Morgan Peyre).
- Add "tempdir" configuration parameter to relocate where to restore data. ([83ed97b](https://gitlab.com/ikus-soft/rdiffweb/commit/83ed97bb99f1e9cf33344f4dcdaf26c22afde72c) by Patrik Dufresne).
- Add copyright statement where missing. Update satement to 2014. ([0b1664d](https://gitlab.com/ikus-soft/rdiffweb/commit/0b1664dfc6bcab12bb69ecd6c4c9c3df7c425263) by Patrik Dufresne).
- Add "id" attribute to login form. Will be used as a token for testing. ([6eba666](https://gitlab.com/ikus-soft/rdiffweb/commit/6eba666e6629acc32e7d4b8c720049f0b5cd9926) by Patrik Dufresne).
- Add new fontello icons. ([ee83aaf](https://gitlab.com/ikus-soft/rdiffweb/commit/ee83aaf18fc37c0ab59f45a31454ec7a89a2242d) by Patrik Dufresne).
- Add logging error to page restore. ([e038dd6](https://gitlab.com/ikus-soft/rdiffweb/commit/e038dd63c4729e2d5ed9b6451f1c847d676beb01) by Patrik Dufresne).

### Fixed

- Fix LDAP TLS. ([be52cc5](https://gitlab.com/ikus-soft/rdiffweb/commit/be52cc5c54683d5a06792937f708a78972d6f11e) by Patrik Dufresne).
- Fix init script. Fix problem related to logs, background process. ([49048b2](https://gitlab.com/ikus-soft/rdiffweb/commit/49048b248fe9eabded27f85ad053000cc276783e) by Patrik Dufresne).
- FIX installation instructions in README ([a334302](https://gitlab.com/ikus-soft/rdiffweb/commit/a3343028a9a3e01d982ce1d1464787fe91bae743) by Morgan Peyre).
- Fix to support "null" dates. ([7639f99](https://gitlab.com/ikus-soft/rdiffweb/commit/7639f99c5485fd1410f7512d0b3c1acc522c9dd1) by Patrik Dufresne).
- Fix tempdir encoding. ([2fade7a](https://gitlab.com/ikus-soft/rdiffweb/commit/2fade7a31e16574447741987ff07f23542349554) by Patrik Dufresne).
- Fix login redirect for edge cases when url need quote. Redirect doesn't work for non-utf-8 chars. ([39db2d0](https://gitlab.com/ikus-soft/rdiffweb/commit/39db2d073c9214c6c57735b05d15c8ee9d6f52b5) by Patrik Dufresne).
- Fix setup to include javascripts. ([f3a5127](https://gitlab.com/ikus-soft/rdiffweb/commit/f3a512731e1c7c0f3aa1a81809429591b816e5bc) by Patrik Dufresne).
- Fix warning reported by pep8 ([3f0d0d9](https://gitlab.com/ikus-soft/rdiffweb/commit/3f0d0d9f4b40cb0fa9ced32674ddf6aa4dc67e81) by Patrik Dufresne).
- Fix restore to delete temporary directory when download is complete. ([75b8f40](https://gitlab.com/ikus-soft/rdiffweb/commit/75b8f40a95832572f13d5a8e487b7314819b1ef6) by Patrik Dufresne).
- Fix sorting to display directory first. ([ff028f1](https://gitlab.com/ikus-soft/rdiffweb/commit/ff028f178835ae42ac566075d91033d6e6af517c) by Patrik Dufresne).
- Fix other encoding issue. ([e708105](https://gitlab.com/ikus-soft/rdiffweb/commit/e708105b5f227aa85027c54306c501b922a60c7e) by Patrik Dufresne).
- Fix filesize for quoted path. ([5b93b9a](https://gitlab.com/ikus-soft/rdiffweb/commit/5b93b9abbf2ca04096183b4ce0266ec442862596) by Patrik Dufresne).
- Fix minor presentation issue. ([1b80e5b](https://gitlab.com/ikus-soft/rdiffweb/commit/1b80e5b3f7286694d46f428eeff17acee2709d32) by Patrik Dufresne).
- Fix indentation to 4 space. Run autopep8 to fix most formatting. ([dec71ae](https://gitlab.com/ikus-soft/rdiffweb/commit/dec71ae7a87c0d93818b951e42c001ec03abbdd0) by Patrik Dufresne).
- Fix encoding support for file and folder restore. ([7aacdbd](https://gitlab.com/ikus-soft/rdiffweb/commit/7aacdbdaf3fe5837d927a5fe0b59ddfec9e25d66) by Patrik Dufresne).
- Fix encoding issue when creating archive ([fd229be](https://gitlab.com/ikus-soft/rdiffweb/commit/fd229be49aa5b08e7e48cd0f55a63c8329e946e0) by Patrik Dufresne).

### Changed

- Change wget download URL ([e0c42c0](https://gitlab.com/ikus-soft/rdiffweb/commit/e0c42c00919673d3d735e49d74ab8dad906f5dac) by Patrik Dufresne).
- Change logrotate configuration to copytruncate the file. ([e1ea067](https://gitlab.com/ikus-soft/rdiffweb/commit/e1ea06715a8b2dc91b2363d8aef3748518696d2c) by Patrik Dufresne).
- Change the navigation layout to avoid showing bootstrap menu button in loging page. Fix #40 ([b8ecbd4](https://gitlab.com/ikus-soft/rdiffweb/commit/b8ecbd48708c7575ca60113d5011a53362a30e87) by Patrik Dufresne).
- Change filter setup to redirect users to setup page if no user in database. ([5018221](https://gitlab.com/ikus-soft/rdiffweb/commit/50182215184cc8f4402ad88cc008b17351814b88) by Patrik Dufresne).
- Change the setup to create a default admin users. ([e9fa9f6](https://gitlab.com/ikus-soft/rdiffweb/commit/e9fa9f60abbe844f98ebee251b1c4e58493b523c) by Patrik Dufresne).
- Change authentication filter to redirect to /login/. ([4452a59](https://gitlab.com/ikus-soft/rdiffweb/commit/4452a596e60e117b09f4f86e274f60479d6ca3f6) by Patrik Dufresne).
- Change GUI to bootstrap. Update templating engine to jinja2 ([2183a35](https://gitlab.com/ikus-soft/rdiffweb/commit/2183a3596f1d09465a5e21e1e8099704278772c8) by Patrik Dufresne).

### Removed

- Remove userdb cache. Ref #38 ([8f1efe5](https://gitlab.com/ikus-soft/rdiffweb/commit/8f1efe5393bc5953e9ee166f5edac91a58ebc8ce) by Patrik Dufresne).
- Remove COUCOU logs ;-) ([803849b](https://gitlab.com/ikus-soft/rdiffweb/commit/803849b9c63c84d973572de713d6f8b0a49d9850) by Patrik Dufresne).
- Remove reference to "rdiffweb-config". ([730bd38](https://gitlab.com/ikus-soft/rdiffweb/commit/730bd38e087d2259271c3f05bd7bb7309bedcf20) by Patrik Dufresne).
- Remove obsolete page error. ([b70bb65](https://gitlab.com/ikus-soft/rdiffweb/commit/b70bb65b2b68344a787923b83f64f08751ca5ab2) by Patrik Dufresne).
- Remove zip vs tar preference. Allow user to select when restoring. Fix #23 ([6fb8c93](https://gitlab.com/ikus-soft/rdiffweb/commit/6fb8c93891f2f97375a3ed2e1d2dbce6b4975d8d) by Patrik Dufresne).

### Merged

- Merge pull request #47 from ikus060/develop ([eac89dc](https://gitlab.com/ikus-soft/rdiffweb/commit/eac89dc20296f3922a3bcad1148c6fdb610f0c76) by Patrik Dufresne).
- Merge pull request #34 from peyremorgan/beta-mofiles-nomanifest ([e1e66fc](https://gitlab.com/ikus-soft/rdiffweb/commit/e1e66fcdef2dcadbb696a156251ce2c175c56b57) by Patrik Dufresne).
- Merge remote-tracking branch 'github/develop' into develop ([2edd91f](https://gitlab.com/ikus-soft/rdiffweb/commit/2edd91f0e5ba821b32310e200f83963d35b38275) by Patrik Dufresne).
- Merge pull request #32 from peyremorgan/beta-readmetypo ([d464204](https://gitlab.com/ikus-soft/rdiffweb/commit/d464204a9a6247da38b8941943c9f67dc562dc5f) by Patrik Dufresne).
- Merge pull request #17 from sechanbask/patch-1 ([9c2e14b](https://gitlab.com/ikus-soft/rdiffweb/commit/9c2e14bb81d29d2f7e9e2da2b309ffc33406ecb6) by Patrik Dufresne).
- Merge pull request #18 from sechanbask/patch-2 ([34f4e62](https://gitlab.com/ikus-soft/rdiffweb/commit/34f4e62a1d90fe7f61da68b1832ad84e34692b2c) by Patrik Dufresne).
- Merge pull request #19 from sechanbask/patch-3 ([16e04f4](https://gitlab.com/ikus-soft/rdiffweb/commit/16e04f4ba561ca6a3d92a02d5a5b204c5603927a) by Patrik Dufresne).
- Merge pull request #20 from sechanbask/patch-4 ([6ca07d3](https://gitlab.com/ikus-soft/rdiffweb/commit/6ca07d3fcfeebd6343516c3834efa28de3e1272e) by Patrik Dufresne).

### Misc

- Enhance repository view. Reduce item size. Include number of repos in title. ([0eb14af](https://gitlab.com/ikus-soft/rdiffweb/commit/0eb14af04bb8b39de2f96f2e5591c244be07dba1) by Patrik Dufresne).
- Correction to init script. Use >> instead of > to write log file. ([216a032](https://gitlab.com/ikus-soft/rdiffweb/commit/216a032412af274fbd183b21e4952b1fa9a2f180) by Patrik Dufresne).
- Upgrade Bootstrap to 3.3.4. Align dropdown menu in xs. Fix #43 ([d5bd0ad](https://gitlab.com/ikus-soft/rdiffweb/commit/d5bd0adfc3062efd21eba9743987bd3372204e21) by Patrik Dufresne).
- Align the "delete" buttons. Fix #42 ([06b0af7](https://gitlab.com/ikus-soft/rdiffweb/commit/06b0af779bc869c0b28627641576f62db70d0b0b) by Patrik Dufresne).
- Hide "Signed in as..." for xs and sm. Fix #41 ([2c43d82](https://gitlab.com/ikus-soft/rdiffweb/commit/2c43d82eb9be786e8497f8b22c4ac393ca192b01) by Patrik Dufresne).
- Avoid replacing configuration file rdw.conf. ([17af6ef](https://gitlab.com/ikus-soft/rdiffweb/commit/17af6efd9f4d63bdd22d0c8885df06fe207297e4) by Patrik Dufresne).
- Include a logrotate configuration to setup.py ([e3d3c38](https://gitlab.com/ikus-soft/rdiffweb/commit/e3d3c381d6770a64b5f1a14efe0895d3017e23f6) by Patrik Dufresne).
- Declare license information in setup.py ([b1ad03c](https://gitlab.com/ikus-soft/rdiffweb/commit/b1ad03c9c93a3b005a659203eae16e79978c340d) by Patrik Dufresne).
- Rename any occurent of backup location to repositories. ([d0aa916](https://gitlab.com/ikus-soft/rdiffweb/commit/d0aa916b7ea71ebf4f25c8f21fd2d81e9b257016) by Patrik Dufresne).
- Minor modifications. Review the entire code base. ([e677df7](https://gitlab.com/ikus-soft/rdiffweb/commit/e677df76f426d36621b885fbd2ee82e03cf014b9) by Patrik Dufresne).
- Update i18n tools to properly load the translation according to users accept-language. ([f8f0265](https://gitlab.com/ikus-soft/rdiffweb/commit/f8f026551a390faa0c0d46f60566134215f49ba0) by Patrik Dufresne).
- Update setup.py to compile the translation when running `python setup.py build` ref #33 #34 ([1622218](https://gitlab.com/ikus-soft/rdiffweb/commit/1622218d1690de24350397b34ec3ebefa548a7a0) by Patrik Dufresne).
- Set rdiffweb branding ([8f31213](https://gitlab.com/ikus-soft/rdiffweb/commit/8f312133de348d4ab784bed53c9ec02509f8cc90) by Patrik Dufresne).
- Update login page format ([510669f](https://gitlab.com/ikus-soft/rdiffweb/commit/510669f2191e3e25f2c62c743013563c57f570f9) by Patrik Dufresne).
- Support symbolic link by showing the target directory content. Fix #30 ([3ab023a](https://gitlab.com/ikus-soft/rdiffweb/commit/3ab023a5a1d26f50c72f90e021336b67c7eaafcd) by Patrik Dufresne).
- Bump version to 0.7.0 ([b739ba3](https://gitlab.com/ikus-soft/rdiffweb/commit/b739ba3c5cc96c32d172e613f32f0e7f23898547) by Patrik Dufresne).
- Update init script to fix some issue related to starting rdiffweb. ([42ba009](https://gitlab.com/ikus-soft/rdiffweb/commit/42ba0092ad05022fc78ef380a6b078806d2d759f) by Patrik Dufresne).
- Update install instruction in README.md ([49a6525](https://gitlab.com/ikus-soft/rdiffweb/commit/49a65252f6fea1dfb9ee1d1335d3d38514e26113) by Patrik Dufresne).
- Minor improvement for mobile ([01f95bb](https://gitlab.com/ikus-soft/rdiffweb/commit/01f95bb2e1fd1ff57ddd5d5fb2bc51249f057b97) by Patrik Dufresne).
- Before validating LDAP credentials, check if user exists in local database. ([c8883c4](https://gitlab.com/ikus-soft/rdiffweb/commit/c8883c4e4a45dee2be040368f1aa03260260d392) by Patrik Dufresne).
- Handle situation where UserRoot is None. ([df25886](https://gitlab.com/ikus-soft/rdiffweb/commit/df25886e4bbb5812ba00bf6fb9915e478587a99d) by Patrik Dufresne).
- Enhance ldap search logs. ([6ab11b8](https://gitlab.com/ikus-soft/rdiffweb/commit/6ab11b87c38850cfa28e8c18db6814bf492bd313) by Patrik Dufresne).
- Correct encoding error in db_sqlite and db_ldap to support username and password with non-ascii characther. ([fa83d62](https://gitlab.com/ikus-soft/rdiffweb/commit/fa83d625f45aa1e17b1be785ad9271ee575a4093) by Patrik Dufresne).
- Correct usage of "title" to be in templates. ([f976a1f](https://gitlab.com/ikus-soft/rdiffweb/commit/f976a1f8140e4bf7f35aebb339a5dd63c7e55091) by Patrik Dufresne).
- Restrict access to /admin/ ([b18d636](https://gitlab.com/ikus-soft/rdiffweb/commit/b18d6366c7ab39ba622689c4442f0c0a809bd511) by Patrik Dufresne).
- Translate rdiffweb to french. Provide translation based on browser accepted language. ([887c9d0](https://gitlab.com/ikus-soft/rdiffweb/commit/887c9d0bd8e54815a7798c519c6b8dcf1429875c) by Patrik Dufresne).
- Minor UI enhancement following review. ([91561a8](https://gitlab.com/ikus-soft/rdiffweb/commit/91561a8380342052906a8e1a29cb0f1287442d15) by Patrik Dufresne).
- Enhance administration view. ([af8031f](https://gitlab.com/ikus-soft/rdiffweb/commit/af8031f4569b5007e40f432a7c827d9909818318) by Patrik Dufresne).
- Provide hint when no backup locations is available. ([8c6d564](https://gitlab.com/ikus-soft/rdiffweb/commit/8c6d5641d67a20456628a27099209855f5979156) by Patrik Dufresne).
- Enhance initial setup. ([c61825e](https://gitlab.com/ikus-soft/rdiffweb/commit/c61825e4ed46cfb4fc499c974f6e3291e9207c44) by Patrik Dufresne).
- Use permalink ([9183ef2](https://gitlab.com/ikus-soft/rdiffweb/commit/9183ef2bd07dcaa860ea470a5445a5ec231d9fba) by Patrik Dufresne).
- Try to fix encoding issue ([3ebb3cc](https://gitlab.com/ikus-soft/rdiffweb/commit/3ebb3cc070f39b00dab1bf1b237d771f414737cb) by Patrik Dufresne).
- Rename all variation of rdiff-web, rdiffWeb into rdiffweb. Fix #24 ([8ff3554](https://gitlab.com/ikus-soft/rdiffweb/commit/8ff35543504361b23552bc787e73acd2a2aec5dc) by Patrik Dufresne).
- Update author information. ([7851f0f](https://gitlab.com/ikus-soft/rdiffweb/commit/7851f0f28c6d81697e67f641c886994ef681a748) by Patrik Dufresne).
- IN PROGRESS - Add LDAP authentication support. ([9ad3a9b](https://gitlab.com/ikus-soft/rdiffweb/commit/9ad3a9bd270973dce840490597d9569d27317200) by Patrik Dufresne).
- Show error message instead of "Invalid date parameter." ([b254a35](https://gitlab.com/ikus-soft/rdiffweb/commit/b254a35bd8a1c90eb6fbf9d19242a3245d1584db) by Patrik Dufresne).
- Update page_end.html ([c596299](https://gitlab.com/ikus-soft/rdiffweb/commit/c59629994282923d132a396f673598b17ca48534) by sechanbask).
- Update login.html ([f4d32a8](https://gitlab.com/ikus-soft/rdiffweb/commit/f4d32a86a734704b8676d7ed2f82e63f7e3257c2) by sechanbask).
- Update setup.py ([37c72a7](https://gitlab.com/ikus-soft/rdiffweb/commit/37c72a76051de029f86308bade3d008d96b15028) by sechanbask).
- Update PKG-INFO ([65e4858](https://gitlab.com/ikus-soft/rdiffweb/commit/65e48580f5f2458963c3921a3f86e419f94bf58d) by sechanbask).

## [v0.6.5](https://gitlab.com/ikus-soft/rdiffweb/tags/v0.6.5) - 2013-08-21

<small>[Compare with v0.6.4](https://gitlab.com/ikus-soft/rdiffweb/compare/v0.6.4...v0.6.5)</small>

### Added

- Add arrow to indicate the sorting direction. ([c33bf58](https://gitlab.com/ikus-soft/rdiffweb/commit/c33bf586a77f3e5766fca556321d918da0b7154d) by Patrik Dufresne).
- Add license informations to source file and package info. ([fec0950](https://gitlab.com/ikus-soft/rdiffweb/commit/fec09501a016c7c033cdb3c6ccf973d41a2aa381) by Patrik Dufresne).

### Fixed

- Fix RDIFF_BACKUP_DATA constant usage in rdw_spider_repos.py ([d17822c](https://gitlab.com/ikus-soft/rdiffweb/commit/d17822cd1666588b0a4c376074579060027d3f02) by Patrik Dufresne).

### Changed

- Change sorting implementation to use TimSort. ([1ef7eef](https://gitlab.com/ikus-soft/rdiffweb/commit/1ef7eefd483f6b9bfa3c0e3938f4fc796a7351cf) by Patrik Dufresne).
- Change the creation of the status entry url to make it relative instead of absolute. ([0378aa2](https://gitlab.com/ikus-soft/rdiffweb/commit/0378aa225ef07ad3ffc80be7f92bdcba9e3d010d) by Patrik Dufresne).

### Merged

- Merge remote-tracking branch 'origin/master' ([23e5302](https://gitlab.com/ikus-soft/rdiffweb/commit/23e53020704342aafa853e0a09f3466027610d76) by Patrik Dufresne).

### Misc

- Update the installation instruction to use v0.6.5 ([e744b1c](https://gitlab.com/ikus-soft/rdiffweb/commit/e744b1cc4da74b965246e2a1825e40ee1fe3ae80) by Patrik Dufresne).
- Update README.md with reference to 0.6.4 ([5a6bf72](https://gitlab.com/ikus-soft/rdiffweb/commit/5a6bf72bf96857d9a180c1c8439d2a3867f73066) by Patrik Dufresne).
- Minor modification to CSS to add more focus to warnings and errors. ([29df2d8](https://gitlab.com/ikus-soft/rdiffweb/commit/29df2d82ca99a1da975cb5514d45a1d6d9b50daa) by Patrik Dufresne).
- Minor change to color palette. ([2de9644](https://gitlab.com/ikus-soft/rdiffweb/commit/2de96449ef48a997bb149c5cef901bec35e6cb40) by Patrik Dufresne).
- Modification to CSS and templates for better support on mobile devices. Fix #4 ([f27b730](https://gitlab.com/ikus-soft/rdiffweb/commit/f27b7308d9cb087dd7c42780ff6435d18ba0a614) by Patrik Dufresne).
- Save sorting preference in local storage. Restore the user preference on page load. Fix #1 ([2c739af](https://gitlab.com/ikus-soft/rdiffweb/commit/2c739afa38579e0eaeced82f0323f7594a70c505) by Patrik Dufresne).
- Validate pages using w3c validator againts HTML5. ([cfa43c7](https://gitlab.com/ikus-soft/rdiffweb/commit/cfa43c717c3e6a25475bbfbd639836fb402c4720) by Patrik Dufresne).
- Add column sorting using JavaScript. Use css :nth-child(even) to replace altRow implementation. ([3b0fb27](https://gitlab.com/ikus-soft/rdiffweb/commit/3b0fb27eb0a26a317ccdee12507c2b3f500ccc3c) by Patrik Dufresne).
- Refactor librdiff.py to fix handling of different timezone for the same increment. Fix #2 ([f31a0a4](https://gitlab.com/ikus-soft/rdiffweb/commit/f31a0a40aad6ab386b410fbfbd40635c2bef9316) by Patrik Dufresne).
- Minor realignment of the login screen using css. ([04352f6](https://gitlab.com/ikus-soft/rdiffweb/commit/04352f64df1f8d52a8872f3fdc9c8bd886753d09) by Patrik Dufresne).

## [v0.6.4](https://gitlab.com/ikus-soft/rdiffweb/tags/v0.6.4) - 2012-10-28

<small>[Compare with first commit](https://gitlab.com/ikus-soft/rdiffweb/compare/38f1029053ac13b9407d640cdd170bcba9c86377...v0.6.4)</small>

### Added

- Add rdiffWeb branding and bump version to 0.6.4 ([a402b31](https://gitlab.com/ikus-soft/rdiffweb/commit/a402b31f1cf98d0aee86d30685e262fc3996e0d0) by Patrik Dufresne).

### Fixed

- Fix minor issue with deployment script. Redesign the pages with modification to templates and CSS. Add JQuery. ([6b88620](https://gitlab.com/ikus-soft/rdiffweb/commit/6b88620c0128f90530b855af3e20a21a1569487c) by Patrik Dufresne).

### Changed

- Change the repository icon and the favicon. ([cb04f81](https://gitlab.com/ikus-soft/rdiffweb/commit/cb04f8173bcfc66ea58046154430908e148f7a87) by Patrik Dufresne).
- Change the location of the rss feed icon. Change the icon. ([ba5c189](https://gitlab.com/ikus-soft/rdiffweb/commit/ba5c1890ee0b6bf43f22c506adc1812262999d88) by Patrik Dufresne).

### Removed

- Remove deprecated emailsEnabled section. ([b26c826](https://gitlab.com/ikus-soft/rdiffweb/commit/b26c82681c124f3c5d914a79068aad0e1ad810f4) by Patrik Dufresne).

### Misc

- Update readme file with installation instruction. ([5abaed3](https://gitlab.com/ikus-soft/rdiffweb/commit/5abaed3117233b45f35a657acf82599fcceb1288) by Patrik Dufresne).
- Make the web server listen on all network interface by default. ([6710cbe](https://gitlab.com/ikus-soft/rdiffweb/commit/6710cbe67614cf7d769f2b12d394493d4c1726b4) by Patrik Dufresne).
- Use overlay to add user in admin panel. ([732fef2](https://gitlab.com/ikus-soft/rdiffweb/commit/732fef244a1b81e4b36aa4af05175522cfc5453b) by Patrik Dufresne).
- Use overlay to select revision to be restored. ([7f82ee4](https://gitlab.com/ikus-soft/rdiffweb/commit/7f82ee41e39a635fa03beab973d1f92818cfbf36) by Patrik Dufresne).
- Commit version 0.6.3 ([8c7147a](https://gitlab.com/ikus-soft/rdiffweb/commit/8c7147a0fed891991fa621ab115d57c43a177c2a) by Patrik Dufresne).
- Initial commit ([38f1029](https://gitlab.com/ikus-soft/rdiffweb/commit/38f1029053ac13b9407d640cdd170bcba9c86377) by ikus060).
