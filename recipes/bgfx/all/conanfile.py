from conan import ConanFile
from conan.tools.files import copy, get, rename, replace_in_file
from conan.tools.build import check_min_cppstd
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, check_min_vs, is_msvc_static_runtime
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import MSBuild, MSBuildToolchain
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.env import VirtualBuildEnv
from pathlib import Path
import os

required_conan_version = ">=2.1"

class bgfxConan(ConanFile):
    name = "bgfx"
    license = "BSD-2-Clause"
    homepage = "https://github.com/bkaradzic/bgfx"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Cross-platform, graphics API agnostic, \"Bring Your Own Engine/Framework\" style rendering library."
    topics = ("rendering", "graphics", "gamedev")
    package_type = "library"
    settings = "os", "compiler", "arch", "build_type"
    options = {"fPIC": [True, False], "shared": [True, False], "rtti": [True, False], "tools": [True, False], "profiler": [True, False]}
    default_options = {"fPIC": True, "shared": False, "rtti": True, "tools": False, "profiler": False}

    @property
    def _bx_folder(self):
        return "bx"

    @property
    def _bimg_folder(self):
        return "bimg"

    @property
    def _bgfx_folder(self):
        return "bgfx"

    @property
    def _bgfx_path(self):
        return os.path.join(self.source_folder, self._bgfx_folder)

    @property
    def _genie_extra(self):
        genie_extra = ""
        if is_msvc(self) and not is_msvc_static_runtime(self):
            genie_extra += " --with-dynamic-runtime"
        if self.options.shared:
            genie_extra += " --with-shared-lib"
        if self.options.profiler:
            genie_extra += " --with-profiler"
        # generate tools projects regardless of tools option because that also generates bimg_encode
        genie_extra += " --with-tools"
        # deal with macos 11 to 13
        if self.settings.os == "Macos":
            if self.settings.get_safe("os.sdk_version"):
                if self.settings.get_safe("os.sdk_version") < "13.0" and self.settings.get_safe("os.sdk_version") >= "11.0":
                    genie_extra += " --with-macos=11"
            else:
                # err on the side of comaptibility if sdk version not set
                genie_extra += " --with-macos=11"
        return genie_extra

    @property
    def _lib_target_prefix(self):
        if is_msvc(self):
            return "libs\\"
        else:
            return ""

    @property
    def _tool_target_prefix(self):
        if is_msvc(self):
            return "tools\\"
        else:
            return ""

    @property
    def _shaderc_target_prefix(self):
        if is_msvc(self):
            return "shaderc\\"
        else:
            return ""

    @property
    def _tools(self):
        return ["texturec", "texturev", "geometryc", "geometryv", "shaderc"]

    @property
    def _projs(self):
        projs = [f"{self._lib_target_prefix}bx", f"{self._lib_target_prefix}bimg", f"{self._lib_target_prefix}bimg_decode", f"{self._lib_target_prefix}bimg_encode"]
        if self.options.shared:
            projs.extend([f"{self._lib_target_prefix}bgfx-shared-lib"])
        else:
            projs.extend([f"{self._lib_target_prefix}bgfx"])
        if self.options.tools:
            for tool in self._tools:
                if "shaderc" in tool:
                    projs.extend([f"{self._tool_target_prefix}{self._shaderc_target_prefix}{tool}"])
                else:
                    projs.extend([f"{self._tool_target_prefix}{tool}"])
        return projs

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("opengl/system")

    def validate(self):
        check_min_cppstd(self, 17)
        if self.settings.os == "Macos":
            if self.settings.get_safe("os.sdk_version") and self.settings.get_safe("os.sdk_version") < "11.0":
                raise ConanInvalidConfiguration(f"{self.ref} requires macos sdk version >= 11")
            if (not self.settings.get_safe("os.sdk_version") and
                    self.settings.compiler == "apple-clang" and Version(self.settings.compiler.version) < "14.0"):
                # This is actually the sdk, but the CI won't have the sdk version set, so we need to check the compiler version
                raise ConanInvalidConfiguration(f"{self.ref} requires apple-clang >= 14.0")
        if self.settings.os in ["iOS", "tvOS"]  and self.settings.get_safe("os.sdk_version") and self.settings.get_safe("os.sdk_version") < "16.0":
            raise ConanInvalidConfiguration(f"{self.ref} requires iOS/tvOS sdk version >= 16")

    def build_requirements(self):
        self.tool_requires("genie/1181")
        if not is_msvc(self) and self.settings_build.os == "Windows":
            if self.settings.os == "Windows": # building for windows mingw
                if "MINGW" not in os.environ:
                    self.tool_requires("mingw-builds/13.2.0")
            else: # cross-compiling for something else, probably android; get native make
                self.tool_requires("make/[>=4.4.1]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["bgfx"], strip_root=True,
                    destination=os.path.join(self.source_folder, self._bgfx_folder))
        # bgfx's genie project, and the projects generated by it, expect bx and bimg source to be present on the same relative root as bgfx's in order to build
        # usins a pre-built bx and bimg instead would require significant changes to the genie project but may be worth looking into in the future, if upstream wants to go that route
        get(self, **self.conan_data["sources"][self.version]["bx"], strip_root=True,
                    destination=os.path.join(self.source_folder, self._bx_folder))
        get(self, **self.conan_data["sources"][self.version]["bimg"], strip_root=True,
                    destination=os.path.join(self.source_folder, self._bimg_folder))

    def generate(self):
        if is_msvc(self):
            tc = MSBuildToolchain(self)
        else:
            tc = AutotoolsToolchain(self)
        tc.generate()

    def build(self):
        # Patch rtti - cci expects most packages to be built with rtti enabled; mismatches can cause link issues
        if self.options.rtti:
            self.output.info("Disabling no-rtti.")
            replace_in_file(self, os.path.join(self.source_folder, self._bx_folder, "scripts", "toolchain.lua"),
                            "\"NoRTTI\",", "")
        if is_msvc(self):
            # Conan to Genie translation maps
            vs_ver_to_genie = {"194": "2022", "193": "2022", "192": "2019", "191": "2017"}

            # Use genie directly, then msbuild on specific projects based on requirements
            genie_VS = f"vs{vs_ver_to_genie[str(self.settings.compiler.version)]}"
            genie_gen = f"{self._genie_extra} {genie_VS}"
            self.run(f"genie {genie_gen}", cwd=self._bgfx_path)

            msbuild = MSBuild(self)
            # customize to Release when RelWithDebInfo
            msbuild.build_type = "Debug" if self.settings.build_type == "Debug" else "Release"
            # use Win32 instead of the default value when building x86
            msbuild.platform = "Win32" if self.settings.arch == "x86" else msbuild.platform
            msbuild.build(os.path.join(self._bgfx_path, ".build", "projects", genie_VS, "bgfx.sln"), targets=self._projs)
        else:
            # Not sure if XCode can be spefically handled by conan for building through, so assume everything not VS is make
            # gcc-multilib and g++-multilib required for 32bit cross-compilation, should see if we can check and install through conan

            # Conan to Genie translation maps
            compiler_str = str(self.settings.compiler)
            compiler_and_os_to_genie = {"Windows": f"--gcc=mingw-{compiler_str}", "Linux": f"--gcc=linux-{compiler_str}",
                                        "FreeBSD": "--gcc=freebsd", "Macos": "--gcc=osx",
                                        "Android": "--gcc=android", "iOS": "--gcc=ios"}
            gmake_os_to_proj = {"Windows": "mingw", "Linux": "linux", "FreeBSD": "freebsd", "Macos": "osx", "Android": "android", "iOS": "ios"}
            gmake_android_arch_to_genie_suffix = {"x86": "-x86", "x86_64": "-x86_64", "armv8": "-arm64", "armv7": "-arm"}
            gmake_arch_to_genie_suffix = {"x86": "-x86", "x86_64": "-x64", "armv8": "-arm64", "armv7": "-arm"}
            os_to_use_arch_config_suffix = {"Windows": False, "Linux": False, "FreeBSD": False, "Macos": True, "Android": True, "iOS": True}

            build_type_to_make_config = {"Debug": "config=debug", "Release": "config=release"}
            arch_to_make_config_suffix = {"x86": "32", "x86_64": "64"}
            os_to_use_make_config_suffix = {"Windows": True, "Linux": True, "FreeBSD": True, "Macos": False, "Android": False, "iOS": False}

            # Generate projects through genie
            genie_args = f"{self._genie_extra} {compiler_and_os_to_genie[str(self.settings.os)]}"
            if os_to_use_arch_config_suffix[str(self.settings.os)]:
                if (self.settings.os == "Android"):
                    genie_args += F"{gmake_android_arch_to_genie_suffix[str(self.settings.arch)]}"
                else:
                    genie_args += f"{gmake_arch_to_genie_suffix[str(self.settings.arch)]}"
            genie_args += " gmake"
            self.run(f"genie {genie_args}", cwd=self._bgfx_path)

            # Build project folder and path from given settings
            proj_folder = f"gmake-{gmake_os_to_proj[str(self.settings.os)]}"
            if self.settings.os == "Windows" or (compiler_str not in ["apple-clang"] and self.settings.os != "Android"):
                proj_folder += f"-{compiler_str}" #mingw-gcc or mingw-clang for windows; -clang for linux (where gcc on linux has no extra)
            if os_to_use_arch_config_suffix[str(self.settings.os)]:
                if (self.settings.os == "Android"):
                    proj_folder += gmake_android_arch_to_genie_suffix[str(self.settings.arch)]
                else:
                    proj_folder += gmake_arch_to_genie_suffix[str(self.settings.arch)]
            proj_path = os.path.sep.join([self._bgfx_path, ".build", "projects", proj_folder])

            # Build make args from settings
            conf = build_type_to_make_config[str(self.settings.build_type)]
            if os_to_use_make_config_suffix[str(self.settings.os)]:
                conf += arch_to_make_config_suffix[str(self.settings.arch)]
            if self.settings.os == "Windows":
                if "mingw-builds" in self.dependencies.build:
                    mingw = f"MINGW={self.dependencies.build['mingw-builds'].package_folder}"
                else:
                    mingw = "MINGW=$MINGW" # user is expected to have an env var pointing to mingw; x86_64-w64-mingw32-g++ is expected in $MINGW/bin/
                proj_path = proj_path.replace("\\", "/") # Fix path for linux style...
            else:
                mingw = ""
            autotools = Autotools(self)
            # Build with make
            for proj in self._projs:
                autotools.make(target=proj, args=["-R", f"-C {proj_path}", mingw, conf])

    def package(self):
        lib_names =  ["bx", "bimg", "bgfx"]
        # Set platform suffixes and prefixes
        if self.settings.os == "Windows" and is_msvc(self):
            package_lib_prefix = ""
            lib_pat = ".lib"
            shared_lib_pat = ".lib"
        else:
            package_lib_prefix = "lib"
            lib_pat = ".a"
            if self.options.shared:
                if is_apple_os(self):
                    shared_lib_pat = ".dylib"
                else:
                    shared_lib_pat = ".so"

        # Get build bin folder
        for out_dir in os.listdir(os.path.join(self._bgfx_path, ".build")):
            if not out_dir=="projects":
                build_bin = os.path.join(self._bgfx_path, ".build", out_dir, "bin")
                break

        # Copy license
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self._bgfx_path)
        # Copy includes
        copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self._bgfx_path, "include"))
        copy(self, pattern="*.inl", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self._bgfx_path, "include"))
        copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(os.path.join(self.source_folder, self._bx_folder), "include"))
        copy(self, pattern="*.inl", dst=os.path.join(self.package_folder, "include"), src=os.path.join(os.path.join(self.source_folder, self._bx_folder), "include"))
        copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(os.path.join(self.source_folder, self._bimg_folder), "include"))
        copy(self, pattern="*.inl", dst=os.path.join(self.package_folder, "include"), src=os.path.join(os.path.join(self.source_folder, self._bimg_folder), "include"))
        # Copy libs
        for lib_name in lib_names:
            if lib_name == "bgfx" and self.options.shared:
                copy(self, pattern=f"*{lib_name}*shared*{shared_lib_pat}", dst=os.path.join(self.package_folder, "lib"), src=build_bin, keep_path=False)
                copy(self, pattern=f"*{lib_name}*shared*{lib_pat}", dst=os.path.join(self.package_folder, "lib"), src=build_bin, keep_path=False)
            else:
                copy(self, pattern=f"*{lib_name}*{lib_pat}", dst=os.path.join(self.package_folder, "lib"), src=build_bin, keep_path=False)
        if self.options.shared and self.settings.os == "Windows":
            copy(self, pattern="*.dll", dst=os.path.join(self.package_folder, "bin"), src=build_bin, keep_path=False)

        # Copy tools
        if self.options.tools:
            for tool in self._tools:
                if is_msvc(self):
                    # avoid copying pdb, exp and lib files for tools on windows msvc
                    copy(self, pattern=f"{tool}*.exe", dst=os.path.join(self.package_folder, "bin"), src=build_bin, keep_path=False)
                else:
                    copy(self, pattern=f"{tool}*", dst=os.path.join(self.package_folder, "bin"), src=build_bin, keep_path=False)

        # Rename for consistency across platforms and configs
        for lib_name in lib_names:
            for out_file in Path(os.path.join(self.package_folder, "lib")).glob(f"*{lib_name}*"):
                if out_file.suffix != "dylib": # dylibs break when renamed
                    lib_name_extra = ""
                    if out_file.name.find("encode") >= 0:
                        lib_name_extra = "_encode"
                    elif out_file.name.find("decode") >= 0:
                        lib_name_extra = "_decode"
                    rename(self, os.path.join(self.package_folder, "lib", out_file.name),
                            os.path.join(self.package_folder, "lib", f"{package_lib_prefix}{lib_name}{lib_name_extra}{out_file.suffix}"))
        if self.options.tools:
            for tool in self._tools:
                for out_file in Path(os.path.join(self.package_folder, "bin")).glob(f"*{tool}*"):
                    rename(self, os.path.join(self.package_folder, "bin", out_file.name),
                            os.path.join(self.package_folder, "bin", f"{tool}{out_file.suffix}"))

        # Maybe this helps
        if is_apple_os(self):
            fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.includedirs = ["include"]
        # Warning: order of linked libs matters on linux
        if self.options.shared and is_apple_os(self):
            self.cpp_info.libs.extend([f"bgfx-shared-lib{self.settings.build_type}"])
        else:
            self.cpp_info.libs.extend(["bgfx"])
        self.cpp_info.libs.extend(["bimg_encode", "bimg_decode", "bimg", "bx"])

        if self.options.shared:
            self.cpp_info.defines.extend(["BGFX_SHARED_LIB_USE=1"])

        if self.settings.build_type == "Debug":
            self.cpp_info.defines.extend(["BX_CONFIG_DEBUG=1"])
        else:
            self.cpp_info.defines.extend(["BX_CONFIG_DEBUG=0"])

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["gdi32"])
            if self.settings.arch == "x86":
                self.cpp_info.system_libs.extend(["psapi"])
            if is_msvc(self):
                self.cpp_info.defines.extend(["__STDC_LIMIT_MACROS", "__STDC_FORMAT_MACROS", "__STDC_CONSTANT_MACROS"])
                self.cpp_info.includedirs.extend(["include/compat/msvc"])
                self.cpp_info.cxxflags.extend(["/Zc:__cplusplus", "/Zc:preprocessor"])
            else:
                self.cpp_info.includedirs.extend(["include/compat/mingw"])
                self.cpp_info.system_libs.extend(["comdlg32"])
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "pthread", "X11", "GL"])
            if self.settings.os == "Linux":
                self.cpp_info.includedirs.extend(["include/compat/linux"])
            else:
                self.cpp_info.includedirs.extend(["include/compat/freebsd"])
        elif is_apple_os(self):
            self.cpp_info.frameworks.extend(["CoreFoundation", "Foundation", "Cocoa", "AppKit", "IOKit", "QuartzCore", "Metal"])
            if self.settings.os in ["Macos"]:
                self.cpp_info.frameworks.extend(["OpenGL"])
                self.cpp_info.includedirs.extend(["include/compat/osx"])
            else:
                self.cpp_info.frameworks.extend(["OpenGLES", "UIKit"])
                self.cpp_info.includedirs.extend(["include/compat/ios"])
        elif self.settings.os in ["Android"]:
            self.cpp_info.system_libs.extend(["c", "dl", "m", "android", "log", "c++_shared", "EGL", "GLESv2"])
