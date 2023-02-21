from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy, get, load, save, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
import os
import re

required_conan_version = ">=1.53.0"


class XorgGccmakedep(ConanFile):
    name = "xorg-gccmakedep"
    description = "script to create dependencies in makefiles using 'gcc -M'"
    topics = ("xorg", "gcc", "dependency", "obsolete")
    license = "MIT"
    homepage = "https://gitlab.freedesktop.org/xorg/util/gccmakedep"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def requirements(self):
        self.requires("xorg-macros/1.19.3")

    def build_requirements(self):
        self.tool_requires("pkgconf/1.7.4")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Windows is not supported by xorg-gccmakedep")

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def package_id(self):
        del self.info.settings.compiler

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        conf_ac_text = load(self, os.path.join(self.source_folder, "configure.ac"))
        topblock = re.match("((?:dnl[^\n]*\n)+)", conf_ac_text, flags=re.MULTILINE).group(1)
        license_text = re.subn(r"^dnl(|\s+([^\n]*))", r"\1", topblock, flags=re.MULTILINE)[0]
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), license_text)

        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libdirs = []

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
