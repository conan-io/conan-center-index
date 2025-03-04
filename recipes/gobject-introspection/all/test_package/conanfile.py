import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps"

    def requirements(self):
        self.requires(self.tested_reference_str, headers=True, libs=True, run=can_run(self))

    def layout(self):
        cmake_layout(self)

    def build_requirements(self):
        if not can_run(self):
            self.tool_requires("gobject-introspection/<host_version>")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["GLIB_INTROSPECTION_DATA_AVAILABLE"] = self.dependencies["gobject-introspection"].options.build_introspection_data
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            if self.settings.os != "Windows":
                gobject_introspection_bin = self.dependencies["gobject-introspection"].cpp_info.bindir
                gobject_introspection_data = self.dependencies["gobject-introspection"].options.build_introspection_data
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
