from conans import ConanFile, CMake, tools
from conans.errors import ConanException
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    @property
    def _executables(self):
        available = []
        #            (executable, option name)
        all_execs = (("gl-info", "gl_info"), 
                     ("al-info", "al_info"), 
                     ("distancefieldconverter", "distance_field_converter"), 
                     ("fontconverter", "font_converter"), 
                     ("imageconverter", "image_converter"), 
                     ("sceneconverter", "scene_converter"))
        for executable, opt_name in all_execs:
            try:
                if getattr(self.options["magnum"], opt_name):
                    available.append(executable)
            except ConanException:
                pass
        return available

    def _importer_plugins_folder(self):
        magnum_plugin_libdir = "magnum-d" if self.settings.build_type == "Debug" else "magnum"
        pkg_dir = "bin" if self.settings.os == "Windows" else "lib"
        return os.path.join(self.deps_cpp_info["magnum"].rootpath, pkg_dir, magnum_plugin_libdir, "importers")

    def build(self):
        cmake = CMake(self)
        for exec in self._executables:
            cmake.definitions["EXEC_{}".format(exec.replace("-", "_")).upper()] = True
        cmake.definitions["IMPORTER_PLUGINS_FOLDER"] = self._importer_plugins_folder().replace("\\", "/")
        cmake.definitions["OBJ_FILE"] = os.path.join(os.path.dirname(__file__), "triangleMesh.obj").replace("\\", "/")
        cmake.definitions["SHARED_PLUGINS"] = self.options["magnum"].shared_plugins
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            for exec in self._executables:
                self.run("magnum-{} --help".format(exec), run_environment=True)

            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
