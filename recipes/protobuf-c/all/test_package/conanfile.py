from conan import ConanFile
from conan.tools.build import can_run, cross_building
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import load, save
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps"
    test_type = "explicit"

    @property
    def _probuf_c_option_file(self):
        return os.path.join(self.build_folder, "protobuf-c_with_protoc")

    def _has_protoc_support(self):
        return load(self, self._probuf_c_option_file) == "True"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build_requirements(self):
        if cross_building(self) and hasattr(self, "settings_build"):
            self.tool_requires(self.tested_reference_str)

    def generate(self):
        VirtualRunEnv(self).generate()
        if cross_building(self) and hasattr(self, "settings_build"):
            VirtualBuildEnv(self).generate()
        else:
            VirtualRunEnv(self).generate(scope="build")
        save(self, self._probuf_c_option_file, str(self.dependencies[self.tested_reference_str].options.with_protoc))
        tc = CMakeToolchain(self)
        tc.variables["WITH_PROTOC"] = self.dependencies[self.tested_reference_str].options.with_protoc
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            if self._has_protoc_support():
                self.run("protoc-gen-c --version", env="conanbuild")
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
