import os

from conans import ConanFile, CMake, tools


class AwsSdkCppTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def configure(self):
        if self.settings.compiler == "Visual Studio":
            if self.settings.build_type == "Release":
                self.settings.compiler.runtime = "MT"
            else:
                self.settings.compiler.runtime = "MTd"
        self.options["aws-sdk-cpp"].build_s3 = True
        self.options["aws-sdk-cpp"].build_logs = True
        self.options["aws-sdk-cpp"].build_monitoring = True
        self.options["aws-sdk-cpp"].build_transfer = True

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "example")
            self.run(bin_path, run_environment=True)
