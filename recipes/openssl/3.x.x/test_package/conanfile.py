from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def _with_legacy(self):
        return (not self.dependencies["openssl"].options.no_legacy and
            ((not self.dependencies["openssl"].options.no_md4) or
              (not self.dependencies["openssl"].options.no_rmd160)))

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["OPENSSL_WITH_LEGACY"] = self._with_legacy()
        tc.cache_variables["OPENSSL_WITH_MD4"] = not self.dependencies["openssl"].options.no_md4
        tc.cache_variables["OPENSSL_WITH_RIPEMD160"] = not self.dependencies["openssl"].options.no_rmd160
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
