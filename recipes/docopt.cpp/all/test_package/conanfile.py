from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["DOCOPTCPP_SHARED"] = self.options["docopt.cpp"].shared
        cmake.configure()
        cmake.build()

    def test(self):
        if tools.cross_building(self.settings):
            if self.settings.os == "Emscripten":
                exe_name = "test_package.js"
            elif tools.os_info.is_windows:
                exe_name = "test_package.exe"
            else:
                exe_name = "test_package"

            assert(os.path.exists(os.path.join("bin", exe_name)))
        else:
            exec_path = os.path.join("bin", "test_package")
            self.run("{} --help".format(exec_path), run_environment=True)
