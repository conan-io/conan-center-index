from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.scm import Version
from conan.tools.files import copy, get, export_conandata_patches, apply_conandata_patches
from conan.tools.layout import cmake_layout
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.53.0"


class YACLibConan(ConanFile):
    name = "yaclib"
    description = "lightweight C++ library for concurrent and parallel task execution"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/YACLib/YACLib"
    license = "MIT"
    topics = "c++", "async", "parallel", "concurrency"
    settings = "os", "arch", "compiler", "build_type"

    _yaclib_flags = {
        "warn": [True, False],
        "coro": [True, False],
        "disable_futex": [True, False],
        "disable_unsafe_futex": [True, False],
        "disable_symmetric_transfer": [True, False],
        "disable_final_suspend_transfer": [True, False],
    }

    options = {
        "fPIC": [True, False],
        **_yaclib_flags,
    }

    default_options = {
        "fPIC": True,
        **{k: False for k in _yaclib_flags},
    }

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "Visual Studio": "14.20",
            "msvc": "192",
            "clang": "8",
            "apple-clang": "12",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        if self.settings.compiler.get_safe("cppstd"):
            tc.variables["YACLIB_CXX_STANDARD"] = self.settings.compiler.cppstd

        flags = []
        for flag in self._yaclib_flags:
            if self.options.get_safe(flag):
                flags.append(flag.upper())

        if flags:
            tc.variables["YACLIB_FLAGS"] = ";".join(flags)

        tc.generate()

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 20 if self.options.coro else 17)
        else:
            if self._compilers_minimum_version.get(str(self.settings.compiler)):
                if Version(self.settings.compiler.version) < self._compilers_minimum_version.get(str(self.settings.compiler)):
                    raise ConanInvalidConfiguration(
                        "yaclib requires a compiler supporting c++17")
            else:
                self.output.warn(
                    "yaclib recipe does not recognize the compiler. yaclib requires a compiler supporting c++17. Assuming it does.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "yaclib")
        self.cpp_info.set_property("cmake_target_name", "yaclib")
        self.cpp_info.set_property("pkg_config_name", "yaclib")
        self.cpp_info.libs = ["libyaclib.a"]
        if self.options.get_safe("coro"):
            if self.settings.libcxx == 'libstdc++11':
                self.cpp_info.cxxflags.append("-fcoroutines")
