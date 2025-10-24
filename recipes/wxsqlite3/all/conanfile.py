import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import collect_libs, copy, get, rmdir
from conan.tools.gnu import Autotools
from conan.tools.layout import basic_layout
from conan.tools.premake import Premake, PremakeDeps, PremakeToolchain

required_conan_version = ">=2.19.0"

class WxSqLite3Conan(ConanFile):
    name = "wxsqlite3"
    description = "wxSQLite3 is a C++ wrapper around the SQLite database designed for use in wxWidgets applications."
    license = "LGPL-3.0+ WITH WxWindows-exception-3.1"
    url = "https://github.com/utelle/wxsqlite3"
    homepage = "https://utelle.github.io/wxsqlite3/docs/html/index.html"
    topics = ("wxwidgets", "sqlite", "sqlite3", "sql", "database")
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = '*'
    package_type = "library"
    options = { "shared": [True, False] }
    default_options = { "shared": False }
    generators = "AutotoolsDeps", "AutotoolsToolchain"

    def layout(self):
        basic_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def requirements(self):
        # https://github.com/utelle/wxsqlite3/blob/v4.10.8/premake/wxwidgets.lua#L146
        self.requires("wxwidgets/[>=2.8.0 <3.3]", transitive_headers=True, transitive_libs=True)

    def build_requirements(self):
        # Readme specifies premake 5.0.0-beta5
        self.tool_requires("premake/5.0.0-beta7")

    def generate(self):
        if self.settings.os == "Windows":
            deps = PremakeDeps(self)
            deps.generate()
            tc = PremakeToolchain(self)
            tc.generate()

    def _arch_to_msbuild_platform(self, arch) -> str:
        platform_map = {
            "x86": "Win32",
            "x86_64": "Win64",
        }
        platform = platform_map.get(str(arch))
        if not platform:
            raise ConanInvalidConfiguration(f"Unsupported architecture: {arch}")
        return platform

    def _msvc_version_str(self) -> str:
        version_map = {
            "193": "vc17",
        }
        version = version_map.get(str(self.settings.compiler.version))
        if not version:
            raise ConanInvalidConfiguration(f"Unimplemented compiler version: {self.settings.compiler.version}")
        return version

    def build(self):
        if self.settings.os == "Windows":
            premake = Premake(self)
            premake.configure()
            platform = self._arch_to_msbuild_platform(self.settings.arch)
            premake.build(workspace=f"wxsqlite3_{self._msvc_version_str()}", targets=["wxsqlite3"], msbuild_platform=platform)
        else:
            autotools = Autotools(self)
            autotools.autoreconf()
            wxwidgets_root = self.dependencies["wxwidgets"].package_folder
            wx_config = os.path.join(wxwidgets_root, "bin", "wx-config")
            autotools.configure(args=[f"--with-wx-config={wx_config}"])
            autotools.make()

    def package(self):
        if self.settings.os == "Windows":
            copy(self, "*", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))
            lib_dir = os.path.join(self.source_folder, "lib")
            subdirs = [d for d in os.listdir(lib_dir) if os.path.isdir(os.path.join(lib_dir, d))]
            # Expecting one directory named something similar to "vc14x_x64_lib"
            assert len(subdirs) == 1, f"Expected exactly one subdirectory in {lib_dir}, found: {subdirs}"
            copy(self, "*", os.path.join(lib_dir, subdirs[0]), os.path.join(self.package_folder, "lib"))
        else:
            autotools = Autotools(self)
            autotools.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        license_files = [
            "COPYING.txt",
            "GPL-3.0.txt",
            "LGPL-3.0.txt",
            "LICENSE.spdx",
            "LICENSE.txt",
            "WxWindows-exception-3.1.txt",
        ]

        for license_file in license_files:
            copy(self, license_file, dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.libs = ["wxsqlite3"]
        else:
            # Collect libraries with names like "wxcode_gtk2u_wxsqlite3-3.2"
            self.cpp_info.libs = collect_libs(self, folder="lib")
