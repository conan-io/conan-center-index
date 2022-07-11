import os
from conan import ConanFile
from conan.tools.files import get, copy


class GRPCProto(ConanFile):
    name = "grpc-proto"
    description = "gRPC-defined protobufs for peripheral services such as health checking, load balancing, etc"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/grpc/grpc-proto"
    topics = "google", "protos", "api"
    settings = "os", "arch", "compiler", "build_type"

    def source(self):
        get(self, **self.conan_data["sources"][str(self.version)], destination=self.source_folder, strip_root=True)

    def package_id(self):
        self.info.header_only()

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, pattern="*.proto", src=self.source_folder, dst=os.path.join(self.package_folder, "res"))

    def package_info(self):
        self.cpp_info.libs = []
        self.cpp_info.includedirs = []
