import os
from conans import ConanFile, CMake, tools


class ProtocConan(ConanFile):
    name = "protoc"
    description = "Protocol Buffers - Google's data interchange format"
    topics = ("conan", "protobuf", "protocol-buffers", "protocol-compiler", "serialization", "rpc", "protocol-compiler")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/protocolbuffers/protobuf"
    license = "BSD-3-Clause"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake", "cmake_find_package"
    short_paths = True
    settings = "os_build", "arch_build", "compiler", "arch"

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
        self.requires.add("protobuf/3.9.1", private=True)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["protobuf_BUILD_TESTS"] = False
        cmake.definitions["protobuf_WITH_ZLIB"] = False
        if self.settings.compiler == "Visual Studio":
            cmake.definitions["protobuf_MSVC_STATIC_RUNTIME"] = "MT" in self.settings.compiler.runtime
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        tools.patch(**self.conan_data["patches"][self.version])
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        cmake_folder = os.path.join(self.package_folder, self._cmake_base_path)
        os.unlink(os.path.join(cmake_folder, "protoc-config-version.cmake"))
        os.unlink(os.path.join(cmake_folder, "protoc-targets-noconfig.cmake"))

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.arch
        self.info.include_build_settings()

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
        self.cpp_info.builddirs = [self._cmake_base_path]
        # INFO: Google Protoc exports a bunch of functions/macro that can be consumed by CMake
        # protoc-config.cmake: provides protobuf_generate function
        # protoc-module.cmake: provides legacy functions, PROTOBUF_GENERATE_CPP PROTOBUF_GENERATE_PYTHON
        # protoc-options.cmake: required by protoc-tools.cmake
        # protoc-targets.cmake: required by protoc-tools.cmake
        self.cpp_info.build_modules = [
            os.path.join(self._cmake_base_path, "protoc-config.cmake"),
            os.path.join(self._cmake_base_path, "protoc-module.cmake"),
            os.path.join(self._cmake_base_path, "protoc-options.cmake"),
            os.path.join(self._cmake_base_path, "protoc-targets.cmake")
        ]

        protoc = "protoc.exe" if self.settings.os_build == "Windows" else "protoc"
        self.env_info.PROTOC_BIN = os.path.normpath(os.path.join(self.package_folder, "bin", protoc))
