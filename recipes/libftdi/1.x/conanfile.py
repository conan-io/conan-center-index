import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class LibFtdiConan(ConanFile):
    name = "libftdi"
    description = "A library to talk to FTDI chips"
    license = "LGPL-2.0-only", "GPLv2-or-later"
    topics = ("conan", "libftdi1")
    homepage = "https://www.intra2net.com/en/developer/libftdi/"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake", "cmake_find_package", "pkg_config"
    settings = "os", "arch", "compiler", "build_type"
    options = {
            "shared": [True, False], 
            "fPIC": [True, False]
    }
    default_options = {
            "shared": False, 
            "fPIC": True
    }
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "libftdi1-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("Building with Visual Studio is not supported")

    def build_requirements(self):
        if not tools.which("pkg-config"):
            self.build_requires("pkgconf/1.7.3")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        options = {
            "BUILD_TESTS": False,
            "EXAMPLES": False,
            "FTDI_EEPROM": False,
            "FTDIPP" : True,
            "STATICLIBS": not self.options.shared
        }
        self._cmake.definitions.update(options)
        self._cmake.configure()
        return self._cmake

    def requirements(self):
        self.requires("libusb/1.0.24")
        self.requires("boost/1.75.0")

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        lib_folder = os.path.join(self.package_folder, "lib",)
        tools.rmdir(os.path.join(lib_folder, "cmake"))
        tools.rmdir(os.path.join(lib_folder, "pkgconfig"))
        os.unlink(os.path.join(self.package_folder, "bin", "libftdi1-config"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "LibFTDI1"
        self.cpp_info.names["cmake_find_package_multi"] = "LibFTDI1"
        self.cpp_info.names["pkgconfig"] = "libftdi1"

        self.cpp_info.components["ftdi"].names["pkg_config"] = "libftdi1"
        self.cpp_info.components["ftdi"].libs = ["ftdi1"]
        self.cpp_info.components["ftdi"].requires = ["libusb::libusb"]
        self.cpp_info.components["ftdi"].includedirs.append(os.path.join("include", "libftdi1"))

        self.cpp_info.components["ftdipp"].names["pkg_config"] = "libftdi1pp"
        self.cpp_info.components["ftdipp"].libs = ["ftdipp1"]
        self.cpp_info.components["ftdipp"].requires = ["ftdi", "boost::headers"]
        self.cpp_info.components["ftdipp"].includedirs.append(os.path.join("include", "libftdipp1"))
