from conan import ConanFile
from conan.tools.files import get, replace_in_file, copy
from conan.tools.build import cross_building
from conan.tools.layout import basic_layout
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.microsoft import VCVars, is_msvc
from conan.tools.gnu import AutotoolsToolchain, Autotools
from conan.tools.apple import is_apple_os
import os

required_conan_version = ">=1.51.3"

class GenieConan(ConanFile):
    name = "genie"
    license = "BSD-3-clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/bkaradzic/GENie"
    description = "Project generator tool"
    topics = ("genie", "project", "generator", "build", "build-systems")
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _settings_build(self):
        # TODO: Remove for Conan v2
        return getattr(self, "settings_build", self.settings)

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler

    def validate(self):
        if hasattr(self, "settings_build") and cross_building(self):
            raise ConanInvalidConfiguration("Cross building is not yet supported. Contributions are welcome")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", default=False, check_type=str):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self):
            self.tool_requires("cccl/1.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    @property
    def _os(self):
        if is_apple_os(self):
            return "darwin"
        return {
            "Windows": "windows",
            "Linux": "linux",
            "FreeBSD": "bsd",
        }[str(self.settings.os)]

    def _patch_compiler(self, cc, cxx):
        replace_in_file(self, os.path.join(self.source_folder, "build", f"gmake.{self._os}", "genie.make"), "CC  = gcc", f"CC  = {cc}")
        replace_in_file(self, os.path.join(self.source_folder, "build", f"gmake.{self._os}", "genie.make"), "CXX = g++", f"CXX = {cxx}")

    @property
    def _genie_config(self):
        return "debug" if self.settings.build_type == "Debug" else "release"

    def generate(self):
        vbe = VirtualBuildEnv(self)
        vbe.generate()
        if is_msvc(self):
            ms = VCVars(self)
            ms.generate()
        else:
            tc = AutotoolsToolchain(self)
            tc.generate()

    def build(self):
        if is_msvc(self):
            self._patch_compiler("cccl", "cccl")
            self.run("make", cwd=self.source_folder)
        else:
            cc = os.environ.get("CC")
            cxx = os.environ.get("CXX")
            if is_apple_os(self):
                if not cc:
                    cc = "clang"
                if not cxx:
                    cxx = "clang"
            else:
                if not cc:
                    cc = "clang" if self.settings.compiler == "clang" else "gcc"
                if not cxx:
                    cxx = "clang++" if self.settings.compiler == "clang" else "g++"
            self._patch_compiler(cc, cxx)

            autotools = Autotools(self)
            autotools.make(args=[f"-C {self.source_folder}", f"OS={self._os}", f"config={self._genie_config}"])

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        bin_ext = ".exe" if self.settings.os == "Windows" else ""
        copy(self, pattern=f"genie{bin_ext}", src=os.path.join(self.source_folder, "bin", self._os), dst=os.path.join(self.package_folder, "bin"))
        if self.settings.build_type == "Debug":
            copy(self, pattern="*.lua", src=os.path.join(self.source_folder, "src"), dst=os.path.join(self.package_folder,"res"))

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []
        
        #TODO remove for conan v2
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bindir}")
        self.env_info.PATH.append(bindir)

        if self.settings.build_type == "Debug":
            resdir = os.path.join(self.package_folder, "res")
            self.output.info(f"Appending PREMAKE_PATH environment variable: {resdir}")
            self.env_info.PREMAKE_PATH.append(resdir)
