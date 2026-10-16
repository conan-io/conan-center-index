import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir

required_conan_version = ">=1.53.0"


class FlashacceptConan(ConanFile):
    name = "flashaccept"
    description = "Fast io_uring TCP accept engine for Linux"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/thealonlevi/flashaccept"
    topics = ("io_uring", "tcp", "accept", "networking", "performance", "linux")
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
        # Pure C library: no C++ runtime settings.
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # flashaccept is built on liburing (>= 2.3); not exposed in public headers.
        self.requires("liburing/2.6")

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(
                f"{self.ref} requires Linux (built on io_uring)."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["FLASHACCEPT_BUILD_EXAMPLES"] = False
        tc.variables["FLASHACCEPT_BUILD_SHARED"] = bool(self.options.shared)
        tc.variables["FLASHACCEPT_BUILD_STATIC"] = not bool(self.options.shared)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        # Conan generates its own CMake/pkg-config files from package_info().
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["flashaccept"]
        self.cpp_info.system_libs = ["pthread"]

        self.cpp_info.set_property("cmake_file_name", "flashaccept")
        self.cpp_info.set_property("cmake_target_name", "flashaccept::flashaccept")
        self.cpp_info.set_property("pkg_config_name", "flashaccept")
