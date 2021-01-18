from conans import CMake, tools, ConanFile
import os


class DefaultNameConan(ConanFile):
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake"

    def _build_cmake(self, use_find_package):
        cmake = CMake(self)

        if self.settings.os == "Android":
            cmake.definitions["CONAN_LIBCXX"] = ""
        # no_zlib is deleted from options for openssl > 1.1.0 because zlib is always required
        cmake.definitions["OPENSSL_WITH_ZLIB"] = \
            ("no_zlib" not in self.options["openssl"]) or (not self.options["openssl"].no_zlib)
        cmake.definitions["USE_FIND_PACKAGE"] = use_find_package
        cmake.definitions["OPENSSL_ROOT_DIR"] = self.deps_cpp_info["openssl"].rootpath
        cmake.definitions["OPENSSL_USE_STATIC_LIBS"] = not self.options["openssl"].shared
        if self.settings.compiler == 'Visual Studio':
            cmake.definitions["OPENSSL_MSVC_STATIC_RT"] = 'MT' in str(self.settings.compiler.runtime)

        cmake.configure()
        cmake.build()

    def build(self):
        self._build_cmake(use_find_package=True)
        self._build_cmake(use_find_package=False)

    def test(self):
        if not tools.cross_building(self.settings, skip_x64_x86=(self.settings.os == "Windows")):
            bin_path = os.path.join("bin", "digest")
            self.run(bin_path, run_environment=True)
        assert os.path.exists(os.path.join(self.deps_cpp_info["openssl"].rootpath, "licenses", "LICENSE"))
