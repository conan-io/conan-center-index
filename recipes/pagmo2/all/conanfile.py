from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.43.0"


class Pagmo2Conan(ConanFile):
    name = "pagmo2"
    description = "pagmo is a C++ scientific library for massively parallel optimization."
    license = ("LGPL-3.0-or-later", "GPL-3.0-or-later")
    topics = ("pagmo", "optimization", "parallel-computing", "genetic-algorithm", "metaheuristics")
    homepage = "https://esa.github.io/pagmo2"
    url = "https://github.com/conan-io/conan-center-index"

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

    exports_sources = "CMakeLists.txt"
    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("boost/1.78.0")
        self.requires("onetbb/2020.3")
        if self.options.with_eigen:
            self.requires("eigen/3.4.0")
        if self.options.with_nlopt:
            self.requires("nlopt/2.7.1")

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15.7",
            "gcc": "7",
            "clang": "5.0",
            "apple-clang": "9.1"
        }

    @property
    def _required_boost_components(self):
        return ["serialization"]

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 17)

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("{} {} requires C++17. Your compiler is unknown. Assuming it supports C++17.".format(self.name, self.version))
        elif lazy_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration("{} {} requires C++17, which your compiler does not support.".format(self.name, self.version))

        # TODO: add ipopt support
        if self.options.with_ipopt:
            raise ConanInvalidConfiguration("ipopt recipe not available yet in CCI")

        miss_boost_required_comp = any(getattr(self.options["boost"], "without_{}".format(boost_comp), True) for boost_comp in self._required_boost_components)
        if self.options["boost"].header_only or miss_boost_required_comp:
            raise ConanInvalidConfiguration("{0} requires non header-only boost with these components: {1}".format(self.name, ", ".join(self._required_boost_components)))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        # do not force MT runtime for static lib
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "if(YACMA_COMPILER_IS_MSVC AND PAGMO_BUILD_STATIC_LIBRARY)",
                              "if(0)")
        # No warnings as errors
        yacma_cmake = os.path.join(self._source_subfolder, "cmake_modules", "yacma", "YACMACompilerLinkerSettings.cmake")
        tools.replace_in_file(yacma_cmake, "list(APPEND _YACMA_CXX_FLAGS_DEBUG \"-Werror\")", "")
        tools.replace_in_file(yacma_cmake, "_YACMA_CHECK_ENABLE_DEBUG_CXX_FLAG(/W4)", "")
        tools.replace_in_file(yacma_cmake, "_YACMA_CHECK_ENABLE_DEBUG_CXX_FLAG(/WX)", "")

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["PAGMO_BUILD_TESTS"] = False
        cmake.definitions["PAGMO_BUILD_BENCHMARKS"] = False
        cmake.definitions["PAGMO_BUILD_TUTORIALS"] = False
        cmake.definitions["PAGMO_WITH_EIGEN3"] = self.options.with_eigen
        cmake.definitions["PAGMO_WITH_NLOPT"] = self.options.with_nlopt
        cmake.definitions["PAGMO_WITH_IPOPT"] = self.options.with_ipopt
        cmake.definitions["PAGMO_ENABLE_IPO"] = False
        cmake.definitions["PAGMO_BUILD_STATIC_LIBRARY"] = not self.options.shared
        cmake.configure()
        return cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING.*", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "pagmo")
        self.cpp_info.set_property("cmake_target_name", "Pagmo::pagmo")
        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["_pagmo"].libs = ["pagmo"]
        self.cpp_info.components["_pagmo"].requires = ["boost::headers", "boost::serialization", "onetbb::onetbb"]
        if self.options.with_eigen:
            self.cpp_info.components["_pagmo"].requires.append("eigen::eigen")
        if self.options.with_nlopt:
            self.cpp_info.components["_pagmo"].requires.append("nlopt::nlopt")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_pagmo"].system_libs.append("pthread")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "pagmo"
        self.cpp_info.filenames["cmake_find_package_multi"] = "pagmo"
        self.cpp_info.names["cmake_find_package"] = "Pagmo"
        self.cpp_info.names["cmake_find_package_multi"] = "Pagmo"
        self.cpp_info.components["_pagmo"].names["cmake_find_package"] = "pagmo"
        self.cpp_info.components["_pagmo"].names["cmake_find_package_multi"] = "pagmo"
        self.cpp_info.components["_pagmo"].set_property("cmake_target_name", "Pagmo::pagmo")
