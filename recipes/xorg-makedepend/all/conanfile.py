from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, load, rmdir, save
from conan.tools.gnu import Autotools, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
import os
import re

required_conan_version = ">=1.53.0"


class XorgMakedepend(ConanFile):
    name = "xorg-makedepend"
    description = "Utility to parse C source files to make dependency lists for Makefiles"
    topics = ("xorg", "dependency", "obsolete")
    license = "MIT"
    homepage = "https://gitlab.freedesktop.org/xorg/util/makedepend"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def requirements(self):
        self.requires("xorg-macros/1.19.3")
        self.requires("xorg-proto/2022.2")

    def build_requirements(self):
        self.build_requires("pkgconf/1.9.3")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Windows is not supported by xorg-makedepend")

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

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

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
        def_h_text = load(self, os.path.join(self.source_folder, "def.h"))
        license_text = next(re.finditer(r"/\*([^*]+)\*/", def_h_text)).group(1)
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), license_text)

        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
