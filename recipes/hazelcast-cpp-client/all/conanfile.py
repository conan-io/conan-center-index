from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.scm import Version
from conan.tools import files
from conan.tools.build import check_min_cppstd

import os

required_conan_version = ">=1.50.0"

class HazelcastCppClient(ConanFile):
    name = "hazelcast-cpp-client"
    description = "C++ client library for Hazelcast in-memory database."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/hazelcast/hazelcast-cpp-client"
    topics = ("hazelcast", "client", "database", "cache", "in-memory", "distributed", "computing", "ssl")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openssl": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openssl": False
    }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            files.copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires("boost/1.79.0")
        if self.options.with_openssl:
            self.requires("openssl/1.1.1q")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        files.get(self,
            **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.variables["WITH_OPENSSL"] = self.options.with_openssl
        if Version(self.version) <= "4.0.0":
            toolchain.variables["BUILD_STATIC_LIB"] = not self.options.shared
            toolchain.variables["BUILD_SHARED_LIB"] = self.options.shared
        else:
            toolchain.variables["BUILD_SHARED_LIBS"] = self.options.shared
        toolchain.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        files.apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "hazelcast-cpp-client")
        self.cpp_info.set_property("cmake_target_name", "hazelcast-cpp-client::hazelcast-cpp-client")

        self.cpp_info.libs = ["hazelcast-cpp-client"]
        self.cpp_info.defines = ["BOOST_THREAD_VERSION=5"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")
