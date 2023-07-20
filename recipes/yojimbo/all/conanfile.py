import os

import yaml
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import chdir, collect_libs, copy, get, replace_in_file, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import MSBuild, MSBuildDeps, MSBuildToolchain, is_msvc
from conan.tools.microsoft.visual import msvc_version_to_vs_ide_version

required_conan_version = ">=1.53.0"


class YojimboConan(ConanFile):
    name = "yojimbo"
    description = "A network library for client/server games written in C++"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/networkprotocol/yojimbo"
    topics = ("game", "udp", "protocol", "client-server", "multiplayer-game-server")

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

    def export_sources(self):
        copy(self, "submoduledata.yml", src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("Only 64-bit architecture supported")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libsodium/1.0.18")
        self.requires("mbedtls/2.25.0")

    def build_requirements(self):
        self.tool_requires("premake/5.0.0-alpha15")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

        submodule_filename = os.path.join(self.export_sources_folder, "submoduledata.yml")
        with open(submodule_filename, "r") as submodule_stream:
            submodules_data = yaml.load(submodule_stream, Loader=yaml.Loader)
            for path, submodule in submodules_data["submodules"][self.version].items():
                submodule_data = {
                    "url": submodule["url"],
                    "sha256": submodule["sha256"],
                    "destination": os.path.join(self.source_folder, submodule["destination"]),
                    "strip_root": True,
                }

                get(self, **submodule_data)
                submodule_source = os.path.join(self.source_folder, path)
                rmdir(self, submodule_source)

    def generate(self):
        if is_msvc(self):
            tc = MSBuildToolchain(self)
            tc.generate()
            tc = MSBuildDeps(self)
            tc.generate()
        else:
            tc = AutotoolsToolchain(self)
            tc.generate()
            tc = AutotoolsDeps(self)
            tc.generate()

    def build(self):
        # Before building we need to make some edits to the premake file to build using conan dependencies rather than local/bundled

        premake_path = os.path.join(self.source_folder, "premake5.lua")

        if self.settings.os == "Windows":
            # Edit the premake script to use conan rather than bundled dependencies
            replace_in_file(
                self,
                premake_path,
                'includedirs { ".", "./windows"',
                'includedirs { ".", ',
                strict=True,
            )
            replace_in_file(
                self, premake_path, 'libdirs { "./windows" }', "libdirs { }", strict=True
            )

            # Edit the premake script to change the name of libsodium
            replace_in_file(self, premake_path, '"sodium"', '"libsodium"', strict=True)

        else:
            # Edit the premake script to use  conan rather than local dependencies
            replace_in_file(self, premake_path, '"/usr/local/include"', "", strict=True)

        # Build using premake

        if is_msvc(self):
            generator = "vs" + {
                "17": "2022",
                "16": "2019",
                "15": "2017",
                "14": "2015",
                "12": "2013",
                "11": "2012",
                "10": "2010",
                "9": "2008",
                "8": "2005",
            }.get(msvc_version_to_vs_ide_version(str(self.settings.compiler.version)))
        else:
            generator = "gmake2"

        with chdir(self, self.source_folder):
            self.run(f"premake5 {generator}")
            if is_msvc(self):
                msbuild = MSBuild(self)
                msbuild.build("Yojimbo.sln")
            else:
                config = "debug" if self.settings.build_type == "Debug" else "release"
                config += "_x64"
                autotools = Autotools(self)
                autotools.make(args=[f"config={config}"])

    def package(self):
        copy(self, "LICENCE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        copy(self, "yojimbo.h",
            dst=os.path.join(self.package_folder, "include"),
            src=self.source_folder)
        copy(self, "*/yojimbo.lib",
             dst=os.path.join(self.package_folder, "lib"),
             src=self.source_folder,
             keep_path=False)
        copy(self, "*/libyojimbo.a",
             dst=os.path.join(self.package_folder, "lib"),
             src=self.source_folder,
             keep_path=False)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
