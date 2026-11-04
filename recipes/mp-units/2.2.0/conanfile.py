import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import default_cppstd, valid_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version

required_conan_version = ">=1.59.0"


def loose_lt_semver(v1, v2):
    lv1 = [int(v) for v in v1.split(".")]
    lv2 = [int(v) for v in v2.split(".")]
    min_length = min(len(lv1), len(lv2))
    return lv1[:min_length] < lv2[:min_length]


class MPUnitsConan(ConanFile):
    name = "mp-units"
    homepage = "https://github.com/mpusz/mp-units"
    description = "The quantities and units library for C++"
    topics = (
        "units",
        "dimensions",
        "quantities",
        "dimensional-analysis",
        "physical-quantities",
        "physical-units",
        "system-of-units",
        "system-of-quantities",
        "isq",
        "si",
        "library",
        "quantity-manipulation",
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "cxx_modules": [True, False],
        "std_format": [True, False],
        "string_view_ret": [True, False],
        "no_crtp": [True, False],
        "contracts": ["none", "gsl-lite", "ms-gsl"],
        "freestanding": [True, False],
    }
    default_options = {
        # "cxx_modules" default set in config_options()
        # "std_format" default set in config_options()
        # "string_view_ret" default set in config_options()
        # "no_crtp" default set in config_options()
        "contracts": "gsl-lite",
        "freestanding": False,
    }
    package_type = "header-library"
    no_copy_source = True

    @property
    def _feature_compatibility(self):
        return {
            "minimum_support": {
                "min_cppstd": "20",
                "compiler": {
                    "gcc": "12",
                    "clang": "16",
                    "apple-clang": "15",
                    "msvc": "",
                    "Visual Studio": "",
                },
            },
            "std_format": {
                "min_cppstd": "20",
                "compiler": {
                    "gcc": "13",
                    "clang": "17",
                    "apple-clang": "",
                    "msvc": "",
                    "Visual Studio": "",
                },
            },
            "cxx_modules": {
                "min_cppstd": "20",
                "compiler": {
                    "gcc": "",
                    "clang": "17",
                    "apple-clang": "",
                    "msvc": "",
                    "Visual Studio": "",
                },
            },
            "static_constexpr_vars_in_constexpr_func": {
                "min_cppstd": "23",
                "compiler": {
                    "gcc": "13",
                    "clang": "17",
                    "apple-clang": "",
                    "msvc": "",
                    "Visual Studio": "",
                },
            },
            "explicit_this": {
                "min_cppstd": "23",
                "compiler": {
                    "gcc": "14",
                    "clang": "18",
                    "apple-clang": "",
                    "msvc": "",
                    "Visual Studio": "",
                },
            },
        }

    @property
    def _option_feature_map(self):
        return {
            "std_format": "std_format",
            "cxx_modules": "cxx_modules",
            "string_view_ret": "static_constexpr_vars_in_constexpr_func",
            "no_crtp": "explicit_this",
        }

    def _set_default_option(self, name):
        compiler = self.settings.compiler
        feature_name = self._option_feature_map[name]
        feature = self._feature_compatibility[feature_name]
        min_version = feature["compiler"].get(str(compiler))
        setattr(
            self.options,
            name,
            bool(
                min_version
                and Version(compiler.version) >= min_version
                and valid_min_cppstd(self, feature["min_cppstd"])
            ),
        )

    def _check_feature_supported(self, name, feature_name=name):
        compiler = self.settings.compiler
        cppstd = compiler.get_safe("cppstd")
        feature = self._feature_compatibility[feature_name]

        # check C++ version
        if cppstd and not valid_min_cppstd(self, feature["min_cppstd"]):
            raise ConanInvalidConfiguration(
                f"'{name}' requires at least cppstd={feature['min_cppstd']} ({cppstd} in use)",
            )

        # check compiler version
        min_version = feature["compiler"].get(str(compiler))
        if min_version == None:
            # not tested compiler being used - use at your own risk
            return
        if min_version == "":
            raise ConanInvalidConfiguration(
                f"'{name}' is not yet supported by any known {compiler} version"
            )
        if loose_lt_semver(str(compiler.version), min_version):
            raise ConanInvalidConfiguration(
                f"'{name}' requires at least {compiler}-{min_version} ({compiler}-{compiler.version} in use)"
            )

    def config_options(self):
        for key in self._option_feature_map.keys():
            self._set_default_option(key)

    def configure(self):
        if self.options.freestanding:
            self.options.rm_safe("std_format")

    def requirements(self):
        if not self.options.freestanding:
            if self.options.contracts == "gsl-lite":
                self.requires("gsl-lite/0.41.0")
            elif self.options.contracts == "ms-gsl":
                self.requires("ms-gsl/4.0.0")
            if not self.options.std_format:
                self.requires("fmt/10.2.1")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.29 <4]")

    def validate(self):
        self._check_feature_supported("mp-units", "minimum_support")
        for key, value in self._option_feature_map.items():
            if self.options.get_safe(key) == True:
                self._check_feature_supported(key, value)
        if self.options.freestanding and self.options.contracts != "none":
            raise ConanInvalidConfiguration(
                "'contracts' should be set to 'none' for a freestanding build"
            )

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if self.options.cxx_modules:
            tc.cache_variables["CMAKE_CXX_SCAN_FOR_MODULES"] = True
            tc.cache_variables["MP_UNITS_BUILD_CXX_MODULES"] = self.options.cxx_modules
        if self.options.freestanding:
            tc.cache_variables["MP_UNITS_API_FREESTANDING"] = True
        else:
            tc.cache_variables["MP_UNITS_API_STD_FORMAT"] = self.options.std_format
        tc.cache_variables["MP_UNITS_API_STRING_VIEW_RET"] = (
            self.options.string_view_ret
        )
        tc.cache_variables["MP_UNITS_API_NO_CRTP"] = self.options.no_crtp
        tc.cache_variables["MP_UNITS_API_CONTRACTS"] = str(
            self.options.contracts
        ).upper()
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder="src")
        if self.options.cxx_modules:
            cmake.build()

    def package_id(self):
        self.info.clear()

    def package(self):
        copy(
            self,
            "LICENSE.md",
            self.source_folder,
            os.path.join(self.package_folder, "licenses"),
        )
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        compiler = self.settings.compiler

        # handle contracts
        if self.options.contracts == "none":
            self.cpp_info.components["core"].defines.append("MP_UNITS_API_CONTRACTS=0")
        elif self.options.contracts == "gsl-lite":
            self.cpp_info.components["core"].requires.append("gsl-lite::gsl-lite")
            self.cpp_info.components["core"].defines.append("MP_UNITS_API_CONTRACTS=2")
        elif self.options.contracts == "ms-gsl":
            self.cpp_info.components["core"].requires.append("ms-gsl::ms-gsl")
            self.cpp_info.components["core"].defines.append("MP_UNITS_API_CONTRACTS=3")

        # handle API options
        self.cpp_info.components["core"].defines.append(
            "MP_UNITS_API_STRING_VIEW_RET="
            + str(int(self.options.string_view_ret == True))
        )
        self.cpp_info.components["core"].defines.append(
            "MP_UNITS_API_NO_CRTP=" + str(int(self.options.no_crtp == True))
        )
        self.cpp_info.components["core"].defines.append(
            "MP_UNITS_API_STD_FORMAT=" + str(int(self.options.std_format == True))
        )
        if not self.options.std_format:
            self.cpp_info.components["core"].requires.append("fmt::fmt")

        # handle hosted configuration
        if not self.options.freestanding:
            self.cpp_info.components["core"].defines.append("MP_UNITS_HOSTED=1")

        if compiler == "msvc":
            self.cpp_info.components["core"].cxxflags = ["/utf-8"]

        self.cpp_info.components["systems"].requires = ["core"]
