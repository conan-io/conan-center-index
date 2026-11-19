from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=2.1"


class MaronaRecipe(ConanFile):
    name = "marona"
    author = "Blessing Nyuwani"
    description = "C++20 Marona Agents, B2A, D2A, realtime streaming and MCP servers"
    license = "MIT"
    homepage = "https://github.com/BlessingNyuwani/marona-cpp"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("ai", "agents", "b2a", "d2a", "mcp", "realtime")
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("nlohmann_json/3.12.0", transitive_headers=True)
        self.requires("libcurl/[>=8 <9]")
        self.requires("jsoncons/1.7.0")
        self.requires("cpp-httplib/0.65.0")

    def validate(self):
        check_min_cppstd(self, "20")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.24 <5]")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        CMakeDeps(self).generate()
        toolchain = CMakeToolchain(self)
        toolchain.variables["MARONA_BUILD_TESTS"] = False
        toolchain.variables["MARONA_BUILD_EXAMPLES"] = False
        toolchain.variables["MARONA_USE_SYSTEM_HTTPLIB"] = True
        toolchain.variables["MARONA_JSONCONS_INCLUDE_DIR"] = self.dependencies["jsoncons"].cpp_info.includedirs[0].replace("\\", "/")
        toolchain.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        CMake(self).install()
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["marona"]
        self.cpp_info.set_property("cmake_file_name", "marona")
        self.cpp_info.set_property("cmake_target_name", "marona::marona")
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]
