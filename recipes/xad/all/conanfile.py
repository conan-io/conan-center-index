from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, export_conandata_patches, get, rm, rmdir, save
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
import os

required_conan_version = ">=2.0.9"


class XadConan(ConanFile):
    name = "xad"
    description = "Comprehensive C++ library for automatic differentiation: forward and adjoint modes, higher-order derivatives and checkpointing"
    license = "AGPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://auto-differentiation.github.io"
    topics = ("automatic-differentiation", "algorithmic-differentiation", "aad", "adjoint", "derivatives", "autodiff")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)
        # The VERSION file in the release archive still carries the "-dev" suffix
        save(self, os.path.join(self.source_folder, "VERSION"), f"{self.version}\n")

    @property
    def _simd_option(self):
        # The compiled part is built for the baseline instruction set; the headers use the consumer's flags
        if str(self.settings.arch) in ("x86", "x86_64"):
            return "SSE2"
        if is_msvc(self) and str(self.settings.arch) == "armv8":
            return "armv8.0"
        return "NONE"

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["XAD_ENABLE_TESTS"] = False
        tc.cache_variables["XAD_WARNINGS_PARANOID"] = False
        tc.cache_variables["XAD_SIMD_OPTION"] = self._simd_option
        tc.cache_variables["XAD_POSITION_INDEPENDENT_CODE"] = bool(self.options.get_safe("fPIC", True))
        if is_msvc(self):
            tc.cache_variables["XAD_STATIC_MSVC_RUNTIME"] = is_msvc_static_runtime(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "XAD")
        self.cpp_info.set_property("cmake_target_name", "XAD::xad")
        # On Windows the library name carries the toolset, runtime and build type
        self.cpp_info.libs = collect_libs(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m", "pthread"]
        if is_msvc(self) and self.settings.build_type == "Debug":
            self.cpp_info.defines.append("_SILENCE_STDEXT_ARR_ITERS_DEPRECATION_WARNING")
