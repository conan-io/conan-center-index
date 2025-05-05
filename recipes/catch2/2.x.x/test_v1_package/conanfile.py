from conans import ConanFile, CMake, tools


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["WITH_MAIN"] = self.options["catch2"].with_main
        cmake.definitions["WITH_BENCHMARK"] = self.options["catch2"].with_main and self.options["catch2"].with_benchmark
        cmake.definitions["WITH_PREFIX"] = self.options["catch2"].with_prefix
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            self.run(f"ctest --output-on-failure -C {self.settings.build_type} -j {tools.cpu_count()}", run_environment=True)
