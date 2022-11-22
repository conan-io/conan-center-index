import os
from conan import ConanFile
from conan.tools.files import get, patch, rmdir
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.errors import ConanInvalidConfiguration


class LibFtdiConan(ConanFile):
    name = "libftdi"
    description = "A library to talk to FTDI chips"
    license = "LGPL-2.0-only", "GPLv2-or-later"
    topics = ("conan", "libftdi1")
    homepage = "https://www.intra2net.com/en/developer/libftdi/"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "CMakeDeps", "CMakeToolchain"
    settings = "os", "arch", "compiler", "build_type"
    options = {
            "shared"             : [True, False], 
            "fPIC"               : [True, False],
            "enable_cpp_wrapper" : [True, False],
            "build_eeprom_tool"  : [True, False],
            "use_streaming"      : [True, False],
    }
    default_options = {
            "shared": False, 
            "fPIC": True,
            "enable_cpp_wrapper": True,
            "build_eeprom_tool" : False,
            "use_streaming"     : True,
    }
    _cmake = None

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            if self.settings.compiler == "Visual Studio":
                self.options.use_streaming = False

    def layout(self):
        cmake_layout(self)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        options = {
            "BUILD_TESTS": False,
            "EXAMPLES": False,
            "FTDI_EEPROM": self.options.build_eeprom_tool,
            "FTDIPP" : self.options.enable_cpp_wrapper,
            "STATICLIBS": not self.options.shared,
            "ENABLE_STREAMING": self.options.use_streaming,
            "LIB_SUFFIX": "",
        }
        self._cmake.configure(variables = options)
        return self._cmake

    def requirements(self):
        self.requires("libusb/1.0.24")
        if self.options.enable_cpp_wrapper:
            self.requires("boost/1.75.0")

    def validate(self):
        if self.settings.compiler == "Visual Studio" and self.options.use_streaming:
            raise ConanInvalidConfiguration("VS doesn't not compile with enabled option use_streaming")

    def build(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            patch(self, **p)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        lib_folder = os.path.join(self.package_folder, "lib",)
        rmdir(self, os.path.join(lib_folder, "cmake"))
        rmdir(self, os.path.join(lib_folder, "pkgconfig"))

    def package_info(self):
        self.cpp_info.names['cmake_find_package'] = "LibFTDI1"
        self.cpp_info.names['cmake_find_package_multi'] = "LibFTDI1"
        self.cpp_info.components["ftdi"].libs = ["ftdi1"]
        self.cpp_info.components["ftdi"].requires = ["libusb::libusb"]
        self.cpp_info.components["ftdi"].includedirs.append(os.path.join("include", "libftdi1"))

        if self.options.enable_cpp_wrapper:
            self.cpp_info.components["ftdipp"].libs = ["ftdipp1"]
            self.cpp_info.components["ftdipp"].requires = ["ftdi", "boost::headers"]
