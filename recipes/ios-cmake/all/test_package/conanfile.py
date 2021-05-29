
import os
from conans import ConanFile


class TestPackageConan(ConanFile):
    settings = "os"

    def test(self):
        if self.settings.os == "iOS":
            cmake_prog = os.environ.get("CONAN_CMAKE_PROGRAM")
            toolchain = os.environ.get("CONAN_CMAKE_TOOLCHAIN_FILE")
            assert (os.path.basename(cmake_prog) == "cmake-wrapper")
            assert (os.path.basename(toolchain) == "ios.toolchain.cmake")
