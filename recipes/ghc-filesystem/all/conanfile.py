from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=1.50.0"


class GhcFilesystemRecipe(ConanFile):
    name = "ghc-filesystem"
    description = "A header-only single-file std::filesystem compatible helper library"
    topics = ("header-only", "filesystem")
    homepage = "https://github.com/gulrak/filesystem"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["GHC_FILESYSTEM_BUILD_TESTING"] = False
        tc.variables["GHC_FILESYSTEM_BUILD_EXAMPLES"] = False
        tc.variables["GHC_FILESYSTEM_WITH_INSTALL"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder,"licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ghc_filesystem")
        self.cpp_info.set_property("cmake_target_name", "ghcFilesystem::ghc_filesystem")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "ghc_filesystem"
        self.cpp_info.filenames["cmake_find_package_multi"] = "ghc_filesystem"
        self.cpp_info.names["cmake_find_package"] = "ghcFilesystem"
        self.cpp_info.names["cmake_find_package_multi"] = "ghcFilesystem"
        self.cpp_info.components["ghc_filesystem"].names["cmake_find_package"] = "ghc_filesystem"
        self.cpp_info.components["ghc_filesystem"].names["cmake_find_package_multi"] = "ghc_filesystem"
        self.cpp_info.components["ghc_filesystem"].set_property("cmake_target_name", "ghcFilesystem::ghc_filesystem")
        self.cpp_info.components["ghc_filesystem"].bindirs = []
        self.cpp_info.components["ghc_filesystem"].libdirs = []
