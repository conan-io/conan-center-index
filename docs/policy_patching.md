# Policy about patching

The main guideline in ConanCenter is to provide already compiled binaries 
for a set of architectures in the least surprising way as possible, so Conan 
can be plugged into existing projects trying to minimize the modifications 
needed. Packages from Conan Center should fulfill the expectations of anyone 
reading the changelog of the library, the documentation, or any statement by 
the library maintainers.

**Build system patches.-** In order to add libraries into ConanCenter sometimes 
it is necessary to apply patches so they can consume existing packages 
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
vulnerabilities by the authors in non-mainstream libraries will be applied 
to packages generated in Conan Center.
