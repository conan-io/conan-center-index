import os
from conans import ConanFile, tools, CMake


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
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "encryption": "libsodium",
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

    def requirements(self):
        if self.options.encryption == "libsodium":
            self.requires.add("libsodium/1.0.18")

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
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
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

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "ZeroMQ"
        self.cpp_info.names["cmake_find_package_multi"] = "ZeroMQ"
        if self.settings.compiler == "Visual Studio":
            version = "_".join(self.version.split("."))
            if self.settings.build_type == "Debug":
                runtime = "-gd" if self.options.shared else "-sgd"
            else:
                runtime = "" if self.options.shared else "-s"
            library_name = "libzmq-mt%s-%s" % (runtime, version)
            if not os.path.isfile(os.path.join(self.package_folder, "lib", library_name)):
                # unfortunately Visual Studio and Ninja generators produce different file names
                toolset = {"12": "v120",
                           "14": "v140",
                           "15": "v141",
                           "16": "v142"}.get(str(self.settings.compiler.version))
                library_name = "libzmq-%s-mt%s-%s" % (toolset, runtime, version)
            self.cpp_info.libs = [library_name]
        else:
            self.cpp_info.libs = ["zmq"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["iphlpapi", "ws2_32"]
        elif self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread", "rt", "m"]
        if not self.options.shared:
            self.cpp_info.defines.append("ZMQ_STATIC")
