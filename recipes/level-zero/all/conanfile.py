from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get, apply_conandata_patches, copy, export_conandata_patches, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
import os


class LevelZeroConan(ConanFile):
    name = "level-zero"
    license = "MIT"
    homepage = "https://github.com/oneapi-src/level-zero"
    url = "https://github.com/conan-io/conan-center-index"
    description = "OneAPI Level Zero Specification Headers and Loader"
    topics = ("api-headers", "loader", "level-zero", "oneapi")
    package_type = "shared-library"

    # Binary configuration
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "10",
            "clang": "7",
            "gcc": "7",
            "msvc": "190",
            "Visual Studio": "15",
        }

    def requirements(self):
        self.requires("spdlog/1.14.1")

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        get(self, **version_data, strip_root=True)

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        toolchain = CMakeToolchain(self)
        toolchain.generate()

    def validate(self):
        if self.settings.os == "Macos":
            raise ConanInvalidConfiguration("This recipe doesn't prepared for macOS.")
        if self.settings.os == "Windows":
            if self.settings.get_safe("subsystem") == "uwp":
                raise ConanInvalidConfiguration(f"{self.ref} does not support UWP on Windows.")
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.components["ze-loader"].libs = ["ze_loader"]
        self.cpp_info.components["ze-loader"].includedirs = ["include", "include/level_zero"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["ze-loader"].system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["ze-loader"].system_libs = ["cfgmgr32"]
            self.cpp_info.components["ze-loader"].set_property("pkg_config_name", "libze_loader")
            self.cpp_info.components["level-zero"].requires = ["ze-loader"]
            self.cpp_info.components["level-zero"].set_property("pkg_config_name", "level-zero")

