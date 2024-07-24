import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class Pagmo2Conan(ConanFile):
    name = "pagmo2"
    description = "pagmo is a C++ scientific library for massively parallel optimization."
    license = ("LGPL-3.0-or-later", "GPL-3.0-or-later")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://esa.github.io/pagmo2"
    topics = ("pagmo", "optimization", "parallel-computing", "genetic-algorithm", "metaheuristics")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_eigen": [True, False],
        "with_nlopt": [True, False],
        "with_ipopt": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_eigen": False,
        "with_nlopt": False,
        "with_ipopt": False,
    }

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15.7",
            "msvc": "191",
            "gcc": "7",
            "clang": "5.0",
            "apple-clang": "9",
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
        self.requires("boost/1.85.0", transitive_headers=True)
        self.requires("onetbb/2021.12.0")
        if self.options.with_eigen:
            self.requires("eigen/3.4.0", transitive_headers=True)
        if self.options.with_nlopt:
            self.requires("nlopt/2.7.1", transitive_headers=True, transitive_libs=True)

    @property
    def _required_boost_components(self):
        return ["serialization"]

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 17)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.name} {self.version} requires C++17, which your compiler does not support."
            )

        # TODO: add ipopt support
        if self.options.with_ipopt:
            raise ConanInvalidConfiguration("ipopt recipe not available yet in CCI")

        miss_boost_required_comp = any(
            self.dependencies["boost"].options.get_safe(f"without_{boost_comp}", True)
            for boost_comp in self._required_boost_components
        )
        if self.dependencies["boost"].options.header_only or miss_boost_required_comp:
            raise ConanInvalidConfiguration(
                "{0} requires non header-only boost with these components: {1}".format(
                    self.name, ", ".join(self._required_boost_components)
                )
            )

        if is_msvc(self) and self.options.shared:
            # test_package.obj : error LNK2019: unresolved external symbol "public: __cdecl boost::archive::codecvt_null<wchar_t>::codecvt_null<wchar_t>(unsigned __int64)"
            # https://github.com/boostorg/serialization/issues/232
            # https://github.com/conda-forge/scipoptsuite-feedstock/pull/44
            raise ConanInvalidConfiguration("Shared builds are currently broken on MSVC")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["PAGMO_BUILD_TESTS"] = False
        tc.variables["PAGMO_BUILD_BENCHMARKS"] = False
        tc.variables["PAGMO_BUILD_TUTORIALS"] = False
        tc.variables["PAGMO_WITH_EIGEN3"] = self.options.with_eigen
        tc.variables["PAGMO_WITH_NLOPT"] = self.options.with_nlopt
        tc.variables["PAGMO_WITH_IPOPT"] = self.options.with_ipopt
        tc.variables["PAGMO_ENABLE_IPO"] = False
        tc.variables["PAGMO_BUILD_STATIC_LIBRARY"] = not self.options.shared
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        # do not force MT runtime for static lib
        if Version(self.version) < "2.18":
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                            "if(YACMA_COMPILER_IS_MSVC AND PAGMO_BUILD_STATIC_LIBRARY)", "if(0)")
        # No warnings as errors
        yacma_cmake = os.path.join(self.source_folder, "cmake_modules", "yacma", "YACMACompilerLinkerSettings.cmake")
        replace_in_file(self, yacma_cmake, 'list(APPEND _YACMA_CXX_FLAGS_DEBUG "-Werror")', "")
        replace_in_file(self, yacma_cmake, "_YACMA_CHECK_ENABLE_DEBUG_CXX_FLAG(/W4)", "")
        replace_in_file(self, yacma_cmake, "_YACMA_CHECK_ENABLE_DEBUG_CXX_FLAG(/WX)", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING.*",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        # https://esa.github.io/pagmo2/quickstart.html#using-pagmo-with-cmake
        self.cpp_info.set_property("cmake_file_name", "Pagmo")
        self.cpp_info.set_property("cmake_target_name", "Pagmo::pagmo")

        self.cpp_info.components["_pagmo"].libs = ["pagmo"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_pagmo"].system_libs.append("pthread")

        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["_pagmo"].requires = ["boost::boost", "onetbb::onetbb"]
        if self.options.with_eigen:
            self.cpp_info.components["_pagmo"].requires.append("eigen::eigen")
        if self.options.with_nlopt:
            self.cpp_info.components["_pagmo"].requires.append("nlopt::nlopt")
        self.cpp_info.filenames["cmake_find_package"] = "pagmo"
        self.cpp_info.filenames["cmake_find_package_multi"] = "pagmo"
        self.cpp_info.names["cmake_find_package"] = "Pagmo"
        self.cpp_info.names["cmake_find_package_multi"] = "Pagmo"
        self.cpp_info.components["_pagmo"].names["cmake_find_package"] = "pagmo"
        self.cpp_info.components["_pagmo"].names["cmake_find_package_multi"] = "pagmo"
