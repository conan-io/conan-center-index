from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get, apply_conandata_patches, copy, export_conandata_patches, rmdir, replace_in_file
from conan.tools.build import check_min_cppstd
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

    def requirements(self):
        self.requires("spdlog/1.14.1")

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        get(self, **version_data, strip_root=True)
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "source", "loader","ze_loader.cpp"),
                        "#ifdef __linux__", "#if defined(__linux__) || defined(__APPLE__)")

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
        if is_apple_os(self):
            self.output.warning("Level Zero is not known to support Apple platforms")
        if self.settings.os == "Windows" and self.settings.get_safe("subsystem") == "uwp":
            raise ConanInvalidConfiguration(f"{self.ref} does not support UWP on Windows.")

        min_cpp_std = "14"
        check_min_cppstd(self, min_cpp_std)

    def build(self):
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
