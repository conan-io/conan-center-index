from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get, apply_conandata_patches, copy, export_conandata_patches


class LevelZeroConan(ConanFile):
    name = "level-zero"
    license = "MIT"
    homepage = "https://github.com/oneapi-src/level-zero"
    url = "https://github.com/conan-io/conan-center-index"
    description = "OneAPI Level Zero Specification Headers and Loader"
    topics = ("api-headers", "loader", "level-zero", "oneapi")
    package_id_non_embed_mode = "patch_mode"
    package_type = "shared-library"

    # Binary configuration
    settings = "os", "arch", "compiler", "build_type"

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        get(self, **version_data, strip_root=True)

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        apply_conandata_patches(self)
        deps = CMakeDeps(self)
        deps.generate()

        toolchain = CMakeToolchain(self)
        toolchain.generate()

    def validate_build(self):
        if self.settings.os == "Macos":
            raise ConanInvalidConfiguration("This package does not support macOS.")
        if self.settings.os == "Windows":
            if self.settings.get_safe("subsystem") == "uwp":
                raise ConanInvalidConfiguration("This library does not support UWP on Windows.")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["ze_loader"]
        self.cpp_info.includedirs = ["include", "include/level_zero"]
