import os
from conan import ConanFile, tools
from conans import CMake

class TestPackage(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["IMPORTER_PLUGINS_FOLDER"] = os.path.join(self.deps_user_info["magnum-plugins"].plugins_basepath, "importers").replace("\\", "/")
        # STL file taken from https://www.thingiverse.com/thing:2798332
        cmake.definitions["CONAN_STL_FILE"] = os.path.join(self.source_folder, "conan.stl").replace("\\", "/")
        cmake.definitions["SHARED_PLUGINS"] = self.options["magnum-plugins"].shared_plugins
        cmake.definitions["TARGET_EMSCRIPTEN"] = bool(self.settings.os == "Emscripten")
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)

        if self.settings.os == "Emscripten":
            bin_path = os.path.join("bin", "test_package.js")
            self.run("node {}".format(bin_path), run_environment=True)
