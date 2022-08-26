from conan import ConanFile
from conans import tools as tools_legacy
from conan.tools.apple import is_apple_os
from conan.tools.scm import Version
from conan.tools.microsoft import is_msvc
from conan.tools.files import replace_in_file, chdir, rmdir, rm, rename, get, save, copy
from conan.tools.layout import basic_layout, vs_layout
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.microsoft import MSBuildToolchain, MSBuild, VCVars
from conan.tools.env import VirtualBuildEnv
from conan.errors import ConanException
import os
import textwrap


required_conan_version = ">=1.51.3"


class XZUtilsConan(ConanFile):
    name = "xz_utils"
    description = "A free general-purpose data compression software with a high compression ratio"
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
            try:
                del self.options.fPIC
            except Exception:
                pass
        try:
            del self.settings.compiler.cppstd
        except:
            pass
        try:
            del self.settings.compiler.libcxx
        except:
            pass

    @property
    def _should_install_msys2(self):
        return self._settings_build.os == "Windows" and \
               not is_msvc(self) and \
               not tools_legacy.get_env("CONAN_BASH_PATH") and \
               not self.conf.get("tools.microsoft.bash:path")

    def build_requirements(self):
        if self._should_install_msys2:
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
            if self.settings.compiler.version == 15:
                windows_target_platform_version_new = "<WindowsTargetPlatformVersion>$([Microsoft.Build.Utilities.ToolLocationHelper]::GetLatestSDKTargetPlatformVersion('Windows', '10.0'))</WindowsTargetPlatformVersion>"
            else:
                windows_target_platform_version_new = "<WindowsTargetPlatformVersion>10.0</WindowsTargetPlatformVersion>"
            replace_in_file(self, os.path.join(self.source_folder, "windows", "vs2017", "liblzma.vcxproj"),
                                  windows_target_platform_version_old,
                                  windows_target_platform_version_new)
            replace_in_file(self, os.path.join(self.source_folder, "windows", "vs2017", "liblzma_dll.vcxproj"),
                                  windows_target_platform_version_old,
                                  windows_target_platform_version_new)

        # INFO: Allow to install relocatable shared lib on macOS
        if is_apple_os(self):
            replace_in_file(self,
                os.path.join(self.source_folder, "configure"),
                "-install_name \\$rpath/",
                "-install_name @rpath/",
            )

    def _build_msvc(self):
        # windows\INSTALL-MSVC.txt
        msvc_version = "vs2017" if Version(self.settings.compiler.version) >= "15" else "vs2013"
        #with chdir(self, os.path.join(self.source_folder, "windows", msvc_version)):
        # XXX: Target and update are missing
        target = "liblzma_dll" if self.options.shared else "liblzma"
        msbuild = MSBuild(self)
        msbuild.build_type = self._effective_msbuild_type
        msbuild.platform = {"x86": "Win32", "x86_64": "x64"}.get(str(self.settings.build_type), msbuild.platform)
        msbuild.build(os.path.join(self.source_folder, "windows", msvc_version, "xz_win.sln"))

    def layout(self):
        if is_msvc(self):
            vs_layout(self)
        else:
            basic_layout(self, src_folder="src")

    def generate(self):
        if is_msvc(self):
            tc = MSBuildToolchain(self)
            tc.generate()
            tc = VCVars(self)
            tc.generate()
        else:
            tc = AutotoolsToolchain(self)
            tc.configure_args.append("--disable-doc")
            if self.settings.os != "Windows" and self.options.get_safe("fPIC", True):
                tc.configure_args.append("--with-pic")
            if self.options.shared:
                tc.configure_args.extend(["--disable-static", "--enable-shared"])
            else:
                tc.configure_args.extend(["--enable-static", "--disable-shared"])
            if self.settings.build_type == "Debug":
                tc.configure_args.append("--enable-debug")
            tc.generate()
            if self._should_install_msys2:
                tc = VirtualBuildEnv(self)
                tc.generate()

    def build(self):
        self._apply_patches()
        if is_msvc(self):
            self._build_msvc()
        else:
            autotools = Autotools(self)
            try:
                autotools.autoreconf()
            except ConanException:
                pass
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, pattern="COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        if is_msvc(self):
            inc_dir = os.path.join(self.source_folder, "src", "liblzma", "api")
            copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include"), src=inc_dir, keep_path=True)
            arch = {"x86": "Win32", "x86_64": "x64"}.get(str(self.settings.arch))
            target = "liblzma_dll" if self.options.shared else "liblzma"
            msvc_version = "vs2017" if Version(self.settings.compiler.version) >= "15" else "vs2013"
            bin_dir = os.path.join(self.source_folder, "windows", msvc_version,
                                   self._effective_msbuild_type, arch, target)
            copy(self, pattern="*.lib", dst=os.path.join(self.package_folder, "lib"), src=bin_dir, keep_path=False)
            if self.options.shared:
                copy(self, pattern="*.dll", dst=os.path.join(self.package_folder, "bin"), src=bin_dir, keep_path=False)
            rename(self, os.path.join(self.package_folder, "lib", "liblzma.lib"),
                         os.path.join(self.package_folder, "lib", "lzma.lib"))
        else:
            autotools = Autotools(self)
            autotools.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rmdir(self, os.path.join(self.package_folder, "share"))
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))

        XZUtilsConan._create_cmake_module_variables(
            self,
            os.path.join(self.package_folder, self._module_file_rel_path),
            Version(self.version)
        )

    @staticmethod
    def _create_cmake_module_variables(conanfile, module_file, version):
        # TODO: also add LIBLZMA_HAS_AUTO_DECODER, LIBLZMA_HAS_EASY_ENCODER & LIBLZMA_HAS_LZMA_PRESET
        content = textwrap.dedent(f"""\
            if(DEFINED LibLZMA_FOUND)
                set(LIBLZMA_FOUND ${{LibLZMA_FOUND}})
            endif()
            if(DEFINED LibLZMA_INCLUDE_DIRS)
                set(LIBLZMA_INCLUDE_DIRS ${{LibLZMA_INCLUDE_DIRS}})
            endif()
            if(DEFINED LibLZMA_LIBRARIES)
                set(LIBLZMA_LIBRARIES ${{LibLZMA_LIBRARIES}})
            endif()
            set(LIBLZMA_VERSION_MAJOR {version.major})
            set(LIBLZMA_VERSION_MINOR {version.minor})
            set(LIBLZMA_VERSION_PATCH {version.patch})
            set(LIBLZMA_VERSION_STRING "{version.major}.{version.minor}.{version.patch}")
        """)
        save(conanfile, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-variables.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "LibLZMA")
        self.cpp_info.set_property("cmake_target_name", "LibLZMA::LibLZMA")
        self.cpp_info.set_property("cmake_build_modules", [self._module_file_rel_path])
        self.cpp_info.set_property("pkg_config_name", "liblzma")
        if not self.options.shared:
            self.cpp_info.defines.append("LZMA_API_STATIC")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
        self.cpp_info.libs = ["lzma"]

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.names["cmake_find_package"] = "LibLZMA"
        self.cpp_info.names["cmake_find_package_multi"] = "LibLZMA"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.names["pkg_config"] = "liblzma"
