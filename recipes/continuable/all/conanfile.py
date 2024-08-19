import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class ContinuableConan(ConanFile):
    name = "continuable"
    description = (
        "C++14 asynchronous allocation aware futures "
        "(supporting then, exception handling, coroutines and connections)"
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Naios/continuable"
    topics = ("asynchronous", "future", "coroutines", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "no_exceptions": [True, False],
        "custom_error_type": [True, False],
        "unhandled_exceptions": [True, False],
        "custom_final_callback": [True, False],
        "immediate_types": [True, False],
    }
    default_options = {
        "no_exceptions": False,
        "custom_error_type": False,
        "unhandled_exceptions": False,
        "custom_final_callback": False,
        "immediate_types": False,
    }
    options_description = {
        "no_exceptions": (
            "Exceptions are disabled and `std::error_condition` is used as error_type. "
            "See tutorial-chaining-continuables-fail for details."
        ),
        "custom_error_type": (
            "Exceptions are disabled and the type defined by `CONTINUABLE_WITH_CUSTOM_ERROR_TYPE` "
            "is used as error_type. See tutorial-chaining-continuables-fail for details."
        ),
        "unhandled_exceptions": (
            "Allows unhandled exceptions in asynchronous call hierarchies. "
            "See tutorial-chaining-continuables-fail for details."
        ),
        "custom_final_callback": (
            "Allows to customize the final callback which can be used to implement custom unhandled"
            " asynchronous exception handlers."
        ),
        "immediate_types": (
            "Don't decorate the used type erasure, "
            "which is done to keep type names minimal for better error messages in debug builds."
        ),
    }
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
            "clang": "3.4",
            "apple-clang": "10",
            "Visual Studio": "14",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("function2/4.2.4")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(
            self,
            pattern="LICENSE.txt",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        copy(
            self,
            pattern="*",
            dst=os.path.join(self.package_folder, "include", "continuable"),
            src=os.path.join(self.source_folder, "include", "continuable"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
        if self.options.no_exceptions:
            self.cpp_info.defines.append("CONTINUABLE_WITH_NO_EXCEPTIONS")
        if self.options.custom_error_type:
            self.cpp_info.defines.append("CONTINUABLE_WITH_CUSTOM_ERROR_TYPE")
        if self.options.unhandled_exceptions:
            self.cpp_info.defines.append("CONTINUABLE_WITH_UNHANDLED_EXCEPTIONS")
        if self.options.custom_final_callback:
            self.cpp_info.defines.append("CONTINUABLE_WITH_CUSTOM_FINAL_CALLBACK")
        if self.options.immediate_types:
            self.cpp_info.defines.append("CONTINUABLE_WITH_IMMEDIATE_TYPES")
