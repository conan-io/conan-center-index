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
        tc.variables.update({
            cmake_key: self.dependencies[self.tested_reference_str].options.get_safe(opt_key, False)
            for (opt_key, cmake_key) in [
                ("enable_cpu", "ENABLE_INTEL_CPU"),
                ("enable_gpu", "ENABLE_INTEL_GPU"),
                ("enable_auto", "ENABLE_AUTO"),
                ("enable_hetero", "ENABLE_HETERO"),
                ("enable_auto_batch", "ENABLE_AUTO_BATCH"),
                ("enable_ir_frontend", "ENABLE_IR_FRONTEND"),
                ("enable_onnx_frontend", "ENABLE_ONNX_FRONTEND"),
                ("enable_tf_frontend", "ENABLE_TF_FRONTEND"),
                ("enable_tf_lite_frontend", "ENABLE_TF_LITE_FRONTEND"),
                ("enable_paddle_frontend", "ENABLE_PADDLE_FRONTEND"),
                ("enable_pytorch_frontend", "ENABLE_PYTORCH_FRONTEND"),
            ]
        })
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path_cpp = os.path.join(self.cpp.build.bindirs[0], "test_package_cpp")
            self.run(bin_path_cpp, env="conanrun")

            bin_path_c = os.path.join(self.cpp.build.bindirs[0], "test_package_c")
            self.run(bin_path_c, env="conanrun")
