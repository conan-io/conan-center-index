import os
from conans import ConanFile, tools, CMake


class CzmqConan(ConanFile):
    name = "czmq"
    homepage = "https://github.com/zeromq/czmq"
    description = "ZeroMQ is a community of projects focused on decentralized messaging and computing"
    topics = ("conan", "zmq", "libzmq", "message-queue", "asynchronous")
    url = "https://github.com/conan-io/conan-center-index"
    license = "MPL-2.0"
    exports_sources = "CMakeLists.txt", "patches/**"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libcurl": [True, False],
        "with_lz4": [True, False],
        "with_libuuid": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libcurl": True,
        "with_lz4": True,
        "with_libuuid": True,
    }
    generators = "cmake"

    _cmake = None
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            # libuuid is not available on Windows
            del self.options.with_uuid

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("openssl/1.1.1d")  # zdigest depends on openssl
        self.requires.add("zeromq/4.3.2")
        if self.options.with_libcurl:
            self.requires("libcurl/7.67.0")
        if self.options.with_lz4:
            self.requires.add("lz4/1.9.2")
        if self.settings.os != "Windows":
            if self.options.with_libuuid:
                self.requires.add("libuuid/1.0.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("czmq-{}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["CZMQ_BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["CZMQ_BUILD_STATIC"] = not self.options.shared
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "CMake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.libs = ["czmq" if self.options.shared else "libczmq"]
            self.cpp_info.system_libs.append("rpcrt4")
        else:
            self.cpp_info.libs = ["czmq"]
            if self.settings.os == "Linux":
                self.cpp_info.system_libs.extend(["pthread", "m"])
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("rpcrt4")
        if not self.options.shared:
            self.cpp_info.defines.append("CZMQ_STATIC")
