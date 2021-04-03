# Packaging Policy

This document gathers all the relevant information regarding the general lines to follow while creating new recipes that will eventually be
part of this repository.

## Sources

**Origin of sources:** Library sources should come from an official origin like the library source code repository or the official
release/download webpage.

**Building from sources:** Recipes should always build packages from library sources.

**Sources not accessible:**

- Library sources that are not publicly available will not be allowed in this repository even if the license allows their redistribution.

- If library sources cannot be downloaded from their official origin or cannot be consumed directly due to their
  format, the recommendation is to contact the publisher and ask them to provide the sources in a way/format that can be consumed
  programmatically.

- In case of needing those binaries to use them as a "build require" for some library, we will consider following the approach of adding it
  as a system recipe (`<build_require>/system`) and making those binaries available in the CI machines (if the license allows it).
