import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import valid_min_cppstd
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
        "import_std": [True, False],
        "std_format": [True, False],
        "string_view_ret": [True, False],
        "no_crtp": [True, False],
        "contracts": ["none", "gsl-lite", "ms-gsl"],
        "freestanding": [True, False],
    }
    default_options = {
        # "cxx_modules" default set in config_options()
        # "import_std" default set in config_options()
        # "std_format" default set in config_options()
        # "string_view_ret" default set in config_options()
        # "no_crtp" default set in config_options()
        "contracts": "gsl-lite",
        "freestanding": False,
    }
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
                    "msvc": "194",
                    "Visual Studio": "17",
                },
            },
            "std_format": {
                "min_cppstd": "20",
                "compiler": {
                    "gcc": "13",
                    "clang": "17",
                    "apple-clang": "",
                    "msvc": "194",
                    "Visual Studio": "17",
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
            "import_std": {
                "min_cppstd": "23",
                "compiler": {"gcc": "", "clang": "18", "apple-clang": "", "msvc": ""},
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
            "import_std": "import_std",
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
        # TODO mixing of `import std;` and regular header files includes does not work for now
        if self.options.import_std:
            self.options.contracts = "none"

    def configure(self):
        if self.options.cxx_modules:
            self.package_type = "static-library"
        else:
            self.package_type = "header-library"
        if self.options.freestanding:
            self.options.rm_safe("std_format")

    def requirements(self):
        if not self.options.freestanding:
            if self.options.contracts == "gsl-lite":
                self.requires("gsl-lite/0.41.0", transitive_headers=True)
            elif self.options.contracts == "ms-gsl":
                self.requires("ms-gsl/4.0.0", transitive_headers=True)
            if not self.options.std_format:
                self.requires("fmt/11.0.1", transitive_headers=True)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.30 <4]")

    def validate(self):
        self._check_feature_supported("mp-units", "minimum_support")
        for key, value in self._option_feature_map.items():
            if self.options.get_safe(key) == True:
                self._check_feature_supported(key, value)
        if self.options.freestanding and self.options.contracts != "none":
            raise ConanInvalidConfiguration(
                "'contracts' should be set to 'none' for a freestanding build"
            )
        # TODO mixing of `import std;` and regular header files includes does not work for now
        if self.options.import_std:
            if self.options.contracts != "none":
                raise ConanInvalidConfiguration(
                    "'contracts' should be set to 'none' to use `import std;`"
                )
            if not self.options.get_safe("std_format", default=True):
                raise ConanInvalidConfiguration(
                    "'std_format' should be enabled to use `import std;`"
                )

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        opt = self.options
        tc = CMakeToolchain(self)
        if opt.cxx_modules:
            tc.cache_variables["CMAKE_CXX_SCAN_FOR_MODULES"] = True
        if opt.import_std:
            tc.cache_variables["CMAKE_CXX_MODULE_STD"] = True
            # TODO current experimental support according to `Help/dev/experimental.rst`
            tc.cache_variables["CMAKE_EXPERIMENTAL_CXX_IMPORT_STD"] = (
                "0e5b6991-d74f-4b3d-a41c-cf096e0b2508"
            )

        # TODO remove the below when Conan will learn to handle C++ modules
        if opt.freestanding:
            tc.cache_variables["MP_UNITS_API_FREESTANDING"] = True
        else:
            tc.cache_variables["MP_UNITS_API_STD_FORMAT"] = opt.std_format
        tc.cache_variables["MP_UNITS_API_CONTRACTS"] = str(opt.contracts).upper()

        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder="src")
        if self.options.cxx_modules:
            cmake.build()

    def package_id(self):
        if self.package_type == "header-library":
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
        # TODO remove the below when Conan will learn to handle C++ modules
        if not self.options.cxx_modules:
            # We have to preserve those files for C++ modules build as Conan
            # can't generate such CMake targets for now
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        compiler = self.settings.compiler
        # TODO remove the branch when Conan will learn to handle C++ modules
        if self.options.cxx_modules:
            # CMakeDeps does not generate C++ modules definitions for now
            # Skip the Conan-generated files and use the mp-unitsConfig.cmake bundled with mp-units
            self.cpp_info.set_property("cmake_find_mode", "none")
            self.cpp_info.builddirs = ["."]
        else:
            # handle contracts
            if self.options.contracts == "none":
                self.cpp_info.components["core"].defines.append(
                    "MP_UNITS_API_CONTRACTS=0"
                )
            elif self.options.contracts == "gsl-lite":
                self.cpp_info.components["core"].requires.append("gsl-lite::gsl-lite")
                self.cpp_info.components["core"].defines.append(
                    "MP_UNITS_API_CONTRACTS=2"
                )
            elif self.options.contracts == "ms-gsl":
                self.cpp_info.components["core"].requires.append("ms-gsl::ms-gsl")
                self.cpp_info.components["core"].defines.append(
                    "MP_UNITS_API_CONTRACTS=3"
                )

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

            # handle import std
            if self.options.import_std:
                self.cpp_info.components["core"].defines.append("MP_UNITS_IMPORT_STD")
                if compiler == "clang" and Version(compiler.version) < 19:
                    self.cpp_info.components["core"].cxxflags.append(
                        "-Wno-deprecated-declarations"
                    )

            if compiler == "msvc":
                self.cpp_info.components["core"].cxxflags.append("/utf-8")

            self.cpp_info.components["systems"].requires = ["core"]
