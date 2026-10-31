import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir

required_conan_version = ">=2.0"


class LemonNgConan(ConanFile):
    name = "lemon-ng"
    description = ("Maintained fork of LEMON, a C++ library of graphs and of "
                   "network optimization")
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/dmeoli/lemon-ng"
    topics = ("graph", "network-flow", "optimization", "lemon")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # LEMON declares no symbol for a DLL
        if self.settings.os == "Windows":
            self.options.shared = False

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["LEMON_VERSION"] = self.version
        for opt in ("TESTS", "DEMOS", "TOOLS", "DOC"):
            tc.cache_variables["LEMON_BUILD_" + opt] = False
        for opt in ("GLPK", "ILOG", "COIN", "SOPLEX"):
            tc.cache_variables["LEMON_ENABLE_" + opt] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder,
             os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "LEMON")
        self.cpp_info.set_property("cmake_target_name", "LEMON::lemon")
        self.cpp_info.set_property("pkg_config_name", "lemon")
        self.cpp_info.libs = ["lemon" if self.settings.os == "Windows"
                              else "emon"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs = ["pthread", "m"]
