import os
from conans import ConanFile, CMake, tools

class TestPackage(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def _importer_plugins_folder(self):
        magnum_plugin_libdir = "magnum-d" if self.settings.build_type == "Debug" else "magnum"
        return os.path.join(self.deps_cpp_info["magnum-plugins"].rootpath, "lib", magnum_plugin_libdir, "importers")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["IMPORTER_PLUGINS_FOLDER"] = self._importer_plugins_folder().replace("\\", "/")
        cmake.definitions["CONAN_STL_FILE"] = os.path.join(os.path.dirname(__file__), "conan.stl").replace("\\", "/")
        cmake.configure()
        cmake.build()

    def test(self):
        # STL file taken from https://www.thingiverse.com/thing:2798332
        stl_path = os.path.join(os.path.dirname(__file__), "conan.stl")

        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
