from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        deps = CMakeDeps(self)
        # deps.check_components_exist = True
        deps.generate()

        tc = CMakeToolchain(self)
        tc.variables["CMAKE_VERBOSE_MAKEFILE"] = True
        # HW plugins
        tc.variables["ENABLE_INTEL_CPU"] = self.dependencies[self.tested_reference_str].options.enable_cpu
        tc.variables["ENABLE_INTEL_GPU"] = self.dependencies[self.tested_reference_str].options.get_safe("enable_gpu", False)
        # SW plugins
        tc.variables["ENABLE_AUTO"] = self.dependencies[self.tested_reference_str].options.enable_auto
        tc.variables["ENABLE_HETERO"] = self.dependencies[self.tested_reference_str].options.enable_hetero
        tc.variables["ENABLE_AUTO_BATCH"] = self.dependencies[self.tested_reference_str].options.enable_auto_batch
        # Frontends
        tc.variables["ENABLE_IR_FRONTEND"] = self.dependencies[self.tested_reference_str].options.enable_ir_frontend
        tc.variables["ENABLE_ONNX_FRONTEND"] = self.dependencies[self.tested_reference_str].options.enable_onnx_frontend
        tc.variables["ENABLE_TF_FRONTEND"] = self.dependencies[self.tested_reference_str].options.enable_tf_frontend
        tc.variables["ENABLE_TF_LITE_FRONTEND"] = self.dependencies[self.tested_reference_str].options.enable_tf_lite_frontend
        tc.variables["ENABLE_PADDLE_FRONTEND"] = self.dependencies[self.tested_reference_str].options.enable_paddle_frontend
        tc.variables["ENABLE_PYTORCH_FRONTEND"] = self.dependencies[self.tested_reference_str].options.enable_pytorch_frontend
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path_c = os.path.join(self.cpp.build.bindirs[0], "test_package_c")
            self.run(bin_path_c, env="conanrun")

            bin_path_cpp = os.path.join(self.cpp.build.bindirs[0], "test_package_cpp")
            self.run(bin_path_cpp, env="conanrun")
