# Policy about patching

The main guideline in ConanCenter is to provide already compiled binaries
for a set of architectures in the least surprising way as possible, so Conan
can be plugged into existing projects trying to minimize the modifications
needed. Packages from Conan Center should fulfill the expectations of anyone
reading the changelog of the library, the documentation, or any statement by
the library maintainers.


<!-- toc -->
## Contents<!-- endToc -->

## Rules

These are the rules that apply to regular version of Conan packages:

**Build system patches.-** In order to add libraries into ConanCenter sometimes
it is NEEDED to apply patches so they can consume existing packages
for requirements and binaries can be generated. These patches are totally
needed for the purpose of ConanCenter and Conan keeps adding features trying
to minimize these changes.

**Source patches.-** ConanCenter DOES NOT accept patches **backporting bugfixes or
features** from upcoming releases, they break the principle of minimum surprise,
they change the behavior of the library and it will no longer match the
documentation or the changelog originally delivered by the authors.

However, ConanCenter DOES accept **working software patches**, these patches
are needed to generate the binaries for architectures not considered by
library maintainers, or to use some compilers or configurations. These patches
make it possible to generate binaries that cannot be generated otherwise, or
they can turn a crashing binary into a working software one (bugs, errors, or
faults are considered working software as long as they produce deterministic
results).

Patches to sources to add support to newer versions of dependencies are
considered feature patches and they are not allowed either. They can
introduce new behaviors or bugs not considered when delivering the
library by maintainers. If a requirement is known not to work, the recipe
should raise a `ConanInvalidConfiguration` from the `validate()` method.

**Vulnerability patches.-** Patches published to CVE databases or declared as
vulnerabilities by the authors in non-mainstream libraries WILL be applied
to packages generated in Conan Center.

**Official release patches.-** If the library documents that a patch should be
applied to sources when building a tag/release from sources, ConanCenter WILL
apply that patch too. This is needed to match the documented behavior or the
binaries of that library offered by other means. [Example here](https://www.boost.org/users/history/version_1_73_0.html).


## Exceptions

Exceptionally, we might find libraries that aren't actively developed and consumers
might benefit from having some bugfixes applied to previous versions while
waiting for the next release, or because the library is no longer maintained. These
are the rules for this exceptional scenario:
 * **new release**, based on some official release and clearly identifiable will
 be create to apply these patches to: PLACEHOLDER_FOR_RELEASE_FORMAT.
 * **only patches backporting bugfixes** will be accepted after they have
 been submitted to the upstream and there is a consensus that it's a bug and the patch is the solution.

ConanCenter will build this patched release and serve its binaries like it does with
any other Conan reference.

Notice that these PLACEHOLDER_FOR_RELEASE_FORMAT releases are unique to ConanCenter
and they can get new patches or discard existing ones according to upstream
considerations. It means that these releases will modify its behavior without previous
notice, the documentation or changelog for these specific releases won't exist. Use
them carefully in your projects.

## Patches: format and conventions

Patches are preferred over `replace_in_file` statement. Patches should always include
a link to the origin where it's taken from (it doesn't apply to build system patches).
They will be listed in `conandata.yml` file and exported together with the recipe.
