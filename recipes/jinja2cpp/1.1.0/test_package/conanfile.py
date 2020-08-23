from conans import ConanFile, CMake, tools
import os

class Jinja2CppTestPackage(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        compiler = self.settings.get_safe("compiler")
        if compiler == 'Visual Studio':
            runtime = self.settings.get_safe("compiler.runtime")
            cmake.definitions["MSVC_RUNTIME_TYPE"] = '/' + runtime
            
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            ext = ".exe" if self.settings.os == "Windows" else ""
            bin_path = os.path.join("bin", "jinja2cpp-test-package" + ext)
            self.run(bin_path, run_environment=True)
