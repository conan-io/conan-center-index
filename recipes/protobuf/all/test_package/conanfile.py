from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
from conan.tools.env import VirtualRunEnv
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        # A workaround for CI only.
        # https://github.com/conan-io/conan-center-index/pull/23573#issue-2246020949
        # Should normally be added without run=True and with a self.tool_requires("protobuf/...") instead
        # to avoid propagating run=True in the host context in the graph.
        self.requires(self.tested_reference_str, run=True)

    def generate(self):
        venv = VirtualRunEnv(self)
        venv.generate(scope="run")
        # Needed for the CI workaround.
        venv.generate(scope="build")

        tc = CMakeToolchain(self)
        tc.variables["protobuf_LITE"] = self.dependencies[self.tested_reference_str].options.lite
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")

            assert os.path.exists(os.path.join(self.build_folder, "addressbook.pb.cc"))
            assert os.path.exists(os.path.join(self.build_folder, "addressbook.pb.h"))
