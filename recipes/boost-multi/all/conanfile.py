import os

from conan import ConanFile
from conan.tools.files import copy


class MultiConan(ConanFile):
    name = "boost-multi"
    version = "0.90.0"
    homepage = "https://github.com/correaa/boost-multi"
    description = "Multidimensional array access to contiguous or regularly contiguous memory. (Not an official Boost library)"
    topics = (
        "multidimensional",
        "array",
        "header-only",
        "generic-programming",
        "boost",
    )
    license = "BSL-1.0"
    url = "https://github.com/correaa/conan-center-index"
    # No settings/options are necessary, this is header only
    exports_sources = "include/*"
    no_copy_source = True
    package_type = "header-library"

    def package(self):
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        copy(self, "LICENSE", self.source_folder, self.package_folder)

    def package_info(self):
        # For header-only packages, libdirs and bindirs are not used
        # so it's recommended to set those as empty.
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = ["include"]
