import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import chdir, copy, get
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import MSBuild, MSBuildToolchain, is_msvc

required_conan_version = ">=1.53.0"


class NativefiledialogConan(ConanFile):
    name = "nativefiledialog"
    description = "A tiny, neat C library that portably invokes native file open and save dialogs."
    license = "Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mlabbe/nativefiledialog"
    topics = ("dialog", "gui")

    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("gtk/3.24.37")

    def validate(self):
        if self.settings.arch not in ["x86", "x86_64"]:
            raise ConanInvalidConfiguration(f"{self.settings.arch} architecture is not supported")

    def build_requirements(self):
        self.tool_requires("premake/5.0.0-beta2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _vs_ide_year(self):
        compiler_version = str(self.settings.compiler.version)
        if str(self.settings.compiler) == "Visual Studio":
            return {
                "12": "2013",
                "14": "2015",
                "15": "2017",
                "16": "2019",
                "17": "2022",
            }[compiler_version]
        else:
            return {
                "180": "2013",
                "190": "2015",
                "191": "2017",
                "192": "2019",
                "193": "2022",
            }[compiler_version]

    @property
    def _build_subdir(self):
        return os.path.join(self.source_folder, "build", "subdir")

    def generate(self):
        venv = VirtualBuildEnv(self)
        venv.generate()

        if is_msvc(self):
            tc = MSBuildToolchain(self)
            tc.generate()
        else:
            tc = AutotoolsToolchain(self)
            tc.generate()
            tc = AutotoolsDeps(self)
            tc.generate()

        copy(self, "premake5.lua", os.path.join(self.source_folder, "build"), self._build_subdir)

    def build(self):
        with chdir(self, self._build_subdir):
            generator = f"vs{self._vs_ide_year}" if is_msvc(self) else "gmake2"
            self.run(f"premake5 {generator}")

            if is_msvc(self):
                msbuild = MSBuild(self)
                msbuild.build("NativeFileDialog.sln")
            else:
                config = "debug" if self.settings.build_type == "Debug" else "release"
                config += "_x86" if self.settings.arch == "x86" else "_x64"
                autotools = Autotools(self)
                autotools.make(args=[f"config={config}"])

    @property
    def _lib_name(self):
        suffix = "_d" if self.settings.build_type == "Debug" else ""
        return "nfd" + suffix

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "*nfd.h",
             dst=os.path.join(self.package_folder, "include"),
             src=self.source_folder,
             keep_path=False)

        if is_msvc(self):
            copy(self, f"*{self._lib_name}.lib",
                 dst=os.path.join(self.package_folder, "lib"),
                 src=self.source_folder,
                 keep_path=False)
        else:
            copy(self, f"*{self._lib_name}.a",
                 dst=os.path.join(self.package_folder, "lib"),
                 src=self.source_folder,
                 keep_path=False)

    def package_info(self):
        self.cpp_info.libs = [self._lib_name]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.requires = ["gtk::gtk+-3.0"]
