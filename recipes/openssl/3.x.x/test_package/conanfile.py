from conan import ConanFile
from conan.errors import ConanException
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

    @property
    def _openssl(self):
        return self.dependencies["openssl"]

    def _with_legacy(self):
        return (not self._openssl.options.no_legacy and
            ((not self._openssl.options.no_md4) or
              (not self._openssl.options.no_rmd160)))

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["OPENSSL_WITH_LEGACY"] = self._with_legacy()
        tc.cache_variables["OPENSSL_WITH_MD4"] = not self._openssl.options.no_md4
        tc.cache_variables["OPENSSL_WITH_RIPEMD160"] = not self._openssl.options.no_rmd160
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
        self._test_fips_module_version()

    def _fips_module_path(self):
        suffix = {"Macos": "dylib", "Windows": "dll"}.get(str(self.settings.os), "so")
        return os.path.join(self._openssl.package_folder, "lib", "ossl-modules", f"fips.{suffix}")

    def _test_fips_module_version(self):
        fips_module_version = self._openssl.options.get_safe("fips_module_version")
        if not fips_module_version:
            return

        fips_module = self._fips_module_path()
        if not os.path.isfile(fips_module):
            raise ConanException(f"FIPS module not found at {fips_module}")

        expected = str(fips_module_version).encode("utf-8")
        with open(fips_module, "rb") as module_file:
            if expected not in module_file.read():
                raise ConanException(f"FIPS module does not report expected version {fips_module_version}")
