from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc_static_runtime, is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rm, rmdir, replace_in_file, save
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
import os
import textwrap

required_conan_version = ">=1.52.0"


class Z3Conan(ConanFile):
    name = "z3"
    description = "The Z3 Theorem Prover"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Z3Prover/z3"
    topics = ("z3", "theorem", "smt", "satisfiability", "prover", "solver")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "multithreaded": [True, False],
        "multiprecision": ["internal", "gmp", "mpir"]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "multithreaded": True,
        "multiprecision": "gmp"
    }

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "Visual Studio": "15.7",
            "clang": "5",
            "apple-clang": "10",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.options.multiprecision == "internal":
            self.provides.append("gmp")

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.output.info(
            f"{self.name} will build using {self.options.multiprecision} multiprecision implementation.")
        if self.options.multiprecision == "mpir":
            self.requires("mpir/3.0.0")
        elif self.options.multiprecision == "gmp":
            self.requires("gmp/6.2.1")
        elif self.options.multiprecision == "internal":
            pass

    def validate(self):
        if Version(self.version) >= "4.8.11":
            if self.info.settings.compiler.cppstd:
                check_min_cppstd(self, self._minimum_cpp_standard)
            compiler = self.settings.compiler
            minimum_version = self._compilers_minimum_version.get(str(self.info.settings.compiler), False)
            if minimum_version:
                if Version(self.info.settings.compiler.version) < minimum_version:
                    raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._minimum_cpp_standard}, which your compiler does not support.")
            else:
                self.output.info(
                    f"{self.name} requires C++17. Your compiler is unknown. Assuming it supports C++17.")
        if is_msvc(self) and self.info.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} can not be built as shared on Visual Studio and msvc.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["PACKAGE_CUSTOM_DEFINITION"] = True
        tc.variables["Z3_USE_LIB_GMP"] = self.options.multiprecision != "internal"
        tc.variables["Z3_USE_LIB_MPIR"] = self.options.multiprecision == "mpir"
        tc.variables["SINGLE_THREADED"] = not self.options.multithreaded
        tc.variables["Z3_BUILD_LIBZ3_SHARED"] = self.options.shared
        tc.variables["Z3_INCLUDE_GIT_HASH"] = False
        tc.variables["Z3_INCLUDE_GIT_DESCRIBE"] = False
        tc.variables["Z3_ENABLE_EXAMPLE_TARGETS"] = False
        tc.variables["Z3_BUILD_DOCUMENTATION"] = False
        if is_msvc(self):
            tc.variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()
        tc = VirtualBuildEnv(self)
        tc.generate(scope="build")

    def build(self):
        apply_conandata_patches(self)

        if self.options.multiprecision == "mpir":
            save(self, os.path.join(self.build_folder, "gmp.h"), textwrap.dedent("""\
                #pragma once
                #include <mpir.h>
                """))

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Z3")
        self.cpp_info.set_property("cmake_target_name", "z3::libz3")

        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["libz3"].libs = [
            "libz3" if self.settings.os == "Windows" else "z3"]
        if not self.options.shared:
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["libz3"]\
                    .system_libs.extend(["pthread", "m"])
        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "Z3"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Z3"
        self.cpp_info.names["cmake_find_package"] = "z3"
        self.cpp_info.names["cmake_find_package_multi"] = "z3"
        self.cpp_info.components["libz3"].names["cmake_find_package"] = "libz3"
        self.cpp_info.components["libz3"].names["cmake_find_package_multi"] = "libz3"
        self.cpp_info.components["libz3"].set_property(
            "cmake_target_name", "z3::libz3")

        libz3_requirements = []
        if self.options.multiprecision == "mpir":
            libz3_requirements.append("mpir::mpir")
        elif self.options.multiprecision == "gmp":
            libz3_requirements.append("gmp::gmp")
        elif self.options.multiprecision == "internal":
            pass
        self.cpp_info.components["libz3"].requires = libz3_requirements
