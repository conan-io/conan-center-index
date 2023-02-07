from conan import ConanFile
from conan.tools.scm import Version
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
from conan.tools.files import save, load
import os
import json


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    @property
    def _skip_test_filename(self):
        return os.path.join(self.build_folder, "skip_test.json")

    def _generate_skip_test_file(self):
        # Attempting to use @rpath without CMAKE_SHARED_LIBRARY_RUNTIME_C_FLAG being
        # set. This could be because you are using a Mac OS X version less than 10.5
        # or because CMake's platform configuration is corrupt.
        # FIXME: Remove once CMake on macOS/M1 CI runners is upgraded.
        # Actually the workaround should be to add cmake/3.22.0 to build requires,
        # but for the specific case of openssl it fails because it is also a requirement of cmake.
        # see https://github.com/conan-io/conan/pull/9839
        dict_test = {"skip_test": self.settings.os == "Macos" and \
                                  self.settings.arch == "armv8" and \
                                  bool(self.dependencies[self.tested_reference_str].options.shared)}
        save(self, self._skip_test_filename, json.dumps(dict_test))

    @property
    def _skip_test(self):
        return bool(json.loads(load(self, self._skip_test_filename)).get("skip_test"))

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        if self.settings.os == "Android":
            tc.cache_variables["CONAN_LIBCXX"] = ""
        openssl = self.dependencies[self.tested_reference_str]
        openssl_version = Version(openssl.ref.version)
        if openssl_version.major == "1" and openssl_version.minor == "1":
            tc.cache_variables["OPENSSL_WITH_ZLIB"] = False
        else:
            tc.cache_variables["OPENSSL_WITH_ZLIB"] = not openssl.options.no_zlib
        tc.generate()
        self._generate_skip_test_file()


    def build(self):
        if not self._skip_test:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if not self._skip_test and can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
