import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
from conan.tools.files import save, load
from conan.tools.apple import is_apple_os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str, run=True)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        introspection_data = self.dependencies["glib"].options.shared and not is_apple_os(self)
        tc = CMakeToolchain(self)
        tc.variables["GLIB_INTROSPECTION_DATA_AVAILABLE"] = introspection_data
        tc.generate()
        save(self, os.path.join(self.build_folder, "gobject_introspection_data"), str(introspection_data))
        save(self, os.path.join(self.build_folder, "gobject_introspection_bin"),
              self.dependencies["gobject-introspection"].cpp_info.bindirs[0])

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            if self.settings.os != "Windows":
                gobject_introspection_bin = load(self, os.path.join(self.build_folder, "gobject_introspection_bin"))
                gobject_introspection_data = load(self, os.path.join(self.build_folder, "gobject_introspection_data")) == "True"
                for tool in ["g-ir-compiler", "g-ir-generate", "g-ir-scanner", "g-ir-annotation-tool"]:
                    if not gobject_introspection_data and tool in ["g-ir-scanner", "g-ir-annotation-tool"]:
                        continue
                    tool_path = os.path.join(gobject_introspection_bin, tool)
                    if os.path.exists(tool_path):
                        self.run(f"{tool_path} --version", env="conanrun")
                    else:
                        raise Exception(f"Tool {tool} not found in {gobject_introspection_bin}")
                tool_path = os.path.join(gobject_introspection_bin, "g-ir-inspect")
                if os.path.exists(tool_path):
                    self.run(f"{tool_path} -h", env="conanrun")

            bin_path = os.path.join(self.cpp.build.bindir, "test_basic")
            self.run(bin_path, env="conanrun")

            bin_path = os.path.join(self.cpp.build.bindir, "test_girepository")
            if os.path.exists(bin_path):
                self.run(bin_path, env="conanrun")
