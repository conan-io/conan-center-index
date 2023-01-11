from conan import ConanFile
from conan.tools.scm import Version
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
import os

required_conan_version = ">=1.50.2 <1.51.0 || >=1.51.2"


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

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

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        if self.settings.os == "Android":
            tc.cache_variables["CONAN_LIBCXX"] = ""
        openssl = self.dependencies["openssl"]
        openssl_version = Version(openssl.ref.version)
        if openssl_version.major == "1" and openssl_version.minor == "1":
            tc.cache_variables["OPENSSL_WITH_ZLIB"] = False
        else:
            tc.cache_variables["OPENSSL_WITH_ZLIB"] = not openssl.options.no_zlib
        tc.generate()


    def build(self):
        if not self._skip_test:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if not self._skip_test and can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "digest")
            self.run(bin_path, env="conanrun")
