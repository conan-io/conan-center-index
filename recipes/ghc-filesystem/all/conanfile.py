import os

from conans import ConanFile, CMake, tools


class GhcFilesystemRecipe(ConanFile):
    name = "ghc-filesystem"
    description = "A header-only single-file std::filesystem compatible helper library"
    topics = ("conan", "ghc-filesystem", "header-only", "filesystem")
    homepage = "https://github.com/gulrak/filesystem"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    generators = "cmake"
    no_copy_source = True
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "filesystem-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["GHC_FILESYSTEM_BUILD_TESTING"] = False
        self._cmake.definitions["GHC_FILESYSTEM_BUILD_EXAMPLES"] = False
        self._cmake.definitions["GHC_FILESYSTEM_WITH_INSTALL"] = True
        self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "ghcFilesystem"
        self.cpp_info.names["cmake_find_package_multi"] = "ghcFilesystem"
        self.cpp_info.components["filesystem"].names["cmake_find_package"] = "ghc_filesystem"
        self.cpp_info.components["filesystem"].names["cmake_find_package_multi"] = "ghc_filesystem"
