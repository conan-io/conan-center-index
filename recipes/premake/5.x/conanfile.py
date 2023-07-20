import glob
import os
import re

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import MSBuild, MSBuildToolchain, is_msvc
from conan.tools.microsoft.visual import msvc_version_to_vs_ide_version
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class PremakeConan(ConanFile):
    name = "premake"
    description = (
        "Describe your software project just once, "
        "using Premake's simple and easy to read syntax, "
        "and build it everywhere"
    )
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://premake.github.io"
    topics = ("build", "build-systems")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "lto": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "lto": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os != "Windows" or is_msvc(self):
            self.options.rm_safe("lto")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if hasattr(self, "settings_build") and cross_building(self, skip_x64_x86=True):
            raise ConanInvalidConfiguration("Cross-building not implemented")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _msvc_version(self):
        ide_version = Version(self.settings.compiler.version).major
        if ide_version > 100:
            ide_version = msvc_version_to_vs_ide_version(ide_version)
        return {
            "12": "2013",
            "14": "2015",
            "15": "2017",
            "16": "2019",
            "17": "2022",
        }[str(ide_version)]

    @property
    def _msvc_build_dir(self):
        return os.path.join(self.source_folder, "build", f"vs{self._msvc_version}")

    def _version_info(self, version):
        res = []
        for p in re.split("[.-]|(alpha|beta)", version):
            if p is None:
                continue
            try:
                res.append(int(p))
                continue
            except ValueError:
                res.append(p)
        return tuple(res)

    @property
    def _gmake_directory_name_prefix(self):
        if self._version_info(self.version) <= self._version_info("5.0.0-alpha14"):
            return "gmake"
        else:
            return "gmake2"

    @property
    def _gmake_platform(self):
        return {
            "FreeBSD": "bsd",
            "Windows": "windows",
            "Linux": "unix",
            "Macos": "macosx",
        }[str(self.settings.os)]

    @property
    def _gmake_build_dir(self):
        return os.path.join(self.source_folder, "build", f"{self._gmake_directory_name_prefix}.{self._gmake_platform}")

    @property
    def _gmake_config(self):
        build_type = "debug" if self.settings.build_type == "Debug" else "release"
        if self.settings.os == "Windows":
            arch = {
                "x86": "x86",
                "x86_64": "x64",
            }[str(self.settings.arch)]
            config = f"{build_type}_{arch}"
        else:
            config = build_type
        return config

    def generate(self):
        if is_msvc(self):
            tc = MSBuildToolchain(self)
            tc.generate()
        else:
            tc = AutotoolsToolchain(self)
            tc.make_args = ["verbose=1", "config={}".format(self._gmake_config)]
            tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        if self.options.get_safe("lto", None) == False:
            for fn in glob.glob(os.path.join(self._gmake_build_dir, "*.make")):
                replace_in_file(self, fn, "-flto", "", strict=False)

    def build(self):
        self._patch_sources()
        if is_msvc(self):
            with chdir(self, self._msvc_build_dir):
                msbuild = MSBuild(self)
                msbuild.build(sln="Premake5.sln")
        else:
            with chdir(self, self._gmake_build_dir):
                autotools = Autotools(self)
                autotools.make(target="Premake5")

    def package(self):
        copy(self, "LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            "*premake5*",
            dst=os.path.join(self.package_folder, "bin"),
            src=os.path.join(self.source_folder, "bin", "release"),
            keep_path=False,
        )

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bindir}")
        self.env_info.PATH.append(bindir)
