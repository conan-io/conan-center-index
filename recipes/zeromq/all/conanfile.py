import os
from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration


class ZeroMQConan(ConanFile):
    name = "zeromq"
    homepage = "https://github.com/zeromq/libzmq"
    description = "ZeroMQ is a community of projects focused on decentralized messaging and computing"
    topics = ("conan", "zmq", "libzmq", "message-queue", "asynchronous")
    url = "https://github.com/conan-io/conan-center-index"
    license = "LGPL-3.0"
    exports_sources = "CMakeLists.txt", "patches/**"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "encryption": [None, "libsodium", "tweetnacl"],
        "with_norm": [True, False],
        "poller": [None, "kqueue", "epoll", "devpoll", "pollset", "poll", "select"]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "encryption": "libsodium",
        "with_norm": False,
        "poller": None
    }
    generators = "cmake", "cmake_find_package"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.os == "Windows" and self.options.with_norm:
            raise ConanInvalidConfiguration(
                "Norm and ZeroMQ are not compatible on Windows yet")

    def requirements(self):
        if self.options.encryption == "libsodium":
            self.requires("libsodium/1.0.18")
        if self.options.with_norm:
            self.requires("norm/1.5.9")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("libzmq-{}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_CURVE"] = bool(self.options.encryption)
        self._cmake.definitions["WITH_LIBSODIUM"] = self.options.encryption == "libsodium"
        self._cmake.definitions["ZMQ_BUILD_TESTS"] = False
        self._cmake.definitions["WITH_PERF_TOOL"] = False
        self._cmake.definitions["BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["ENABLE_CPACK"] = False
        self._cmake.definitions["WITH_DOCS"] = False
        self._cmake.definitions["WITH_DOC"] = False
        self._cmake.definitions["WITH_NORM"] = self.options.with_norm
        if self.options.poller:
            self._cmake.definitions["POLLER"] = self.options.poller
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        os.unlink(os.path.join(self._source_subfolder, "builds", "cmake", "Modules", "FindSodium.cmake"))

        if self.options.encryption == "libsodium":
            os.rename("Findlibsodium.cmake", "FindSodium.cmake")
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                                       "SODIUM_FOUND",
                                       "libsodium_FOUND")
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                                       "SODIUM_INCLUDE_DIRS",
                                       "libsodium_INCLUDE_DIRS")
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                                       "SODIUM_LIBRARIES",
                                       "libsodium_LIBRARIES")

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING*", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "CMake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        # TODO: CMake imported target shouldn't be namespaced
        self.cpp_info.names["cmake_find_package"] = "ZeroMQ"
        self.cpp_info.names["cmake_find_package_multi"] = "ZeroMQ"
        self.cpp_info.names["pkg_config"] = "libzmq"
        libzmq_target = "libzmq" if self.options.shared else "libzmq-static"
        self.cpp_info.components["libzmq"].names["cmake_find_package"] = libzmq_target
        self.cpp_info.components["libzmq"].names["cmake_find_package_multi"] = libzmq_target
        self.cpp_info.components["libzmq"].libs = tools.collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.components["libzmq"].system_libs = ["iphlpapi", "ws2_32"]
        elif self.settings.os == "Linux":
            self.cpp_info.components["libzmq"].system_libs = ["pthread", "rt", "m"]
        if not self.options.shared:
            self.cpp_info.components["libzmq"].defines.append("ZMQ_STATIC")
        if self.options.encryption == "libsodium":
            self.cpp_info.components["libzmq"].requires.append("libsodium::libsodium")
        if self.options.with_norm:
            self.cpp_info.components["libzmq"].requires.append("norm::norm")
