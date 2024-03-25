from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
import os

from conan.tools.files import save, load


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        if self.dependencies["magnum-extras"].options.ui:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

        # Workaround for Conan v1
        save(self, os.path.join(self.generators_folder, "extras_path"), self.dependencies["magnum-extras"].package_folder)
        save(self, os.path.join(self.generators_folder, "options_player"), str(self.dependencies["magnum-extras"].options.player))
        save(self, os.path.join(self.generators_folder, "options_ui_gallery"), str(self.dependencies["magnum-extras"].options.ui_gallery))
        save(self, os.path.join(self.generators_folder, "options_ui"), str(self.dependencies["magnum-extras"].options.ui))

    def test(self):
        if can_run(self):
            extras_path = load(self, os.path.join(self.generators_folder, "extras_path"))
            options_player = load(self, os.path.join(self.generators_folder, "options_player")) == "True"
            options_ui_gallery = load(self, os.path.join(self.generators_folder, "options_ui_gallery")) == "True"
            options_ui = load(self, os.path.join(self.generators_folder, "options_ui")) == "True"
            executable_ext = ".exe" if self.settings.os == "Windows" else ""
            if options_player:
                assert os.path.exists(os.path.join(extras_path, "bin", f"magnum-player{executable_ext}"))
                # (Cannot run in headless mode) self.run("magnum-player --help")
            if options_ui_gallery:
                assert os.path.exists(os.path.join(extras_path, "bin", f"magnum-ui-gallery{executable_ext}"))
                # (Cannot run in headless mode) self.run("magnum-ui-gallery --help")
            if options_ui:
                bin_path = os.path.join(self.cpp.build.bindir, "test_package")
                self.run(bin_path, env="conanrun")
