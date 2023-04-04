from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.53.0"


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

    @property
    def _min_cppstd(self):
        return "17"

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "msvc": "191",
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10.0",
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

    def validate(self):
        if is_msvc(self) and self.options.shared and Version(self.version) < "1.20.0":
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support shared lib with Visual Studio")

        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

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
            self.cpp_info.system_libs.extend(["pthread", "rt", "m"])
        if is_msvc(self):
            self.cpp_info.defines.append("_USE_MATH_DEFINES")
            if Version(self.version) < "1.20.0" and not self.options.shared:
                # weird but required in those versions of dataframe
                self.cpp_info.defines.append("LIBRARY_EXPORTS")
        if "1.20.0" <= Version(self.version) < "2.0.0" and self.options.shared:
            self.cpp_info.defines.append("HMDF_SHARED")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "DataFrame"
        self.cpp_info.names["cmake_find_package_multi"] = "DataFrame"
