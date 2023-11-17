import os

from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, save
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("eigen/3.4.0")
        self.requires("fast_double_parser/0.7.0", transitive_headers=True)
        self.requires("fmt/10.0.0", transitive_headers=True)
        # FIXME: enable when llvm-openmp has been migrated to Conan v2
        # if self.options.with_openmp and self.settings.compiler in ("clang", "apple-clang"):
        #     self.requires("llvm-openmp/12.0.1")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_STATIC_LIB"] = not self.options.shared
        tc.cache_variables["USE_DEBUG"] = self.settings.build_type in ["Debug", "RelWithDebInfo"]
        tc.cache_variables["USE_OPENMP"] = self.options.with_openmp
        tc.cache_variables["BUILD_CLI"] = False
        if is_apple_os(self):
            tc.cache_variables["APPLE_OUTPUT_DYLIB"] = True
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        cmakelists_path = os.path.join(self.source_folder, "CMakeLists.txt")
        # Fix OpenMP detection for Clang
        replace_in_file(self, cmakelists_path, "AppleClang", "Clang|AppleClang")
        # Fix vendored dependency includes
        common_h = os.path.join(self.source_folder, "include", "LightGBM", "utils", "common.h")
        for lib in ["fmt", "fast_double_parser"]:
            replace_in_file(self, common_h, f"../../../external_libs/{lib}/include/", "")
        # Add dependencies
        extra_cmake_content = (
            "find_package(fmt REQUIRED CONFIG)\n"
            "find_package(Eigen3 REQUIRED CONFIG)\n"
            "find_package(fast_double_parser REQUIRED CONFIG)\n"
        )
        if Version(self.version).major >= 4:
            targets = ["lightgbm_objs", "lightgbm_capi_objs"]
        else:
            targets = ["lightgbm", "_lightgbm"]
        for target in targets:
            extra_cmake_content += (
                f"target_link_libraries({target} PRIVATE "
                "fmt::fmt Eigen3::Eigen fast_double_parser::fast_double_parser)\n"
            )
        save(self, cmakelists_path, extra_cmake_content, append=True)


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
        if not self.options.shared and self.options.with_openmp:
            if is_msvc(self):
                openmp_flags = ["-openmp"]
            elif self.settings.compiler == "gcc":
                openmp_flags = ["-fopenmp"]
            elif self.settings.compiler in ("clang", "apple-clang"):
                openmp_flags = ["-Xpreprocessor", "-fopenmp"]
            else:
                openmp_flags = []
            self.cpp_info.exelinkflags.extend(openmp_flags)
            self.cpp_info.sharedlinkflags.extend(openmp_flags)
