# Using the Curated Conan Center Index Conan repositories

<!-- mdformat-toc start --slug=github --no-anchors --maxlevel=6 --minlevel=2 -->

- [Building against the staging repository](#building-against-the-staging-repository)
- [Using standard build profiles](#using-standard-build-profiles)

<!-- mdformat-toc end -->

To use the Curated Conan Center Index Conan repositories, add the following
repositories to Conan, and disable the one not currently in use:

```text
conan-center-dl: http://artifactory.dlogics.com:8081/artifactory/api/conan/conan-center-dl [Verify SSL: True, Disabled: True]
conan-center-dl-staging: http://artifactory.dlogics.com:8081/artifactory/api/conan/conan-center-dl-staging [Verify SSL: True]
```

The best way to do this is to add the repositories to `remotes.txt` in a Conan
configuration repo, which is already done in the `curated-conan-center-index`
branch of the `conan-config` Git repository:

```text
conan-local http://artifactory.dlogics.com:8081/artifactory/api/conan/conan-local True
conan-alias-production http://artifactory.dlogics.com:8081/artifactory/api/conan/conan-alias-production True
conan-alias-staging http://artifactory.dlogics.com:8081/artifactory/api/conan/conan-alias-staging True
conan-center-dl http://artifactory.dlogics.com:8081/artifactory/api/conan/conan-center-dl True
conan-center-dl-staging http://artifactory.dlogics.com:8081/artifactory/api/conan/conan-center-dl-staging True
```

Add the `curated-conan-center-index` to your `dlconfig.yaml` by adding
`--branch curated-conan-center-index` to the `config_args` key:

```yaml
config:
    # Basic configuration variables
    global:
        # Base configurations, may be overridden by platform

        # Conan configuration. `conan config install` installs configuration file from this URL.
        # See: https://docs.conan.io/en/latest/reference/commands/consumer/config.html#conan-config-install
        # This is usually a pointer to a Git repo, from which it clones the default branch
        config_url: git@octocat.dlogics.com:datalogics/conan-config.git
        config_args: --branch curated-conan-center-index
```

dl-conan-build-tools will use `curated-conan-center-index` by default once the
Curated Conan Center Index goes live.

The [`invoke conan.install-config`][install-config] task in
`dl-conan-build-tools` will figure out if you're using the production repository
(the default) or the staging repository (see below), and disable the repository
that is not in use. To ensure consistency, it will also remove any packages from
the local cache that were from a now-missing-or-disabled remote.
`conan.install-config` is called from `conan.login` and `bootstrap`.

## Building against the staging repository

The staging repository corresponds to the `develop` branch of the Curated Conan
Center Index. It is the first repository to receive new changes:

- Packages created or updated at Datalogics should be merged to `develop`.
- The `merge-upstream` task runs automatically in Jenkins to bring in changes
  from https://github.com/conan-io/conan-center-index.

The easiest way to build against the staging repository is to define the
environment variable `DL_CONAN_CENTER_INDEX=staging`. This can be done in your
command shell, or in an environment variable in a `Jenkinsfile`, perhaps
controlled by a parameter.

## Using standard build profiles

The `curated-conan-center-index` branch of `conan-config` introduces some
standard build profiles. Build profiles are used to obtain Conan packages that
are in the build environment: these packages are usually tools like CMake or
Doxygen. The Curated Conan Center Index repositories contain
[pre-built versions of tools](automatic-tool-builds.md) that use these profiles.

The standard build profiles are named after operating system and architecture.

It is recommended that projects that use split build/host profiles use the
standard build profiles.

The profiles are:

- `build-profile-aix-ppc`
- `build-profile-aix-ppc-gcc`
- `build-profile-linux-arm`
- `build-profile-linux-intel`
- `build-profile-macos-arm`
- `build-profile-macos-intel`
- `build-profile-solaris-sparc`
- `build-profile-solaris-sparc-32`
- `build-profile-windows-intel`

[install-config]: https://octocat.dlogics.com/pages/datalogics/dl-conan-build-tools/conan_install_config.html
