from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class SnitchConan(ConanFile):
    name = "snitch"
    description = "Lightweight C++20 testing framework"
    topics = ("snitch", "unit-test")
    license = "BSL-1.0"
    homepage = "https://github.com/snitch-org/snitch"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "header_only": [True, False],
        "with_main": [True, False],
        "with_exceptions": [True, False],
        "with_timings": [True, False],
        "with_shorthand_macros": [True, False],
        "with_default_color": [True, False],
        "with_success_decompose": [True, False],
        "with_reporters": [None, "ANY"],
        "max_test_cases": ["ANY"], # integer
        "max_nested_sections": ["ANY"], # integer
        "max_expr_length": ["ANY"], # integer
        "max_message_length": ["ANY"], # integer
        "max_test_name_length": ["ANY"], # integer
        "max_tag_length": ["ANY"], # integer
        "max_captures": ["ANY"], # integer
        "max_capture_length": ["ANY"], # integer
        "max_unique_tags": ["ANY"], # integer
        "max_command_line_args": ["ANY"], # integer
        "max_registered_reporters": ["ANY"], # integer
        "max_path_length": ["ANY"] # integer
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "header_only": False,
        "with_main": True,
        "with_exceptions": True,
        "with_timings": True,
        "with_shorthand_macros": True,
        "with_default_color": True,
        "with_success_decompose": False,
        "with_reporters": "all",
        "max_test_cases": 5000,
        "max_nested_sections": 8,
        "max_expr_length": 1024,
        "max_message_length": 1024,
        "max_test_name_length": 1024,
        "max_tag_length": 256,
        "max_captures": 8,
        "max_capture_length": 256,
        "max_unique_tags": 1024,
        "max_command_line_args": 1024,
        "max_registered_reporters": 8,
        "max_path_length": 1024
    }

    @property
    def _min_cppstd(self):
        return "20"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "10",
            "Visual Studio": "17",
            "msvc": "193",
            "clang": "10",
            "apple-clang": "10",
        }

    @property
    def _available_reporters(self):
        return ["xml", "teamcity"]

    def config_options(self):
        if self.settings.os == "Windows":
            # Position-independent code is irrelevant on Windows; this is UNIX only.
            del self.options.fPIC

    def configure(self):
        if self.options.shared or self.options.header_only:
            # Position-independent code is only relevant for static builds.
            self.options.rm_safe("fPIC")

        if self.options.header_only:
            # Shared vs static is irrelevant in header-only mode, so should be removed.
            del self.options.shared

    def package_id(self):
        if self.info.options.header_only:
            # In header-only mode, the OS, architecture, and compiler don't matter.
            # However do not clear options; they influence the content of the header file.
            self.info.settings.clear()

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler doesn't support")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)

        # Basic configuration
        tc.cache_variables["SNITCH_DO_TEST"] = False
        tc.cache_variables["SNITCH_UNITY_BUILD"] = True

        # Library format
        tc.cache_variables["SNITCH_HEADER_ONLY"] = self.options.header_only

        # Feature toggles
        tc.cache_variables["SNITCH_DEFINE_MAIN"] = self.options.with_main
        tc.cache_variables["SNITCH_WITH_EXCEPTIONS"] = self.options.with_exceptions
        tc.cache_variables["SNITCH_WITH_TIMINGS"] = self.options.with_timings
        tc.cache_variables["SNITCH_WITH_SHORTHAND_MACROS"] = self.options.with_shorthand_macros
        tc.cache_variables["SNITCH_DEFAULT_WITH_COLOR"] = self.options.with_default_color
        tc.cache_variables["SNITCH_DECOMPOSE_SUCCESSFUL_ASSERTIONS"] = self.options.with_success_decompose

        for reporter in str(self.options.with_reporters).split(','):
            reporter = reporter.strip()
            if reporter == "all":
                tc.cache_variables["SNITCH_WITH_ALL_REPORTERS"] = True
                break
            elif reporter in self._available_reporters:
                tc.cache_variables["SNITCH_WITH_ALL_REPORTERS"] = False
                tc.cache_variables[f"SNITCH_WITH_{reporter.upper()}_REPORTER"] = True
            else:
                raise ConanInvalidConfiguration(f"unknown reporter '{reporter}'")

        # Configurable limits
        tc.cache_variables["SNITCH_MAX_TEST_CASES"] = str(self.options.max_test_cases)
        tc.cache_variables["SNITCH_MAX_NESTED_SECTIONS"] = str(self.options.max_nested_sections)
        tc.cache_variables["SNITCH_MAX_EXPR_LENGTH"] = str(self.options.max_expr_length)
        tc.cache_variables["SNITCH_MAX_MESSAGE_LENGTH"] = str(self.options.max_message_length)
        tc.cache_variables["SNITCH_MAX_TEST_NAME_LENGTH"] = str(self.options.max_test_name_length)
        tc.cache_variables["SNITCH_MAX_TAG_LENGTH"] = str(self.options.max_tag_length)
        tc.cache_variables["SNITCH_MAX_CAPTURES"] = str(self.options.max_captures)
        tc.cache_variables["SNITCH_MAX_CAPTURE_LENGTH"] = str(self.options.max_capture_length)
        tc.cache_variables["SNITCH_MAX_UNIQUE_TAGS"] = str(self.options.max_unique_tags)
        tc.cache_variables["SNITCH_MAX_COMMAND_LINE_ARGS"] = str(self.options.max_command_line_args)
        tc.cache_variables["SNITCH_MAX_REGISTERED_REPORTERS"] = str(self.options.max_registered_reporters)
        tc.cache_variables["SNITCH_MAX_PATH_LENGTH"] = str(self.options.max_path_length)

        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        target = "snitch-header-only" if self.options.header_only else "snitch"

        self.cpp_info.set_property("cmake_file_name", "snitch")
        self.cpp_info.set_property("cmake_target_name", f"snitch::{target}")
        self.cpp_info.set_property("pkg_config_name", "snitch")

        if self.options.header_only:
            self.cpp_info.components["_snitch"].bindirs = []
            self.cpp_info.components["_snitch"].libdirs = []
        else:
            self.cpp_info.components["_snitch"].libs = ['snitch']
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.append("m")

        # TODO: to remove in conan v2 once legacy generators removed
        self.cpp_info.names["cmake_find_package"] = "snitch"
        self.cpp_info.names["cmake_find_package_multi"] = "snitch"
        self.cpp_info.names["pkg_config"] = "snitch"
        self.cpp_info.components["_snitch"].names["cmake_find_package"] = target
        self.cpp_info.components["_snitch"].names["cmake_find_package_multi"] = target
        self.cpp_info.components["_snitch"].set_property("cmake_target_name", f"snitch::{target}")
