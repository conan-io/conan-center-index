from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, stdcpp_library
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"

class STXConan(ConanFile):
    name = 'stx'
    description = 'C++17 & C++ 20 error-handling and utility extensions.'
    license = 'MIT'
    url = 'https://github.com/conan-io/conan-center-index'
    homepage = 'https://github.com/lamarrr/STX'
    topics = ('error-handling', 'result', 'option', 'backtrace', 'panic')
    package_type = "static-library"
    settings = 'os', 'arch', 'compiler', 'build_type'
    options = {
        'fPIC': [True, False],
        'backtrace': [True, False],
        'custom_panic_handler': [True, False],
    }
    default_options = {
        'fPIC': True,
        'backtrace': False,
        'custom_panic_handler': False,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "clang": "7",
            "apple-clang": "12",
            "Visual Studio": "16",
            "msvc": "192",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.backtrace:
            self.requires('abseil/20230125.3')

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if self.settings.compiler == "clang":
            libcxx = stdcpp_library(self)
            compiler_version = Version(self.settings.compiler.version)
            if (libcxx == "stdc++" and compiler_version < 9) or (libcxx == "c++" and compiler_version < 10):
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd} language and standard library features "
                    f"which clang < {compiler_version} with lib{libcxx} lacks"
                )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables['STX_ENABLE_BACKTRACE'] = self.options.backtrace
        tc.variables['STX_CUSTOM_PANIC_HANDLER'] = self.options.custom_panic_handler
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

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
        self.cpp_info.libs = ["stx"]

        if self.options.backtrace:
            self.cpp_info.requires = [
                'abseil::absl_stacktrace',
                'abseil::absl_symbolize'
            ]

        if self.settings.os in ["Linux", "FreeBSD", 'Android']:
            self.cpp_info.system_libs = ['atomic']
