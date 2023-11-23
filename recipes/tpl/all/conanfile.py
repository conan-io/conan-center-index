import os

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout

required_conan_version = ">=1.54.0"


class PackageConan(ConanFile):
    name = "tpl"
    description = "A small binary serialization library for C"
    license = "BSD-1-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://troydhanson.github.io/tpl/"
    topics = ("serialization",)

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
        copy(self, "CMakeLists.txt", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["tpl"]
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.defines.append("TPL_NOLIB")
