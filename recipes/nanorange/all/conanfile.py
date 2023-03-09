from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, check_min_vs
from conan.tools.scm import Version
import os

required_conan_version = ">=1.52.0"

class NanorangeConan(ConanFile):
    name = "nanorange"
    description = "NanoRange is a C++17 implementation of the C++20 Ranges proposals (formerly the Ranges TS)."
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tcbrindle/NanoRange"
    topics = ("ranges", "C++17", "Ranges TS", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "deprecation_warnings": [True, False],
        "std_forward_declarations": [True, False],
    }
    default_options = {
        "deprecation_warnings": True,
        "std_forward_declarations": True,
    }
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        version = Version( self.settings.compiler.version )
        compiler = self.settings.compiler
        if self.settings.compiler.cppstd and \
           not any([str(self.settings.compiler.cppstd) == std for std in ["17", "20", "gnu17", "gnu20"]]):
            raise ConanInvalidConfiguration(f"{self.ref} requires at least c++17")
        elif is_msvc(self):
            check_min_vs("192")
            if not any([self.settings.compiler.cppstd == std for std in ["17", "20"]]):
                raise ConanInvalidConfiguration(f"{self.ref} requires at least c++17")
        else:
            if ( compiler == "gcc" and version < "7" ) or ( compiler == "clang" and version < "5" ):
                raise ConanInvalidConfiguration(f"{self.ref} requires a compiler that supports at least C++17")
            elif compiler == "apple-clang" and version < "10":
                    raise ConanInvalidConfiguration(f"{self.ref} requires a compiler that supports at least C++17")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE_1_0.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.hpp",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        if not self.options.deprecation_warnings:
            self.cpp_info.defines.append("NANORANGE_NO_DEPRECATION_WARNINGS")
        if not self.options.std_forward_declarations:
            self.cpp_info.defines.append("NANORANGE_NO_STD_FORWARD_DECLARATIONS")
