import os

from conan import ConanFile
from conan.tools.env import VirtualBuildEnv
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools import files
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.51.0"


class PixmanConan(ConanFile):
    name = "pixman"
    description = "Pixman is a low-level software library for pixel manipulation"
    topics = ("pixman", "graphics", "compositing", "rasterization")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://cairographics.org/"
    license = ("LGPL-2.1-only", "MPL-1.1")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _autotools = None

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _includedir(self):
        return os.path.join("include", "pixman-1")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        self.tool_requires("meson/0.63.2")

    def layout(self):
        basic_layout(self, src_folder="source")

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options.update({
            "libpng": "disabled",
            "gtk": "disabled"
        })
        tc.generate()

        env = VirtualBuildEnv(self)
        env.generate()

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("pixman can only be built as a static library on Windows")

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _patch_sources(self):
        files.apply_conandata_patches(self)
        files.replace_in_file(self, os.path.join(self.source_folder, "meson.build"), "subdir('test')", "")
        files.replace_in_file(self, os.path.join(self.source_folder, "meson.build"), "subdir('demos')", "")

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        files.copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        files.rm(self, "*.la", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = files.collect_libs(self)
        self.cpp_info.includedirs.append(self._includedir)
        self.cpp_info.set_property("pkg_config_name", "pixman-1")
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["pthread", "m"]
