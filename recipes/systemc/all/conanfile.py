from conan import ConanFile, conan_version
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


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
        if is_apple_os(self):
            raise ConanInvalidConfiguration("Macos build not supported")

        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration(
                "Building SystemC as a shared library on Windows is currently not supported"
            )

        if (
            conan_version.major == 1
            and self.settings.compiler == "gcc"
            and Version(self.settings.compiler.version) <= "5"
        ):
            raise ConanInvalidConfiguration(
                f"GCC {self.settings.compiler.version} is not supported by SystemC on Conan v1"
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

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
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
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

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "SystemCLanguage"
        self.cpp_info.filenames["cmake_find_package_multi"] = "SystemCLanguage"
        self.cpp_info.names["cmake_find_package"] = "SystemC"
        self.cpp_info.names["cmake_find_package_multi"] = "SystemC"
        self.cpp_info.components["_systemc"].names["cmake_find_package"] = "systemc"
        self.cpp_info.components["_systemc"].names["cmake_find_package_multi"] = "systemc"
        self.cpp_info.components["_systemc"].set_property("cmake_target_name", "SystemC::systemc")
