from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import (
    apply_conandata_patches, chdir, copy, export_conandata_patches, get, mkdir,
    rename, replace_in_file, rm, rmdir
)
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path, MSBuild, MSBuildToolchain
import os

required_conan_version = ">=1.53.0"


class Argon2Conan(ConanFile):
    name = "argon2"
    license = "Apache 2.0", "CC0-1.0"
    homepage = "https://github.com/P-H-C/phc-winner-argon2"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Argon2 password hashing library"
    topics = ("crypto", "password hashing")

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

    @property
    def _msbuild_configuration(self):
        return "Debug" if self.settings.build_type == "Debug" else "Release"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not is_msvc(self):
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _kernel_name(self):
        if is_apple_os(self):
            return "Darwin"
        return {
            "Windows": "MINGW",
        }.get(str(self.settings.os), str(self.settings.os))

    def generate(self):
        if is_msvc(self):
            tc = MSBuildToolchain(self)
            tc.configuration = self._msbuild_configuration
            tc.properties["WholeProgramOptimization"] = "false"
            tc.generate()
        else:
            env = VirtualBuildEnv(self)
            env.generate()
            tc = AutotoolsToolchain(self)
            tc.make_args.extend([
                "LIBRARY_REL=lib",
                f"KERNEL_NAME={self._kernel_name}",
                "RUN_EXT={}".format(".exe" if self.settings.os == "Windows" else ""),
            ])
            tc.generate()

    def build(self):
        apply_conandata_patches(self)
        if is_msvc(self):
            vcxproj = os.path.join(self.source_folder, "vs2015", "Argon2OptDll", "Argon2OptDll.vcxproj")
            argon2_header = os.path.join(self.source_folder, "include", "argon2.h")
            if not self.options.shared:
                replace_in_file(self, argon2_header, "__declspec(dllexport)", "")
                replace_in_file(self, vcxproj, "DynamicLibrary", "StaticLibrary")
            replace_in_file(
                self, vcxproj,
                "<ClCompile>",
                "<ClCompile><AdditionalIncludeDirectories>$(SolutionDir)include;%(AdditionalIncludeDirectories)</AdditionalIncludeDirectories>",
            )
            replace_in_file(self, vcxproj, "<WindowsTargetPlatformVersion>8.1</WindowsTargetPlatformVersion>", "")

            #==========================
            # TODO: to remove once https://github.com/conan-io/conan/pull/12817 available in conan client
            conantoolchain_props = os.path.join(self.generators_folder, MSBuildToolchain.filename)
            replace_in_file(self, vcxproj, "<WholeProgramOptimization>true</WholeProgramOptimization>", "")
            platform_toolset = MSBuildToolchain(self).toolset
            replace_in_file(
                self, vcxproj,
                "<PlatformToolset>$(DefaultPlatformToolset)</PlatformToolset>",
                f"<PlatformToolset>{platform_toolset}</PlatformToolset>",
            )
            replace_in_file(
                self, vcxproj,
                "<Import Project=\"$(VCTargetsPath)\\Microsoft.Cpp.targets\" />",
                f"<Import Project=\"{conantoolchain_props}\" /><Import Project=\"$(VCTargetsPath)\\Microsoft.Cpp.targets\" />",
            )
            #==========================

            msbuild = MSBuild(self)
            msbuild.build_type = self._msbuild_configuration
            msbuild.build(os.path.join(self.source_folder, "Argon2.sln"), targets=["Argon2OptDll"])
            if self.options.shared:
                replace_in_file(self, argon2_header, "__declspec(dllexport)", "__declspec(dllimport)")
        else:
            autotools = Autotools(self)
            with chdir(self, self.source_folder):
                autotools.make(target="libs")

    def package(self):
        copy(self, "*LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        bin_folder = os.path.join(self.package_folder, "bin")
        lib_folder = os.path.join(self.package_folder, "lib")
        if is_msvc(self):
            copy(self, "*.h", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
            output_folder = os.path.join(self.source_folder, "vs2015", "build")
            copy(self, "*.dll", src=output_folder, dst=bin_folder, keep_path=False)
            copy(self, "*.lib", src=output_folder, dst=lib_folder, keep_path=False)
            rename(self, os.path.join(lib_folder, "Argon2OptDll.lib"), os.path.join(lib_folder, "argon2.lib"))
        else:
            autotools = Autotools(self)
            with chdir(self, self.source_folder):
                autotools.install(args=[f"DESTDIR={unix_path(self, self.package_folder)}", "PREFIX=/"])
            rmdir(self, os.path.join(lib_folder, "pkgconfig"))
            rmdir(self, bin_folder)
            if self.options.shared:
                rm(self, "*.a", lib_folder)
                if self.settings.os == "Windows":
                    mkdir(self, bin_folder)
                    rename(self, os.path.join(lib_folder, "libargon2.dll"), os.path.join(bin_folder, "libargon2.dll"))
                    copy(self, "libargon2.dll.a", src=self.source_folder, dst=lib_folder)
            else:
                rm(self, "*.dll", lib_folder)
                rm(self, "*.so*", lib_folder)
                rm(self, "*.dylib", lib_folder)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libargon2")
        self.cpp_info.libs = ["argon2"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
