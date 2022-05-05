2022-05-01

Note that the libsodium project does not create new release version numbers since 1.0.18

Instead, they maintain a fork branch (stable) into which they cherry-pick commits.
Consumers of the library are expected to simply use the current head of the stable branch.

To update the version on CCI, add a new entry from this branch:
https://github.com/jedisct1/libsodium/commits/stable
