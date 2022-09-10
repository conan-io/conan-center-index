from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, replace_in_file, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.50.0"


class DataFrameConan(ConanFile):
    name = "dataframe"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/hosseinmoein/DataFrame"
    description = (
        "C++ DataFrame for statistical, Financial, and ML analysis -- in modern C++ "
        "using native types, continuous memory storage, and no pointers are involved"
    )
    topics = (
        "dataframe",
        "data-science",
        "numerical-analysis",
        "multidimensional-data",
        "heterogeneous",
        "cpp",
        "statistical-analysis",
        "financial-data-analysis",
        "financial-engineering",
        "data-analysis",
        "trading-strategies",
        "machine-learning",
        "trading-algorithms",
        "financial-engineering",
        "large-data",
    )

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10.0" if Version(self.version) >= "1.12.0" else "9.0",
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

    def validate(self):
        if is_msvc(self) and self.info.options.shared and Version(self.version) < "1.20.0":
            raise ConanInvalidConfiguration(
                "dataframe {} doesn't support shared lib with Visual Studio".format(self.version)
            )

        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, "17")

        minimum_version = self._minimum_compilers_version.get(str(self.info.settings.compiler), False)
        if minimum_version and Version(self.info.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                "{} requires C++17, which your compiler does not support.".format(self.name)
            )

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if Version(self.version) >= "1.20.0":
            tc.variables["HMDF_TESTING"] = False
            tc.variables["HMDF_EXAMPLES"] = False
            tc.variables["HMDF_BENCHMARKS"] = False
        elif Version(self.version) >= "1.14.0":
            tc.variables["ENABLE_TESTING"] = False
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Don't pollute RPATH
        if Version(self.version) < "1.20.0":
            replace_in_file(
                self,
                os.path.join(self.source_folder, "CMakeLists.txt"),
                textwrap.dedent("""\
                    include(AddInstallRPATHSupport)
                    add_install_rpath_support(BIN_DIRS "${CMAKE_INSTALL_FULL_LIBDIR}"
                                              LIB_DIRS "${CMAKE_INSTALL_FULL_BINDIR}"
                                              INSTALL_NAME_DIR "${CMAKE_INSTALL_FULL_LIBDIR}"
                                              USE_LINK_PATH)
                """),
                "",
            )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "License", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        # Remove packaging files & MS runtime files
        for dir_to_remove in [
            os.path.join("lib", "cmake"),
            os.path.join("lib", "share"),
            os.path.join("lib", "pkgconfig"),
            "CMake",
        ]:
            rmdir(self, os.path.join(self.package_folder, dir_to_remove))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "DataFrame")
        self.cpp_info.set_property("cmake_target_name", "DataFrame::DataFrame")
        self.cpp_info.set_property("pkg_config_name", "DataFrame")
        self.cpp_info.libs = ["DataFrame"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread", "rt"])
        if is_msvc(self):
            self.cpp_info.defines.append("_USE_MATH_DEFINES")
            if Version(self.version) < "1.20.0" and not self.options.shared:
                # weird but required in those versions of dataframe
                self.cpp_info.defines.append("LIBRARY_EXPORTS")
        if Version(self.version) >= "1.20.0" and self.options.shared:
            self.cpp_info.defines.append("HMDF_SHARED")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "DataFrame"
        self.cpp_info.names["cmake_find_package_multi"] = "DataFrame"
        self.cpp_info.names["pkg_config"] = "DataFrame"
