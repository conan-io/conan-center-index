from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class DoctestConan(ConanFile):
    name = "doctest"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/onqtam/doctest"
    description = "C++11/14/17/20 single header testing framework"
    topics = ("header-only", "unit-test", "tdd")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    license = "MIT"

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*doctest.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))
        for cmake_file in ("doctest.cmake", "doctestAddTests.cmake"):
            copy(self, cmake_file, src=os.path.join(self.source_folder, "scripts", "cmake"),
                                   dst=os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "doctest")
        self.cpp_info.set_property("cmake_target_name", "doctest::doctest")
        # Upstream config file populates CMAKE_MODULE_PATH so that doctest.cmake & doctestAddTests.cmake
        # are discoverable, therefore their folder is appended to builddirs.
        # But this config file doesn't include these module files directly,
        # thus they are not defined as cmake_build_modules
        self.cpp_info.builddirs.append(os.path.join("lib", "cmake"))
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        if self._is_mingw:
            # See https://sourceforge.net/p/mingw-w64/bugs/727/
            # can't use destructors in thread_local with mingw
            self.cpp_info.defines.append("DOCTEST_THREAD_LOCAL=")
