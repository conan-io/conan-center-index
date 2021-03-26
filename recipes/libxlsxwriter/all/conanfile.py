import os
from conans import ConanFile, CMake, tools


class LibxlsxwriterConan(ConanFile):
    name = "libxlsxwriter"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jmcnamara/libxlsxwriter"
    topics = ("conan", "Excel", "XLSX")
    description = "A C library for creating Excel XLSX files"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False, 
        "fPIC": True
    }
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("minizip/1.2.11")
        self.requires("zlib/1.2.11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("libxlsxwriter-RELEASE_{}".format(self.version), self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["BUILD_EXAMPLES"] = False
        self._cmake.definitions["USE_STATIC_MSVC_RUNTIME"] = (self.settings.os == "Windows" and "MT" in str(self.settings.compiler.runtime))
        self._cmake.definitions["USE_SYSTEM_MINIZIP"] = True

        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("License.txt", src=self._source_subfolder, dst="licenses")


    def package_info(self):
        self.cpp_info.libs = ["xlsxwriter"]

