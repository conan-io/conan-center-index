import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, replace_in_file

required_conan_version = ">=1.53.0"


class awskvspicConan(ConanFile):
    name = "aws-kvs-pic"
    description = "Platform Independent Code for Amazon Kinesis Video Streams"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/awslabs/amazon-kinesis-video-streams-pic"
    topics = ("aws", "kvs", "kinesis", "video", "stream")

    package_type = "library"
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
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"] and self.options.shared:
            raise ConanInvalidConfiguration("This library can only be built shared on Linux")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_DEPENDENCIES"] = False
        tc.generate()

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), " -fPIC", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.components["kvspic"].libs = ["kvspic"]
        self.cpp_info.components["kvspic"].set_property("pkg_config_name", "libkvspic")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["kvspic"].system_libs = ["dl", "rt", "pthread"]

        self.cpp_info.components["kvspicClient"].libs = ["kvspicClient"]
        self.cpp_info.components["kvspicClient"].set_property("pkg_config_name", "libkvspicClient")

        self.cpp_info.components["kvspicState"].libs = ["kvspicState"]
        self.cpp_info.components["kvspicState"].set_property("pkg_config_name", "libkvspicState")

        self.cpp_info.components["kvspicUtils"].libs = ["kvspicUtils"]
        self.cpp_info.components["kvspicUtils"].set_property("pkg_config_name", "libkvspicUtils")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["kvspicUtils"].system_libs = ["dl", "rt", "pthread"]
