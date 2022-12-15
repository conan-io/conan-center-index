import os
from conan import ConanFile
from conan.tools.files import get, rmdir, export_conandata_patches
from conan.tools.files import apply_conandata_patches, copy
from conan.tools.cmake import CMakeToolchain, CMake, CMakeDeps, cmake_layout
from conan.errors import ConanInvalidConfiguration


class LibFtdiConan(ConanFile):
    name = "libftdi"
    description = "A library to talk to FTDI chips"
    license = "LGPL-2.0-only", "GPLv2-or-later"
    topics = ("conan", "libftdi1")
    homepage = "https://www.intra2net.com/en/developer/libftdi/"
    url = "https://github.com/conan-io/conan-center-index"
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

    def export_sources(self):
        export_conandata_patches(self)

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

    def generate(self):
        tc = CMakeToolchain(self)
        # Boolean values are preferred instead of "ON"/"OFF"
        tc.variables["BUILD_TESTS"] = False
        tc.variables["EXAMPLES"] = False
        tc.variables["FTDI_EEPROM"] = self.options.build_eeprom_tool
        tc.variables["FTDIPP"] = self.options.enable_cpp_wrapper
        tc.variables["ENABLE_STREAMING"] = self.options.use_streaming
        tc.variables["LIB_SUFFIX"] = ""
        tc.generate()
        # In case there are dependencies listed on requirements, CMakeDeps should be used
        tc = CMakeDeps(self)
        tc.generate()

    def requirements(self):
        self.requires("libusb/1.0.24")
        if self.options.enable_cpp_wrapper:
            self.requires("boost/1.75.0")

    def validate(self):
        if self.settings.compiler == "Visual Studio" and self.options.use_streaming:
            raise ConanInvalidConfiguration("VS doesn't not compile with enabled option use_streaming")

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
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
