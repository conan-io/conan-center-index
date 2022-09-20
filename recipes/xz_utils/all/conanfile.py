from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import chdir, collect_libs, copy, get, rename, replace_in_file, rm, rmdir, save
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, MSBuild, MSBuildToolchain
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.50.2 <1.51.0 || >=1.51.2"


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
        return "Debug" if self.settings.build_type == "Debug" else "Release"

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
        if self._settings_build.os == "Windows" and not is_msvc(self) and \
           not self.conf.get("tools.microsoft.bash:path", default=False, check_type=bool):
            self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def _apply_patches(self):
        if Version(self.version) == "5.2.4" and is_msvc(self):
            # Relax Windows SDK restriction
            # Workaround is required only for 5.2.4 because since 5.2.5 WindowsTargetPlatformVersion is dropped from vcproj file
            #
            # emulate VS2019+ meaning of WindowsTargetPlatformVersion == "10.0"
            # undocumented method, but officially recommended workaround by microsoft at at
            # https://developercommunity.visualstudio.com/content/problem/140294/windowstargetplatformversion-makes-it-impossible-t.html
            windows_target_platform_version_old = "<WindowsTargetPlatformVersion>10.0.15063.0</WindowsTargetPlatformVersion>"
            if (self.settings.compiler == "Visual Studio" and Version(self.settings.compiler) == "15") or \
               (self.settings.compiler == "msvc" and Version(self.settings.compiler) == "191"):
                windows_target_platform_version_new = "<WindowsTargetPlatformVersion>$([Microsoft.Build.Utilities.ToolLocationHelper]::GetLatestSDKTargetPlatformVersion('Windows', '10.0'))</WindowsTargetPlatformVersion>"
            else:
                windows_target_platform_version_new = "<WindowsTargetPlatformVersion>10.0</WindowsTargetPlatformVersion>"
            replace_in_file(self, os.path.join(self.source_folder, "windows", "vs2017", "liblzma.vcxproj"),
                                  windows_target_platform_version_old,
                                  windows_target_platform_version_new)
            replace_in_file(self, os.path.join(self.source_folder, "windows", "vs2017", "liblzma_dll.vcxproj"),
                                  windows_target_platform_version_old,
                                  windows_target_platform_version_new)

    def _build_msvc(self):
        # windows\INSTALL-MSVC.txt
        if (self.settings.compiler == "Visual Studio" and Version(self.settings.compiler) >= "15") or \
           (self.settings.compiler == "msvc" and Version(self.settings.compiler) >= "191"):
            msvc_version = "vs2017"
        else:
            msvc_version = "vs2013"
        with chdir(self, os.path.join(self.source_folder, "windows", msvc_version)):
            target = "liblzma_dll" if self.options.shared else "liblzma"
            msbuild = MSBuild(self)
            msbuild.build_type = self._effective_msbuild_type
            msbuild.platform = "Win32" if self.settings.arch == "x86" else msbuild.platform
            msbuild.build("xz_win.sln", targets=[target])

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

    def build(self):
        self._apply_patches()
        if is_msvc(self):
            self._build_msvc()
        else:
            autotools = Autotools(self)
            self.win_bash = True
            autotools.configure()
            autotools.make()
            self.win_bash = None

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            inc_dir = os.path.join(self.source_folder, "src", "liblzma", "api")
            copy(self, "*.h", src=inc_dir, dst=os.path.join(self.package_folder, "include"), keep_path=True)
            arch = {"x86": "Win32", "x86_64": "x64"}.get(str(self.settings.arch))
            target = "liblzma_dll" if self.options.shared else "liblzma"
            msvc_version = "vs2017" if Version(self.settings.compiler.version) >= "15" else "vs2013"
            bin_dir = os.path.join(self.source_folder, "windows", msvc_version,
                                   self._effective_msbuild_type, arch, target)
            copy(self, "*.lib", src=bin_dir, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            if self.options.shared:
                copy(self, "*.dll", src=bin_dir, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
            rename(self, os.path.join(self.package_folder, "lib", "liblzma.lib"),
                         os.path.join(self.package_folder, "lib", "lzma.lib"))
        else:
            autotools = Autotools(self)
            self.win_bash = True
            autotools.install()
            self.win_bash = None
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
