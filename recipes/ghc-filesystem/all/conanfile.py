from conan import ConanFile, tools
from conans import CMake
import os

required_conan_version = ">=1.43.0"


class GhcFilesystemRecipe(ConanFile):
    name = "ghc-filesystem"
    description = "A header-only single-file std::filesystem compatible helper library"
    topics = ("ghc-filesystem", "header-only", "filesystem")
    homepage = "https://github.com/gulrak/filesystem"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = CMake(self)
        cmake.definitions["GHC_FILESYSTEM_BUILD_TESTING"] = False
        cmake.definitions["GHC_FILESYSTEM_BUILD_EXAMPLES"] = False
        cmake.definitions["GHC_FILESYSTEM_WITH_INSTALL"] = True
        cmake.configure(source_folder=self._source_subfolder)
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ghc_filesystem")
        self.cpp_info.set_property("cmake_target_name", "ghcFilesystem::ghc_filesystem")
        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["ghc_filesystem"].bindirs = []
        self.cpp_info.components["ghc_filesystem"].frameworkdirs = []
        self.cpp_info.components["ghc_filesystem"].libdirs = []
        self.cpp_info.components["ghc_filesystem"].resdirs = []

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "ghc_filesystem"
        self.cpp_info.filenames["cmake_find_package_multi"] = "ghc_filesystem"
        self.cpp_info.names["cmake_find_package"] = "ghcFilesystem"
        self.cpp_info.names["cmake_find_package_multi"] = "ghcFilesystem"
        self.cpp_info.components["ghc_filesystem"].names["cmake_find_package"] = "ghc_filesystem"
        self.cpp_info.components["ghc_filesystem"].names["cmake_find_package_multi"] = "ghc_filesystem"
        self.cpp_info.components["ghc_filesystem"].set_property("cmake_target_name", "ghcFilesystem::ghc_filesystem")
