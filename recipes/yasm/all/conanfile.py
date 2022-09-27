from conan import ConanFile
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.build import cross_building
from conan.tools.files import chdir, copy, download, get, mkdir, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
from conan.tools.layout import basic_layout, vs_layout
from conan.tools.microsoft import is_msvc, MSBuildDeps, MSBuildToolchain, MSBuild, VCVars

import os


required_conan_version = ">=1.52.0"

class YASMConan(ConanFile):
    name = "yasm"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/yasm/yasm"
    description = "Yasm is a complete rewrite of the NASM assembler under the 'new' BSD License"
    topics = ("yasm", "installer", "assembler")
    license = "BSD-2-Clause"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def layout(self):
        if is_msvc(self):
            vs_layout(self)
        else:
            basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        get(self, **self.conan_data["sources"][self.version][0],
                  destination=self.source_folder, strip_root=True)
        download(self, **self.conan_data["sources"][self.version][1],
                       filename=os.path.join(self.source_folder, "YASM-VERSION-GEN.bat"))

    @property
    def _msvc_subfolder(self):
        return os.path.join(self.source_folder, "Mkfiles", "vc10")

    def _generate_vs(self):
        with chdir(self, self._msvc_subfolder):
            tc = MSBuildToolchain(self)
            tc.generate()
            tc = MSBuildDeps(self)
            tc.generate()
            tc = VCVars(self)
            tc.generate()

    def _generate_autotools(self):
        tc = AutotoolsToolchain(self)
        enable_debug = "yes" if self.settings.build_type == "Debug" else "no"
        tc.configure_args.extend([
            f"--enable-debug={enable_debug}",
            "--disable-rpath",
            "--disable-nls",
        ])
        tc.generate()
        tc = PkgConfigDeps(self)
        tc.generate()
        tc = AutotoolsDeps(self)
        tc.generate()
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

    def generate(self):
        if is_msvc(self):
            self._generate_vs()
        else:
            self._generate_autotools()

    def build(self):
        if is_msvc(self):
            msbuild = MSBuild(self)
            msbuild.build_type = "Debug" if self.settings.build_type == "Debug" else "Release"
            msbuild.platform = "Win32" if self.settings.arch == "x86" else msbuild.platform
            msbuild.build(sln="project_2017.sln")
        else:
            autotools = Autotools(self)
            autotools.autoreconf()
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, pattern="BSD.txt", dst="licenses", src=self.source_folder)
        copy(self, pattern="COPYING", dst="licenses", src=self.source_folder)
        if is_msvc(self):
            arch = {
                "x86": "Win32",
                "x86_64": "x64",
            }[str(self.settings.arch)]
            mkdir(self, os.path.join(self.package_folder, "bin"))
            build_type = "Debug" if self.settings.build_type == "Debug" else "Release"
            copy(self, pattern="yasm.exe",
                    src=os.path.join(self._msvc_subfolder, arch, build_type),
                    dst=os.path.join(self.package_folder, "bin"))
            copy(self, pattern="yasm.exe*", src=self.source_folder, dst="bin", keep_path=False)
        else:
            autotools = Autotools(self)
            autotools.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.PATH.append(bin_path)
