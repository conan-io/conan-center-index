from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
import os

required_conan_version = ">=1.53.0"


class NormConan(ConanFile):
    name = "norm"
    description = "A reliable multicast transport protocol"
    topics = ("multicast", "transport protocol", "nack-oriented reliable multicast")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.nrl.navy.mil/itd/ncs/products/norm"
    license = "NRL"
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
        self.requires("libxml2/2.12.3") # dependency of protolib actually

    def source(self):
        get(self, **self.conan_data["sources"][self.version])

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["NORM_CUSTOM_PROTOLIB_VERSION"] = "./protolib" # FIXME: use external protolib when available in CCI
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        if self.options.shared:
            rm(self, "*proto*", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "norm")
        self.cpp_info.set_property("cmake_target_name", "norm::norm")
        self.cpp_info.libs = ["norm"]
        if not self.options.shared:
            self.cpp_info.libs.append("protokit")

        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines.append("NORM_USE_DLL")

        if self.settings.os == "Windows":
            # system libs of protolib actually
            self.cpp_info.system_libs.extend(["ws2_32", "iphlpapi", "user32", "gdi32", "advapi32", "ntdll"])
        elif self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl", "rt"])
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
