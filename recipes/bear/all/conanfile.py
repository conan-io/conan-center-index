from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, check_max_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.scm import Version
import os


required_conan_version = ">=2.0.6"


class BearConan(ConanFile):
    name = "bear"
    description = "Bear is a tool that generates a compilation database for clang tooling"
    license = "GPL-3.0-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rizsotto/Bear"
    topics = ("clang", "compilation", "database", "llvm")
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("grpc/1.50.1")
        if Version(self.version) >= "3.1":
            self.requires("fmt/10.2.1")
            self.requires("spdlog/1.14.1")
            self.requires("nlohmann_json/3.11.3")
        else:
            # fmt < v10 is required, but v9 is not compatible with spdlog recipe versions
            self.requires("fmt/8.1.1")
            self.requires("spdlog/1.10.0")
            self.requires("nlohmann_json/3.11.2")

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        self.tool_requires("grpc/<host_version>")
        self.tool_requires("protobuf/3.21.12")
        # Older version of CMake fails to build object libraries in the correct order
        self.tool_requires("cmake/[>=3.20 <4]")

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def validate(self):
        check_min_cppstd(self, 17)
        # fmt/ranges.h fails to compile with C++20
        check_max_cppstd(self, 17)
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(f"{self.ref} can not be built on windows.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_UNIT_TESTS"] = False
        tc.variables["ENABLE_FUNC_TESTS"] = False
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

        pc = PkgConfigDeps(self)
        pc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "source"))
        cmake.build()

    def package(self):
        copy(self, pattern="COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        # some files extensions and folders are not allowed. Please, read the FAQs to get informed.
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []
