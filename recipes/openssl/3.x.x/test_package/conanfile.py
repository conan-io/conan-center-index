from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
import os

required_conan_version = ">=1.50.2 <1.51.0 || >=1.51.2"


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    @property
    def _with_legacy(self):
        openssl = self.dependencies["openssl"]
        return (not openssl.options.no_legacy and
            ((not openssl.options.no_md4) or
              (not openssl.options.no_rmd160)))

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        openssl = self.dependencies["openssl"]
        tc.cache_variables["OPENSSL_WITH_ZLIB"] = not openssl.options.no_zlib
        tc.cache_variables["OPENSSL_WITH_LEGACY"] = self._with_legacy
        tc.cache_variables["OPENSSL_WITH_MD4"] = not openssl.options.no_md4
        tc.cache_variables["OPENSSL_WITH_RIPEMD160"] = not openssl.options.no_rmd160
        if self.settings.os == "Android":
            tc.cache_variables["CONAN_LIBCXX"] = ""
        tc.generate()


    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "digest")
            self.run(bin_path, env="conanrun")

            if not self.options["openssl"].no_legacy:
                bin_legacy_path = os.path.join(self.cpp.build.bindirs[0], "digest_legacy")
                self.run(bin_legacy_path, run_environment=True)

            if not self.options["openssl"].no_stdio:
                self.run("openssl version", run_environment=True)
        assert os.path.exists(os.path.join(self.deps_cpp_info["openssl"].rootpath, "licenses", "LICENSE.txt"))
