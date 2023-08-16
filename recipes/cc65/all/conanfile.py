import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, replace_in_file, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import MSBuild, is_msvc, msvs_toolset, MSBuildToolchain

required_conan_version = ">=1.47.0"


class Cc65Conan(ConanFile):
    name = "cc65"
    description = "A freeware C compiler for 6502 based systems"
    license = "Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://cc65.github.io/"
    topics = ("compiler", "cmos", "6502", "8bit")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")
        if is_msvc(self):
            if self.settings.arch not in ("x86", "x86_64"):
                raise ConanInvalidConfiguration("Invalid arch")
            if self.settings.arch == "x86_64":
                self.output.info("This recipe will build x86 instead of x86_64 (the binaries are compatible)")

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        if str(self.info.settings.compiler) in ["msvc", "Visual Studio"]:
            if self.info.settings.arch == "x86_64":
                self.info.settings.arch = "x86"
        del self.info.settings.compiler

    def build_requirements(self):
        if is_msvc(self):
            self.tool_requires("make/4.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if is_msvc(self):
            tc = MSBuildToolchain(self)
            tc.generate()
        tc = AutotoolsToolchain(self)
        tc.make_args += [
            f"PREFIX=/",
            f"datadir=/bin/share/cc65",
            f"samplesdir=/samples",
        ]
        if self.settings.os == "Windows":
            tc.make_args.append("EXE_SUFFIX=.exe")
        tc.generate()

    def _build_msvc(self):
        msbuild = MSBuild(self)
        msbuild.build(sln=os.path.join(self.source_folder, "src", "cc65.sln"))
        with chdir(self, os.path.join(self.source_folder, "libsrc")):
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def _build_autotools(self):
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.make()

    def _patch_sources(self):
        apply_conandata_patches(self)
        if is_msvc(self):
            with chdir(self, os.path.join(self.source_folder, "src")):
                for fn in os.listdir("."):
                    if not fn.endswith(".vcxproj"):
                        continue
                    replace_in_file(self, fn, "v141", msvs_toolset(self))
                    replace_in_file(self, fn,
                                    ("<WindowsTargetPlatformVersion>"
                                     "10.0.16299.0"
                                     "</WindowsTargetPlatformVersion>"),
                                    "")
        if self.settings.os == "Windows":
            # Add ".exe" suffix to calls from cl65 to other utilities
            for fn, var in [
                ("cc65", "CC65"),
                ("ca65", "CA65"),
                ("co65", "CO65"),
                ("ld65", "LD65"),
                ("grc65", "GRC"),
            ]:
                v = f"{var},".ljust(5)
                replace_in_file(self, os.path.join(self.source_folder, "src", "cl65", "main.c"),
                    f'CmdInit (&{v} CmdPath, "{fn}");',
                    f'CmdInit (&{v} CmdPath, "{fn}.exe");')

    def build(self):
        self._patch_sources()
        if is_msvc(self):
            self._build_msvc()
        else:
            self._build_autotools()

    def _package_msvc(self):
        copy(self, "*.exe",
             dst=os.path.join(self.package_folder, "bin"),
             src=os.path.join(self.source_folder, "bin"),
             keep_path=False)
        for dir in ("asminc", "cfg", "include", "lib", "target"):
            copy(self, "*",
                 dst=os.path.join(self.package_folder, "bin", "share", "cc65", dir),
                 src=os.path.join(self.source_folder, dir))

    def _package_autotools(self):
        with chdir(self, os.path.join(self.source_folder)):
            autotools = Autotools(self)
            autotools.install()
        rmdir(self, os.path.join(self.package_path, "samples"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        if is_msvc(self):
            self._package_msvc()
        else:
            self._package_autotools()

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []

        bin_ext = ".exe" if self.settings.os == "Windows" else ""
        bindir = os.path.join(self.package_folder, "bin")
        datadir = os.path.join(self.package_folder, "bin", "share", "cc65")

        self.output.info(f"Setting CC65_HOME environment variable: {datadir}")
        self.buildenv_info.define_path("CC65_HOME", datadir)

        cc65_cc = os.path.join(bindir, "cc65" + bin_ext)
        self.output.info(f"Setting CC65 environment variable: {cc65_cc}")
        self.buildenv_info.define_path("CC65", cc65_cc)

        cc65_as = os.path.join(bindir, "ca65" + bin_ext)
        self.output.info(f"Setting AS65 environment variable: {cc65_as}")
        self.buildenv_info.define_path("AS65", cc65_as)

        cc65_ld = os.path.join(bindir, "cl65" + bin_ext)
        self.output.info(f"Setting LD65 environment variable: {cc65_ld}")
        self.buildenv_info.define_path("LD65", cc65_ld)

        # TODO: Legacy, to be removed on Conan 2.0
        self.output.info(f"Appending PATH environment variable: {bindir}")
        self.env_info.PATH.append(bindir)
        self.env_info.CC65_HOME = datadir
        self.env_info.CC65 = cc65_cc
        self.env_info.AS65 = cc65_as
        self.env_info.LD65 = cc65_ld
