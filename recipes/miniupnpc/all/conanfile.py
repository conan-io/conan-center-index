from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class MiniupnpcConan(ConanFile):
    name = "miniupnpc"
    description = "UPnP client library/tool to access Internet Gateway Devices."
    license = "BSD-3-Clause"
    topics = ("upnp", "networking", "internet-gateway")
    homepage = "https://github.com/miniupnp/miniupnp"
    url = "https://github.com/conan-io/conan-center-index"

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
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["UPNPC_BUILD_STATIC"] = not self.options.shared
        tc.variables["UPNPC_BUILD_SHARED"] = self.options.shared
        tc.variables["UPNPC_BUILD_TESTS"] = False
        tc.variables["UPNPC_BUILD_SAMPLE"] = False
        tc.variables["NO_GETADDRINFO"] = False
        tc.variables["UPNPC_NO_INSTALL"] = False
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Do not force PIC
        replace_in_file(self, os.path.join(self.source_folder, "miniupnpc", "CMakeLists.txt"),
                              "set(CMAKE_POSITION_INDEPENDENT_CODE ON)", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "miniupnpc"))
        cmake.build()

    def package(self):
        if Version(self.version) >= "2.2.4":
            copy(self, "LICENSE", src=self.source_folder,
                                  dst=os.path.join(self.package_folder, "licenses"))
        else:
            copy(self, "LICENSE", src=os.path.join(self.source_folder, "miniupnpc"),
                                  dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "miniupnpc")
        self.cpp_info.set_property("cmake_target_name", "miniupnpc::miniupnpc")
        self.cpp_info.set_property("pkg_config_name", "miniupnpc")
        prefix = "lib" if self.settings.os == "Windows" and not self.options.shared else ""
        self.cpp_info.libs = [f"{prefix}miniupnpc"]
        if not self.options.shared:
            self.cpp_info.defines.append("MINIUPNP_STATICLIB")
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["iphlpapi", "ws2_32"]
        elif self.settings.os == "SunOS":
            self.cpp_info.system_libs = ["socket", "nsl", "resolv"]
