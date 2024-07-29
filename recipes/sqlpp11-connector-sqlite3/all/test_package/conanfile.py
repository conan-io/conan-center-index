import os
import sqlite3

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
from conan.tools.files import save, load


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        with_sqlcipher = bool(self.dependencies["sqlpp11-connector-sqlite3"].options.with_sqlcipher)
        save(self, os.path.join(self.build_folder, "with_sqlcipher"), repr(with_sqlcipher))

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            with_sqlcipher = load(self, os.path.join(self.build_folder, "with_sqlcipher")) == "True"
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")
            # test that the database is encrypted when sqlcipher is used
            con = sqlite3.connect("test.db")
            cursor = con.cursor()
            try:
                cursor.execute("select * from tab_sample")
            except sqlite3.DatabaseError:
                assert with_sqlcipher
                self.output.info("database is encrypted with sqlcipher")
                return
            assert not with_sqlcipher
            self.output.info("database is not encrypted")
