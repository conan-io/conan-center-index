from conans import ConanFile, CMake, tools
import os

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_paths", "cmake_find_package"

    def _cxxabi_compiler_opt(self):
      if self.settings.compiler.libcxx == "libstdc++":
        return "-D_GLIBCXX_USE_CXX11_ABI=0"

      return ""


    def build(self):
        cmake = CMake(self)
        defs = {
          "CMAKE_CXX_FLAGS": self._cxxabi_compiler_opt()
        }
        cmake.configure(defs=defs)
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            self.run(os.path.join(os.getcwd(), "test_package"), run_environment=True)
