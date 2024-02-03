from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import export_conandata_patches, get, load, copy
import os

required_conan_version = ">=1.53.0"

class EtcdCppApiv3Conan(ConanFile):
    name = "etcd-cpp-apiv3"
    package_type = "library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/etcd-cpp-apiv3/etcd-cpp-apiv3"
    license = "etcd-cpp-apiv3"
    description = ("C++ library for etcd's v3 client APIs, i.e., ETCDCTL_API=3.")
    topics = ("etcd-cpp-apiv3", "api")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

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
        self.requires("protobuf/3.21.12")
        self.requires("openssl/[>=1.1 <4]")
        self.requires("grpc/1.54.3")
        self.requires("cpprestsdk/2.10.19") # add condition about BUILD_ETCD_CORE_ONLY

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["gRPC_VERSION"] = self.dependencies["grpc"].ref.version
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

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "etcd-cpp-apiv3")
        self.cpp_info.set_property("cmake_target_name", "etcd-cpp-apiv3::etcd-cpp-apiv3")
        self.cpp_info.set_property("pkg_config_name", "etcd-cpp-apiv3")

        self.cpp_info.names["cmake_find_package"] = "etcd-cpp-apiv3"
        self.cpp_info.names["cmake_find_package_multi"] = "etcd-cpp-apiv3"
