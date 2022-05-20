from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class EtcdGrpcConan(ConanFile):
    name = "etcd-grpc"
    description = "DSSL etcd gRPC headers library"
    topics = ("conan", "grpc", "protobuf", "etcd")
    url = "https://github.com/trassir/etcd-grpc"
    homepage = "https://github.com/trassir/etcd-grpc"
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": True,
        "fPIC": True
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    requires = (
        "c-ares/1.15.0.dssl1",
        "grpc/1.44.0",
        "protobuf/3.19.2"
    )

    def configure(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("etcd-grpc should not be built on Windows")

    @property
    def original_version(self):
        if 'dssl' in self.version:
            v = self.version.split('.')
            return '.'.join(v[:-1])
        return self.version

    def source(self):
        tools.get(**self.conan_data["sources"][self.original_version])
        extracted_dir = self.name + "-" + self.original_version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)

        if self.options.shared:
            cmake.definitions["CONAN_BUILD_SHARED_LIBS"] = "ON"

        cmake.configure(build_folder=self._build_subfolder, source_folder=self._source_subfolder)
        return cmake

    def build(self):
        protobuf_module = self.deps_cpp_info["protobuf"]
        protoc_path = os.path.join(protobuf_module.rootpath, protobuf_module.bindirs[0], "protoc")

        grpc_module = self.deps_cpp_info["grpc"]
        grpc_cpp_plugin_path = os.path.join(grpc_module.rootpath, grpc_module.bindirs[0], "grpc_cpp_plugin")

        proto_dir = "%s/proto" % self._source_subfolder
        out_dir = "%s/src" % self._source_subfolder

        self.run("%s -I %s --grpc_out=%s --plugin=protoc-gen-grpc=%s %s/rpc.proto" %
            (protoc_path, proto_dir, out_dir, grpc_cpp_plugin_path, proto_dir),
            run_environment=True)

        self.run("%s -I %s --cpp_out=%s %s/*.proto" %
            (protoc_path, proto_dir, out_dir, proto_dir),
            run_environment=True)

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs.append("etcd-grpc")

