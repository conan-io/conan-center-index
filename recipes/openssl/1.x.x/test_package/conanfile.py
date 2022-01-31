from conans import CMake, tools, ConanFile
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        if self.settings.os == "Android":
            cmake.definitions["CONAN_LIBCXX"] = ""
        openssl_version = tools.Version(self.deps_cpp_info["openssl"].version)
        if openssl_version.major == "1" and openssl_version.minor == "1":
            cmake.definitions["OPENSSL_WITH_ZLIB"] = False
        else:
            cmake.definitions["OPENSSL_WITH_ZLIB"] = not self.options["openssl"].no_zlib
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "digest")
            self.run(bin_path, run_environment=True)
        assert os.path.exists(os.path.join(self.deps_cpp_info["openssl"].rootpath, "licenses", "LICENSE"))
