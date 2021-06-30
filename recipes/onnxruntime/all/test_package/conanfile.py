from conans import ConanFile, CMake, tools
import os
import os.path


class OnnxRuntimeTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

        if not os.path.exists("squeezenet.onnx"):
            tools.download(
                "https://github.com/microsoft/onnxruntime/raw/"
                "v1.7.1/csharp/testdata/squeezenet.onnx",
                "squeezenet.onnx"
            )

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
