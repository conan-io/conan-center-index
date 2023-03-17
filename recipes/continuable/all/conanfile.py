import os
import functools

from conan import ConanFile
from conan.tools.scm import Version
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy, rename
from conan.errors import ConanInvalidConfiguration


required_conan_version = ">=1.28.0"


class ContinuableConan(ConanFile):
    name = "continuable"
    description = "C++14 asynchronous allocation aware futures (supporting then, exception handling, coroutines and connections)"
    topics = "asynchronous", "future", "coroutines", "header-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Naios/continuable"
    license = "MIT"
    settings = "os", "compiler"
    no_copy_source = True
    requires = (
        "function2/4.1.0",
    )
    options = {
        # Exceptions are disabled and `std::error_condition` is used as error_type. See tutorial-chaining-continuables-fail for details.
        "no_exceptions": [True, False],
        # Exceptions are disabled and the type defined by `CONTINUABLE_WITH_CUSTOM_ERROR_TYPE` is used as error_type.
        # See tutorial-chaining-continuables-fail for details.
        "custom_error_type": [True, False],
        # Allows unhandled exceptions in asynchronous call hierarchies. See tutorial-chaining-continuables-fail for details.
        "unhandled_exceptions": [True, False],
        # Allows to customize the final callback which can be used to implement custom unhandled asynchronous exception handlers.
        "custom_final_callback": [True, False],
        # Don"t decorate the used type erasure, which is done to keep type names minimal for better error messages in debug builds.
        "immediate_types": [True, False],
    }
    default_options = {
        "no_exceptions": False,
        "custom_error_type": False,
        "unhandled_exceptions": False,
        "custom_final_callback": False,
        "immediate_types": False
    }

    def validate(self):
        minimal_cpp_standard = "14"
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, minimal_cpp_standard)
        minimal_version = {
            "gcc": "5",
            "clang": "3.4",
            "apple-clang": "10",
            "Visual Studio": "14"
        }
        compiler = str(self.settings.compiler)
        if compiler not in minimal_version:
            self.output.warning(
                "%s recipe lacks information about the %s compiler standard version support" % (self.name, compiler))
            self.output.warning(
                "%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))
            return
        version = Version(self.settings.compiler.version)
        if version < minimal_version[compiler]:
            raise ConanInvalidConfiguration("%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        src = functools.partial(os.path.join, self.source_folder)
        dst = functools.partial(os.path.join, self.package_folder)
        hdrs = ("include", "continuable")
        copy(self, pattern="LICENSE.txt", dst=dst("licenses"), src=src(""))
        copy(self, pattern="*", dst=dst(*hdrs), src=src(*hdrs))

    def package_info(self):
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

    def package_id(self):
        self.info.clear()
