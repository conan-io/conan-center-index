from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout
import os
import io


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    @property
    def _needs_openssl(self):
        return not (self.settings.os == "Windows" or is_apple_os(self))

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            stream = io.StringIO()
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, stream, env="conanrun")
            self.output.info(stream.getvalue())
            if self._needs_openssl:
                assert "found static libcrypto" in stream.getvalue()
