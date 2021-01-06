import os

from conans import ConanFile, CMake, tools


class GhcFilesystemRecipe(ConanFile):
    name = "ghcfilesystem"
    description = "A header-only single-file std::filesystem compatible helper library"
    topics = ("conan", "bhcfilesystem", "header-only", "filesystem")
    homepage = "https://github.com/gulrak/filesystem"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    no_copy_source=True
    
    _cmake = None
    
    options = {
        "run_tests": [True, False]
    }

    default_options = {
        "run_tests": False
    }
   
    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "filesystem-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["GHC_FILESYSTEM_BUILD_TESTING"] = self.options.run_tests
        self._cmake.definitions["GHC_FILESYSTEM_BUILD_EXAMPLES"] = False
        self._cmake.definitions["GHC_FILESYSTEM_WITH_INSTALL"] = True
#        if self.options.run_tests:
#            os.environ["CXXFLAGS"] = "-Wno-deprecated-declarations"  # TODO required? compiler specific!
        self._cmake.configure(
            source_folder=self._source_subfolder,
            build_folder=self._build_subfolder
        )
        return self._cmake

    def build(self):
        if self.options.run_tests:
            cmake = self._configure_cmake()
            cmake.build()
            cmake.test()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.builddirs = [os.path.join("lib", "cmake", "ghcFilesystem")]
        self.cpp_info.names["cmake_find_package"] = "ghcFilesystem"
        self.cpp_info.names["cmake_find_package_multi"] = "ghcFilesystem"

