import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, load, replace_in_file, save
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, NMakeToolchain

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
            # Build fails with
            # NMAKE : fatal error U1077: 'jam0 JamFile' : return code '0xc0000005'
            raise ConanInvalidConfiguration("ftjam doesn't build with Visual Studio yet")

    def validate_build(self):    
        if hasattr(self, "settings_build") and cross_building(self):
            raise ConanInvalidConfiguration("ftjam can't be cross-built")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.tool_requires("winflexbison/2.5.24")
        else:
            self.tool_requires("bison/3.8.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if is_msvc(self):
            tc = NMakeToolchain(self)
            tc.generate()
        else:
            tc = AutotoolsToolchain(self)
            tc.generate()

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
        with chdir(self, self.source_folder):
            if self.settings.os == "Windows":
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
        jam_bin = os.path.join(jam_path, "jam")
        if self.settings.os == "Windows":
            jam_bin += ".exe"
        self.buildenv.define_path("JAM", jam_bin)
        self.runenv.define_path("JAM", jam_bin)

        # toolset of the system using ftjam
        jam_toolset = self._jam_toolset(self.settings.os, self.settings.compiler)
        if jam_toolset:
            self.buildenv.define("JAM_TOOLSET", jam_toolset)
            self.runenv.define("JAM_TOOLSET", jam_toolset)

        # TODO: Legacy, to be removed on Conan 2.0
        self.env_info.PATH.append(jam_path)
        self.env_info.JAM = jam_bin
        if jam_toolset:
            self.env_info.JAM_TOOLSET = jam_toolset
