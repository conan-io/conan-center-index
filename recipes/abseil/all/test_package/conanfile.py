from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.scm import Version
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    @property
    def _skip_cpp17_build(self):
        # 20240116 added a hasher for std::filesystem::path, so absl/hash/internal/hash.h
        # includes <filesystem> if in C++17 mode. GCC 7 supported C++17, but notably
        # <filesystem> was added in GCC 8.
        return Version(self.dependencies["abseil"].ref.version) >= "20240116" \
            and self.settings.compiler == "gcc" \
            and Version(self.settings.compiler.version).major == 7

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CXX20_SUPPORTED"] = Version(self.dependencies["abseil"].ref.version) > "20210324.2"
        tc.variables["SKIP_CPP_17_BUILD"] = self._skip_cpp17_build
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(f"{bin_path} -s", env="conanrun")
            bin_global_path = os.path.join(self.cpp.build.bindirs[0], "test_package_global")
            self.run(f"{bin_global_path} -s", env="conanrun")
