# Changelog

### 27-January-2021 - 09:37 CET

- Feature: PropulateProperties: Notify alert error if there are orphan packages, but keep going #577
- Feature: Capture output and exit code running Conan commands #578
- Feature: New job to delete an Artifactory repo #575
- Fix: AutomaticMerge: Fix alerts when there are no errors #576
- Fix: PopulateProperties: Do not raise if a property assignment fails, go with the next one #586
- Fix: Improve packages generated message #579
- Fix: BuildSingleReference: Add boolean parameter to configure hooks errors #592
- Fix: Handle scenario where a package doesn't have properties (#603)

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
 - [fix] Fix error affecting PRs that were blocked in the past by a team member
 - [fix] Fix issue with properties associated to new configurations

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
