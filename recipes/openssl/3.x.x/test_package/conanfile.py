from conans import CMake, tools, ConanFile
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake", "cmake_find_package", "pkg_config"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["OPENSSL_WITH_ZLIB"] = not self.options["openssl"].no_zlib
        if self.settings.os == "Android":
            cmake.definitions["CONAN_LIBCXX"] = ""
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "digest")
            self.run(bin_path, run_environment=True)

            if not self.options["openssl"].no_stdio:
                self.run("openssl version", run_environment=True)
        assert os.path.exists(os.path.join(self.deps_cpp_info["openssl"].rootpath, "licenses", "LICENSE.txt"))

        for fn in ("libcrypto.pc", "libssl.pc", "openssl.pc",):
            assert os.path.isfile(os.path.join(self.build_folder, fn))
