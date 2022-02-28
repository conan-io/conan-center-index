from conans import CMake, tools, ConanFile
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package"

    @property
    def _skip_test(self):
        # Attempting to use @rpath without CMAKE_SHARED_LIBRARY_RUNTIME_C_FLAG being
        # set. This could be because you are using a Mac OS X version less than 10.5
        # or because CMake's platform configuration is corrupt.
        # FIXME: Remove once CMake on macOS/M1 CI runners is upgraded.
        # Actually the workaround should be to add cmake/3.22.0 to build requires,
        # but for the specific case of openssl it fails because it is also a requirement of cmake.
        # see https://github.com/conan-io/conan/pull/9839
        return self.settings.os == "Macos" and self.settings.arch == "armv8" \
               and self.options["openssl"].shared

    def build(self):
        if not self._skip_test:
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
        if not self._skip_test and not tools.cross_building(self):
            bin_path = os.path.join("bin", "digest")
            self.run(bin_path, run_environment=True)
            if self.settings.os == 'Macos' and self.options["openssl"].shared:
                # Ensure we can run install_name_tool on the libraries
                libssl_dylib = 'libssl.dylib'
                libssl = os.path.join(self.deps_cpp_info["openssl"].rootpath, 'lib', libssl_dylib)
                self.run(f'rm -f {libssl_dylib}')
                self.run(f'cp {libssl} {libssl_dylib}')
                long_rpath = 'poijfpeoifjperwonfjpnocjpnqoefjpneojntvqpeonijtpqeonrvtijpqvneoitjvqpneoitjnvpqeonijtvpqoeijrtvpqoeritjvpqeoijtqpevnoitjpqenotijqepo'
                self.run(f'install_name_tool -add_rpath {long_rpath} {libssl_dylib}')
        assert os.path.exists(os.path.join(self.deps_cpp_info["openssl"].rootpath, "licenses", "LICENSE"))
