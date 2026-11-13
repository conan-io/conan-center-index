from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=2.1"


class SdlnetConan(ConanFile):
    name = "sdl_net"
    description = "A networking library for SDL"
    license = "Zlib"
    topics = ("sdl2", "sdl2_net", "sdl", "sdl_net", "net", "networking")
    homepage = "https://www.libsdl.org/projects/SDL_net"
    url = "https://github.com/conan-io/conan-center-index"
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
    implements = ["auto_shared_fpic"]
    languages = "C"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("sdl/[>=3.2.6 <4]", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if self.options.shared != self.dependencies["sdl"].options.shared:
            raise ConanInvalidConfiguration("sdl & sdl_net must be built with the same 'shared' option value")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        lib_suffix = ""
        if is_msvc(self) and not self.options.shared:
            lib_suffix = "-static"
        self.cpp_info.libs = [f"SDL3_net{lib_suffix}"]
        self.cpp_info.set_property("cmake_file_name", "SDL3_net")
        suffix = "-static" if not self.options.shared else ""
        self.cpp_info.set_property("cmake_target_name", f"SDL3_net::SDL3_net{suffix}")
        self.cpp_info.set_property("pkg_config_name", "sdl3-net")

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32", "iphlpapi"])
