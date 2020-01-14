from conans import ConanFile, CMake, tools
import os

class Jinja2CppTestPackage(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        compiler = self.settings.get_safe("compiler")
        if compiler == 'Visual Studio':
            runtime = self.settings.get_safe("compiler.runtime")
            cmake.definitions["MSVC_RUNTIME_TYPE"] = '/' + runtime
            
        cmake.configure()
        cmake.build()

    def test(self):
        if tools.os_info.is_windows:
            bin_path = str(self.settings.build_type).lower()
            extension = ".exe"
        elif tools.os_info.is_linux:
            bin_path = "."
            extension = ""
        else:
            bin_path = "."
            extension = ""

        self.run(os.path.join(bin_path, "jinja2cpp-test-package" + extension), run_environment=True)
