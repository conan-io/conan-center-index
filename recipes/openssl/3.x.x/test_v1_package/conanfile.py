from conans import CMake, tools, ConanFile
from conan.tools.build import cross_building
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake", "cmake_find_package", "pkg_config"

    def _with_legacy(self):
        return (not self.options["openssl"].no_legacy and
            ((not self.options["openssl"].no_md4) or
              (not self.options["openssl"].no_rmd160)))

    def build(self):
        cmake = CMake(self)
        cmake.definitions["OPENSSL_WITH_ZLIB"] = not self.options["openssl"].no_zlib
        cmake.definitions["OPENSSL_WITH_LEGACY"] = self._with_legacy()
        cmake.definitions["OPENSSL_WITH_MD4"] = not self.options["openssl"].no_md4
        cmake.definitions["OPENSSL_WITH_RIPEMD160"] = not self.options["openssl"].no_rmd160
        if self.settings.os == "Android":
            cmake.definitions["CONAN_LIBCXX"] = ""
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join("bin", "digest")
            self.run(bin_path, run_environment=True)

            if not self.options["openssl"].no_legacy:
                bin_legacy_path = os.path.join("bin", "digest_legacy")
                self.run(bin_legacy_path, run_environment=True)

            if not self.options["openssl"].no_stdio:
                self.run("openssl version", run_environment=True)
        assert os.path.exists(os.path.join(self.deps_cpp_info["openssl"].rootpath, "licenses", "LICENSE.txt"))

        for fn in ("libcrypto.pc", "libssl.pc", "openssl.pc",):
            assert os.path.isfile(os.path.join(self.build_folder, fn))
