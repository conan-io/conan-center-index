from conans import ConanFile, CMake, tools
import os
import textwrap


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            with open("test.ini", "w") as fn:
                fn.write(textwrap.dedent("""\
                    [protocol]
                    version = 1337
                    [user]
                    name = conan-center-index
                    email = info@conan.io
                    """))
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
