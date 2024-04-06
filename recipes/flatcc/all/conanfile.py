import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building, can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class FlatccConan(ConanFile):
    name = "flatcc"
    description = "C language binding for Flatbuffers, an efficient cross platform serialization library"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/dvidelabs/flatcc"
    topics = ("flatbuffers", "serialization")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "portable": [True, False],
        "gnu_posix_memalign": [True, False],
        "runtime_lib_only": [True, False],
        "verify_assert": [True, False],
        "verify_trace": [True, False],
        "reflection": [True, False],
        "native_optim": [True, False],
        "fast_double": [True, False],
        "ignore_const_condition": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "portable": False,
        "gnu_posix_memalign": True,
        "runtime_lib_only": False,
        "verify_assert": False,
        "verify_trace": False,
        "reflection": True,
        "native_optim": False,
        "fast_double": False,
        "ignore_const_condition": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os == "Windows":
            if is_msvc(self) and self.options.shared:
                # Building flatcc shared libs with Visual Studio is broken
                raise ConanInvalidConfiguration("Building flatcc libraries shared is not supported")
            if Version(self.version) == "0.6.0" and self.settings.compiler == "gcc":
                raise ConanInvalidConfiguration("Building flatcc with MinGW is not supported")
        if cross_building(self) and not can_run(self):
            raise ConanInvalidConfiguration(f"Cross-building for a non-native architecture ({self.settings.arch}) is not supported")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["FLATCC_PORTABLE"] = self.options.portable
        tc.variables["FLATCC_GNU_POSIX_MEMALIGN"] = self.options.gnu_posix_memalign
        tc.variables["FLATCC_RTONLY"] = self.options.runtime_lib_only
        tc.variables["FLATCC_INSTALL"] = True
        tc.variables["FLATCC_COVERAGE"] = False
        tc.variables["FLATCC_DEBUG_VERIFY"] = self.options.verify_assert
        tc.variables["FLATCC_TRACE_VERIFY"] = self.options.verify_trace
        tc.variables["FLATCC_REFLECTION"] = self.options.reflection
        tc.variables["FLATCC_NATIVE_OPTIM"] = self.options.native_optim
        tc.variables["FLATCC_FAST_DOUBLE"] = self.options.fast_double
        tc.variables["FLATCC_IGNORE_CONST_COND"] = self.options.ignore_const_condition
        tc.variables["FLATCC_TEST"] = False
        tc.variables["FLATCC_ALLOW_WERROR"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        if self.settings.build_type == "Debug" and not self.settings.os == "Windows":
            debug_suffix = "_d" if self.settings.build_type == "Debug" else ""
            os.rename(os.path.join(self.package_folder, "bin", f"flatcc{debug_suffix}"),
                      os.path.join(self.package_folder, "bin", "flatcc"))
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        fix_apple_shared_install_name(self)

    def package_info(self):
        debug_suffix = "_d" if self.settings.build_type == "Debug" else ""
        if not self.options.runtime_lib_only:
            self.cpp_info.libs.append(f"flatcc{debug_suffix}")
        self.cpp_info.libs.append(f"flatccrt{debug_suffix}")

        # TODO: to remove in conan v2
        bin_path = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_path)
