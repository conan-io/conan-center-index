from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
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

    @property
    def _compilers_minimum_version(self):
        # Minimum compiler version having C++11 math functions
        return {
            "apple-clang": "3.3",
            "gcc": "4.9",
            "clang": "6",
            "Visual Studio": "14", # guess
            "msvc": "190",
        }

    def validate(self):
        if Version(self.version) >= "1.51":
            if self.settings.compiler.get_safe("cppstd"):
                check_min_cppstd(self, 11)

            def loose_lt_semver(v1, v2):
                return all(int(p1) < int(p2) for p1, p2 in zip(str(v1).split("."), str(v2).split(".")))

            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version and loose_lt_semver(str(self.settings.compiler.version), minimum_version):
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++11 math functions, which your compiler does not support."
                )

        if self.options.precision not in ["float", "double"]:
            # FIXME: add support for extended, quadruple and variable precisions
            # (may require external libs: boost multiprecision for quadruple, mpfr for variable)
            raise ConanInvalidConfiguration("extended, quadruple and variable precisions not yet supported in this recipe")

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
        tc.generate()

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
        if not self.options.tools:
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

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "geographiclib"
        self.cpp_info.filenames["cmake_find_package_multi"] = "geographiclib"
        self.cpp_info.names["cmake_find_package"] = "GeographicLib"
        self.cpp_info.names["cmake_find_package_multi"] = "GeographicLib"
        if self.options.tools:
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
