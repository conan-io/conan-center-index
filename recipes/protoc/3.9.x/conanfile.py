import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class ProtocConan(ConanFile):
    name = "protoc"
    description = "Protocol Buffers - Google's data interchange format"
    topics = ("conan", "protobuf", "protocol-buffers", "protocol-compiler", "serialization", "rpc", "protocol-compiler")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/protocolbuffers/protobuf"
    license = "BSD-3-Clause"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"
    settings = "os_build", "arch_build", "compiler"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _cmake_base_path(self):
        return os.path.join("lib", "cmake", "protoc")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = "protobuf-" + self.version
        os.rename(extracted_folder, self._source_subfolder)

    def requirements(self):
        self.requires("protobuf/3.9.1", private=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["CMAKE_INSTALL_CMAKEDIR"] = self._cmake_base_path.replace("\\", "/")
        self._cmake.definitions["protobuf_BUILD_TESTS"] = False
        self._cmake.definitions["protobuf_WITH_ZLIB"] = False
        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["protobuf_MSVC_STATIC_RUNTIME"] = "MT" in self.settings.compiler.runtime
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        tools.patch(**self.conan_data["patches"][self.version])
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_id(self):
        del self.info.settings.compiler
        self.info.include_build_settings()

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        self.cpp_info.build_modules = [
            os.path.join(self._cmake_base_path, "protoc-module.cmake"),
            os.path.join(self._cmake_base_path, "protoc-options.cmake"),
            os.path.join(self._cmake_base_path, "protoc-generate.cmake"),
        ]
        self.cpp_info.builddirs = [self._cmake_base_path]

        protoc = "protoc.exe" if self.settings.os_build == "Windows" else "protoc"
        self.env_info.PROTOC_BIN = os.path.normpath(os.path.join(self.package_folder, "bin", protoc))
