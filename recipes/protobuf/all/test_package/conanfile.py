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
        # note `run=True` so that the runenv can find protoc
        self.requires(self.tested_reference_str, run=True)

    def generate(self):
        venv = VirtualRunEnv(self)
        venv.generate(scope="run")
        # Needed for the CI workaround.
        venv.generate(scope="build")

        tc = CMakeToolchain(self)
        tc.variables["protobuf_LITE"] = self.dependencies[self.tested_reference_str].options.lite
        # Additional logic to override the make program on MacOS if /usr/bin/make is found by CMake
        # which otherwise prevents the propagation of DYLD_LIBRARY_PATH as set by the VirtualBuildEnv
        tc.cache_variables["CMAKE_PROJECT_test_package_INCLUDE"] = os.path.join(self.source_folder, "macos_make_override.cmake")
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")

            # Invoke protoc in the same way CMake would
            self.run(f"protoc --proto_path=\"{self.source_folder}\" --cpp_out=\"{self.build_folder}\" \"{self.source_folder}\"/addressbook.proto", env="conanrun")
            assert os.path.exists(os.path.join(self.build_folder, "addressbook.pb.cc"))
            assert os.path.exists(os.path.join(self.build_folder, "addressbook.pb.h"))
