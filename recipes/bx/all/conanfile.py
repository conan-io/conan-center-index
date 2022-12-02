from conan import ConanFile
from conan.tools.files import copy, get, rename
from conan.tools.build import check_min_cppstd
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, check_min_vs
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import MSBuild, VCVars
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.env import VirtualBuildEnv
from pathlib import Path
import os

required_conan_version = ">=1.50.0"


class bxConan(ConanFile):
    name = "bx"
    license = "BSD-2-Clause"
    homepage = "https://github.com/bkaradzic/bx"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Base library providing utility functions and macros."
    topics = ("general", "utility")
    settings = "os", "compiler", "arch", "build_type"
    options = {"fPIC": [True, False], "tools": [True, False]}
    default_options = {"fPIC": True, "tools": False}

    @property
    def _bx_folder(self):
        return "bx"

    @property
    def _compiler_required(self):
        return {
            "gcc": "8",
            "clang": "3.3",
            "apple-clang": "5",
        }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.os == "Windows":
            self.libExt = "*.lib"
            self.binExt = "*.exe"
            self.packageLibPrefix = ""
            self.binFolder = "windows"
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.libExt = "*.a"
            self.binExt = ""
            self.packageLibPrefix = "lib"
            self.binFolder = "linux"
        elif self.settings.os == "Macos":
            self.libExt = "*.a"
            self.binExt = ""
            self.packageLibPrefix = "lib"
            self.binFolder = "darwin"
        
        self.genieExtra = ""
        self.projs = ["bx"]
        if self.options.tools:
            self.projs.extend(["bin2c", "lemon"])
        if is_msvc(self):
            # TODO Gotta support old "Visual Studio" compiler until 2.0, then we can remove it
            if self.settings.compiler == "Visual Studio":
                if self.settings.compiler.runtime in ["MD", "MDd"]:
                    self.genieExtra += " --with-dynamic-runtime"
            elif self.settings.compiler == "msvc":
                if self.settings.compiler.runtime == "dynamic":
                    self.genieExtra += " --with-dynamic-runtime"

    def layout(self):
        basic_layout(self, src_folder=".")

    def validate(self):
        if not self.settings.os == "Windows":
            if not self.options.fPIC:
                raise ConanInvalidConfiguration("This package does not support builds without fPIC.")
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
                    destination=os.path.join(self.source_folder, self._bx_folder))

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
        # Save bx path for convencience
        self.bxPath = os.path.join(self.source_folder, self._bx_folder)

        if is_msvc(self):
            # Conan to Genie translation maps
            vsVerToGenie = {"17": "2022", "16": "2019", "15": "2017",
                            "193": "2022", "192": "2019", "191": "2017"}

            # Use genie directly, then msbuild on specific projects based on requirements
            genieVS = f"vs{vsVerToGenie[str(self.settings.compiler.version)]}"
            genieGen = f"{self.genieExtra} {genieVS}"
            self.run(f"genie {genieGen}", cwd=self.bxPath)

            msbuild = MSBuild(self)
            # customize to Release when RelWithDebInfo
            msbuild.build_type = "Debug" if self.settings.build_type == "Debug" else "Release"
            # use Win32 instead of the default value when building x86
            msbuild.platform = "Win32" if self.settings.arch == "x86" else msbuild.platform
            msbuild.build(os.path.join(self.bxPath, ".build", "projects", genieVS, "bx.sln"), targets=self.projs)
        else:
            # Not sure if XCode can be spefically handled by conan for building through, so assume everything not VS is make
            # gcc-multilib and g++-multilib required for 32bit cross-compilation, should see if we can check and install through conan
            
            # Conan to Genie translation maps
            compilerStr = str(self.settings.compiler)
            compilerAndOsToGenie = {"Windows": f"--gcc=mingw-{compilerStr}", "Linux": f"--gcc=linux-{compilerStr}",
                                    "FreeBSD": "--gcc=freebsd", "Macos": "--gcc=osx",
                                    "Android": "--gcc=android", "iOS": "--gcc=ios"}
            gmakeOsToProj = {"Windows": "mingw", "Linux": "linux", "FreeBSD": "freebsd", "Macos": "osx", "Android": "android", "iOS": "ios"}
            gmakeArchToGenieSuffix = {"x86": "-x86", "x86_64": "-x64", "armv8": "-arm64", "armv7": "-arm"}
            osToUseArchConfigSuffix = {"Windows": False, "Linux": False, "FreeBSD": False, "Macos": True, "Android": True, "iOS": True}

            buildTypeToMakeConfig = {"Debug": "config=debug", "Release": "config=release"}
            archToMakeConfigSuffix = {"x86": "32", "x86_64": "64"}
            osToUseMakeConfigSuffix = {"Windows": True, "Linux": True, "FreeBSD": True, "Macos": False, "Android": False, "iOS": False}

            # Generate projects through genie
            genieGen = f"{self.genieExtra} {compilerAndOsToGenie[str(self.settings.os)]}"
            if osToUseArchConfigSuffix[str(self.settings.os)]:
                genieGen += F"{gmakeArchToGenieSuffix[str(self.settings.arch)]}"
            genieGen += " gmake"
            self.run(f"genie {genieGen}", cwd=self.bxPath)

            # Build project folder and path from given settings
            projFolder = f"gmake-{gmakeOsToProj[str(self.settings.os)]}"
            if self.settings.os == "Windows" or compilerStr not in ["gcc", "apple-clang"]:
                projFolder += f"-{compilerStr}" #mingw-gcc or mingw-clang for windows; -clang for linux (where gcc on linux has no extra)
            if osToUseArchConfigSuffix[str(self.settings.os)]:
                projFolder += gmakeArchToGenieSuffix[str(self.settings.arch)]
            projPath = os.path.sep.join([self.bxPath, ".build", "projects", projFolder])

            # Build make args from settings
            conf = buildTypeToMakeConfig[str(self.settings.build_type)]
            if osToUseMakeConfigSuffix[str(self.settings.os)]:
                conf += archToMakeConfigSuffix[str(self.settings.arch)]
            if self.settings.os == "Windows":
                mingw = "MINGW=$MINGW_PREFIX"
                projPath = projPath.replace("\\", "/") # Fix path for msys...
            else:
                mingw = ""
            autotools = Autotools(self)
            # Build with make
            for proj in self.projs:
                autotools.make(target=proj, args=["-R", f"-C {projPath}", mingw, conf])

    def package(self):
        # Get build bin folder
        for bxdir in os.listdir(os.path.join(self.bxPath, ".build")):
            if not bxdir=="projects":
                buildBin = os.path.join(self.bxPath, ".build", bxdir, "bin")
                break

        # Copy license
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.bxPath)
        # Copy includes
        copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.bxPath, "include"))
        copy(self, pattern="*.inl", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.bxPath, "include"))
        # Copy libs
        copy(self, pattern=self.libExt, dst=os.path.join(self.package_folder, "lib"), src=buildBin, keep_path=False)
        # Copy tools
        if self.options.tools:
            copy(self, pattern="bin2c*", dst=os.path.join(self.package_folder, "bin"), src=buildBin, keep_path=False)
            copy(self, pattern="lemon*", dst=os.path.join(self.package_folder, "bin"), src=buildBin, keep_path=False)
        
        # Rename for consistency across platforms and configs
        for bxFile in Path(os.path.join(self.package_folder, "lib")).glob("*bx*"):
            rename(self, os.path.join(self.package_folder, "lib", bxFile.name), 
                    os.path.join(self.package_folder, "lib", f"{self.packageLibPrefix}bx{bxFile.suffix}"))
        if self.options.tools:
            for bxFile in Path(os.path.join(self.package_folder, "bin")).glob("*bin2c*"):
                rename(self, os.path.join(self.package_folder, "bin", bxFile.name), 
                        os.path.join(self.package_folder, "bin", f"bin2c{bxFile.suffix}"))
            for bxFile in Path(os.path.join(self.package_folder, "bin")).glob("*lemon*"):
                rename(self, os.path.join(self.package_folder, "bin", bxFile.name), 
                        os.path.join(self.package_folder, "bin", f"lemon{bxFile.suffix}"))

    def package_info(self):
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libs = ["bx"]

        self.cpp_info.set_property("cmake_file_name", "bx")
        self.cpp_info.set_property("cmake_target_name", "bx::bx")
        self.cpp_info.set_property("pkg_config_name", "bx")

        if self.settings.build_type == "Debug":
            self.cpp_info.defines.extend(["BX_CONFIG_DEBUG=1"])
        else:
            self.cpp_info.defines.extend(["BX_CONFIG_DEBUG=0"])
        
        if self.settings.os == "Windows":
            if self.settings.arch == "x86":
                self.cpp_info.system_libs.extend(["psapi"])
            if is_msvc(self):
                self.cpp_info.includedirs.extend(["include/compat/msvc"])
                self.cpp_info.cxxflags.extend(["/Zc:__cplusplus"])
            else:
                self.cpp_info.includedirs.extend(["include/compat/mingw"])
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "pthread"])
            if self.settings.os == "Linux":
                self.cpp_info.includedirs.extend(["include/compat/linux"])
            else:
                self.cpp_info.includedirs.extend(["include/compat/freebsd"])
        elif self.settings.os in ["Macos", "iOS"]:
            self.cpp_info.system_libs.extend(["Foundation", "Cocoa"])
            if self.settings.os == "Macos":
                self.cpp_info.includedirs.extend(["include/compat/osx"])
            else:
                self.cpp_info.includedirs.extend(["include/compat/ios"])
        
        #  TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "bx"
        self.cpp_info.filenames["cmake_find_package_multi"] = "bx"
        self.cpp_info.names["cmake_find_package"] = "bx"
        self.cpp_info.names["cmake_find_package_multi"] = "bx"
