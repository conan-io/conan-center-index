from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.scm import Version
import os


required_conan_version = ">=2"


class BearConan(ConanFile):
    name = "bear"
    description = "Bear is a tool that generates a compilation database for clang tooling"
    license = "GPL-3.0-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rizsotto/Bear"
    topics = ("clang", "compilation", "database", "llvm")
    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("grpc/[>=1.50.1 <2]")
        self.requires("spdlog/1.11.0")
        self.requires("fmt/[>=9.1.0 <11]")
        self.requires("nlohmann_json/3.11.2")

    def build_requirements(self):
        self.tool_requires("grpc/<host_version>")

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def validate(self):
        check_min_cppstd(self, 17)
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(f"{self.ref} can not be built on windows.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_UNIT_TESTS"] = False
        tc.variables["ENABLE_FUNC_TESTS"] = False
        tc.generate()
        # In case there are dependencies listed on requirements, CMakeDeps should be used
        tc = CMakeDeps(self)
        tc.generate()

        pc = PkgConfigDeps(self)
        pc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
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
