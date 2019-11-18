from conans import ConanFile, tools, CMake
import os


class DoctestConan(ConanFile):
    name = "doctest"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/onqtam/doctest"
    description = "C++11/14/17/20 single header testing framework"
    license = "MIT"
    settings = ("os", "compiler", "build_type", "arch")
    generators = "cmake"
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["DOCTEST_WITH_TESTS"] = False
        cmake.configure(build_folder=self._build_subfolder, source_folder=self._source_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        if self._is_mingw:
            # See https://sourceforge.net/p/mingw-w64/bugs/727/
            # can't use destructors in thread_local with mingw
            self.cpp_info.defines.append("DOCTEST_THREAD_LOCAL=")

    def package_id(self):
        self.info.header_only()
