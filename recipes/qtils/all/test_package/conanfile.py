from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import can_run, check_min_cppstd
from conan.tools.cmake import cmake_layout, CMake
from conan.tools.scm import Version
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 20)  # 与主包保持一致

        # 验证编译器版本
        minimum_version = {
            "apple-clang": "11",
            "clang": "10",
            "gcc": "10",
            "msvc": "192",
            "Visual Studio": "16",
        }
        compiler = str(self.settings.compiler)
        version = str(self.settings.compiler.version)
        if compiler in minimum_version and Version(version) < minimum_version[compiler]:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires {compiler} >= {minimum_version[compiler]}"
            )

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")
