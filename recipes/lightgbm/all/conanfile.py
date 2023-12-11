import os

from conan import ConanFile, conan_version
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, export_conandata_patches, apply_conandata_patches
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class LightGBMConan(ConanFile):
    name = "lightgbm"
    description = (
        "A fast, distributed, high performance gradient boosting "
        "(GBT, GBDT, GBRT, GBM or MART) framework based on decision tree algorithms, "
        "used for ranking, classification and many other machine learning tasks."
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/microsoft/LightGBM"
    topics = ("machine-learning", "boosting")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openmp": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openmp": True,
    }

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if conan_version.major == 1 and self.settings.compiler == "apple-clang":
            # https://github.com/conan-io/conan-center-index/pull/18759#issuecomment-1817470331
            del self.options.with_openmp

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("eigen/3.4.0")
        self.requires("fast_double_parser/0.7.0", transitive_headers=True, transitive_libs=True)
        self.requires("fmt/10.1.1", transitive_headers=True, transitive_libs=True)
        if self.options.get_safe("with_openmp") and self.settings.compiler in ["clang", "apple-clang"]:
            self.requires("llvm-openmp/17.0.4", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_STATIC_LIB"] = not self.options.shared
        tc.cache_variables["USE_DEBUG"] = self.settings.build_type in ["Debug", "RelWithDebInfo"]
        tc.cache_variables["USE_OPENMP"] = self.options.get_safe("with_openmp", False)
        tc.cache_variables["BUILD_CLI"] = False
        if is_apple_os(self):
            tc.cache_variables["APPLE_OUTPUT_DYLIB"] = True
        tc.variables["_MAJOR_VERSION"] = Version(self.version).major
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Fix vendored dependency includes
        common_h = os.path.join(self.source_folder, "include", "LightGBM", "utils", "common.h")
        for lib in ["fmt", "fast_double_parser"]:
            replace_in_file(self, common_h, f"../../../external_libs/{lib}/include/", "")
        # Unvendor Eigen3
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "include_directories(${EIGEN_DIR})", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(build_script_folder=self.source_path.parent)
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "LightGBM")
        self.cpp_info.set_property("cmake_target_name", "LightGBM::LightGBM")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "LightGBM"
        self.cpp_info.names["cmake_find_package_multi"] = "LightGBM"

        self.cpp_info.libs = ["lib_lightgbm"] if is_msvc(self) else ["_lightgbm"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32", "iphlpapi"])
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")

        # OpenMP preprocessor directives are used in a number of public headers, such as:
        # https://github.com/microsoft/LightGBM/blob/master/include/LightGBM/tree.h#L188
        if self.options.get_safe("with_openmp"):
            openmp_flags = []
            if is_msvc(self):
                openmp_flags = ["-openmp"]
            elif self.settings.compiler == "gcc":
                openmp_flags = ["-fopenmp"]
            elif self.settings.compiler in ["clang", "apple-clang"]:
                openmp_flags = ["-Xpreprocessor", "-fopenmp"]
            self.cpp_info.cxxflags.extend(openmp_flags)
            self.cpp_info.exelinkflags.extend(openmp_flags)
            self.cpp_info.sharedlinkflags.extend(openmp_flags)
