from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
import os

required_conan_version = ">=2.4"

class PlutoSVGConan(ConanFile):
    name = "plutosvg"
    description = "PlutoSVG is a compact and efficient SVG rendering library written in C"
    license = "MIT"
    topics = ("vector", "graphics", "svg")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/sammycage/plutosvg"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_freetype": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_freetype": True,
    }

    languages = "C"
    implements = ["auto_shared_fpic"]

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # Public symbols and used in headers
        self.requires("plutovg/1.0.0", transitive_headers=True, transitive_libs=True)
        if self.options.with_freetype:
            self.requires("freetype/2.13.2")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options["examples"] = "disabled"
        tc.project_options["tests"] = "disabled"
        tc.project_options["freetype"] = "enabled" if self.options.with_freetype else "disabled"
        tc.generate()
        tc = PkgConfigDeps(self)
        tc.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["plutosvg"]
        self.cpp_info.includedirs = [os.path.join("include", "plutosvg")]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["m"]
        if self.options.with_freetype:
            self.cpp_info.defines.append("PLUTOSVG_HAS_FREETYPE")
        if not self.options.shared:
            self.cpp_info.defines.append("PLUTOSVG_BUILD_STATIC")
