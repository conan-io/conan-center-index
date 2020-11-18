from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

class OatppSwaggerConan(ConanFile):
    name = "podofo"
    license = "GNU-2"
    homepage = "http://podofo.sourceforge.net"
    url = "https://github.com/conan-io/conan-center-index"
    description = "PoDoFo is a library to work with the PDF file format."
    topics = ("conan", "PDF", "PoDoFo", "podofo")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake", "cmake_find_package"
    exports_sources = "CMakeLists.txt"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration("PoDoFo requires GCC >=5")

    def requirements(self):
        self.requires("freetype/2.10.4")
        if self.settings.os == "Linux":
            self.requires("fontconfig/2.13.92")
        self.requires("libjpeg/9d")
        self.requires("libunistring/0.9.10")
        self.requires("libtiff/4.1.0"),
        self.requires("libidn/1.36")
        self.requires("openssl/1.1.1g")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("podofo-{0}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["PODOFO_BUILD_LIB_ONLY"] = True
        if self.options.shared:
            self._cmake.definitions["PODOFO_BUILD_SHARED"] = True
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "podofo"
        self.cpp_info.filenames["cmake_find_package_multi"] = "podofo"
        self.cpp_info.names["pkg_config"] = "libpodofo-0"
        self.cpp_info.names["cmake_find_package"] = "podofo"
        self.cpp_info.names["cmake_find_package_multi"] = "podofo"
        self.cpp_info.libs = ["podofo"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]
