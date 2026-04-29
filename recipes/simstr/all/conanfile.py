from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, export_conandata_patches, apply_conandata_patches, rmdir
from conan.tools.scm import Version
import os


required_conan_version = ">=2.1"


class PackageConan(ConanFile):
    name = "simstr"
    description = "Yet another C++ strings library implementation"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/orefkov/simstr"
    topics = ("strings", "expression templates", "c++20")
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

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("simdutf/[>=7.5 <8]")

    def validate(self):
        check_min_cppstd(self, 20)
        compiler = str(self.settings.compiler)
        compiler_version = Version(self.settings.compiler.version)

        if compiler == "gcc" and compiler_version < "13":
            raise ConanInvalidConfiguration(f"{self.ref} requires at least GCC 13 for proper C++20 support")
        elif compiler == "clang" and compiler_version < "17":
            raise ConanInvalidConfiguration(f"{self.ref} requires at least Clang 17 for proper C++20 support")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.20]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["SIMSTR_BUILD_TESTS"] = False
        tc.cache_variables["SIMSTR_BENCHMARKS"] = False
        tc.cache_variables["SIMSTR_LINK_NATVIS"] = False
        tc.cache_variables["USE_SYSTEM_DEPS"] = True
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["simstr"]
        self.cpp_info.includedirs = [os.path.join("include", f"simstr-{self.version}")]
