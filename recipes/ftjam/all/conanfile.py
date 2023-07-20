import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, load, replace_in_file, save
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import VCVars, is_msvc

required_conan_version = ">=1.47.0"


class FtjamConan(ConanFile):
    name = "ftjam"
    description = "Jam (ftjam) is a small open-source build tool that can be used as a replacement for Make."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.freetype.org/jam/"
    topics = ("build", "make")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration("ftjam doesn't build with Visual Studio yet")
        if hasattr(self, "settings_build") and cross_building(self):
            raise ConanInvalidConfiguration("ftjam can't be cross-built")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self):
            self.tool_requires("automake/1.16.5")
        if self.settings.os != "Windows":
            self.tool_requires("bison/3.8.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = AutotoolsToolchain(self)
        tc.generate()
        if is_msvc(self):
            vcvars = VCVars(self)
            vcvars.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "jamgram.c"), "\n#line", "\n//#line")

    def _jam_toolset(self, os, compiler):
        if is_msvc(self):
            return "VISUALC"
        if compiler == "intel-cc":
            return "INTELC"
        if os == "Windows":
            return "MINGW"
        return None

    def build(self):
        self._patch_sources()
        if self.settings.os == "Windows":
            with chdir(self, self.source_folder):
                # toolset name of the system building ftjam
                jam_toolset = self._jam_toolset(self.settings.os, self.settings.compiler)
                if is_msvc(self):
                    self.run(f"nmake -f builds/win32-visualc.mk JAM_TOOLSET={jam_toolset}")
                else:
                    os.environ["PATH"] += os.pathsep + os.getcwd()
                    autotools = Autotools(self)
                    autotools.make(args=[f"JAM_TOOLSET={jam_toolset}", "-f", "builds/win32-gcc.mk"])
        else:
            autotools = Autotools(self)
            autotools.configure(build_script_folder=os.path.join(self.source_folder, "builds", "unix"))
            with chdir(self, self.source_folder):
                autotools.make()

    def _extract_license(self):
        txt = load(self, os.path.join(self.source_folder, "jam.c"))
        license_txt = txt[: txt.find("*/") + 3]
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), license_txt)

    def package(self):
        self._extract_license()
        if self.settings.os == "Windows":
            if not is_msvc(self):
                copy(self, "*.exe",
                    src=os.path.join(self.source_folder, "bin.nt"),
                    dst=os.path.join(self.package_folder, "bin"))
        else:
            copy(self, "jam",
                 src=os.path.join(self.source_folder, "bin.unix"),
                 dst=os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []

        jam_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {jam_path}")
        self.env_info.PATH.append(jam_path)

        jam_bin = os.path.join(jam_path, "jam")
        if self.settings.os == "Windows":
            jam_bin += ".exe"
        self.output.info(f"Setting JAM environment variable: {jam_bin}")
        self.env_info.JAM = jam_bin

        # toolset of the system using ftjam
        jam_toolset = self._jam_toolset(self.settings.os, self.settings.compiler)
        if jam_toolset:
            self.output.info(f"Setting JAM_TOOLSET environment variable: {jam_toolset}")
            self.env_info.JAM_TOOLSET = jam_toolset
