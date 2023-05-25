from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain
from conan.tools.env import VirtualBuildEnv
from conan.tools.layout import basic_layout
import os

class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    _res_folder = ""

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()
        tc = VirtualBuildEnv(self)
        tc.generate(scope="build")

        self._res_folder = self.dependencies["opentelemetry-proto"].conf_info.get("user.opentelemetry-proto:proto_root")

    def test(self):
        # TODO: to remove in conan v2
        if self._res_folder == "":
            self._res_folder = self.deps_user_info["opentelemetry-proto"].proto_root

        assert os.path.isfile(os.path.join(self._res_folder, "opentelemetry", "proto", "common", "v1", "common.proto"))
