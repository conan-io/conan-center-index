import os
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake
from conan.tools.files import (get, copy, apply_conandata_patches,
                               export_conandata_patches)
from conan.errors import ConanInvalidConfiguration


required_conan_version = ">=2.4"


class IntelDfpConan(ConanFile):
    name = "intel-dfp"
    description = "Software decimal floating-point arithmetic implementation"
    license = "Intel"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = ("https://www.intel.com/content/www/us/en/developer/articles/"
                "tool/intel-decimal-floating-point-math-library.html")
    topics = ("decimal", "dfp", "ieee-754", "intel")

    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "call_by_reference": [True, False],
        "global_rounding": [True, False],
        "global_exception": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "call_by_reference": False,
        "global_rounding": False,
        "global_exception": False
    }

    implements = ["auto_shared_fpic"]
    languages = "C"

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "CMakeLists.txt", self.recipe_folder,
             dst=self.export_sources_folder)
    
    def validate(self):
        if self.settings.os == "Macos":
            raise ConanInvalidConfiguration("Recipe does not currently support Macos, PR welcomed")

    def source(self):
        get(self, **self.conan_data["sources"][self.version])
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CALL_BY_REF"] = self.options.call_by_reference
        tc.variables["GLOBAL_RND"] = self.options.global_rounding
        tc.variables["GLOBAL_EXC"] = self.options.global_exception
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        if not self.conf.get("tools.build:skip_test", default=False):
            cmake.build(target="readtest")
            cmake.ctest()

    def package(self):
        copy(self, "eula.txt",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["intel_dfp"]
        self.cpp_info.set_property("cmake_file_name", "intel_dfp")
        self.cpp_info.set_property("cmake_target_name", "intel_dfp::intel_dfp")

        defs = {"DECIMAL_CALL_BY_REFERENCE": self.options.call_by_reference,
                "DECIMAL_GLOBAL_ROUNDING": self.options.global_rounding,
                "DECIMAL_GLOBAL_EXCEPTION_FLAGS":
                    self.options.global_exception}
        self.cpp_info.defines = [f"{k}={int(bool(v))}"
                                 for k, v in defs.items()]

        if self.settings.compiler in ("clang", "gcc"):
            self.cpp_info.defines.append("_WCHAR_T=__WCHAR_TYPE__")
        elif self.settings.compiler == "msvc":
            self.cpp_info.defines.append("_WCHAR_T=_NATIVE_WCHAR_T_DEFINED")
