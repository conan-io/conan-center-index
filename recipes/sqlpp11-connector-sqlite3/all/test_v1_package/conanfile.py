from conans import ConanFile, CMake
from conan.tools.build import cross_building
import os
import sqlite3

class TestPackageV1Conan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)

            # test that the database is encrypted when sqlcipher is used
            con = sqlite3.connect("test.db")
            cursor = con.cursor()
            try:
                cursor.execute("select * from tab_sample")
            except sqlite3.DatabaseError:
                assert self.options["sqlpp11-connector-sqlite3"].with_sqlcipher
                self.output.info("database is encrypted with sqlcipher")
                return
            assert not self.options["sqlpp11-connector-sqlite3"].with_sqlcipher
            self.output.info("database is not encrypted")
