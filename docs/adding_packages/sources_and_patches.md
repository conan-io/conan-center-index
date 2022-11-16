# Sources and Patches

This documents contains everything related to the `source()`. This includes picking sources, where they should come from and goes into when and how to modify sources.
These are a very important aspects and it helps us to establish the quality of the packages offered by ConanCenter.

<!-- toc -->
## Contents

  * [Sources](#sources)<!-- endToc -->

## Sources

**Origin of sources:**

* Library sources should come from an official origin like the library source code repository or the official
release/download webpage.

* If an official source archive is available, it should be preferred over an auto-generated archive.

**Source immutability:** Downloaded source code stored under `source` folder should not be modified. Any patch or `replace_in_file` statement should be applied to the copy of this source code when a build is executed (basically in `build()` method).

**Building from sources:** Recipes should always build packages from library sources.

**Sources not accessible:**

* Library sources that are not publicly available will not be allowed in this repository even if the license allows their redistribution.

* If library sources cannot be downloaded from their official origin or cannot be consumed directly due to their
  format, the recommendation is to contact the publisher and ask them to provide the sources in a way/format that can be consumed
  programmatically.

* In case of needing those binaries to use them as a "build require" for some library, we will consider following the approach of adding it
  as a system recipe (`<build_require>/system`) and making those binaries available in the CI machines (if the license allows it).
