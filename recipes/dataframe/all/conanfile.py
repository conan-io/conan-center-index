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
    description = (
        "C++ DataFrame for statistical, Financial, and ML analysis -- in modern C++ "
        "using native types and contiguous memory storage"
    )
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/hosseinmoein/DataFrame"
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
        if Version(self.version) < "2.1.0":
            return "17"
        elif Version(self.version) <= "2.2.0":
            return "20"
        else:
            return "23"

    @property
    def _minimum_compilers_version(self):
        return {
            "17": {
                "Visual Studio": "15",
                "msvc": "191",
                "gcc": "7",
                "clang": "6",
                "apple-clang": "10.0",
            },
            "20": {
                "Visual Studio": "16",
                "msvc": "192",
                "gcc": "11",
                "clang": "12",
                "apple-clang": "13",
            },
            "23": {
                "Visual Studio": "17",
                "msvc": "192",
                "gcc": "13",
                "clang": "15",
                "apple-clang": "15",
            },
        }.get(self._min_cppstd, {})

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

    def build_requirements(self):
        if Version(self.version) >= "3.7.0":
            self.tool_requires("cmake/[>=3.20]")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if Version(self.version) >= "2.2.0":
            if (self.settings.compiler == "clang" and Version(self.settings.compiler.version) < "13.0.0" and \
                self.settings.compiler.libcxx == "libc++"):
                raise ConanInvalidConfiguration(f"{self.ref} doesn't support clang < 13.0.0 with libc++.")
            if self.settings.compiler == "apple-clang" and Version(self.settings.compiler.version) < "14.0.0":
                raise ConanInvalidConfiguration(f"{self.ref} doesn't support apple-clang < 14.0.0.")


    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["HMDF_TESTING"] = False
        tc.variables["HMDF_EXAMPLES"] = False
        tc.variables["HMDF_BENCHMARKS"] = False
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
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
        if self.options.shared:
            self.cpp_info.defines.append("HMDF_SHARED")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "DataFrame"
        self.cpp_info.names["cmake_find_package_multi"] = "DataFrame"
