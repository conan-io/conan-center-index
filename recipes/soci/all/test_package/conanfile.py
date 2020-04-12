from conans.model.conan_file import ConanFile, tools
from conans import CMake
import os
import sys


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake"

    def _with_backend(self, backend_opt):
      return backend_opt == True or backend_opt == 'None' and self.options['soci'].with_all_backends

    def build(self):
        cmake = CMake(self)

        if self.settings.compiler.cppstd != 'None':
            cmake.definitions["CMAKE_CXX_STANDARD"] = self.settings.compiler.cppstd

        if self._with_backend(self.options['soci'].with_backend_sqlite3):
            cmake.definitions["WITH_SQLITE3"] = "TRUE"

        if self._with_backend(self.options['soci'].with_backend_empty):
            cmake.definitions["WITH_EMPTY"] = "TRUE"

        if self._with_backend(self.options['soci'].with_backend_mysql):
            cmake.definitions["WITH_MYSQL"] = "TRUE"

        if self._with_backend(self.options['soci'].with_backend_odbc):
            cmake.definitions["WITH_ODBC"] = "TRUE"

        if self._with_backend(self.options['soci'].with_backend_postgresql):
            cmake.definitions["WITH_POSTGRESQL"] = "TRUE"

        cmake.verbose = True
        cmake.configure()
        cmake.build()


    def test(self):
        if tools.cross_building(self.settings):
            return
        bt = self.settings.build_type
        self.run('ctest --output-on-error -C %s' % bt, run_environment=True)
