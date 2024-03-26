# Changelog

### 20-March-2024 - 11:13 CET

- [fix] Changing Version Ranges in dependencies is now bump dependencies
- [fix] Static library package type should be built with both all static and all shared dependencies

### 13-March-2024 - 11:08 CET

- [feature] Build with both */*:shared=True/False option when package type is declared as ``shared-library``.
- [fix] Fix ValidateInfra python version check to be aligned with the latest Jenkins version.

### 07-February-2024 - 15:43 CET

- [feature] Add waiting list for new collaborators that are not found in access request issue.
- [feature] Skip building bump dependencies PRs by default. It will require manual CI trigger.

### 24-January-2024 - 12:13 CET

- [feature] Update Conan 1.x branch to version 1.62.0
- [feature] Update Conan 2.x branch to version 2.0.16
- [feature] Require review from maintainers for Bump version and Bump requirements
- [fix] Show header-only option in the build CI summary table
- [fix] Use build/host profile conf also in test package
- [fix] Use only string to handle Github labels

### 05-December-2023 - 16:23 CET

- [fix] Use the correct profile to test a tool_require.
- [feature] Add armv8 extra flag in profile arch when building in Macos M1.
- [fix] Prioritization of non-shared builds.
- [fix] Do not raise an exception in case slack fails.
- [fix] Remove epochs.
- [fix] Remove some dead code.

### 26-Oct-2023 - 12:13 CEST

- [feature] Allow X.Y semver for version bumps
- [feature] Add assert message for parent commit checks on PR checkout
- [feature] JobRelauncher restarts both Conan v1 and v2 pipelines.
- [fix] Do not close the report issue of the recipe export check

### 11-Oct-2023 - 12:17 CEST

- [feature] Update Conan 2.x to the version 2.0.12 in the CI
- [feature] Update Conan 1.x to the version 1.61.0 in the CI

### 06-Oct-2023 - 10:15 CEST

- [feature] Label PRs with version conflict properly
- [feature] Add motivation message when under maintenance
- [feature] Wait for sibling job in master right before promote
- [fix] No longer run Conan v2 export step
- [fix] Ensure build order follows only static first
- [fix] Disable quiet period for all jobs except CCI multibranch

### 25-Sep-2023 - 14:33 CEST

- [feature] Label PRs that have missing dependencies.
- [feature] Remove check regression for Conan v2 pipeline.
- [feature] Start deprecating epochs support in profile configurations.
- [fix] Run TapaholesRepo job only once per week.
- [fix] Run ListPackages job only once per week.

### 01-Sep-2023 - 19:58 CEST

- [fix] Use Unix separators for Windows folder path when creating CI workspace.

### 31-August-2023 - 12:57 CEST

- [feature] Support specific PR number for Automatic Merge.
- [feature] Use temporary folder for build workspace.
- [fix] Rename BuildSingleReference folder to bsr to overcome Windows long path.
- [fix] Remove graph info from logs to avoid long loading.
- [fix] Remove deprecated search index for Conan Center.

### 17-August-2023 - 11:42 CEST

- [fix] Fix type error when catching generic exceptions in Jenkins
- [fix] Bump dependencies no longer allow version range
- [feature] Show recipe revision on the pull-request summary table

### 04-August-2023 - 10:26 CEST

- [feature] Enable Conan 2.0.8
- [feature] Enable Conan 1.60.2
- [feature] Update Jenkins server version
- [hotfix] Better error management when having CI build timeout

### 19-July-2023 - 09:45 CEST

- [fix] Fix message processing if no message is passed.
- [fix] Fix automatic merge priority to follow the correct PR order.
- [fix] Waiting for Conan 2.x result after building Conan 1.x.
- [fix] Bump version should not be tagged when removing old versions.
- [feature] Improve internal logs to get more information about epochs.
- [feature] Add an option to disable some jobs.
- [feature] Disable branch indexing job runs on cci multibranch job.
- [feature] Enable Conan 2.0.8

### 04-May-2023 - 16:05 CEST

- [bugfix] Fix cppstd issues when selecting the value to use in profiles.
- [feature] Add support for raising `InvalidConfiguration` in `validate_build()` method in recipes.
- [feature] Update library requirements for Conan client 2.0.4
- [feature] Inform users when Conan v2 CI build is mandatory for merging.
- [feature] Implement different "under maintenance" levels: OFF, MINOR, MAJOR, CRITICAL.
- [feature] ValidateInfrastrucure: Check Artifactory repos exist.
- [feature] Move variables to new folder properties approach.

### 12-April-2023 - 16:18 CEST

- [feature] Add ListPackages job the posibility to update a list via PR
- [feature] Add c3i-conan2-ready label when modifying .c3i/conan_v2_ready_references.yml
- [hotfix] Use Conan helpers to update Conan Center page
- [hotfix] Automatic Merge reduces the number of requests for each execution

### 03-April-2023 - 10:26 CEST

- [fix] Remove options usage from build profile.
- [fix] Fix promotion of recipe/packages when artifacts already exist in target repo.
- [feature] Make master branch promotion job wait for sibling jobs (to avoid recipe promotion race condition).
- [feature] Improve request of reviews and remove timeout.

### 24-March-2023 - 12:00 CET

- [feature] Install Conan command extensions for Conan v2
- [feature] Reduce Github requests number to execute Automatic Merge CI job
- [hotfix] Improve Promote Package CI job logging for better debug

### 10-March-2023 - 19:55 CET

- [feature] Add priority to pull requests
- [hotfix] Avoid extra http requests to run automatic merge faster

### 10-March-2023 - 13:15 CET

- [hotfix] No longer update conan_v2_ready_references.yml automatically
- [bugfix] Validate Green and clean PRs first when executing automatic merge CI job

### 07-March-2023 - 17:05 CET

- [hotfix] Automatic merge skips git conflicts
- [hotfix] config label for "v2 ready" depends on PR author

### 03-March-2023 - 11:05 CET

- [feature] Update ready_v2_references.yml file automatically
- [fix] Do not reuse the same build folder to avoid busy files

### 21-February-2023 - 17:22 CET

- [fix] Fix bug with cppstd entry in configuration files.
- [fix] Fix configuration read of list from an external yaml file.

### 21-February-2023 - 12:44 CET

- [feature] ScheduledExportCheck: Collect warnings from hooks and publish them to a separate table.
- [feature] AutomaticMerge: Add conditional status checks with allowlist.
- [feature] AutomaticMerge: Add branches config to merge branches automatically.
- [feature] Conan: Add methods to get the latest recipe revision.
- [feature] Bump library requirements to support the latest Conan versions.
- [fix] PromotePackages: Fix an issue when promoting multiple references.
- [fix] UpdateSearchIndex: Fix conan inspect call command.

### 14-February-2023 - 15:32 CET

- [fix] Fix ScheduledExportCheck job not updating hook validation issues.
- [fix] Fix missing GitHub labels for PRs with "bump version" and "bump dependencies"
- [feature] PromotePackages: Add a parameter to promote multiple references.
- [feature] Increase `conan test` time limit to 1 hour.
- [feature] Add request header for GitHub API version.

### 03-February-2023 - 10:24 CET

- [fix] Fix macOS deployment target / minos value.
- [feature] Validate: Add return code for license check.
- [feature] Add references list and force parameters to TapaholesRepo job.
- [feature] Add new ListPackages job.
- [feature] Update Conan versions library requirements to 1.58.0 and 2.0.0-beta9.

### 20-January-2023 - 16:09 CET

- [feature] Make feedback messages of PRs configurable.
- [feature] Add status icon to the title of PRs comments.
- [fix] Fix Conan v2 error when getting revisions.

### 16-January-2023 - 16:43 CET

- [fix] ValidateInfrastructure: Fix Conan version check.
- [feature] TapaholesRepo: Build references when there are 0 packages for a recipe revision.

### 12-January-2023 - 19:33 CET

- [fix] Fix Conan v2 download/upload recipe commands.

### 12-January-2023 - 11:21 CET

- [feature] Add support for Conan v2 beta 7.
- [feature] Check complete Conan version on ValidateInfrastructure.
- [fix] Increase `conan test` timeout value.
- [fix] Fix stage name when calculating build configurations.

### 10-January-2023 - 15:20 CET

- [feature] Add entry in config to disable merging labels from the multibranch job.
- [feature] Add timeout to `conan test` command.
- [feature] Add API wrapper support for status page.
- [refactor] Separate build configuration calculation from pull-request interaction (labels/comments).
- [feature] Take main repository from configuration for Tapaholes jobs.

### 15-December-2022 - 11:12 CET

- [feature] Set github feeback title via config file (`feedback_title`).
- [fix] Fix log summary html table for shared option with Conan v2.
- [fix] ValidateInfra: Remove same OS version check for Macos nodes.

### 09-December-2022 - 11:38 CET

- [feature] Add environment variable to build with different Xcode/apple-clang compilers on Macos agents.
- [feature] Add `MACOSX_DEPLOYMENT_TARGET` and `SDKROOT` env variables to build stages on Macos.
- [feature] Add `LongPathsEnabled` registry key check on Windows to Validate Infrastructure job.
- [fix] Fix git user on commits when updating docs for supported platforms and configurations.
- [fix] Fix getting commit hash when writing GitHub error messages.
- [fix] Fix Conan v2 inspect command.
- [fix] Fix condition when waiting for another job to finish.

### 14-November-2022 - 11:54 CET

- [feature] Disable inactivity count for Access Request job.
- [feature] Add `github-actions[bot]` to permanent users list.
- [feature] No need to run ValidateInfrastructure job for Access Request and Reviewers update pull-requests.
- [fix] JobRelauncher retry property fix.

### 07-November-2022 - 11:17 CET

- [feature] Improve Access Request's pull-request description mentioning users.
- [fix] Access Request should not remove reviewers and maintainers.
- [fix] Access Request should count requests done on the same day as the pull request.
- [fix] Avoid posting pipeline title in GitHub messages if feedback is empty.

### 27-October-2022 - 15:18 CEST

- [feature] Add under maintenance check to AccessRequest and ScheduledExportCheck jobs.
- [feature] AccessRequest: Remove inactive users.
- [feature] Accept Major.Minor as bump version.
- [feature] Add message title to gihtub comments.
- [fix] Update maintainers list and fix output.
- [fix] Remove dummy files from tests.
- [fix] Make sure contributors are not removed in Access request PR.

### 17-October-2022 - 10:33 CEST

- [feature] Improve management of GitHub labels on pull requests.
- [feature] New EpochsSummary job to show epoch status for each reference.
- [feature] Save bot comments as labels as job artifacts for easier user feedback.
- [feature] Ability to wait for a job and merge bot messages from another pipeline: Allows to provide feedback to users in PRs from the Conan v2 pipeline in the future.
- [feature] Add timeout to AutomaticMerge job.
- [feature] Add note about Windows SDK on supported platforms documentation.
- [fix] Fix getting package IDs from Artifactory in the Conan v2 pipeline.
- [fix] Bump dependencies pull requests should only consider modified comments.
- [fix] ValidateInfrastructure job parameter for macos executors.

### 20-September-2022 - 14:27 CEST

- [feature] Handle scenarios where some files are removed.
- [feature] Simplify logic to detect references to be built in a pull request.
- [feature] Workaround in Conan v2 commands to list package IDs in a pull request.
- [feature] Bump minimum required Conan client version.
- [fix] When merging a pull request, check recipe revisions only against the pull-request repository.
- [fix] Do not consider GitHub check runs for pull requests opened by a bot.
- [fix] Consider files renamed in pull requests as "added" and "removed".
- [fix] Cover use-case when a pull request adds just one conanfile.py.
- [fix] Simplify assignment of GitHub labels.
- [fix] Use backquotes in GitHub comments.
- [fix] Fix promotion of packages with Conan v2.

### 1-September-2022 - 10:21 CEST

- [feature] Avoid `test_v?_package` folders that don't match the Conan version.
- [feature] Keep at least 3 days of job logs.
- [fix] Properly encode GitHub API URLs.
- [fix] Replace invalid chars when generating profiles.
- [refactor] Refactors around the GitHub classes implementation.

### 18-August-2022 - 15:21 CEST

- [fix] Conan v2: Check recipe revision only if it has been successfully exported.
- [feature]: Consider changes from `master` before merging a pull-request. If those changes result in a new recipe revision, the pull-request is triggered again.

### 8-August-2022 - 11:25 CEST

- [fix] Take into account status checks from GitHub actions before merging a pull-request.
- [feature] Double check that the recipe revision exported using Conan v2 matches the one exported by Conan v1.
- [feature] Fail if required Conan version is not available on Linux containers instead of falling back to latest.

### 22-July-2022 - 12:13 CEST

- [feature]: ValidateInfrastructure: Add check to verify CMake 3.21 is installed in Windows machines.
- [feature]: ValidateInfrastructure: Execute the validation when a pull-request is modifying configuration files.
- [feature]: Conan v2: Iterate `cppstd` values in profiles to build first match.
- [feature]: Conan v2: Apply `shared` option for the whole dependency graph.
- [feature]: Add `tools.apple.sdk_path` to configuration in Macos (required by new build helpers).
- [feature]: Set `tools.system.package_manager:mode=install` and `tools.system.package_manager:sudo=True` in configuration files (required by new system package manager helpers to mimic the behavior of old ones).
- [feature]: Upgrade required Conan versions to work with the library. Minimum versions tested are now `1.49.0` and `2.0.0b1`.
- [fix]: ValidateInfrastructure: Fix error message split.
- [bugfix]: Accept missing HTTP code for requests.

### 06-July-2022 - 14:28 CEST

- [feature]: Configure AccessRequest job to run on Mondays and Thursdays.
- [fix]: Improve Conan v2 export message.
- [fix]: Fix config parameters for RelaunchUnexpected job
- [fix]: Make AccessRequest job open PR against cci repo.
- [fix]: DSL: Remove old jobs by date only
- [refactor]: Refactor GitHub-related code utilities.

### 27-June-2022 - 17:29 CEST

- [fix] Fix "no changes detected" issue in some pull-requests.
- [fix] Avoid static builds with static runtime in MSVC compiler.
- [fix] Fix Conan v2 export checkout of sources.
- [fix] Conan v2: Avoid reading configuration entries that do not exist.
- [feature] Avoid failure in some jobs when the system is under maintenance.
- [feature] ValidateInfrastructure job now works for `msvc` & Visual Studio 2022.
- [feature] Conan v2: support hooks installation.
- [feature] Add more parameters to DSL scripts.

### 08-June-2022 - 16:29 CEST

- [feature] Allow changes in multiple folders (except for the `recipes` one).
- [feature] Detect changes made in a future `linters` folder.
- [feature] Validate configuration files in pull-requests that modifies them.
- [feature] Add support for more Conan v2 commands.
- [feature] DSL: Parameterize jenkinsfile path.
- [fix] DSL: Discard old builds to avoid consuming all inodes.
- [fix] Remove `under maintenance` label in pull requests.
- [fix] Add a detailed message for Conan v2 export.
- [fix] Abort `RelaunchUnexpectedError` job when the system is under maintenance.

### 19-May-2022 - 15:52 CEST

- [feature] Add Conan v2 export extra step in pull-request job.
- [feature] Tag pull-requests as "under maintenance" when the build service is not available.
- [config] Update Conan version to 1.47.0.
- [feature] Check right WinSDK in ValidateInfrastructure job.
- [fix] Fix access request job for authorized users.
- [feature] New Conan v2 commands: info and recipe revision.
- [feature] Store package ID cache at job level.

### 10-May-2022 - 17:05 CEST

- [fix] Exclude `shared=True` and runtime `MT/MTd` profile configuration from builds.
- [job] RelaunchUnexpectedError: a new job to automatically retrigger failed jobs.
- [feature] Ability to load the configuration file from an external source.
- [feature] Allow changes to files in the `.c3i` folder.
- [config] Move reviewers and approved users to configuration files.
- [config] Move automatic merge parameters to the configuration file.
- [config] Move GitHub activation to configuration file.
- [config] Remove default configuration.
- [feature] Added compatibility for more Conan 2 commands.
- [fix] Avoid regeneration of folder and multibranch jobs by the DSL cron job.

### 28-April-2022 - 9:56 CEST

- [config] Update Conan client to 1.46.2
- [fix] Do not create GitHub pull-request statuses in advance.
- [fix] Move some Conan command calls to the wrapper.
- [feature] Added compatibility for Conan v2 export command.
- [config] Changed the required number of reviewers: 1 team and 1 community is enough

### 21-April-2022 - 13:46 CEST

- [feature] Updated Python version to > 3.7 in all build agents.
- [feature] Added CMake and Python versions to the infrastructure information.
- [config] Added new community reviewers.
- [feature] Moved Jenkins and Slack to the configuration file.
- [feature] Retry each build config if there is an unexpected error.
- [feature] Added logging to collect information about some jobs.
- [feature] Use a real build profile for cross-building configurations.
- [bugfix] Improve export error report.

### 31-March-2022 - 11:55 CEST

- [config] Upgrade Conan client version to 1.45.0.

### 25-March-2022 - 09:54 CET

- [feature] Updated CMake version to 3.20 only in MacOS machines.
- [feature] Collect requirements from test_package as well.
- [feature] Make the conan-center-bot write a comment after merging a `Bump version` or `Bump dependencies` labeled pull request.
- [feature] Allow SecheduledExportCheck job to report in any issue.
- [feature] DSL: Add cron triggers to some jobs.
- [feature] DSL: Disable concurrent builds on some jobs.
- [feature] Adapt paths for Ansible machines.
- [bugfix] Fix wrong log links in conan-center-bot message.
- [fix] Use consistent slashes in paths.
- [fix] Fix alert for job cancellation.

### 09-March-2022 - 13:37 CET

- [feature] Merge pull-requests that bump version automatically.
- [feature] Get requirements from `conan info --dry-build` command.
- [feature] Use reference with recipe revision for `conan info` commands.
- [feature] Add possibility to load the configuration from file.
- [fix] Fix DSL typo for access request job.
- [fix] Removed retries from pull-request builds (introduced long ago to avoid timeout issues).
- [refactor] Completely remove resource locking for executors.

### 24-February-2022 - 14:03 CET

- [fix] Fix encoding issues in `summary.html` file.
- [fix] Specify branch discovery in DSL for cci multibranch job.

### 22-February-2022 - 10:26 CET

- [feature] Merge pull-request that bump dependencies automatically.
- [feature] Notify about Visual Studio license status in ValidateInfrastructure.
- [config] Upgrade Conan client version to 1.44.1.
- [fix] Fix potential race condition calculating package IDs.

### 16-February-2022 - 12:46 CET

- [fix] Pin Artifactory client library version.

### 10-February-2022 - 16:44 CET

- [fix] Fix DSL parameters and TapaholesList name.
- [feature] Added ConanReference string conversion in call-stacks.
- [fix] Fix ValidateInfrastructure executors and labels count.

### 04-February-2022 - 12:48 CET

- [bugfix] Avoid race-conditions in Conan client instance.
- [hotfix] Race condition reading/writing a file.

### 03-February-2022 - 17:01 CET

- [feature] New label to identify pull-requests that are just bumping dependencies version.
- [bugfix] Fixed bugs with promotion and properties for references that don't build any binary.
- [feature] Add parameter to chose if documentation of supported platforms should be updated automatically.
- [feature] Improve Conan version regex to accept development versions

### 26-January-2022 - 11:14 CET

- [config] Add MacOS apple-clang 13.0 configuration to a new epoch.
- [feature] Handle `header_only=True` default option in recipes.
- [feature] Notify failed builds due to expired Visual Studio licenses.
- [feature] Tapaholes job now sets epoch as well.
- [fix] Throw error if configuration file to use is not found.
- [feature] Add missing DSL job descriptions.
- [feature] Child jobs use the same parent folder.
- [refactor] Remove resource locking.

### 18-January-2022 - 16:49 CET

- [config] Bump Conan client version to 1.43.3.

### 29-December-2021 - 16:41 CET

- [config] Add Linux GCC 11, Clang 12 & 13 configurations with new epoch feature.
- [config] Drop Linux GCC 6 and clang 10 configurations.
- [fix] Fixed some unexpected errors.
- [feature] Prepare pipeline to work with ansible provisioned machines.

### 17-December-2021 - 09:56 CET

- [feature] Introduce 'epoch' concept to build configurations as a strategy to build packages for new compilers.
- [feature] Allow pull-requests to build packages from different recipes for the same library.
- [feature] Profiles and logs from builds in the packages generated summary are now open in a new tab.
- [fix] Improve error reporting of mismatched revision in PRs.

### 14-December-2021 - 09:13 CET

- [config] Bump Conan client version to 1.43.0.

### 01-December-2021 - 12:29 CET

- [config] Bump Conan client version to 1.42.2.

### 24-November-2021 - 17:49 CET

- [feature] Return host requirements when computing package IDs.

### 22-November-2021 - 17:53 CET

- [feature] Cache computation of package IDs.

### 15-November-2021 - 11:03 CET

- [feature] Add `xlarge` pod size in Linux for building packages with higher memory requirements.

### 11-November-2021 - 13:22 CET

- [config] Bump Conan client version to 1.41.0
- [fix] Identify PRs to `CONTRIBUTING.md` as changes in docs.
- [feature] Added Jenkins DSLs for job descriptions.
- [fix] Parse integer value when assigning properties.

### 18-October-2021 - 17:05 CEST

- [config] Upgrade Conan version to 1.40.4
- [fix] Replace `Unauthorized User` label by `User-approval pending`
- [feat] Remove `os_build` and `arch_build` from generated profiles

### 11-October-2021 - 12:14 CEST

- [configs] Configurable Github statuses to check
- [configs] Pairing between configurations and workers (docker images, win/macos servers,...) is configurable in runtime.
- [feature] Early(iest) stop after failure: ignore any extra messages. It provides faster feedback for users.
- [feature] Skip stale pull-requests from automatic review requests.
- [feature] Add node-pool with more resources. It allows the CI to delegate certain builds that require higher RAM limits to it (configured manually).
- [fix] Removed EAP, now it should be named _"Access requests"_ everywhere
- [fix] Improved checks for infrastructure and configuration. It also fixes the auto-generated documentation for _"Supported platforms and configurations"_.
- [job] New job to remove dead branches from CI

### 01-October-2021 - 13:08 CEST

- [hotfix] Apply patch for <https://github.com/conan-io/conan/issues/9695> (Added root certificate for Let's encrypt)

### 21-September-2021 - 12:09 CEST

- [config] Upgrade Conan version to 1.39.0.

### 7-September-2021 - 16:49 CEST

- [configs] Remove Visual Studio 2015
- [configs] Remove Macos apple-clang 10
- [configs] Remove Linux GCC 4.9
- [configs] Linux Clang: keep only latest versions 10 and 11
- [feature] Rename EAP to Access Request.
- [feature] Display merge error in pull-requests.

### 6-September-2021 - 11:15 CEST

- [feature] Display useful CI status notifications in Github pull requests.
- [feature] Upgrade Conan client version to 1.38.0.
- [feature] Move the Conan and Artifactory configuration out of the Jenkins library.
- [feature] Use separated files for the different profile configurations.

### 3-August-2021 - 13:29 CEST

- [feature] BuildSingleReference: Create packages for apple-clang armv8 (Apple M1) in pull-requests' builds.
- [feature] BuildSingleReference: Enforce empty workspace for Windows and MacOS nodes.
- [feature] Different approach to work with configuration files for profiles (internal modularibility).
- [feature] Allow jobs to use multiple configuration files for profiles.
- [fix] ValidateInfrastructure: Minor fixes to the automatic generation of "Supported platforms and configurations" documentation page.
- [fix] PromotePackages: Fix promotion of references that contain symbols.

### 13-July-2021 - 10:24 CEST

- [fix] DeleteRepo: Fix JFrog CLI commands.

### 07-July-2021 - 08:36 CEST

- [feature] UpgradeConan: Upgrade pip before installing Conan.
- [feature] Upgrade Conan client to the 1.37.2 version.

### 02-July-2021 - 16:45 CEST

- [feature] Do not run the CI for branches starting with `bot/...` (branches intended for automations).
- [feature] Remove all remotes when configuring the Conan client.
- [feature] ValidateInfrastructure: Update "Supported platforms and configurations" doc automatically.
- [fix] UpdateSearchIndex: Fix parsing of package data.
- [feature] BuildSingleReference: Add `MSBUILDDISABLENODEREUSE` environment variable for MSBuild to avoid errors when compiling in parallel.

### 01-June-2021 - 08:59 CEST

- [feature] RequestReviews: Add column to enable/disable review requests (any user).
- [testing] Use declared Conan version to run tests.
- [internal] Pay some technical debt.
- [internal] Simplify workflow, all packages already have properties.

### 25-May-2021 - 13:42 CEST

- [feature] AutomaticMerge: Skip pull-requests that fail to merge.

### 24-May-2021 - 15:59 CEST

- [feature] Start to crossbuild Apple M1 using two profiles approach (extra build).
- [feature] Detect and report when a PR has missing dependencies.
- [feature] Upgrade Conan version to 1.35.2.
- [feature] Use only one Artifactory repository per pull request.

### 14-May-2021 - 17:24 CEST

- [fix] Add `--dry-build` to `conan info` commands, it will expand also the build-requires that would have
  failed during the build stage.
- [fix] Escape character comma when assigning properties to Artifactory.
- [fix] Add `--force` when adding remotes.

### 30-April-2021 - 13:52 CEST

- [feature] Add mark in logs to indicate output has been trimmed.
- [feature] Stop uploading packages to Bintray.
- [job] RequestReviews: Automatically request team reviews for PRs ready for review.
- [job] Add checks to validate infrastructure: MacOS version and AVX2 in CPU features.

### 08-April-2021 - 17:01 CEST

- [feature] Hide previous comments by the bot.
- [feature] Use Artifactory API to promote packages from one repository to another.
- [job] Add ability to specify a repository and branch for the hooks when running the export check.
- [job] Add checks to validate infrastructure: Python version, Macos features.

### 05-March-2021 - 15:28 CET

- [feature] Stop generating packages for apple-clang 9.1.
- [feature] Raise error if `ConanInvalidConfiguration` is raised from `build()` method.
- [feature] BuildSingleReference: All PRs use the new workflow.
- [feature] Allow modifications in the _.github_ folder for GitHub bots and actions.
- [feature] Use BuildSingleReference job to build packages (if needed) during a merge.
- [feature] BuildSingleReference: Add build environment property to packages.
- [feature] Tapaholes: Delete repositories after running jobs.
- [feature] AutomaticMerge: Add information to the description of the job.
- [feature] Add new "CleanupArtifactory" job to remove repositories of unmerged PRs.
- [feature] PopulateProperties: Remove packages after using them to compute properties.
- [fix] Add timeout and retry flags to all `curl` commands to avoid intermittent job failures.

### 22-February-2021 - 10:42 CET

- [feature] Add new profiles to generate new compiler configurations in pull requests:
  - Linux: gcc 10, clang 10, clang 11.
  - Macos: apple-clang 12.0.
- [feature] Updated Conan client to the 1.33.1 version.
- [engineering] PromotePackages: Remove packages after uploading.

### 05-February-2021 - 13:20 CET

- [job] New job to upgrade Conan version (Windows and Macos workers).
- [job] New job to validate infrastructure: versions of tools, installed components,... (more checks to be added).
- [feature] Call external DeleteRepo job to remove repositories from Artifactory after a pull-request is merged.
- [feature] New workflow for pull-requests: use `BuildSingleReference` job and better messages (canary deployment).
- [engineering] Refactor functions to retrieve information from GitHub API.

### 27-January-2021 - 09:37 CET

- Feature: PropulateProperties: Notify alert error if there are orphan packages, but keep going.
- Feature: Capture output and exit code running Conan commands.
- Feature: New job to delete an Artifactory repo.
- Fix: AutomaticMerge: Fix alerts when there are no errors.
- Fix: PopulateProperties: Do not raise if a property assignment fails, go with the next one.
- Fix: Improve packages generated message.
- Fix: BuildSingleReference: Add boolean parameter to configure hooks errors.
- Fix: Handle scenario where a package doesn't have properties.

### 30-December-2020 - 13:24 CET

- [feature] BuildSingleReference: Run tests for packages that already exist.
- [feature] BuildSingleReference: Add functionality so it is able to build a PR merging into 'master'.
- [feature] Specify Conan version to use in every node call (decouple from conan-docker-tools updates).
- [fix] AddBetaUser: Fix "ghost" user added weekly for deleted users.

### 29-December-2020 - 17:18 CET

- Updated Conan client to the 1.32.1 version in Windows and Mac agents.

### 14-December-2020 - 09:51 CET

- [feature] Remove repositories after a pull-request is merged.
- [feature] Run promotion in parallel for merge-commits.
- [feature] Viewer for summary.json files.
- [feature] Trigger a BuildSingleReference job at the end of pull-request jobs to build new configurations.
- [fix] Manage repository permissions independently in pull-requests.

### 27-November-2020 - 10:14 CEST

- [feature] More (and better) properties are stored in Artifactory for each package.
- [feature] Use modularized jobs in CI to run parts of the pipeline.
- [fix] Fix error affecting PRs that were blocked in the past by a team member.
- [fix] Fix issue with properties associated to new configurations.

### 18-November-2020 - 12:58 CEST

- [fix] Notify unexpected errors to slack channel (add link to message).
- [job] AutomaticMerge: Fix PRs blocked by non team member users.
- [bug] Build everything but OK or INVALID_CONFIG.
- [fix] Do not use `--all` argument with `conan upload` when the package ID is given.
- [fix] Fix error getting properties when the recipe doesn't have options.
- [job] Tapaholes: Propose new profile set including new compiler configurations.

### 18-November-2020 - 11:23 CEST

- Updated Conan client to the 1.31.3 version in Windows and Mac agents.

### 23-October-2020 - 17:13 CEST

- [feature] ListProfiles: Add 'profiles' to inputs, make it required.
- [feature] Tapaholes: Parameter to accept packages in order from a JSON list.
- [fix] AutomaticMerge: Consider pagination when reading pull-request reviews.
- [job] PopulateProperties: Compute and assign properties to packages-revs and recipe-revs.
- [job] PromotePackages: Copy Conan packages and properties from one repo to another.

### 19-October-2020 - 17:15 CEST

- Updated Conan client to the 1.30.2 version in Windows and Mac agents.

### 14-October-2020 - 17:49 CEST

- [hotfix] Use non greedy regex to capture the pull-request number.

### 10-October-2020 - 21:20 CEST

- [fix] Wait longer for Artifactory to create new repositories.

### 10-October-2020 - 20:52 CEST

- [job] TapaholesRepo: use full path to the recipe itself.

### 10-October-2020 - 20:36 CEST

- [job] BuildSingleReference: assign properties at recipe-revision level

### 10-October-2020 - 15:53 CEST

- [job] TapaholesRepo: create remote repository for each run.
- [job] BuildSingleReference: apply environment to every Conan command.

### 09-October-2020 - 23:43 CEST

- [fix] AutomaticMerge: if the PR cannot be merged (conflicts) go and try the next one.
- [fix] Use existing TMP folder in Windows.
- [fix] BuildSingleReference: minor fixes.

### 07-October-2020 - 17:06 CEST

- [fix] Minor fix to AutomaticMerge job (#390)
- [fix] Modify temp folder, it will no longer be the root of the workspace.
- [job] Populate artifact properties from BuildSingleReference job.
- [job] New job to iterate Github repository (and commit) and find packages missing from remote.

### 29-September-2020 - 16:21 CEST

- [feature] Use indexer V2 API.
- [job] Add force parameter to UpdateSearchIndex job to force reindex of packages.
- [job] New UpdateSearchIndexMaster job to reindex (if needed) packages in ConanCenter repository.

### 23-September-2020 - 15:48 CEST

- [job] AutomaticMerge: Approved and changes requested reviews should prevail.

### 21-September-2020 - 17:59 CEST

- [fix] Remove duplicated credentials.
- [job] AutomaticMerge: Block if a team member requested changes on any commit.
- [job] AutomaticMerge: Show pull request number on the summary.

### 21-September-2020 - 10:44 CEST

- Updated Conan client to the 1.29.1 version in Windows and Mac agents.

### 17-September-2020 - 17:42 CEST

- [job] Inspect PRs and merge automatically if approved.
- [job] Build single reference.
- [job] Main tapaholes job: Build single references in correct order.
- [feature] Iterate profiles in a given order (adding tests to check).
- [feature] Add new users to EAP automatically only on Mondays.
- [feature] Distribute jobs taking into account resources.
- [feature] Labels 'Error' and 'Unexpected error' are mutually exclusive.
- [bugfix] Every new node offers a clean workspace (shorter paths).
- [bugfix] Upload packages: upload one first, then the rest to avoid missing files issue.
- [bugfix] Fix 'parallelGroup' when there are more workers than tasks.
- [bugfix] Retry if failure setting the BuildStatus property.
- [fix] Use the actual commit from the 'master' branch to compute diffs.
- [fix] Use environment variables to log into Conan repository.

### 17-August-2020 - 11:20 CEST

- Raise error if zero packages are generated
- Remove "No beta user" label if corresponding check pass
- [engineering] Unify catchs and simplify slackSend function
- [engineering] Pipeline step to create all packages in stages
- [engineering] Pipeline step to compute and reduce 'packageID'
- [engineering] Simplify 'ComputePackageIDs' command

### 12-August-2020 - 10:12 CEST

- Updated Conan client to the 1.28.1 version in Windows and Mac agents.

### 11-August-2020 - 14:19 CEST

- [engineering] Read allowed users from a file.
- [engineering] Check for beta users in all environments.
- [engineering] Set date in issue description for hooks validation job.

### 4-August-2020 - 20:19 CEST

- [engineering] Remove short-paths home after creating packages.

### 31-July-2020 - 23:14 CEST

- [engineering] Use `force` flag to update the ConanCenter metadata.
- [engineering] Remove local packages created after their upload to avoid disk space issues.

### 24-July-2020 - 13:05 CEST

- Renamed Jenkins project from `conan-center-pull-request` to `cci` to improve issues with long workspace paths in Windows agents.

### 24-July-2020 - 12:52 CEST

- Updated Conan client to the 1.27.1 version in Windows and Mac agents.

### 17-July-2020 - 18:54 CEST

- [feature] Allow documentation inside the repository itself in the `docs` folder
- [feature] Add scheduled job to validate recipes using last released hooks
- [feature] Minimize paths used by the CCI library to build packages
- [bugfix] Recover the shortest path for the `CONAN_USER_HOME_SHORT` environment variable
- [engineering] Improve regression testing for pipeline jobs.

### 30-June-2020 - 16:10 CEST

- Add JenkinsPipelineUnit to test the Jenkinsfile
- [bug] Compare keys in maps using actual strings
- Clean workspace after running the job
- Clean workspace for all nodes
- [refact] Promote usage of 'ConanReference'
- [ListProfiles] New job to list profiles
- [fix] Add grabs to all vars
- [Refactor] getTmpDir() util
- [ListProfiles] Optionally use reference to list profiles
- [refact] Some cleaning around build configurations
- [fix] Profiles no longer contain empty [env] and [build_requires] sections
- [fix] Fix checkExportSanity function

### 24-June-2020 - 10:55 CEST

- Updated Conan client to the 1.26.1 version in Windows and Mac agents.

### 18-June-2020 - 18:40 CEST

- Remove short paths limitation in all Windows agents.

### 04-June-2020 - 10:39 CEST

- Add `CONAN_SKIP_BROKEN_SYMLINKS_CHECK=1` in master jobs.

### 02-June-2020 - 13:06 CEST

- Avoid partial rebuilds in master jobs. Added `all_packages_done` property for every reference to track the completion of packages creation.

### 02-June-2020 - 00:02 CEST

- Updated CMake to 3.16.4 in Windows and Mac agents.

### 20-May-2020 - 10:34 CEST

- Updated Conan client to the 1.25.2 version in Windows and Mac agents.

### 14-May-2020 - 15:52 CEST

- Updated Conan client to 1.25.1 version in Windows and Mac agents.

### 13-May-2020 - 09:47 CEST (08e2be6)

- [refact] Simplify around ComputePackageID and CreatePackage
- [refact] No need to pass 'winTmpPath' everywhere
- Move the 'retryIze' call inside the scope of the node (Might improve [#1020](https://github.com/conan-io/conan-center-index/issues/1020))
