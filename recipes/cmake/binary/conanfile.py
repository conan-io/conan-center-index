import os

from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration


required_conan_version = ">=1.51.0"

class CMakeConan(ConanFile):
    name = "cmake"
    package_type = "application"
    description = "CMake, the cross-platform, open-source build system."
    topics = ("build", "installer")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Kitware/CMake"
    license = "BSD-3-Clause"
    settings = "os", "arch"

    def validate(self):
        if self.settings.arch == "x86":
            raise ConanInvalidConfiguration("No 32-bit binaries are currently provided for CMake")
        if self.settings.os == "Windows" and self.settings.arch == "armv8" and Version(self.version) < "3.24":
            raise ConanInvalidConfiguration("CMake only supports ARM64 binaries on Windows starting from 3.24")

    def build(self):
        get(self, **self.conan_data["sources"][self.version][str(self.settings.os)][str(self.settings.arch)],
            destination=self.source_folder, strip_root=True)

    def package(self):
        copy(self, "*", src=self.build_folder, dst=self.package_folder)

        if self.settings.os == "Macos":
            docs_folder = os.path.join(self.build_folder, "Cmake.app", "Contents", "doc")
        else:
            docs_folder = os.path.join(self.build_folder, "doc")

        copy(self, "Copyright.txt", src=docs_folder, dst=os.path.join(self.package_folder, "licenses"), keep_path=False)

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        if self.settings.os == "Macos":
            bindir = os.path.join(self.package_folder, "CMake.app", "Contents", "bin")
            self.cpp_info.bindirs = [bindir]
        else:
            bindir = os.path.join(self.package_folder, "bin")
        
        # Needed for compatibility with v1.x - Remove when 2.0 becomes the default
        self.output.info(f"Appending PATH environment variable: {bindir}")
        self.env_info.PATH.append(bindir)
