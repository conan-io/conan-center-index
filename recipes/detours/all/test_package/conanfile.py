from conan import ConanFile, tools
from conans import CMake
import io
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.verbose = 1
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self, skip_x64_x86=True):
            bin_path = os.path.join("bin", "test_package")
            buffer = io.StringIO()
            self.run(f"{bin_path} \"{os.path.join(self.build_folder, 'bin')}\"", run_environment=True, output=buffer)
            print(buffer.getvalue())
            assert "I found your message! It was 'A secret text'! I am 1337! :^)" in buffer.getvalue()
