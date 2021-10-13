import os.path

from conans import ConanFile, CMake, tools


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    requires = "protobuf/3.17.1"

    def test(self):
        if not tools.cross_building(self):
            res_folder = self.deps_cpp_info["opentelemetry-proto"].res_paths[0]
            protofile = os.path.join(res_folder, "opentelemetry", "proto", "common", "v1", "common.proto")
            self.run(f"protoc -I={res_folder} --cpp_out=. {protofile}", run_environment=True)
            assert os.path.isfile(os.path.join("opentelemetry", "proto", "common", "v1", "common.pb.cc"))
            assert os.path.isfile(os.path.join("opentelemetry", "proto", "common", "v1", "common.pb.h"))
