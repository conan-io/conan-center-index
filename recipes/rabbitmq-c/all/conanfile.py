import os

from conans import CMake, ConanFile, tools

required_conan_version = ">=1.28.0"

class RabbitmqcConan(ConanFile):
    name = "rabbitmq-c"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/alanxz/rabbitmq-c"
    description = "This is a C-language AMQP client library for use with v2.0+ of the RabbitMQ broker."

    topics = ("rabbitmq-c", "rabbitmq", "message queue")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False], "ssl": [True, False]}
    default_options = {"shared": False, "fPIC": True, "ssl": False}
    generators = "cmake", "cmake_find_package"
    exports_sources = ["CMakeLists.txt"]
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.ssl:
            self.requires("openssl/1.1.1l")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "{}-{}".format(self.name, self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake is None:
            self._cmake = CMake(self)
            self._cmake.definitions["BUILD_EXAMPLES"] = False
            self._cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
            self._cmake.definitions["BUILD_STATIC_LIBS"] = not self.options.shared
            self._cmake.definitions["BUILD_TESTS"] = False
            self._cmake.definitions["BUILD_TOOLS"] = False
            self._cmake.definitions["BUILD_TOOLS_DOCS"] = False
            self._cmake.definitions["ENABLE_SSL_SUPPORT"] = self.options.ssl
            self._cmake.definitions["BUILD_API_DOCS"] = False
            self._cmake.definitions["RUN_SYSTEM_TESTS"] = False
            self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE-MIT", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "rabbitmq-c"
        self.cpp_info.filenames["cmake_find_package_multi"] = "rabbitmq-c"
        self.cpp_info.names["cmake_find_package"] = "rabbitmq"
        self.cpp_info.names["cmake_find_package_multi"] = "rabbitmq"
        self.cpp_info.names["pkg_config"] = "librabbitmq"
        rabbitmq_target = "rabbitmq" if self.options.shared else "rabbitmq-static"
        self.cpp_info.components["rabbitmq"].names["cmake_find_package"] = rabbitmq_target
        self.cpp_info.components["rabbitmq"].names["cmake_find_package_multi"] = rabbitmq_target
        if self.settings.os == "Windows":
            self.cpp_info.components["rabbitmq"].libs = [
                "rabbitmq.4" if self.options.shared else "librabbitmq.4"
            ]
            self.cpp_info.components["rabbitmq"].system_libs.extend(["crypt32", "ws2_32"])
        else:
            self.cpp_info.components["rabbitmq"].libs = ["rabbitmq"]
            if self.settings.os == "Linux":
                self.cpp_info.components["rabbitmq"].system_libs.append("pthread")
        if not self.options.shared:
            self.cpp_info.components["rabbitmq"].defines.append("AMQP_STATIC")
        if self.options.ssl:
            self.cpp_info.components["rabbitmq"].requires.append("openssl::openssl")
