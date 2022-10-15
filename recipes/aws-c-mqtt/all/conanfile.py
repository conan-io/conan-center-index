from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc_static_runtime, is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rm, rmdir, replace_in_file
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv

import os

required_conan_version = ">=1.47.0"


class AwsCMQTT(ConanFile):
    name = "aws-c-mqtt"
    description = "C99 implementation of the MQTT 3.1.1 specification."
    license = "Apache-2.0",
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/awslabs/aws-c-mqtt"
    topics = ("aws", "amazon", "cloud", "mqtt")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def requirements(self):
        self.requires("aws-c-common/0.8.2")
        self.requires("aws-c-cal/0.5.13")
        self.requires("aws-c-io/0.13.4")
        self.requires("aws-c-http/0.6.22")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "aws-c-mqtt"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "aws-c-mqtt")
        self.cpp_info.set_property("cmake_target_name", "AWS::aws-c-mqtt")

        self.cpp_info.filenames["cmake_find_package"] = "aws-c-mqtt"
        self.cpp_info.filenames["cmake_find_package_multi"] = "aws-c-mqtt"
        self.cpp_info.names["cmake_find_package"] = "AWS"
        self.cpp_info.names["cmake_find_package_multi"] = "AWS"
        self.cpp_info.components["aws-c-mqtt-lib"].names["cmake_find_package"] = "aws-c-mqtt"
        self.cpp_info.components["aws-c-mqtt-lib"].names["cmake_find_package_multi"] = "aws-c-mqtt"
        self.cpp_info.components["aws-c-mqtt-lib"].set_property("cmake_target_name", "AWS::aws-c-mqtt")

        self.cpp_info.components["aws-c-mqtt-lib"].libs = ["aws-c-mqtt"]
        self.cpp_info.components["aws-c-mqtt-lib"].requires = [
            "aws-c-common::aws-c-common-lib",
            "aws-c-cal::aws-c-cal-lib",
            "aws-c-io::aws-c-io-lib",
            "aws-c-http::aws-c-http-lib"
        ]
