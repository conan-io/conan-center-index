import os

from conan import ConanFile
from conan.errors import ConanException
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
from conan.tools.microsoft import unix_path


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    @property
    def _executables(self):
        available = []
        # (executable, option name)
        all_execs = [
            ("gl-info", "gl_info"),
            ("al-info", "al_info"),
            ("distancefieldconverter", "distance_field_converter"),
            ("fontconverter", "font_converter"),
            ("imageconverter", "image_converter"),
            ("sceneconverter", "scene_converter"),
        ]
        for executable, opt_name in all_execs:
            if self.dependencies["magnum"].options.get_safe(opt_name, False):
                available.append(executable)
        return available

    def generate(self):
        tc = CMakeToolchain(self)
        for exec in self._executables:
            tc.variables["EXEC_{}".format(exec.replace("-", "_")).upper()] = True
        plugins_root = self.dependencies["magnum"].conf_info.get("user.magnum:plugins_basepath", check_type=str)
        tc.variables["IMPORTER_PLUGINS_FOLDER"] = unix_path(self, os.path.join(plugins_root, "importers"))
        tc.variables["OBJ_FILE"] = unix_path(self, os.path.join(self.source_folder, "triangleMesh.obj"))
        tc.variables["SHARED_PLUGINS"] = self.dependencies["magnum"].options.shared_plugins
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            for exec in self._executables:
                self.run(f"magnum-{exec} --help")

            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")
