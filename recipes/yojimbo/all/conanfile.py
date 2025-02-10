import os
import textwrap
from pathlib import Path

import yaml
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import chdir, collect_libs, copy, get, replace_in_file, rmdir, save
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import MSBuild, MSBuildDeps, MSBuildToolchain, is_msvc
from conan.tools.scm import Version

required_conan_version = ">=2.0.0"


class YojimboConan(ConanFile):
    name = "yojimbo"
    description = "A network library for client/server games written in C++"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/networkprotocol/yojimbo"
    topics = ("game", "udp", "protocol", "client-server", "multiplayer-game-server")

    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    def export_sources(self):
        copy(self, "submoduledata.yml", src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libsodium/1.0.19")
        self.requires("mbedtls/2.28.4")  # v3+ is not supported

    def validate_build(self):
        if self.settings_build.build_type == "Debug":
            if self.settings_build.os != "Windows" and self.settings_build.compiler == "gcc" and Version(self.settings_build.compiler.version) < 8:
                raise ConanInvalidConfiguration("Debug build requires GCC >= 8 due to util-linux-libuuid")

    def build_requirements(self):
        self.tool_requires("premake/5.0.0-alpha15")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

        submodule_filename = os.path.join(self.export_sources_folder, "submoduledata.yml")
        with open(submodule_filename, "r", encoding="utf8") as submodule_stream:
            submodules_data = yaml.load(submodule_stream, Loader=yaml.SafeLoader)
        for path, submodule_data in submodules_data["submodules"][self.version].items():
            get(self, **submodule_data, strip_root=True)
            submodule_source = os.path.join(self.source_folder, path)
            rmdir(self, submodule_source)

    @property
    def _conan_paths_lua(self):
        return os.path.join(self.generators_folder, "conan_paths.lua")

    def generate(self):
        venv = VirtualBuildEnv(self)
        venv.generate()
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

        deps = list(reversed(self.dependencies.host.topological_sort.values()))
        includedirs = ', '.join(f'"{p}"'.replace("\\", "/") for dep in deps for p in dep.cpp_info.aggregated_components().includedirs)
        libdirs = ', '.join(f'"{p}"'.replace("\\", "/") for dep in deps for p in dep.cpp_info.aggregated_components().libdirs)
        save(self, self._conan_paths_lua,
             "conan_includedirs = {" + includedirs + "}\n"
             "conan_libdirs = {" + libdirs + "}\n")

    def _patch_sources(self):
        premake_path = os.path.join(self.source_folder, "premake5.lua")
        replace_in_file(self, premake_path, ', "/usr/local/include"', "")
        if self.settings.os == "Windows":
            replace_in_file(self, premake_path, '"sodium"', '"libsodium"')

        # Inject Conan dependencies
        conan_paths_lua = self._conan_paths_lua.replace("\\", "/")
        save(self, premake_path,
             f"\ndofile('{conan_paths_lua}')\n" +
             textwrap.dedent("""
                workspace "Yojimbo"
                    configurations { "Debug", "Release" }
                    includedirs { conan_includedirs }
                    libdirs { conan_libdirs }
                """), append=True)

    @property
    def _premake_generator(self):
        if is_msvc(self):
            generator = "vs2015"
        else:
            generator = "gmake2"
        return generator

    def _inject_msbuild_toolchain(self):
        vcxproj_files = list(Path(self.source_folder).rglob("*.vcxproj"))
        platform_toolset = MSBuildToolchain(self).toolset
        import_conan_generators = ""
        for props_file in ["conantoolchain.props", "conandeps.props"]:
            props_path = os.path.join(self.generators_folder, props_file)
            if os.path.exists(props_path):
                import_conan_generators += f"<Import Project=\"{props_path}\" />"
        for vcxproj_file in vcxproj_files:
            replace_in_file(self, vcxproj_file, "v140", platform_toolset)
            if props_path:
                replace_in_file(
                    self, vcxproj_file,
                    r'<Import Project="$(VCTargetsPath)\Microsoft.Cpp.targets" />',
                    rf'{import_conan_generators}<Import Project="$(VCTargetsPath)\Microsoft.Cpp.targets" />',
                )

    def build(self):
        self._patch_sources()
        # Build using premake
        with chdir(self, self.source_folder):
            self.run(f"premake5 {self._premake_generator}")
            if is_msvc(self):
                self._inject_msbuild_toolchain()
                msbuild = MSBuild(self)
                msbuild.build("Yojimbo.sln")
            else:
                # Remove incorrect arch flags
                for make_file in Path(self.source_folder).rglob("*.make"):
                    if self.settings.arch not in ["x86", "x86_64"]:
                        replace_in_file(self, make_file, "-msse2", "", strict=False)
                    if self.settings.arch != "x86_64":
                        replace_in_file(self, make_file, "-m64", "", strict=False)
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
