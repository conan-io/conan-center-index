import os

from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class FlintConan(ConanFile):
    name = "flint"
    description = "FLINT (Fast Library for Number Theory)"
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.flintlib.org"
    topics = ("math", "numerical")

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

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("gmp/6.3.0", transitive_headers=True, transitive_libs=True)
        self.requires("mpfr/4.2.1", transitive_headers=True, transitive_libs=True)
        if is_msvc(self):
            self.requires("pthreads4w/3.0.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_TESTING"] = False
        tc.cache_variables["BUILD_DOCS"] = False
        tc.cache_variables["WITH_NTL"] = False
        # IPO/LTO breaks clang builds
        tc.cache_variables["IPO_SUPPORTED"] = False
        # No BLAS yet
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_CBLAS"] = True
        # handle run in a cross-build
        if cross_building(self):
            tc.cache_variables["FLINT_USES_POPCNT_EXITCODE"] = "1"
            tc.cache_variables["FLINT_USES_POPCNT_EXITCODE__TRYRUN_OUTPUT"] = ""
        tc.generate()

        deps = CMakeDeps(self)
        if Version(self.version) <= "3.0.1":
            deps.set_property("pthreads4w", "cmake_file_name", "PThreads")
        else:
            # https://github.com/flintlib/flint/commit/c6cc1078cb55903b0853fb1b6dc660887842dadf
            deps.set_property("pthreads4w", "cmake_file_name", "PThreads4W")
        deps.set_property("pthreads4w", "cmake_target_name", "PThreads4W::PThreads4W")
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "MPFR_", "mpfr_")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libflint")
        self.cpp_info.set_property("cmake_target_name", "libflint::libflint")

        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["pthread", "m"]

        self.cpp_info.includedirs.append(os.path.join("include", "flint"))
        self.cpp_info.libs = ["flint"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "libflint"
        self.cpp_info.names["cmake_find_package_multi"] = "libflint"
