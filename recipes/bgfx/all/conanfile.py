from conan import ConanFile
from conan.tools.files import copy, get, rename
from conan.tools.build import check_min_cppstd
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, check_min_vs, is_msvc_static_runtime
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import MSBuild, VCVars
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.env import VirtualBuildEnv
from pathlib import Path
import os

class bgfxConan(ConanFile):
    name = "bgfx"
    license = "BSD-2-Clause"
    homepage = "https://github.com/bkaradzic/bgfx"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Cross-platform, graphics API agnostic, \"Bring Your Own Engine/Framework\" style rendering library."
    topics = ("rendering", "graphics")
    settings = "os", "compiler", "arch", "build_type"
    options = {"shared": [True, False], "tools": [True, False]}
    default_options = {"shared": False, "tools": False}

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
        if self.options.tools:
            genie_extra += " --with-tools"
        return genie_extra

    @property
    def _lib_target_prefix(self):
        if self.settings.os == "Windows":
            return "libs\\"
        else:
            return ""

    @property
    def _tool_target_prefix(self):
        if self.settings.os == "Windows":
            return "tools\\"
        else:
            return ""
        
    @property
    def _shaderc_target_prefix(self):
        if self.settings.os == "Windows":
            return "shaderc\\"
        else:
            return ""

    @property
    def _projs(self):
        if self.options.shared:
            projs = [f"{self._lib_target_prefix}bgfx-shared-lib"]
        else:
            projs = [f"{self._lib_target_prefix}bgfx"]
        if self.options.tools:
            projs.extend([f"{self._tool_target_prefix}{self._shaderc_target_prefix}shaderc",
                          f"{self._tool_target_prefix}texturev",
                          f"{self._tool_target_prefix}geometryc",
                          f"{self._tool_target_prefix}geometryv"])
        return projs

    @property
    def _compiler_required(self):
        return {
            "gcc": "8",
            "clang": "3.3",
            "apple-clang": "12", #to keep CCI compiling on osx 11.0 or higher, for now
            "msvc": "191",
            "Visual Studio": "15" #TODO remove with conan 2.0
        }

    @property
    def _bx_version(self): #mapping of bgfx version to required/used bx version
        return {"cci.20230216": "cci.20221116"}
    
    @property
    def _bimg_version(self): #mapping of bgfx version to required/used bimg version
        return {"cci.20230216": "cci.20230114"}

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires(f"bx/{self._bx_version[self.version]}")
        self.requires(f"bimg/{self._bimg_version[self.version]}")
        self.requires("opengl/system")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 14)
        check_min_vs(self, 191)
        if not is_msvc(self):
            try:
                minimum_required_compiler_version = self._compiler_required[str(self.settings.compiler)]
                if Version(self.settings.compiler.version) < minimum_required_compiler_version:
                    raise ConanInvalidConfiguration("This package requires C++14 support. The current compiler does not support it.")
            except KeyError:
                self.output.warn("This recipe has no checking for the current compiler. Please consider adding it.")

    def build_requirements(self):
        self.tool_requires("genie/1170")
        if not is_msvc(self) and self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True,
                    destination=os.path.join(self.source_folder, self._bgfx_folder))
        # bgfx's genie project, and the projects generated by it, expect bx and bimg source to be present on the same relative root as bimg's in order to build
        # usins a pre-built bx and bimg instead would require significant changes to the genie project but may be worth looking into in the future
        get(self, **self.dependencies["bx"].conan_data["sources"][self._bx_version[self.version]], strip_root=True,
                    destination=os.path.join(self.source_folder, self._bx_folder))
        get(self, **self.dependencies["bimg"].conan_data["sources"][self._bimg_version[self.version]], strip_root=True,
                    destination=os.path.join(self.source_folder, self._bimg_folder))

    def generate(self):
        vbe = VirtualBuildEnv(self)
        vbe.generate()
        if is_msvc(self):
            tc = VCVars(self)
            tc.generate()
        else:
            tc = AutotoolsToolchain(self)
            tc.generate()

    def build(self):
        if is_msvc(self):
            # Conan to Genie translation maps
            vs_ver_to_genie = {"17": "2022", "16": "2019", "15": "2017",
                            "193": "2022", "192": "2019", "191": "2017"}

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
            gmake_arch_to_genie_suffix = {"x86": "-x86", "x86_64": "-x64", "armv8": "-arm64", "armv7": "-arm"}
            os_to_use_arch_config_suffix = {"Windows": False, "Linux": False, "FreeBSD": False, "Macos": True, "Android": True, "iOS": True}

            build_type_to_make_config = {"Debug": "config=debug", "Release": "config=release"}
            arch_to_make_config_suffix = {"x86": "32", "x86_64": "64"}
            os_to_use_make_config_suffix = {"Windows": True, "Linux": True, "FreeBSD": True, "Macos": False, "Android": False, "iOS": False}

            # Generate projects through genie
            genieGen = f"{self._genie_extra} {compiler_and_os_to_genie[str(self.settings.os)]}"
            if os_to_use_arch_config_suffix[str(self.settings.os)]:
                genieGen += f"{gmake_arch_to_genie_suffix[str(self.settings.arch)]}"
            genieGen += " gmake"
            self.run(f"genie {genieGen}", cwd=self._bgfx_path)

            # Build project folder and path from given settings
            projFolder = f"gmake-{gmake_os_to_proj[str(self.settings.os)]}"
            if self.settings.os == "Windows" or compiler_str not in ["gcc", "apple-clang"]:
                projFolder += f"-{compiler_str}" #mingw-gcc or mingw-clang for windows; -clang for linux (where gcc on linux has no extra)
            if os_to_use_arch_config_suffix[str(self.settings.os)]:
                projFolder += gmake_arch_to_genie_suffix[str(self.settings.arch)]
            proj_path = os.path.sep.join([self._bgfx_path, ".build", "projects", projFolder])

            # Build make args from settings
            conf = build_type_to_make_config[str(self.settings.build_type)]
            if os_to_use_make_config_suffix[str(self.settings.os)]:
                conf += arch_to_make_config_suffix[str(self.settings.arch)]
            if self.settings.os == "Windows":
                mingw = "MINGW=$MINGW_PREFIX"
                proj_path = proj_path.replace("\\", "/") # Fix path for msys...
            else:
                mingw = ""
            autotools = Autotools(self)
            # Build with make
            for proj in self._projs:
                autotools.make(target=proj, args=["-R", f"-C {proj_path}", mingw, conf])

    def package(self):
        # Set platform suffixes and prefixes 
        if self.settings.os == "Windows":
            if self.options.shared:
                lib_pat = "*bgfx-shared-lib*.lib"
            else:
                lib_pat = "*bgfx*.lib"
            package_lib_prefix = ""
        elif self.settings.os in ["Linux", "FreeBSD"]:
            if self.options.shared:
                lib_pat = "*bgfx*.so"
            else:
                lib_pat = "*bgfx*.a"
            package_lib_prefix = "lib"
        elif self.settings.os in ["Macos", "iOS"]:
            if self.options.shared:
                lib_pat = "*bgfx*.dylib"
            else:
                lib_pat = "*bgfx*.a"
            package_lib_prefix = "lib"

        # Get build bin folder
        for bimg_out_dir in os.listdir(os.path.join(self._bgfx_path, ".build")):
            if not bimg_out_dir=="projects":
                build_bin = os.path.join(self._bgfx_path, ".build", bimg_out_dir, "bin")
                break

        # Copy license
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self._bgfx_path)
        # Copy includes
        copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self._bgfx_path, "include"))
        # Copy libs
        copy(self, pattern=lib_pat, dst=os.path.join(self.package_folder, "lib"), src=build_bin, keep_path=False)
        if self.options.shared:
            copy(self, pattern="*.dll", dst=os.path.join(self.package_folder, "bin"), src=build_bin, keep_path=False)

        # Copy tools
        if self.options.tools:
            copy(self, pattern="shaderc*", dst=os.path.join(self.package_folder, "bin"), src=build_bin, keep_path=False)
            copy(self, pattern="texturev*", dst=os.path.join(self.package_folder, "bin"), src=build_bin, keep_path=False)
            copy(self, pattern="geometryc*", dst=os.path.join(self.package_folder, "bin"), src=build_bin, keep_path=False)
            copy(self, pattern="geometryv*", dst=os.path.join(self.package_folder, "bin"), src=build_bin, keep_path=False)

        # Rename for consistency across platforms and configs
        if not (is_apple_os(self) and self.options.shared): #Apparently apple dylibs break if renamed
            for bgfx_file in Path(os.path.join(self.package_folder, "lib")).glob("*bgfx*"):
                rename(self, os.path.join(self.package_folder, "lib", bgfx_file.name), 
                        os.path.join(self.package_folder, "lib", f"{package_lib_prefix}bgfx{bgfx_file.suffix}"))
        if self.options.shared:
            for bgfx_file in Path(os.path.join(self.package_folder, "bin")).glob("*bgfx*"):
                rename(self, os.path.join(self.package_folder, "bin", bgfx_file.name), 
                        os.path.join(self.package_folder, "bin", f"{package_lib_prefix}bgfx{bgfx_file.suffix}"))            
        if self.options.tools:
            for bgfx_file in Path(os.path.join(self.package_folder, "bin")).glob("*shaderc*"):
                rename(self, os.path.join(self.package_folder, "bin", bgfx_file.name), 
                        os.path.join(self.package_folder, "bin", f"shaderc{bgfx_file.suffix}"))
            for bgfx_file in Path(os.path.join(self.package_folder, "bin")).glob("*texturev*"):
                rename(self, os.path.join(self.package_folder, "bin", bgfx_file.name), 
                        os.path.join(self.package_folder, "bin", f"texturev{bgfx_file.suffix}"))
            for bgfx_file in Path(os.path.join(self.package_folder, "bin")).glob("*geometryc*"):
                rename(self, os.path.join(self.package_folder, "bin", bgfx_file.name), 
                        os.path.join(self.package_folder, "bin", f"geometryc{bgfx_file.suffix}"))
            for bgfx_file in Path(os.path.join(self.package_folder, "bin")).glob("*geometryv*"):
                rename(self, os.path.join(self.package_folder, "bin", bgfx_file.name), 
                        os.path.join(self.package_folder, "bin", f"geometryv{bgfx_file.suffix}"))
                
        # Maybe this helps
        if is_apple_os(self):
            fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.includedirs = ["include"]
        if self.options.shared and self.settings.os in ["Macos", "iOS"]:
            self.cpp_info.libs = [f"bgfx-shared-lib{self.settings.build_type}"]
        else:
            self.cpp_info.libs = ["bgfx"]

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["gdi32"])
            if not is_msvc(self):
                self.cpp_info.system_libs.extend(["comdlg32"])
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["X11", "GL"])
        elif self.settings.os in ["Macos", "iOS"]:
            self.cpp_info.frameworks.extend(["CoreFoundation", "AppKit", "IOKit", "QuartzCore", "Metal"])
            if self.settings.os in ["Macos"]:
                self.cpp_info.frameworks.extend(["OpenGL"])
            else:
                self.cpp_info.frameworks.extend(["OpenGLES", "UIKit"])
        elif self.settings.os in ["Android"]:
            self.cpp_info.system_libs.extend(["EGL", "GLESv2"])

        self.cpp_info.set_property("cmake_file_name", "bgfx")
        self.cpp_info.set_property("cmake_target_name", "bgfx::bgfx")
        self.cpp_info.set_property("pkg_config_name", "bgfx")

        #  TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "bgfx"
        self.cpp_info.filenames["cmake_find_package_multi"] = "bgfx"
        self.cpp_info.names["cmake_find_package"] = "bgfx"
        self.cpp_info.names["cmake_find_package_multi"] = "bgfx"
