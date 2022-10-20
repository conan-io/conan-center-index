from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, replace_in_file, rmdir
import os

required_conan_version = ">=1.47.0"


class MiniupnpcConan(ConanFile):
    name = "miniupnpc"
    description = "UPnP client library/tool to access Internet Gateway Devices."
    license = "BSD-3-Clause"
    topics = ("miniupnpc", "upnp", "networking", "internet-gateway")
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
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
           del self.settings.compiler.libcxx
        except Exception:
           pass
        try:
           del self.settings.compiler.cppstd
        except Exception:
           pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

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
        copy(self, "LICENSE", src=os.path.join(self.source_folder, "miniupnpc"),
                              dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

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
