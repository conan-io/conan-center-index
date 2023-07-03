from conan import ConanFile
from conan.tools.files import copy, get

import os


class NanoRTConan(ConanFile):
    name = "nanort"
    #version = "0bb8ab5"
    # No settings/options are necessary, this is header only
    exports_sources = "include/*"
    # We can avoid copying the sources to the build folder in the cache
    no_copy_source = True

    # TODO: !!!: metadata: license, description, topics, url, homepage, etc.

    def source(self):
       get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "nanort.h", self.source_folder, os.path.join(self.package_folder, "include", "nanort"))

    def package_info(self):
        # For header-only packages, libdirs and bindirs are not used
        # so it's necessary to set those as empty.
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
