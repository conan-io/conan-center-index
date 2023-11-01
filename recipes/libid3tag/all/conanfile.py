import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import chdir, copy, get, replace_in_file, rm
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import MSBuild, MSBuildToolchain, is_msvc, MSBuildDeps

required_conan_version = ">=1.53.0"


class LibId3TagConan(ConanFile):
    name = "libid3tag"
    description = "ID3 tag manipulation library."
    license = "GPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.underbit.com/products/mad/"
    topics = ("mad", "id3", "MPEG", "audio", "decoder")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")

    def validate(self):
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration("libid3tag does not support shared library for MSVC")
        if self.settings.arch == "armv8" and self.options.shared:
            raise ConanInvalidConfiguration("shared library build is not supported for armv8")

    def build_requirements(self):
        if not is_msvc(self):
            self.tool_requires("gnu-config/cci.20210814")
            if self._settings_build.os == "Windows":
                self.win_bash = True
                if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                    self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if is_msvc(self):
            tc = MSBuildToolchain(self)
            tc.generate()
            deps = MSBuildDeps(self)
            deps.generate()
        else:
            tc = AutotoolsToolchain(self)
            tc.generate()
            deps = AutotoolsDeps(self)
            deps.generate()

    def build(self):
        if is_msvc(self):
            self._build_msvc()
        else:
            self._build_autotools()

    def _build_msvc(self):
        kwargs = {}
        with chdir(self, os.path.join(self.source_folder, "msvc++")):
            # cl : Command line error D8016: '/ZI' and '/Gy-' command-line options are incompatible
            replace_in_file(self, "libid3tag.dsp", "/ZI ", "")
            if self.settings.compiler == "clang":
                replace_in_file(self, "libid3tag.dsp", "CPP=cl.exe", "CPP=clang-cl.exe")
                replace_in_file(self, "libid3tag.dsp", "RSC=rc.exe", "RSC=llvm-rc.exe")
                kwargs["toolset"] = "ClangCl"
            if self.settings.arch == "x86_64":
                replace_in_file(self, "libid3tag.dsp", "Win32", "x64")
            self.run("devenv /Upgrade libid3tag.dsp")
            msbuild = MSBuild(self)
            msbuild.build(sln="libid3tag.vcxproj", **kwargs)

    def _build_autotools(self):
        for gnu_config in [
            self.conf.get("user.gnu-config:config_guess", check_type=str),
            self.conf.get("user.gnu-config:config_sub", check_type=str),
        ]:
            if gnu_config:
                copy(self, os.path.basename(gnu_config), src=os.path.dirname(gnu_config), dst=self.source_folder)
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def _install_autotools(self):
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.install()
        rm(self, "*.la", self.package_folder, recursive=True)

    def package(self):
        for license_file in ["COPYRIGHT", "COPYING", "CREDITS"]:
            copy(self, license_file,
                 dst=os.path.join(self.package_folder, "licenses"),
                 src=self.source_folder)
        if is_msvc(self):
            copy(self, "*.lib",
                 dst=os.path.join(self.package_folder, "lib"),
                 src=self.source_folder,
                 keep_path=False)
            copy(self, "id3tag.h",
                 dst=os.path.join(self.package_folder, "include"),
                 src=self.source_folder)
        else:
            self._install_autotools()

    def package_info(self):
        self.cpp_info.libs = ["libid3tag" if is_msvc(self) else "id3tag"]
