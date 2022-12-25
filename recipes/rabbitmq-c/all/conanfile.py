from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=1.46.0"


class RabbitmqcConan(ConanFile):
    name = "rabbitmq-c"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/alanxz/rabbitmq-c"
    description = "This is a C-language AMQP client library for use with v2.0+ of the RabbitMQ broker."
    topics = ("rabbitmq-c", "rabbitmq", "message queue")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "ssl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "ssl": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def requirements(self):
        if self.options.ssl:
            self.requires("openssl/1.1.1q")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["BUILD_STATIC_LIBS"] = not self.options.shared
        tc.variables["BUILD_TESTS"] = False
        tc.variables["BUILD_TOOLS"] = False
        tc.variables["BUILD_TOOLS_DOCS"] = False
        tc.variables["ENABLE_SSL_SUPPORT"] = self.options.ssl
        tc.variables["BUILD_API_DOCS"] = False
        tc.variables["RUN_SYSTEM_TESTS"] = False
        tc.generate()

        if self.options.ssl:
            deps = CMakeDeps(self)
            deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE-MIT", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        rabbitmq_target = "rabbitmq" if self.options.shared else "rabbitmq-static"
        self.cpp_info.set_property("cmake_file_name", "rabbitmq-c")
        self.cpp_info.set_property("cmake_target_name", f"rabbitmq::{rabbitmq_target}")
        self.cpp_info.set_property("pkg_config_name", "librabbitmq")

        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        if self.settings.os == "Windows":
            self.cpp_info.components["rabbitmq"].libs = [
                "rabbitmq.4" if self.options.shared else "librabbitmq.4"
            ]
            self.cpp_info.components["rabbitmq"].system_libs.extend(["crypt32", "ws2_32"])
        else:
            self.cpp_info.components["rabbitmq"].libs = ["rabbitmq"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["rabbitmq"].system_libs.append("pthread")
        if not self.options.shared:
            self.cpp_info.components["rabbitmq"].defines.append("AMQP_STATIC")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "rabbitmq-c"
        self.cpp_info.filenames["cmake_find_package_multi"] = "rabbitmq-c"
        self.cpp_info.names["cmake_find_package"] = "rabbitmq"
        self.cpp_info.names["cmake_find_package_multi"] = "rabbitmq"
        self.cpp_info.names["pkg_config"] = "librabbitmq"
        self.cpp_info.components["rabbitmq"].names["cmake_find_package"] = rabbitmq_target
        self.cpp_info.components["rabbitmq"].names["cmake_find_package_multi"] = rabbitmq_target
        self.cpp_info.components["rabbitmq"].set_property("cmake_target_name", f"rabbitmq::{rabbitmq_target}")
        self.cpp_info.components["rabbitmq"].set_property("pkg_config_name", "librabbitmq")
        if self.options.ssl:
            self.cpp_info.components["rabbitmq"].requires.append("openssl::openssl")
