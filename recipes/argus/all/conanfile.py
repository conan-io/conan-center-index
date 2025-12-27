from conan import ConanFile
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=2.4"

class ArgusConan(ConanFile):
    name = "argus"
    description = "Argus is a cross-platform modern feature-rich command-line argument parser for C"
    topics = ("conan", "argus", "libargus", "command-line", "arguments", "parser", "cli", "argparse")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lucocozz/Argus"
    license = "MIT"
    language = "C"
    settings = "os", "arch", "compiler", "build_type"
    implements = ["auto_shared_fpic"]
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "regex": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "regex": False,
    }

    def validate(self):
        if self.settings.compiler == "msvc":
            raise ConanInvalidConfiguration("Argus does not support MSVC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.regex:
            self.requires("pcre2/10.42")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options["regex"] = bool(self.options.regex)
        tc.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "argus")
        self.cpp_info.set_property("cmake_target_name", "argus::argus")
        self.cpp_info.libs = ["argus"]
        if self.options.regex:
            self.cpp_info.defines.append("ARGUS_REGEX")
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("pkg_config_name", "argus")
