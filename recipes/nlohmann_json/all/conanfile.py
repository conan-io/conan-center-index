from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class NlohmannJsonConan(ConanFile):
    name = "nlohmann_json"
    homepage = "https://github.com/nlohmann/json"
    description = "JSON for Modern C++ parser and generator."
    topics = "json", "header-only"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    options = {
        "enable_exceptions": [True, False],
        "enable_implicit_conversions": [True, False],
        "enable_enum_serialization": [True, False],
        "enable_diagnostics": [True, False],
        "enable_diagnostic_positions": [True, False],
        "enable_global_udls": [True, False],
        "enable_io": [True, False],
        "enable_legacy_discarded_value_comparison": [True, False],
    }
    default_options = {
        "enable_exceptions": True,
        "enable_implicit_conversions": True,
        "enable_enum_serialization": True,
        "enable_diagnostics": False,
        "enable_diagnostic_positions": False,
        "enable_global_udls": True,
        "enable_io": True,
        "enable_legacy_discarded_value_comparison": False,
    }

    @property
    def _minimum_cpp_standard(self):
        return 11

    def config_options(self):
        if Version(self.version) < "3.9.0":
            self.options.rm_safe("enable_implicit_conversions")
        if Version(self.version) < "3.10.0":
            self.options.rm_safe("enable_diagnostics")
            self.options.rm_safe("enable_io")
        if Version(self.version) < "3.11.0":
            self.options.rm_safe("enable_enum_serialization")
            self.options.rm_safe("enable_global_udls")
            self.options.rm_safe("enable_legacy_discarded_value_comparison")
        if Version(self.version) < "3.12.0":
            self.options.rm_safe("enable_diagnostic_positions")

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._minimum_cpp_standard)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        pass

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE*", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "nlohmann_json")
        self.cpp_info.set_property("cmake_target_name", "nlohmann_json::nlohmann_json")
        self.cpp_info.set_property("pkg_config_name", "nlohmann_json")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # Options unsupported by this version are removed in config_options() and define nothing.
        # The 0/1 macros are always defined, so behavior never depends on the header defaults.
        for option, enabled, disabled in [
            ("enable_exceptions", None, "JSON_NOEXCEPTION"),
            ("enable_io", None, "JSON_NO_IO"),
            ("enable_implicit_conversions", "JSON_USE_IMPLICIT_CONVERSIONS=1", "JSON_USE_IMPLICIT_CONVERSIONS=0"),
            ("enable_enum_serialization", "JSON_DISABLE_ENUM_SERIALIZATION=0", "JSON_DISABLE_ENUM_SERIALIZATION=1"),
            ("enable_diagnostics", "JSON_DIAGNOSTICS=1", "JSON_DIAGNOSTICS=0"),
            ("enable_diagnostic_positions", "JSON_DIAGNOSTIC_POSITIONS=1", "JSON_DIAGNOSTIC_POSITIONS=0"),
            ("enable_global_udls", "JSON_USE_GLOBAL_UDLS=1", "JSON_USE_GLOBAL_UDLS=0"),
            ("enable_legacy_discarded_value_comparison", "JSON_USE_LEGACY_DISCARDED_VALUE_COMPARISON=1", "JSON_USE_LEGACY_DISCARDED_VALUE_COMPARISON=0"),
        ]:
            value = self.options.get_safe(option)
            if value is None:
                continue
            define = enabled if value else disabled
            if define:
                self.cpp_info.defines.append(define)
