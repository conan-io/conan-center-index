from conans import ConanFile, CMake, tools
import os


class ProtocConanFile(ConanFile):
    _base_name = "protobuf"
    name = "protoc"
    version = "3.9.1"
    description = "Protocol Buffers - Google's data interchange format"
    topics = ("conan", "protobuf", "protocol-buffers", "protocol-compiler", "serialization", "rpc", "protocol-compiler")
    url = "https://github.com/bincrafters/conan-protobuf"
    homepage = "https://github.com/protocolbuffers/protobuf"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "BSD-3-Clause"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt", "protoc.patch"]
    generators = "cmake"
    short_paths = True
    keep_imports = True

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    settings = "os_build", "arch_build", "compiler", "arch"

    def build_requirements(self):
        self.build_requires("protobuf/{}".format(self.version))

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["protobuf_BUILD_TESTS"] = False
        cmake.definitions["protobuf_WITH_ZLIB"] = False
        if self.settings.compiler == "Visual Studio":
            cmake.definitions["protobuf_MSVC_STATIC_RUNTIME"] = "MT" in self.settings.compiler.runtime
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        tools.patch(base_path=self._source_subfolder, patch_file="protoc.patch")
        cmake = self._configure_cmake()
        cmake.build()

    def source(self):
        sha256 = "98e615d592d237f94db8bf033fba78cd404d979b0b70351a9e5aaff725398357"
        tools.get("{0}/archive/v{1}.tar.gz".format(self.homepage, self.version), sha256=sha256)
        extracted_dir = self._base_name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def imports(self):
        # when built with protobuf:shared=True, protoc will require its libraries to run
        # so we copy those from protobuf package
        if tools.os_info.is_linux:
            # `ldd` shows dependencies named like libprotoc.so.3.9.1.0
            self.protobuf_dylib_mask = "*.so.*"
        else:
            assert False, "protoc package was not checked on your system"
        self.copy(self.protobuf_dylib_mask, dst="lib", src="lib", root_package="protobuf")

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(self.protobuf_dylib_mask, dst="lib", src="lib")

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("env_info.PATH: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        protoc = "protoc.exe" if self.settings.os_build == "Windows" else "protoc"
        self.env_info.PROTOC_BIN = os.path.normpath(os.path.join(self.package_folder, "bin", protoc))
