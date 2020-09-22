from conans import ConanFile, CMake, tools
from conans.tools import download, unzip
import os, re

class h5ppConan(ConanFile):
    name = "h5pp"
    version = "1.8.2"
    description = "A C++17 wrapper for HDF5 with focus on simplicity"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/DavidAce/h5pp"
    topics = ("conan","h5pp","hdf5", "binary", "storage")
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"
    requires = "eigen/3.3.7", "spdlog/1.7.0", "hdf5/1.12.0"
    exports_sources = ["CMakeLists.txt"]

    options = {
        'tests'     :[True,False],
        'examples'  :[True,False],
        'verbose'   :[True,False],
        }

    default_options = (
        'tests=False',
        'examples=False',
        'verbose=False',
    )

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        tools.check_min_cppstd(self, "17")
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["H5PP_ENABLE_TESTS"]         = self.options.tests
            self._cmake.definitions["H5PP_BUILD_EXAMPLES"]       = self.options.examples
            self._cmake.definitions["H5PP_PRINT_INFO"]           = self.options.verbose
            self._cmake.definitions["H5PP_DOWNLOAD_METHOD"]      = "conan"
            self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def build(self):
        if self.options.tests or self.options.examples:
            cmake = self._configure_cmake()
            cmake.build()

    def test(self):
        if self.options.tests:
            cmake = self._configure_cmake()
            cmake.build()
            cmake.test()
        else:
            print("Tests have not been enabled. To enable, set option h5pp:tests=True")

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_id(self):
        self.info.header_only()
