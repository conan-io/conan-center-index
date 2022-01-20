import os
from conans import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps
from conan.tools.cross_building import cross_building as tools_cross_building
from conan.tools.layout import cmake_layout
from conans.errors import ConanException


required_conan_version = ">=1.43.0"


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "VirtualRunEnv"

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

    def generate(self):
        tc = CMakeToolchain(self)
        for exec in self._executables:
            tc.variables["EXEC_{}".format(exec.replace("-", "_")).upper()] = True
        tc.variables["IMPORTER_PLUGINS_FOLDER"] = os.path.join(self.deps_user_info["magnum"].plugins_basepath, "importers").replace("\\", "/")
        tc.variables["OBJ_FILE"] =  os.path.join("..", "..", "test_package", "triangleMesh.obj").replace("\\", "/")
        tc.variables["SHARED_PLUGINS"] = self.options["magnum"].shared_plugins
        tc.generate()

    def layout(self):
        cmake_layout(self)
        self.folders.source = os.path.join("..", "test_package")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools_cross_building(self):
            for exec in self._executables:
                self.run("magnum-{} --help".format(exec), env="conanrun")

            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
