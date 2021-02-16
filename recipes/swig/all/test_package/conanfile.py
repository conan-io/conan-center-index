from conans import CMake, ConanFile, tools


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    __cmake = None

    @property
    def _cmake(self):
        if not self.__cmake:
            self.__cmake = CMake(self)
        return self.__cmake

    @property
    def _can_build(self):
        # FIXEM: Fix SWIG Python build with Visual Studio
        # Have a problem linking final module with Visual Studio. CMake finds
        # correct Python library, but linker tries to use _d variant and fails.
        if self.settings.compiler == "Visual Studio" and self.settings.build_type == "Debug":
            return False
        return True

    def build(self):
        if self._can_build:
            self._cmake.configure()
            self._cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            if self._can_build:
                self._cmake.test(output_on_failure=True)
            self.run("swig -version")
