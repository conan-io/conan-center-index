from conan import ConanFile
from conan.tools.files import copy


class MultiConan(ConanFile):
    name = "b-multi"
    homepage = "https://gitlab.com/correaa/boost-multi"
    description = "Multidimensional array access to contiguous or regularly contiguous memory. (Not an official Boost library)"
    topics = (
        "array",
        "multidimensional",
        "library",
    )
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "header-library"
    no_copy_source = True

    def package(self):
        # This will also copy the "include" folder
        copy(self, "*.hpp", self.source_folder, self.package_folder)

    def package_info(self):
        # For header-only packages, libdirs and bindirs are not used
        # so it's recommended to set those as empty.
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
