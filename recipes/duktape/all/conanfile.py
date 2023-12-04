import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get

required_conan_version = ">=1.53.0"


class DuktapeConan(ConanFile):
    name = "duktape"
    description = "Duktape is an embeddable Javascript engine, with a focus on portability and compact footprint."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://duktape.org"
    topics = ("javascript", "engine", "embeddable", "compact")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if self.settings.os == "Windows" and self.options.shared:
            # Duktape has a configure script with a number of options.
            # However, it requires python 2 and PyYAML package
            # which is quite an unusual combination to have.
            # The most crucial option is --dll which enables
            # DUK_F_DLL_BUILD and the following defines.
            tc.preprocessor_definitions["DUK_EXTERNAL_DECL"] = "extern __declspec(dllexport)"
            tc.preprocessor_definitions["DUK_EXTERNAL"] = "__declspec(dllexport)"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=self.export_sources_folder)
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["duktape"]
        if not self.options.shared and self.settings.os in ("Linux", "FreeBSD", "SunOS"):
            self.cpp_info.system_libs = ["m"]
