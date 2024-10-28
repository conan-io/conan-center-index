from conans import CMake, ConanFile, tools
from conans.errors import ConanException


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def _poco_option(self, name, default):
        try:
            return getattr(self.options["poco"], name, default)
        except (AttributeError, ConanException):
            return default

    def build(self):
        cmake = CMake(self)
        cmake.definitions["TEST_CRYPTO"] = self.options["poco"].enable_crypto
        cmake.definitions["TEST_UTIL"] = self.options["poco"].enable_util
        cmake.definitions["TEST_NET"] = False
        cmake.definitions["TEST_NETSSL"] = False
        cmake.definitions["TEST_SQLITE"] = self.options["poco"].enable_data_sqlite
        cmake.definitions["TEST_ENCODINGS"] = self._poco_option("enable_encodings", False)
        cmake.definitions["TEST_JWT"] = self._poco_option("enable_jwt", False)
        cmake.definitions["TEST_PROMETHEUS"] = self._poco_option("enable_prometheus", False)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            self.run(f"ctest --output-on-failure -C {self.settings.build_type} -j {tools.cpu_count()}", run_environment=True)
