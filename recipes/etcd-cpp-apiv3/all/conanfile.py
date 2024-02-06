from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import export_conandata_patches, get, copy, rmdir
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
import os

required_conan_version = ">=1.53.0"

class EtcdCppApiv3Conan(ConanFile):
    name = "etcd-cpp-apiv3"
    package_type = "library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/etcd-cpp-apiv3/etcd-cpp-apiv3"
    license = "BSD-3-Clause"
    description = ("C++ library for etcd's v3 client APIs, i.e., ETCDCTL_API=3.")
    topics = ("etcd", "api", )

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _is_legacy_one_profile(self):
        return not hasattr(self, "settings_build")

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

    def build_requirements(self):
        if not self._is_legacy_one_profile:
            self.tool_requires("protobuf/<host_version>")
            self.tool_requires("grpc/<host_version>")

    def requirements(self):
        self.requires("protobuf/3.21.12")
        self.requires("openssl/[>=1.1 <4]")
        self.requires("grpc/1.54.3")
        self.requires("cpprestsdk/2.10.19", transitive_headers=True, transitive_libs=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if self._is_legacy_one_profile:
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = CMakeToolchain(self)
        tc.variables["gRPC_VERSION"] = self.dependencies["grpc"].ref.version
        tc.variables["ETCD_CMAKE_CXX_STANDARD"] = self.settings.compiler.get_safe("cppstd", "11")
        tc.variables["OpenSSL_DIR"] = self.dependencies["openssl"].package_folder
        tc.generate()

        cmake_deps = CMakeDeps(self)
        cmake_deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["etcd-cpp-api"]
