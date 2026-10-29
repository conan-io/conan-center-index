import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir

required_conan_version = ">=2.0"


class ReliableConan(ConanFile):
    name = "reliable"
    description = "A simple reliability layer for UDP-based protocols: " \
                  "packet acknowledgement and fragmentation"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mas-bandwidth/reliable"
    topics = ("udp", "networking", "games", "reliability")
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
        # plain C library: the C++ settings do not affect the package
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # tests, example, soak, stats and fuzz harnesses default ON when reliable is
        # the top-level project; none of them are part of the package.
        tc.cache_variables["RELIABLE_BUILD_TESTS"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        # upstream spells it LICENCE
        copy(self, "LICENCE", self.source_folder,
             os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        # upstream installs reliable.pc; Conan generators replace it
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["reliable"]
        # match the reliable.pc that upstream installs
        self.cpp_info.set_property("pkg_config_name", "reliable")
        if self.settings.os in ["Linux", "FreeBSD"]:
            # fabs/pow in the rtt, jitter and bandwidth statistics
            self.cpp_info.system_libs = ["m"]

