from conan import ConanFile
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
import os

class LibcargsConan(ConanFile):
    name = "libcargs"
    version = "1.0.1"
    description = "Modern C library for command-line argument parsing with an elegant, macro-based API"
    topics = ("conan", "cargs", "libcargs", "command-line", "arguments", "parser", "cli", "argparse")
    url = "https://github.com/lucocozz/cargs"
    homepage = "https://github.com/lucocozz/cargs"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "disable_regex": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "disable_regex": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # Pure C library
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if not self.options.disable_regex:
            self.requires("pcre2/10.42")

    def source(self):
        # Use the version from the metadata, requires a git tag usually
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options["buildtype"] = str(self.settings.build_type).lower()
        tc.project_options["disable_regex"] = self.options.disable_regex
        tc.project_options["tests"] = False
        tc.project_options["examples"] = False
        tc.project_options["benchmarks"] = False
        # Conan uses 'relwithdebinfo', Meson uses 'debugoptimized'
        if self.settings.build_type == "RelWithDebInfo":
             tc.project_options["buildtype"] = "debugoptimized"
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
        self.cpp_info.set_property("cmake_file_name", "libcargs")
        self.cpp_info.set_property("cmake_target_name", "libcargs::libcargs")
        
        self.cpp_info.libs = ["cargs"]
        
        if self.options.disable_regex:
            self.cpp_info.defines.append("CARGS_NO_REGEX")
        
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
        
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("pkg_config_name", "cargs")
