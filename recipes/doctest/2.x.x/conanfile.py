import os
from conan import ConanFile
from conan.tools import files


class DoctestConan(ConanFile):
    name = "doctest"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/onqtam/doctest"
    description = "C++11/14/17/20 single header testing framework"
    topics = ("doctest", "header-only", "unit-test", "tdd")
    settings = "os", "compiler"
    license = "MIT"

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        files.copy(
            self,
            pattern="LICENSE.txt",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        files.copy(
            self,
            pattern="*doctest.h",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "include"),
        )

        cmake_script_dirs = {
            "src": os.path.join(self.source_folder, "scripts/cmake"),
            "dst": os.path.join(self.package_folder, "lib/cmake"),
        }

        files.copy(self, pattern="doctest.cmake", **cmake_script_dirs)
        files.copy(self, pattern="doctestAddTests.cmake", **cmake_script_dirs)

    def package_info(self):
        if self._is_mingw:
            # See https://sourceforge.net/p/mingw-w64/bugs/727/
            # can't use destructors in thread_local with mingw
            self.cpp_info.defines.append("DOCTEST_THREAD_LOCAL=")

        self.cpp_info.builddirs.append("lib/cmake")
        self.cpp_info.set_property(
            "cmake_build_modules", [os.path.join("lib", "cmake", "doctest.cmake")]
        )

    def package_id(self):
        self.info.clear()
