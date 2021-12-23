import functools

from conans import ConanFile, CMake, tools
import os


class ProtobufcConan(ConanFile):
    name = "protobuf-c"
    license = "https://github.com/protobuf-c/protobuf-c/blob/master/LICENSE"
    homepage = "https://github.com/protobuf-c/protobuf-c"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"
    description = "conan package for protobuf-c"
    topics = ("cpp11", "cpp14", "cpp17", "protocol-buffers", "protocol-compiler", "serialization", "rpc", "protocol-compiler", "c")
    exports_sources = ["patches/**"]
    _source_subfolder = "source_subfolder"
    requires = [
        "protobuf/3.19.2",
    ]
    options = {
        "proto3": [True, False],
        "protoc": [True, False],
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "proto3": True,
        "protoc": True,
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        tools.check_min_cppstd(self, "11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(f"{self.name}-{self.version}", self._source_subfolder)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_PROTO3"] = self.options.proto3
        cmake.definitions["BUILD_PROTOC"] = self.options.protoc
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        cmake.definitions["BUILD_TESTS"] = False
        cmake.definitions["HAS_SYSTEM_PROTOBUF"] = False
        cmake.configure(source_folder=f"{self._source_subfolder}/build-cmake")
        return cmake

    def build(self):
        if "patches" in self.conan_data and self.version in self.conan_data["patches"]:
            for patch in self.conan_data["patches"][self.version]:
                tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses", keep_path=False)

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "ProtobufC"
        self.cpp_info.filenames["cmake_find_package_multi"] = "protobuf-c"
        self.cpp_info.names["cmake_find_package"] = "protobuf-c"
        self.cpp_info.names["cmake_find_package_multi"] = "protobuf-c"
        self.cpp_info.libs = ["protobuf-c"]
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.bindirs = ["bin"]

        bin_dir = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_dir}")
        self.env_info.PATH.append(bin_dir)
