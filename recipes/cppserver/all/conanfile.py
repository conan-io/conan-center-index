from conan import ConanFile
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, collect_libs
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"

class CppServer(ConanFile):
    name = "cppserver"
    description = "Ultra fast and low latency asynchronous socket server and" \
        " client C++ library with support TCP, SSL, UDP, HTTP, HTTPS, WebSocket" \
        " protocols and 10K connections problem solution."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/chronoxor/CppServer"
    topics = ("network", "socket", "asynchronous", "low-latency")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
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
        self.requires("asio/1.27.0", transitive_headers=True)
        self.requires("openssl/[>=1.1 <4]", transitive_headers=True, transitive_libs=True)
        self.requires("cppcommon/1.0.3.0", transitive_headers=True)

    def validate(self):
        check_min_cppstd(self, 17)

    def build_requirements(self):
        if Version(self.version) >= "1.0.2.0":
            self.tool_requires("cmake/[>=3.20 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.variables["CPPSERVER_MODULE"] = False
        tc.generate()

        dpes = CMakeDeps(self)
        dpes.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))
        copy(self, pattern="*.inl", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32", "crypt32", "mswsock"]
