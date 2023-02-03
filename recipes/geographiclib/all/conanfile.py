from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, get, replace_in_file, rm, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


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
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    @property
    def _compilers_minimum_version(self):
        # Minimum compiler version having C++11 math functions
        return {
            "apple-clang": "3.3",
            "gcc": "4.9",
            "clang": "6",
            "Visual Studio": "14", # guess
        }

    def validate(self):
        if Version(self.version) >= "1.51":
            if self.info.settings.compiler.cppstd:
                check_min_cppstd(self, 11)

            def lazy_lt_semver(v1, v2):
                lv1 = [int(v) for v in v1.split(".")]
                lv2 = [int(v) for v in v2.split(".")]
                min_length = min(len(lv1), len(lv2))
                return lv1[:min_length] < lv2[:min_length]

            minimum_version = self._compilers_minimum_version.get(str(self.info.settings.compiler), False)
            if minimum_version and lazy_lt_semver(str(self.info.settings.compiler.version), minimum_version):
                raise ConanInvalidConfiguration("geographiclib {} requires C++11 math functions, which your compiler does not support.".format(self.version))

        if self.info.options.precision not in ["float", "double"]:
            # FIXME: add support for extended, quadruple and variable precisions
            # (may require external libs: boost multiprecision for quadruple, mpfr for variable)
            raise ConanInvalidConfiguration("extended, quadruple and variable precisions not yet supported in this recipe")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

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
        # it does not work on Windows but is not needed
        replace_in_file(self, cmakelists, "add_subdirectory (js)", "")
        # Don't install system libs
        replace_in_file(self, cmakelists, "include (InstallRequiredSystemLibraries)", "")
        # Don't build tools if asked
        if not self.options.tools:
            replace_in_file(self, cmakelists, "add_subdirectory (tools)", "")
            replace_in_file(self, os.path.join(self.source_folder, "cmake", "CMakeLists.txt"),
                                  "${TOOLS}", "")

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

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "geographiclib")
        self.cpp_info.set_property("cmake_target_name", "GeographicLib::GeographicLib")
        self.cpp_info.set_property("pkg_config_name", "geographiclib")
        self.cpp_info.libs = collect_libs(self)
        self.cpp_info.defines.append("GEOGRAPHICLIB_SHARED_LIB={}".format("1" if self.options.shared else "0"))

        if self.options.tools:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "geographiclib"
        self.cpp_info.filenames["cmake_find_package_multi"] = "geographiclib"
        self.cpp_info.names["cmake_find_package"] = "GeographicLib"
        self.cpp_info.names["cmake_find_package_multi"] = "GeographicLib"
