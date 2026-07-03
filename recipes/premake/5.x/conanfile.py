import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.files import chdir, copy, get
from conan.tools.gnu import AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import MSBuild, MSBuildToolchain, VCVars, is_msvc
from conan.tools.scm import Version

required_conan_version = ">=2.1"


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

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler

    def requirements(self):
        if self.settings.os != "Windows":
            self.requires("util-linux-libuuid/2.39.2")

    def validate(self):
        if cross_building(self, skip_x64_x86=True):
            raise ConanInvalidConfiguration("Cross-building not implemented")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _ide_version(self):
        return {"195": "2026",
                "194": "2022",
                "193": "2022",
                "192": "2019",
                "191": "2017",
                "190": "2015",
                "180": "2013"}.get(str(self.settings.compiler.version))

    @property
    def _msvc_sln(self):
        # VS2026 switched to the newer .slnx solution format
        ext = "sln" if Version(self.settings.compiler.version) < 195 else "slnx"
        return f"Premake5.{ext}"

    @property
    def _bootstrap_arch(self):
        return {
            "x86": "x86",
            "x86_64": "x86_64",
            "armv8": "AARCH64",
        }.get(str(self.settings.arch), str(self.settings.arch))

    @property
    def _bootstrap_config(self):
        return "debug" if self.settings.build_type == "Debug" else "release"

    @property
    def _bootstrap_dir(self):
        return os.path.join(self.source_folder, "build", "bootstrap")

    def generate(self):
        if is_msvc(self):
            VCVars(self).generate()
            tc = MSBuildToolchain(self)
            tc.generate()
        else:
            tc = AutotoolsToolchain(self)
            tc.generate()
            deps = AutotoolsDeps(self)
            deps.generate()

    def _generate_build_files(self):
        """Bootstrap premake using its own Bootstrap.mak/Bootstrap.bat, following
        https://premake.github.io/docs/Building-Premake#using-the-git-code-repository
        """
        with chdir(self, self.source_folder):
            if is_msvc(self):
                # Stops before the devenv build so we can build with Conan's own MSBuild below.
                self.run(
                    f"nmake -f Bootstrap.mak windows-base "
                    f"MSDEV=vs{self._ide_version} PLATFORM={self._bootstrap_arch}"
                )
            else:
                # These targets bootstrap a minimal premake, embed the Lua scripts, generate the
                # gmake project files, and build the final premake5 binary, all in one go.
                make, target = {
                    "Linux": ("make", "linux"),
                    "Macos": ("make", "osx"),
                    "FreeBSD": ("gmake", "bsd"),
                    "Windows": ("mingw32-make", "mingw"),
                }[str(self.settings.os)]
                self.run(
                    f"{make} -f Bootstrap.mak {target} "
                    f"PLATFORM={self._bootstrap_arch} CONFIG={self._bootstrap_config}"
                )

    def build(self):
        self._generate_build_files()
        if is_msvc(self):
            with chdir(self, self._bootstrap_dir):
                msbuild = MSBuild(self)
                msbuild.build(sln=self._msvc_sln)

    def package(self):
        copy(self, "LICENSE.txt",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        suffix = ".exe" if self.settings.os == "Windows" else ""
        copy(self, f"*/premake5{suffix}",
             dst=os.path.join(self.package_folder, "bin"),
             src=os.path.join(self.source_folder, "bin"),
             keep_path=False)

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []
