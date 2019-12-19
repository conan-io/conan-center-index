import os
from conans import ConanFile, tools, CMake


class ZeroMQConan(ConanFile):
    name = "zeromq"
    homepage = "https://github.com/zeromq/libzmq"
    description = "ZeroMQ is a community of projects focused on decentralized messaging and computing"
    topics = ("conan", "zmq", "libzmq", "message-queue", "asynchronous")
    url = "https://github.com/conan-io/conan-center-index"
    license = "LGPL-3.0"
    exports_sources = ["CMakeLists.txt", "zeromq_extra.cmake"]
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
    generators = "cmake"

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        if self.options.encryption == "libsodium":
            self.requires.add("libsodium/1.0.18")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("libzmq-{}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["ENABLE_CURVE"] = self.options.encryption is not None
        cmake.definitions["WITH_LIBSODIUM"] = self.options.encryption == "libsodium"
        cmake.definitions["ZMQ_BUILD_TESTS"] = False
        cmake.definitions["WITH_PERF_TOOL"] = False
        cmake.definitions["BUILD_SHARED"] = self.options.shared
        cmake.definitions["BUILD_STATIC"] = not self.options.shared
        cmake.definitions["ENABLE_CPACK"] = False
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING*", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "CMake"))

        self.copy("zeromq_extra.cmake", dst=os.path.join(self.package_folder, "lib", "cmake", "zeromq"))

    def package_info(self):
        self.cpp_info.name = "ZeroMQ"
        self.cpp_info.names["pkg_config"] = "libzmq"
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
            self.cpp_info.system_libs = ["iphlpapi", "ws2_32"]
        else:
            self.cpp_info.libs = ["zmq"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["pthread", "rt", "m"])
        if not self.options.shared:
            self.cpp_info.defines.append("ZMQ_STATIC")
        self.cpp_info.builddirs = [os.path.join("lib", "cmake", "zeromq")]
        self.cpp_info.build_modules = [os.path.join("lib", "cmake", "zeromq", "zeromq_extra.cmake")]
