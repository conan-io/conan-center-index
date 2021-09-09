from conans import CMake, ConanFile, tools


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package"
    test_type = "build_requires", "requires"  # add "requires", while not necessary, to ensure building swig when using 2 profiles

    @property
    def _can_build(self):
        # FIXME: SWIG Python with Visual Studio Debug - unable to find Python library at link
        # FIXME: SWIG Python with Visual Studio - unable to load generated module in tests
        return self.settings.compiler != "Visual Studio"

    def build(self):
        self.run("swig -swiglib", run_environment=True)
        if self._can_build:
            cmake = CMake(self)
            cmake.verbose = True
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self):
            cmake = CMake(self)
            cmake.test(output_on_failure=True)
            self.run("swig -version", run_environment=True)
