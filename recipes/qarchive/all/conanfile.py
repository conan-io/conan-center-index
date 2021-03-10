import os
from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration
from textwrap import dedent

class qarchiveConan(ConanFile):
    name = "qarchive"
    license = "BSD-3-Clause"
    homepage = "https://antonyjr.in/QArchive/"
    url = "https://github.com/conan-io/conan-center-index"
    description = ("QArchive is a cross-platform C++ library that modernizes libarchive ,\
                    This library helps you to extract and compress archives supported by libarchive")
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, "fPIC": True}
    generators = "cmake", "cmake_find_package"
    topics = ("conan", "qt", "Qt", "compress", "libarchive")
    exports_sources = ["CMakeLists.txt", "patches/*"]
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.configure()
        return self._cmake

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def build_requirements(self):
        self.build_requires("cmake/3.19.6")

    def requirements(self):
        self.requires("libarchive/3.4.0")
        self.requires("qt/5.15.2")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "QArchive-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.names["cmake_find_package"] = "QArchive"
        self.cpp_info.names["cmake_find_package_multi"] = "QArchive"
