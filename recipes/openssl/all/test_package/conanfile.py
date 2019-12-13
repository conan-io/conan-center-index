from conans import CMake, tools, ConanFile
from conans.errors import ConanException
import os


class DefaultNameConan(ConanFile):
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake", "cmake_find_package"

    def _build_cmake(self, use_find_package):
        cmake = CMake(self)

        if self.settings.os == "Android":
            cmake.definitions["CONAN_LIBCXX"] = ""
        cmake.definitions["USE_FIND_PACKAGE"] = use_find_package
        cmake.definitions["OPENSSL_ROOT_DIR"] = self.deps_cpp_info["openssl"].rootpath
        cmake.definitions["OPENSSL_USE_STATIC_LIBS"] = not self.options["openssl"].shared
        if self.settings.compiler == 'Visual Studio':
            cmake.definitions["OPENSSL_MSVC_STATIC_RT"] = 'MT' in str(self.settings.compiler.runtime)

        cmake.configure()
        cmake.build()
        if use_find_package:
            for bad_target in ("test_crypto_bad", "test_ssl_bad"):
                try:
                    cmake.build(target=bad_target)
                    assert False
                except ConanException:
                    pass

    def build(self):
        self._build_cmake(use_find_package=True)
        self._build_cmake(use_find_package=False)

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "digest")
            self.run(bin_path, run_environment=True)
            bin_path = os.path.join("bin", "test_crypto")
            self.run(bin_path, run_environment=True)
            bin_path = os.path.join("bin", "test_ssl")
            self.run(bin_path, run_environment=True)
        assert os.path.exists(os.path.join(self.deps_cpp_info["openssl"].rootpath, "licenses", "LICENSE"))
