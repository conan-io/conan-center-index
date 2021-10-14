import os.path

from conans import ConanFile, CMake, tools


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def test(self):
        res_folder = self.deps_cpp_info["opentelemetry-proto"].res_paths[0]
        include_folder = self.deps_cpp_info["opentelemetry-proto"].include_paths[0]
        assert os.path.isfile(os.path.join(include_folder, "opentelemetry", "proto", "common", "v1", "common.pb.cc"))
        assert os.path.isfile(os.path.join(include_folder, "opentelemetry", "proto", "common", "v1", "common.pb.h"))
        assert os.path.isfile(os.path.join(res_folder, "opentelemetry", "proto", "common", "v1", "common.proto"))
