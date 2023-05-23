from conans import ConanFile, CMake, tools
from conans.errors import ConanException


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def _approvaltests_option(self, name, default):
        try:
            return getattr(self.options["approvaltests.cpp"], name, default)
        except (AttributeError, ConanException):
            return default

    def build(self):
        cmake = CMake(self)
        cmake.definitions["WITH_BOOSTTEST"] = self._approvaltests_option("with_boosttest", False)
        cmake.definitions["WITH_CATCH"] = self.options["approvaltests.cpp"].with_catch2
        cmake.definitions["WITH_GTEST"] = self.options["approvaltests.cpp"].with_gtest
        cmake.definitions["WITH_DOCTEST"] = self.options["approvaltests.cpp"].with_doctest
        cmake.definitions["WITH_CPPUTEST"] = self._approvaltests_option("with_cpputest", False)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            self.run(f"ctest --output-on-failure -C {self.settings.build_type}", run_environment=True)
