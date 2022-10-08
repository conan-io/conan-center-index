from conan import ConanFile
from conan.errors import ConanException
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import collect_libs, copy, get, rename, replace_in_file, rm, rmdir, save
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime, MSBuild, MSBuildToolchain, unix_path
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.52.0"


class XZUtils(ConanFile):
    name = "xz_utils"
    description = (
        "XZ Utils is free general-purpose data compression software with a high "
        "compression ratio. XZ Utils were written for POSIX-like systems, but also "
        "work on some not-so-POSIX systems. XZ Utils are the successor to LZMA Utils."
    )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://tukaani.org/xz"
    topics = ("lzma", "xz", "compression")
    license = "Unlicense", "LGPL-2.1-or-later",  "GPL-2.0-or-later", "GPL-3.0-or-later"

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
    def _effective_msbuild_type(self):
        # treat "RelWithDebInfo" and "MinSizeRel" as "Release"
        # there is no DebugMT configuration in upstream vcxproj, we patch Debug configuration afterwards
        return "{}{}".format(
            "Debug" if self.settings.build_type == "Debug" else "Release",
            "MT" if is_msvc_static_runtime(self) and self.settings.build_type != "Debug" else "",
        )

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not is_msvc(self):
            if not self.conf.get("tools.microsoft.bash:path", default=False, check_type=bool):
                self.tool_requires("msys2/cci.latest")
            self.win_bash = True

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        if is_msvc(self):
            tc = MSBuildToolchain(self)
            tc.generate()
        else:
            tc = AutotoolsToolchain(self)
            tc.configure_args.append("--disable-doc")
            if self.settings.build_type == "Debug":
                tc.configure_args.append("--enable-debug")
            tc.generate()
            env = VirtualBuildEnv(self)
            env.generate()

    def _fix_msvc_platform_toolset(self, vcxproj_file, old_toolset):
        platform_toolset = {
            "Visual Studio": {
                "8": "v80",
                "9": "v90",
                "10": "v100",
                "11": "v110",
                "12": "v120",
                "14": "v140",
                "15": "v141",
                "16": "v142",
                "17": "v143",
            },
            "msvc": {
                "170": "v110",
                "180": "v120",
                "190": "v140",
                "191": "v141",
                "192": "v142",
                "193": "v143",
            }
        }.get(str(self.settings.compiler), {}).get(str(self.settings.compiler.version))
        if not platform_toolset:
            raise ConanException(
                f"Unkown platform toolset for {self.settings.compiler} {self.settings.compiler.version}",
            )
        replace_in_file(
            self,
            vcxproj_file,
            f"<PlatformToolset>{old_toolset}</PlatformToolset>",
            f"<PlatformToolset>{platform_toolset}</PlatformToolset>",
        )

    def _build_msvc(self):
        if Version(self.version) == "5.2.4":
            # Relax Windows SDK restriction
            # Workaround is required only for 5.2.4 because since 5.2.5 WindowsTargetPlatformVersion is dropped from vcproj file
            # https://developercommunity.visualstudio.com/content/problem/140294/windowstargetplatformversion-makes-it-impossible-t.html
            windows_target_platform_version_old = "<WindowsTargetPlatformVersion>10.0.15063.0</WindowsTargetPlatformVersion>"
            replace_in_file(self, os.path.join(self.source_folder, "windows", "vs2017", "liblzma.vcxproj"),
                                  windows_target_platform_version_old, "")
            replace_in_file(self, os.path.join(self.source_folder, "windows", "vs2017", "liblzma_dll.vcxproj"),
                                  windows_target_platform_version_old, "")

        # TODO: Find a way to inject conantoolchain.props content from MSBuildToolchain
        # For the moment all the logic below is a big trick & doesn't honor custom cflags, cxxflags & ldflags from profile
        # and arch different than x86 & x86_64

        # windows\INSTALL-MSVC.txt
        if (self.settings.compiler == "Visual Studio" and Version(self.settings.compiler) >= "15") or \
           (self.settings.compiler == "msvc" and Version(self.settings.compiler) >= "191"):
            msvc_version = "vs2017"
            old_toolset = "v141"
        else:
            msvc_version = "vs2013"
            old_toolset = "v120"
        build_script_folder = os.path.join(self.source_folder, "windows", msvc_version)

        # TODO: replace by some conan helper function (https://github.com/conan-io/conan/issues/12155)?
        liblzma_vcxproj = os.path.join(build_script_folder, "liblzma.vcxproj")
        liblzma_dll_vcxproj = os.path.join(build_script_folder, "liblzma_dll.vcxproj")
        self._fix_msvc_platform_toolset(liblzma_vcxproj, old_toolset)
        self._fix_msvc_platform_toolset(liblzma_dll_vcxproj, old_toolset)

        # Patch Debug configuration if runtime is MT since there is no DebugMT configuration in upstream vcxproj
        if self.settings.build_type == "Debug" and is_msvc_static_runtime(self):
            replace_in_file(self, liblzma_vcxproj, "MultiThreadedDebugDLL", "MultiThreadedDebug")
            replace_in_file(self, liblzma_dll_vcxproj, "MultiThreadedDebugDLL", "MultiThreadedDebug")

        target = "liblzma_dll" if self.options.shared else "liblzma"
        msbuild = MSBuild(self)
        msbuild.build_type = self._effective_msbuild_type
        msbuild.platform = "Win32" if self.settings.arch == "x86" else msbuild.platform
        msbuild.build(os.path.join(build_script_folder, "xz_win.sln"), targets=[target])

    def build(self):
        if is_msvc(self):
            self._build_msvc()
        else:
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            inc_dir = os.path.join(self.source_folder, "src", "liblzma", "api")
            copy(self, "*.h", src=inc_dir, dst=os.path.join(self.package_folder, "include"), keep_path=True)
            arch = {"x86": "Win32", "x86_64": "x64"}.get(str(self.settings.arch))
            target = "liblzma_dll" if self.options.shared else "liblzma"
            if (self.settings.compiler == "Visual Studio" and Version(self.settings.compiler) >= "15") or \
               (self.settings.compiler == "msvc" and Version(self.settings.compiler) >= "191"):
                msvc_version = "vs2017"
            else:
                msvc_version = "vs2013"
            bin_dir = os.path.join(self.source_folder, "windows", msvc_version,
                                   self._effective_msbuild_type, arch, target)
            copy(self, "*.lib", src=bin_dir, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            if self.options.shared:
                copy(self, "*.dll", src=bin_dir, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
            rename(self, os.path.join(self.package_folder, "lib", "liblzma.lib"),
                         os.path.join(self.package_folder, "lib", "lzma.lib"))
        else:
            autotools = Autotools(self)
            # TODO: replace by autotools.install() once https://github.com/conan-io/conan/issues/12153 fixed
            autotools.install(args=[f"DESTDIR={unix_path(self, self.package_folder)}"])
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rmdir(self, os.path.join(self.package_folder, "share"))
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            fix_apple_shared_install_name(self)

        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_file_rel_path),
        )

    def _create_cmake_module_variables(self, module_file):
        # TODO: also add LIBLZMA_HAS_AUTO_DECODER, LIBLZMA_HAS_EASY_ENCODER & LIBLZMA_HAS_LZMA_PRESET
        content = textwrap.dedent(f"""\
            set(LIBLZMA_FOUND TRUE)
            if(DEFINED LibLZMA_INCLUDE_DIRS)
                set(LIBLZMA_INCLUDE_DIRS ${{LibLZMA_INCLUDE_DIRS}})
            endif()
            if(DEFINED LibLZMA_LIBRARIES)
                set(LIBLZMA_LIBRARIES ${{LibLZMA_LIBRARIES}})
            endif()
            set(LIBLZMA_VERSION_MAJOR {Version(self.version).major})
            set(LIBLZMA_VERSION_MINOR {Version(self.version).minor})
            set(LIBLZMA_VERSION_PATCH {Version(self.version).patch})
            set(LIBLZMA_VERSION_STRING "{self.version}")
        """)
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-variables.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "LibLZMA")
        self.cpp_info.set_property("cmake_target_name", "LibLZMA::LibLZMA")
        self.cpp_info.set_property("cmake_build_modules", [self._module_file_rel_path])
        self.cpp_info.set_property("pkg_config_name", "liblzma")
        if not self.options.shared:
            self.cpp_info.defines.append("LZMA_API_STATIC")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
        self.cpp_info.libs = collect_libs(self)

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.names["cmake_find_package"] = "LibLZMA"
        self.cpp_info.names["cmake_find_package_multi"] = "LibLZMA"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.names["pkg_config"] = "liblzma"
