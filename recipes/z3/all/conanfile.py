import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import get, copy, rmdir
from conan.tools.scm import Version

required_conan_version = ">=2"


class Z3Conan(ConanFile):
    name = "z3"
    description = "The Z3 Theorem Prover"
    topics = ("z3", "theorem", "smt", "satisfiability", "prover", "solver")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Z3Prover/z3"
    license = "MIT"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "multithreaded": [True, False],
        "use_gmp": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "multithreaded": True,
        "use_gmp": False
    }

    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.use_gmp:
            self.requires("gmp/6.3.0")

    def validate(self):
        check_min_cppstd(self, 11)

    def validate_build(self):
        check_min_cppstd(self, 17 if Version(self.version) < "4.14" else 20)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["Z3_USE_LIB_GMP"] = self.options.use_gmp
        tc.variables["Z3_SINGLE_THREADED"] = not self.options.multithreaded
        tc.variables["Z3_BUILD_LIBZ3_SHARED"] = self.options.shared
        tc.variables["Z3_INCLUDE_GIT_HASH"] = False
        tc.variables["Z3_INCLUDE_GIT_DESCRIBE"] = False
        tc.variables["Z3_ENABLE_EXAMPLE_TARGETS"] = False
        tc.variables["Z3_BUILD_DOCUMENTATION"] = False
        # Set the flag `stdlib` for Clang on Linux to fix the linker errors
        if self.settings.os == "Linux" and self.settings.compiler == "clang":
            # Possible values: `libc++`, `libstdc++11` and `libstdc++`
            stdlib = f" -stdlib={self.settings.compiler.libcxx}".rstrip("1")
            tc.variables["CMAKE_CXX_FLAGS"] = tc.variables.get("CMAKE_CXX_FLAGS", "") + stdlib
        tc.generate()

        deps = CMakeDeps(self)
        # Override the target name of the GMP library provided by Conan Center
        deps.set_property("gmp", "cmake_target_name", "GMP::GMP")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", os.path.join(self.source_folder), os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Z3")
        self.cpp_info.set_property("cmake_target_name", "z3::libz3")

        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["libz3"].libs = ["libz3" if self.settings.os == "Windows" else "z3"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libz3"].system_libs.extend(["pthread", "m"])

        self.cpp_info.components["libz3"].set_property("cmake_target_name", "z3::libz3")
        self.cpp_info.components["libz3"].requires = ["gmp::gmp"] if self.options.use_gmp else []
