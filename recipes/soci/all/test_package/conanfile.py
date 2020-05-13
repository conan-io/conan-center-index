from conans.model.conan_file import ConanFile, tools
from conans import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)

        cmake.definitions["WITH_EMPTY"] = self.options["soci"].with_backend_empty
        cmake.definitions["WITH_SQLITE3"] = self.options["soci"].with_backend_sqlite3
        cmake.definitions["WITH_MYSQL"] = self.options["soci"].with_backend_mysql
        cmake.definitions["WITH_ODBC"] = self.options["soci"].with_backend_odbc
        cmake.definitions["WITH_POSTGRESQL"] = self.options["soci"].with_backend_postgresql

        cmake.configure()
        cmake.verbose = True
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            if self.options["soci"].with_backend_empty:
                self.run(os.path.join("bin", "test_empty"), run_environment=True)
            if self.options["soci"].with_backend_sqlite3:
                self.run(os.path.join("bin", "test_sqlite3"), run_environment=True)
            if self.options["soci"].with_backend_mysql:
                self.run(os.path.join("bin", "test_mysql"), run_environment=True)
            if self.options["soci"].with_backend_odbc:
                self.run(os.path.join("bin", "test_odbc"), run_environment=True)
            if self.options["soci"].with_backend_postgresql:
                self.run(os.path.join("bin", "test_postgresql"), run_environment=True)
