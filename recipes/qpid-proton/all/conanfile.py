from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, export_conandata_patches, apply_conandata_patches
from conan.tools.microsoft import is_msvc

import os

required_conan_version = ">=2.4.0"


class QpidProtonConan(ConanFile):
    name = "qpid-proton"
    description = "Qpid Proton is a high-performance, lightweight messaging library."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://qpid.apache.org/proton/"
    topics = ("conan", "qpid", "proton", "messaging", "message", "queue", "topic", "mq", "amqp")
    package_type = "shared-library"
    languages = ["C", "C++"]
    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if not is_msvc(self):
            self.requires("openssl/[>=1.1 <4]")
        if self.settings.os == "Macos":
            self.requires("libuv/[>=1 <2]")
        self.requires("jsoncpp/[>=1.9.6 <2]")

    def validate(self):
        check_min_cppstd(self, 14)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16]")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=1.7 <3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], filename=f"{self.version}.tar.gz", strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_TESTING"] = False
        tc.cache_variables["BUILD_TOOLS"] = False
        tc.cache_variables["BUILD_EXAMPLES"] = False
        tc.cache_variables["BUILD_BINDINGS"] = "cpp"
        # Do not mess up the LIB_INSTALL_DIR
        tc.cache_variables["LIB_SUFFIX"] = ""

        tc.cache_variables["ENABLE_JSONCPP"] = True
        tc.cache_variables["ENABLE_OPENTELEMETRYCPP"] = False
        tc.cache_variables["ENABLE_WARNING_ERROR"] = False
        tc.cache_variables["ENABLE_UNDEFINED_ERROR"] = False
        tc.cache_variables["ENABLE_LINKTIME_OPTIMIZATION"] = False
        tc.cache_variables["ENABLE_HIDE_UNEXPORTED_SYMBOLS"] = False
        tc.cache_variables["ENABLE_FUZZ_TESTING"] = False
        tc.cache_variables["ENABLE_BENCHMARKS"] = False

        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_CyrusSASL"] = True
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_Doxygen"] = True
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_SWIG"] = True
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_opentelemetry-cpp"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("libuv", "cmake_file_name", "Libuv")
        deps.set_property("libuv", "cmake_target_name", "Libuv::Libuv")
        deps.set_property("jsoncpp", "cmake_file_name", "JsonCpp")
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

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ProtonCpp")
        # C core components
        self.cpp_info.components["proton"].set_property("cmake_target_name", "Proton::proton")
        self.cpp_info.components["proton"].set_property("pkg_config_name", "libqpid-proton")
        self.cpp_info.components["proton"].libs = [f"qpid-proton"]
        if is_msvc(self):
            self.cpp_info.components["proton"].system_libs.extend(["secur32", "crypt32", "Ws2_32"])
        else:
            self.cpp_info.components["proton"].requires = ["openssl::ssl"]

        self.cpp_info.components["core"].set_property("cmake_target_name", "Proton::core")
        self.cpp_info.components["core"].set_property("pkg_config_name", "libqpid-proton-core")
        self.cpp_info.components["core"].libs = [f"qpid-proton-core"]
        if is_msvc(self):
            self.cpp_info.components["core"].system_libs.extend(["secur32", "crypt32", "Ws2_32"])
        else:
            self.cpp_info.components["core"].requires = ["openssl::ssl"]
        if self.settings.os == "Macos":
            self.cpp_info.components["core"].requires.append("libuv::libuv")

        self.cpp_info.components["proactor"].set_property("cmake_target_name", "Proton::proactor")
        self.cpp_info.components["proactor"].set_property("pkg_config_name", "libqpid-proton-proactor")
        self.cpp_info.components["proactor"].libs = [f"qpid-proton-proactor"]
        self.cpp_info.components["proactor"].requires = ["core"]
        if is_msvc(self):
            self.cpp_info.components["proactor"].system_libs.extend(["secur32", "crypt32", "Ws2_32"])
        else:
            self.cpp_info.components["proactor"].requires = ["openssl::ssl"]
        # C++ binding
        self.cpp_info.components["cpp"].set_property("cmake_target_name", "Proton::cpp")
        self.cpp_info.components["cpp"].set_property("pkg_config_name", "libqpid-proton-cpp")
        self.cpp_info.components["cpp"].libs = [f"qpid-proton-cpp"]
        self.cpp_info.components["cpp"].requires = ["core", "proactor", "jsoncpp::jsoncpp"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["cpp"].system_libs.append("pthread")
