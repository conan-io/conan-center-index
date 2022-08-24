from conans import ConanFile, tools, CMake
import os


class DoctestConan(ConanFile):
    name = "doctest"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/onqtam/doctest"
    description = "C++11/14/17/20 single header testing framework"
    topics = ("doctest", "header-only", "unit-test", "tdd")
    settings = "os", "compiler"
    license = "MIT"
    _source_subfolder = "source_subfolder"

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        pass

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*doctest.h", dst="include", src=self._source_subfolder)

        cmake_script_dirs = {
            "src": os.path.join(self._source_subfolder, "scripts/cmake"),
            "dst": "lib/cmake"
        }

        self.copy(pattern="doctest.cmake", **cmake_script_dirs)
        self.copy(pattern="doctestAddTests.cmake", **cmake_script_dirs)

    def package_info(self):
        if self._is_mingw:
            # See https://sourceforge.net/p/mingw-w64/bugs/727/
            # can't use destructors in thread_local with mingw
            self.cpp_info.defines.append("DOCTEST_THREAD_LOCAL=")

        self.cpp_info.builddirs.append("lib/cmake")
        self.cpp_info.build_modules.append("lib/cmake/doctest.cmake")

    def package_id(self):
        self.info.header_only()
