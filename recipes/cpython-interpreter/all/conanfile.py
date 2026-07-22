import os
from pathlib import Path

from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.errors import ConanInvalidConfiguration
from conan.tools.scm import Version


required_conan_version = ">=2"


class CpythonInterpreterConan(ConanFile):
    name = "cpython-interpreter"
    package_type = "application"
    description = "Portable CPython interpreter from python-build-standalone."
    topics = ("python", "installer", "interpreter")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/astral-sh/python-build-standalone"
    license = "PSF-2.0"
    settings = "os", "arch"

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.arch == "x86" and self.settings.os != "Windows":
            raise ConanInvalidConfiguration("CPython binaries for x86 architecture are only provided for Windows. ")
        if self.settings.os == "Windows" and self.settings.arch == "armv8" and Version(self.version) < "3.11.14":
            raise ConanInvalidConfiguration("CPython prebuilt binaries for Windows arm64 are not provided for this version.")
        if self.settings.arch not in ["x86_64", "armv8", "x86"]:
            raise ConanInvalidConfiguration("CPython binaries are only provided for x86_64, armv8 and x86 (Windows). ")

    def build(self):
        arch = str(self.settings.arch)
        get(self, **self.conan_data["sources"][self.version][str(self.settings.os)][arch],
            destination=self.source_folder)

    def package(self):
        source_folder = os.path.join(self.source_folder, "python")
        copy(self, "*", src=source_folder, dst=self.package_folder)

        if self.settings.os == "Windows":
            license_folder = source_folder
        else:
            major_minor = ".".join(self.version.split(".")[:2])
            license_folder = os.path.join(source_folder, "lib", f"python{major_minor}")
        copy(self, "LICENSE.txt", src=license_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        # this package is intended for using as an application, not as a library
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        if self.settings.os == "Windows":
            self.cpp_info.bindirs = ["."]

        bindir = Path(self.package_folder) / (self.cpp_info.bindirs[0] if self.cpp_info.bindirs else ".")
        python_exe = bindir / "python3"
        if not python_exe.exists():
            python_exe = bindir / "python"
        if not python_exe.exists() and self.settings.os == "Windows":
            python_exe = bindir / "python.exe"

        if python_exe.exists():
            python_root = python_exe.parent.parent if python_exe.parent.name == "bin" else python_exe.parent
            python_root_str = str(python_root)
            self.buildenv_info.define("Python3_ROOT_DIR", python_root_str)
            # Otherwise an active venv/conda would outrank Python3_ROOT_DIR.
            self.buildenv_info.define("Python3_FIND_VIRTUALENV", "STANDARD")
