# Automatically resolved merge conflicts

conan-center-index at DL is a fork of the conan-io/conan-center-index repo run
by the Conan project. There is some project metadata that has the same names (
such as the `.github` directory and `README.md`), and as such, there is
potential for merge conflicts.

The `invoke merge-upstream` task can automatically resolve some of those merge
conflicts.

<!-- mdformat-toc start --slug=github --no-anchors --maxlevel=6 --minlevel=2 -->

- [Files that both conan-io and Datalogics modify](#files-that-both-conan-io-and-datalogics-modify)
  - [Why `.gitattributes-merge` and not `.gitattributes`](#why-gitattributes-merge-and-not-gitattributes)
  - [Verifying the coverage of `.gitattributes-merge`](#verifying-the-coverage-of-gitattributes-merge)
- [Files that Datalogics has deleted](#files-that-datalogics-has-deleted)
- [References](#references)

<!-- mdformat-toc end -->

## Files that both conan-io and Datalogics modify

For files that both conan-io and Datalogics modify, add them to the
`.gitattributes-merge` file with an attribute of `merge=ours`. The
`invoke merge-upstream` task arranges for there to be a merge driver called
"ours", which resolves modify/modify conflicts in favor of "our" branch, i.e.,
Datalogics.

As an example, this file currently contains:

```
# Conflicts that should always resolve in favor of Datalogics
# See the section "Merge Strategies" at the end of
# https://www.git-scm.com/book/en/v2/Customizing-Git-Git-Attributes
/README.md merge=ours
/.github/** merge=ours
```

### Why `.gitattributes-merge` and not `.gitattributes`

It's not possible to use custom merge drivers on GitHub, so if the `merge=ours`
attributes were put into the `.gitattributes` file, it would cause problems with
merges done by GitHub. To avoid breaking GitHub, this project uses the separate
file `.gitattributes-merge`, and uses the
[`core.attributesFile`](https://git-scm.com/docs/git-config#Documentation/git-config.txt-coreattributesFile)
configuration option to add it to the list of attributes files.

### Verifying the coverage of `.gitattributes-merge`

To verify the coverage of `.gitattributes-merge`, use the
[`git check-attr`](https://git-scm.com/docs/git-check-attr) command to search
for the merge attributes on files.
[`git ls-files`](https://git-scm.com/docs/git-ls-files) lists files that are
part of the repository, and use `grep` to ignore files that have unspecified
merge attributes.

```bash
$ git ls-files | git -c core.attributesFile=.gitattributes-merge check-attr --stdin merge | grep -v 'merge: unspecified'
.github/PULL_REQUEST_TEMPLATE.md: merge: ours
README.md: merge: ours
```

## Files that Datalogics has deleted

If there are files that Datalogics has deleted, but conan-io has modified, those
files are automatically resolved in favor of Datalogics, by removing them.

If we decide we need those files, one can bring them into the Datalogics fork by
using commands like the following:

```shell
git remote add conan-io git@github.com:conan-io/conan-center-index.git
git fetch conan-io
git checkout conan-io/master -- <the file to add from conan-io>
git commit
```

...and then making a pull request.

## References

- [Git documentation: 8.2 Customizing Git - Git Attributes](https://www.git-scm.com/book/en/v2/Customizing-Git-Git-Attributes)
