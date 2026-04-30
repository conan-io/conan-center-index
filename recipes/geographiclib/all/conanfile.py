from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import (
    apply_conandata_patches, copy, export_conandata_patches, get,
    replace_in_file, rm, rmdir, collect_libs
)
from conan.tools.scm import Version
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.53.0"


class GeographiclibConan(ConanFile):
    name = "geographiclib"
    description = "Convert geographic units and solve geodesic problems"
    topics = ("geographiclib", "geodesic")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://geographiclib.sourceforge.io"
    license = "MIT"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "precision": ["float", "double", "extended", "quadruple", "variable"],
        "tools": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "precision": "double",
        "tools": True,
    }

    @property
    def _min_cppstd(self):
        if Version(self.version) >= "2.4":
            return 14
        if Version(self.version) >= "1.51":
            return 11
        return None

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

    def validate(self):
        if Version(self.version) >= "2.6":
            min_cppstd = 17
        elif Version(self.version) >= "2.4":
            min_cppstd = 14
        elif Version(self.version) >= "1.51":
            min_cppstd = 11
        else:
            min_cppstd = None
        
        if min_cppstd:
            check_min_cppstd(self, min_cppstd)

        if self.options.precision not in ["float", "double"]:
            # FIXME: add support for extended, quadruple and variable precisions
            # (may require external libs: boost multiprecision for quadruple, mpfr for variable)
            raise ConanInvalidConfiguration("extended, quadruple and variable precisions not yet supported in this recipe")

    def build_requirements(self):
        if Version(self.version) >= "2.5":
            self.tool_requires("cmake/[>=3.17 <4]")
        elif Version(self.version) >= "2.4":
            self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _cmake_option_precision(self):
        return {
            "float": 1,
            "double": 2,
            "extended": 3,
            "quadruple": 4,
            "variable": 5,
        }.get(str(self.options.precision))

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["GEOGRAPHICLIB_LIB_TYPE"] = "SHARED" if self.options.shared else "STATIC"
        tc.variables["GEOGRAPHICLIB_PRECISION"] = self._cmake_option_precision
        if (not self.options.tools) and (Version(self.version) >= "2.3"):
            # https://github.com/geographiclib/geographiclib/pull/39#issuecomment-2885315450
            tc.variables["BINDIR"] = "OFF"
        tc.generate()

        VirtualBuildEnv(self).generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        if Version(self.version) < "2":
            # it does not work on Windows but is not needed
            replace_in_file(self, cmakelists, "add_subdirectory (js)", "")
        # Don't install system libs
        replace_in_file(self, cmakelists, "include (InstallRequiredSystemLibraries)", "")
        # Disable -Werror
        replace_in_file(self, cmakelists, "-Werror", "")
        replace_in_file(self, cmakelists, "/WX", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        for folder in [
            "share", "sbin", "python", "matlab", "doc", "cmake",
            os.path.join("lib", "python"),
            os.path.join("lib", "pkgconfig"),
            os.path.join("lib", "cmake"),
        ]:
            rmdir(self, os.path.join(os.path.join(self.package_folder, folder)))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        if (not self.options.tools) and (Version(self.version) < "2.3"):
            rmdir(self, os.path.join(self.package_folder, "sbin"))
            bin_files = [it for it in os.listdir(os.path.join(self.package_folder, "bin")) if not it.endswith(".dll")]
            for it in bin_files:
                rm(self, it, os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "geographiclib")
        self.cpp_info.set_property("cmake_target_name", "GeographicLib::GeographicLib")
        self.cpp_info.set_property("pkg_config_name", "geographiclib")
        # Geographic library name is GeographicLib since version 2.x (was Geographic before)
        # It uses a debug postfix _d on Windows or when using multi-configuration generators (like Ninja Multi-Config)
        # It's hard to track when using multi-configuration generators, so collect_libs is used
        # Plus, it adds -i postfix on Windows when using shared libraries
        self.cpp_info.libs = collect_libs(self)
        self.cpp_info.defines.append("GEOGRAPHICLIB_SHARED_LIB={}".format("1" if self.options.shared else "0"))
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]

