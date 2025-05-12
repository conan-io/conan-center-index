from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.build import check_min_cppstd
import os

from conan.tools.scm import Version

required_conan_version = ">=2.1"


class SystemcConan(ConanFile):
    name = "systemc"
    description = ("SystemC is a set of C++ classes and macros which provide "
                   "an event-driven simulation interface.")
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.accellera.org/"
    topics = ("simulation", "modeling", "esl", "tlm")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "disable_async_updates": [True, False],
        "disable_copyright_msg": [True, False],
        "disable_virtual_bind": [True, False],
        "enable_assertions": [True, False],
        "enable_immediate_self_notifications": [True, False],
        "enable_pthreads": [True, False],
        "enable_phase_callbacks": [True, False],
        "enable_phase_callbacks_tracing": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "disable_async_updates": False,
        "disable_copyright_msg": False,
        "disable_virtual_bind": False,
        "enable_assertions": True,
        "enable_immediate_self_notifications": False,
        "enable_pthreads": False,
        "enable_phase_callbacks": False,
        "enable_phase_callbacks_tracing": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            self.options.rm_safe("enable_pthreads")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if is_apple_os(self) and Version(self.version) < "3.0.1":
            raise ConanInvalidConfiguration("Macos build not supported")

        if Version(self.version) >= "3.0.0":
            # INFO: Starting from SystemC 3.0.0, C++17 is required
            # https://github.com/accellera-official/systemc/blob/3.0.0/src/CMakeLists.txt#L65
            check_min_cppstd(self, "17")

        if self.settings.os == "Windows" and self.options.shared and Version(self.version) < 3:
            raise ConanInvalidConfiguration(
                "Building SystemC as a shared library on Windows is currently not supported"
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["DISABLE_ASYNC_UPDATES"] = self.options.disable_async_updates
        tc.variables["DISABLE_COPYRIGHT_MESSAGE"] = self.options.disable_copyright_msg
        tc.variables["DISABLE_VIRTUAL_BIND"] = self.options.disable_virtual_bind
        tc.variables["ENABLE_ASSERTIONS"] = self.options.enable_assertions
        tc.variables["ENABLE_IMMEDIATE_SELF_NOTIFICATIONS"] = self.options.enable_immediate_self_notifications
        tc.variables["ENABLE_PTHREADS"] = self.options.get_safe("enable_pthreads", False)
        tc.variables["ENABLE_PHASE_CALLBACKS"] = self.options.get_safe("enable_phase_callbacks", False)
        tc.variables["ENABLE_PHASE_CALLBACKS_TRACING"] = self.options.get_safe("enable_phase_callbacks_tracing", False)
        if Version(self.version) < "3.0.0":
            tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5" # CMake 4 support
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        copy(self, "NOTICE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "SystemCLanguage")
        self.cpp_info.set_property("cmake_target_name", "SystemC::systemc")

        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["_systemc"].libs = ["systemc"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_systemc"].system_libs = ["pthread", "m"]
        if is_msvc(self):
            self.cpp_info.components["_systemc"].cxxflags.append("/vmg")
            if Version(self.version) >= 3 and self.options.shared:
                # https://github.com/accellera-official/systemc/blob/main/INSTALL.md#33-building-against-a-systemc-dll
                self.cpp_info.components["_systemc"].defines = ["SC_WIN_DLL"]
                self.cpp_info.components["_systemc"].libs = [f"systemc-{self.version}"]

        self.cpp_info.components["_systemc"].set_property("cmake_target_name", "SystemC::systemc")
        if Version(self.version) >= "3" and self.settings.os == "Macos":
            # INFO: sanitizer methods are undefined on Mac, need to force linker to ignore them
            # https://github.com/accellera-official/systemc/blob/3.0.1/src/CMakeLists.txt#L103
            self.cpp_info.components["_systemc"].exelinkflags = ["LINKER:-U,___sanitizer_start_switch_fiber", "LINKER:-U,___sanitizer_finish_switch_fiber"]
