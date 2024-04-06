import os

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, export_conandata_patches, get, rmdir, replace_in_file

required_conan_version = ">=1.53.0"


class KcpConan(ConanFile):
    name = "kcp"
    description = "A Fast and Reliable ARQ Protocol"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/skywind3000/kcp"
    topics = ("ARQ", "TCP", "protocol")

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
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.variables["BUILD_TESTING"] = False
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        # Fix shared builds on Windows
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        " STATIC", "")
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "ARCHIVE DESTINATION",
                        "RUNTIME DESTINATION bin\nARCHIVE DESTINATION")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["kcp"]
