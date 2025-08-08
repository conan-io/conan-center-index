import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.build import can_run
from conan.tools.env import Environment, VirtualRunEnv
from conan.tools.files import copy


class openfxTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps"

    def requirements(self):
        self.requires(self.tested_reference_str)

    @property
    def _plugin_folder(self):
        return os.path.join(self.build_folder, self.cpp.build.bindir, "Plugins")

    def _create_bundle_for_plugin(self, plugin_name, destination_folder):
        archdir = None
        if self.settings.os == "Windows":
            if self.settings.arch == "x86_64":
                archdir = "Win64"
            elif self.settings.arch == "x86":
                archdir = "Win32"
        elif self.settings.os == "Macos":
            archdir = "MacOS"
        elif self.settings.os == "Linux":
            if self.settings.arch == "x86_64":
                archdir = "Linux-x86-64"
            else:
                archdir = f"Linux-{self.settings.arch}"

        bundle_contents_path = os.path.join(destination_folder, f"{plugin_name}.bundle","Contents")
        copy(self, plugin_name, src=os.path.join(self.build_folder, self.cpp.build.bindir),
            dst=os.path.join(bundle_contents_path, archdir))
        copy(self, "Info.plist", src=os.path.join(self.source_folder, "..", "Support", "Plugins", "Invert"),
            dst=bundle_contents_path)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

        # Create an environment script that defines the OFX_PLUGIN_PATH
        env1 = Environment()
        env1.define_path("OFX_PLUGIN_PATH", self._plugin_folder)
        env1.vars(self, scope="run").save_script("ofx_plugin_dir")

        vre = VirtualRunEnv(self)
        vre.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()

        # Build test_package binary that uses the HostSupport code and an invert_plugin.ofx that uses the
        # plugin Support code.
        cmake.build()

        # Create a bundle in the plugin folder for the plugin we just built.
        self._create_bundle_for_plugin("invert_plugin.ofx", self._plugin_folder)

    def layout(self):
        cmake_layout(self)

    def test(self):
        # Skip execution -- we only care that the plugin builds
        pass
