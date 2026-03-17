from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir
from conan.tools.build import check_min_cppstd
import os

required_conan_version = ">=2.1"

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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("grpc/[>=1.54.3 <2]")
        self.requires("protobuf/[*]")
        self.requires("openssl/[>=1.1 <4]")
        self.requires("cpprestsdk/2.10.19", transitive_headers=True, transitive_libs=True)

    def build_requirements(self):
        self.tool_requires("protobuf/<host_version>")
        self.tool_requires("grpc/<host_version>")
    
    def validate(self):
        # etcd-cpp-apiv3 requires at least C++14, but if grpc is >=1.70.0, C++17 is required
        min_cppstd = "17" if self.dependencies["grpc"].ref.version >= "1.70.0" else "14"
        if min_cppstd == "17":
            self.output.warning("etcd-cpp-apiv3 requires C++14, but grpc >=1.70.0 requires C++17. Enforcing C++17.")
        check_min_cppstd(self, min_cppstd)
    
    def export_sources(self):
        export_conandata_patches(self)
    
    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)
        apply_conandata_patches(self)

    def generate(self):

        tc = CMakeToolchain(self)
        tc.cache_variables["gRPC_VERSION"] = str(self.dependencies["grpc"].ref.version)
        tc.cache_variables["OpenSSL_DIR"] = self.dependencies["openssl"].package_folder.replace('\\', '/')
        tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5"
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
