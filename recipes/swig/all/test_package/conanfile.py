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
        # FIXME: SWIG Python with Visual Studio Debug - unable to find Python library at link
        # FIXME: SWIG Python with Visual Studio - unable to load generated module in tests
        return self.settings.compiler != "Visual Studio"

    def build(self):
        if self._can_build:
            with tools.run_environment(self):
                self._cmake.configure()
                self._cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            if self._can_build:
                self._cmake.test(output_on_failure=True)
            self.run("swig -version", run_environment=True)
