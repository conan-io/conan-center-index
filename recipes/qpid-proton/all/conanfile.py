from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, export_conandata_patches, get, rmdir
from conan.tools.microsoft import is_msvc

import os

required_conan_version = ">=2.1.0"

class QpidProtonConan(ConanFile):
    version = "0.40.0"
    name = "qpid-proton"
    description = "Qpid Proton is a high-performance, lightweight messaging library."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://qpid.apache.org/proton/"
    topics = ("conan", "qpid", "proton", "messaging", "message", "queue", "topic", "mq", "amqp")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "tools": [True, False],
        "tls": [True, False],
        "with_opentelemetry": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "tools": False,
        "tls": True,
        "with_opentelemetry": True,
    }

    @property
    def _min_cppstd(self):
        return "14"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("openssl/3.3.2")
        self.requires("cyrus-sasl/2.1.28")
        if self.options.with_opentelemetry:
            self.requires("opentelemetry-cpp/1.14.2")
        if self.settings.os == "Macos":
            self.requires("libuv/1.49.2")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, "14")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")
        self.tool_requires("cpython/[>=3.9]")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=1.7 <3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], filename=f"{self.version}.tar.gz", strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)

        tc.variables["BUILD_PYTHON"] = False
        tc.variables["BUILD_RUBY"] = False
        tc.variables["BUILD_GO"] = False

        tc.variables["ENABLE_WARNING_ERROR"] = False
        tc.variables["ENABLE_UNDEFINED_ERROR"] = False
        tc.variables["ENABLE_LINKTIME_OPTIMIZATION"] = False
        tc.variables["ENABLE_HIDE_UNEXPORTED_SYMBOLS"] = False
        tc.variables["ENABLE_FUZZ_TESTING"] = False
        tc.variables["ENABLE_BENCHMARKS"] = False

        tc.variables["BUILD_STATIC_LIBS"] = not bool(self.options["shared"])

        tc.variables["BUILD_TESTING"] = False
        tc.variables["BUILD_TOOLS"] = bool(self.options["tools"])
        tc.variables["BUILD_EXAMPLES"] = False
        if self.settings.os == "Macos":
            tc.variables["BUILD_TLS"] = False
        else:
            tc.variables["BUILD_TLS"] = bool(self.options["tls"])

        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("libuv", "cmake_file_name", "Libuv")
        deps.set_property("libuv", "cmake_target_name", "Libuv::Libuv")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="NOTICE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "QpidProton")

        suffix = "-static" if is_msvc(self) and not self.options.shared else ""

        self.cpp_info.components["proton"].set_property("cmake_target_name", "Proton::proton")
        self.cpp_info.components["proton"].libs = [f"qpid-proton{suffix}"]
        self.cpp_info.components["proton"].requires = ["openssl::ssl", "cyrus-sasl::cyrus-sasl"]

        self.cpp_info.components["core"].set_property("cmake_target_name", "Proton::core")
        self.cpp_info.components["core"].libs = [f"qpid-proton-core{suffix}"]
        self.cpp_info.components["core"].requires = ["openssl::ssl", "cyrus-sasl::cyrus-sasl"]

        self.cpp_info.components["proactor"].set_property("cmake_target_name", "Proton::proactor")
        self.cpp_info.components["proactor"].libs = [f"qpid-proton-proactor{suffix}"]
        self.cpp_info.components["proactor"].requires = ["core"]

        self.cpp_info.components["cpp"].set_property("cmake_target_name", "Proton::cpp")
        self.cpp_info.components["cpp"].libs = [f"qpid-proton-cpp{suffix}"]
        self.cpp_info.components["cpp"].requires = ["core", "proactor"]

        if self.options["tls"] and self.settings.os != "Macos":
            self.cpp_info.components["tls"].set_property("cmake_target_name", "Proton::tls")
            self.cpp_info.components["tls"].libs = [f"qpid-proton-tls{suffix}"]

        if self.settings.os == "Macos":
            self.cpp_info.components["core"].requires.append("libuv::libuv")

        if self.options["with_opentelemetry"]:
            self.cpp_info.components["cpp"].requires.append("opentelemetry-cpp::opentelemetry-cpp")
