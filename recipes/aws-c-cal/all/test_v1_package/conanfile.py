from conans import ConanFile, CMake, tools
from conan.tools.apple import is_apple_os
import os
import io


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    @property
    def _needs_openssl(self):
        return not (self.settings.os == "Windows" or is_apple_os(self))

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            stream = io.StringIO()
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, stream, run_environment=True)
            self.output.info(stream.getvalue())
            if self._needs_openssl:
                assert "found static libcrypto" in stream.getvalue()
