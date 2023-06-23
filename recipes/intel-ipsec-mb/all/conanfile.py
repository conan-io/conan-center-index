from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc
from conan.tools.files import get, copy, rmdir
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"


class PackageConan(ConanFile):
    name = "intel-ipsec-mb"
    description = "Intel(R) Multi-Buffer Crypto for IPSec"
    license = "BSD-3-Clause"
    homepage = "https://github.com/intel/intel-ipsec-mb"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("intel", "IPSec", "IPSec_MB")
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
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration(f"The architecture '{self.settings.arch}' is not supported.")
        if self.settings.os not in ("FreeBSD", "Linux", "Windows"):
            raise ConanInvalidConfiguration(f"The O.S. '{self.settings.os}' is not supported.")
        if self.settings.os == "Windows" and not is_msvc(self):
            raise ConanInvalidConfiguration(f"{self.ref} only supports msvc on Windows.")

    def build_requirements(self):
        self.tool_requires("nasm/2.15.05")
        self.tool_requires("cmake/[>3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # INFO: intel-ipsec-mb project forces shared by default.
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target="IPSec_MB")

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "intel-ipsec-mb.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "lib"), keep_path=False)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "man"))

    def package_info(self):
        self.cpp_info.libs = ["IPSec_MB"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
