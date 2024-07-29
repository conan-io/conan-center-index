import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMakeToolchain, CMake, CMakeDeps, cmake_layout
from conan.tools.files import get, rmdir, export_conandata_patches, apply_conandata_patches, copy
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class LibFtdiConan(ConanFile):
    name = "libftdi"
    description = "A library to talk to FTDI chips"
    license = ("LGPL-2.0-only", "GPLv2-or-later")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.intra2net.com/en/developer/libftdi/"
    topics = "ftdi"

    package_type = "library"
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            if is_msvc(self):
                self.options.use_streaming = False

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self.options.build_eeprom_tool or self.options.enable_cpp_wrapper:
            self.license = ("LGPL-2.1-only", "GPL-2.0-only")
        else:
            self.license = "LGPL-2.1-only"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # libusb.h is used in public ftdi.h
        self.requires("libusb/1.0.26", transitive_headers=True, transitive_libs=True)
        if self.options.enable_cpp_wrapper:
            # boost/shared_ptr.hpp is used in public ftdi.hpp
            self.requires("boost/1.83.0", transitive_headers=True)

    def validate(self):
        if is_msvc(self) and self.options.use_streaming:
            raise ConanInvalidConfiguration("VS doesn't not compile with enabled option use_streaming")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTS"] = False
        tc.variables["EXAMPLES"] = False
        tc.variables["FTDI_EEPROM"] = self.options.build_eeprom_tool
        tc.variables["FTDIPP"] = self.options.enable_cpp_wrapper
        tc.variables["ENABLE_STREAMING"] = self.options.use_streaming
        tc.variables["LIB_SUFFIX"] = ""
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING.LIB", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        if self.options.build_eeprom_tool or self.options.enable_cpp_wrapper:
            copy(self, "COPYING.GPL", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        lib_folder = os.path.join(self.package_folder, "lib")
        rmdir(self, os.path.join(lib_folder, "cmake"))
        rmdir(self, os.path.join(lib_folder, "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "LibFTDI1")

        self.cpp_info.components["ftdi"].set_property("pkg_config_name", "libftdi1")
        self.cpp_info.components["ftdi"].libs = ["ftdi1"]
        self.cpp_info.components["ftdi"].requires = ["libusb::libusb"]
        self.cpp_info.components["ftdi"].includedirs.append(os.path.join("include", "libftdi1"))

        if self.options.enable_cpp_wrapper:
            self.cpp_info.components["ftdipp"].set_property("pkg_config_name", "libftdipp1")
            self.cpp_info.components["ftdipp"].libs = ["ftdipp1"]
            self.cpp_info.components["ftdipp"].requires = ["ftdi", "boost::headers"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["ftdipp"].system_libs.append("m")

        # TODO: Remove "self.cpp_info.filenames.." statements in Conan V2
        self.cpp_info.filenames["cmake_find_package"] = "LibFTDI1"
        self.cpp_info.filenames["cmake_find_package_multi"] = "LibFTDI1"
