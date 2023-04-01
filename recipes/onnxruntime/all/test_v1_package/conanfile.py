from conans import ConanFile, CMake, tools
import os


class ONNXRuntimeTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            onnx_path = os.path.join(self.source_folder, os.pardir, "test_package", "matmul_cast_inputs.onnx")
            self.run(f"{bin_path} {onnx_path}", run_environment=True)
