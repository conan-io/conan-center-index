import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain, CMakeDeps
from conan.tools.env import VirtualRunEnv
from conan.tools.files import save, load


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str, run=True)

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
        VirtualRunEnv(self).generate()
        tc = CMakeToolchain(self)
        for exec in self._executables:
            tc.variables["EXEC_{}".format(exec.replace("-", "_")).upper()] = True
        plugins_root = self.dependencies["magnum"].conf_info.get("user.magnum:plugins_basepath", check_type=str)
        tc.variables["IMPORTER_PLUGINS_FOLDER"] = os.path.join(plugins_root, "importers").replace("\\", "/")
        tc.variables["OBJ_FILE"] = os.path.join(self.source_folder, "triangleMesh.obj").replace("\\", "/")
        tc.variables["SHARED_PLUGINS"] = self.dependencies["magnum"].options.shared_plugins
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

        save(self, os.path.join(self.build_folder, "executables"), "\n".join(self._executables))

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            executables = load(self, os.path.join(self.build_folder, "executables")).splitlines()
            for exec in executables:
                self.run(f"magnum-{exec} --help", env="conanrun")

            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")
