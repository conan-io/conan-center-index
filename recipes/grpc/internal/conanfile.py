from conans import ConanFile, tools
import os

required_conan_version = ">=1.43.0"

class grpcInternalConan(ConanFile):
    name = "grpc_internal"
    description = "Google's RPC (remote procedure call) library and framework."
    topics = ("grpc", "rpc")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/grpc/grpc"
    license = "Apache-2.0"

    @property
    def _source_subfolder(self):
        return "grpc_internal"

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def package_id(self):
        del self.info.options.secure

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        # We are fine with protobuf::protoc coming from conan generated Find/config file
        # TODO: to remove when moving to CMakeToolchain (see https://github.com/conan-io/conan/pull/10186)
        tools.replace_in_file(os.path.join(self._source_subfolder, "cmake", "protobuf.cmake"),
            "find_program(_gRPC_PROTOBUF_PROTOC_EXECUTABLE protoc)",
            "set(_gRPC_PROTOBUF_PROTOC_EXECUTABLE $<TARGET_FILE:protobuf::protoc>)"
        )
        if tools.Version(self.version) >= "1.39.0" and tools.Version(self.version) < "1.42.0":
            # Bug introduced in https://github.com/grpc/grpc/pull/26148
            # Reverted in https://github.com/grpc/grpc/pull/27626
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                    "if(gRPC_INSTALL AND NOT CMAKE_CROSSCOMPILING)",
                    "if(gRPC_INSTALL)")

    def build(self):
        self._patch_sources()

    def package(self):
        self.copy("*.h", dst="include/", src="./", keep_path=True)

    def package_info(self):
        self.cpp_info.includedirs = ["include/", "include/grpc_internal"]
