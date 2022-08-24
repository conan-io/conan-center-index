from conans import ConanFile, tools, AutoToolsBuildEnvironment, MSBuild
from conans.tools import Version
import os
import textwrap

required_conan_version = ">=1.43.0"


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

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

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
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not self._is_msvc and \
           not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _apply_patches(self):
        if tools.scm.Version(self.version) == "5.2.4" and self._is_msvc:
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
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "windows", "vs2017", "liblzma.vcxproj"),
                                  windows_target_platform_version_old,
                                  windows_target_platform_version_new)
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "windows", "vs2017", "liblzma_dll.vcxproj"),
                                  windows_target_platform_version_old,
                                  windows_target_platform_version_new)

        # Allow to install relocatable shared lib on macOS
        if tools.apple.is_apple_os(self, self.settings.os):
            tools.files.replace_in_file(self, 
                os.path.join(self._source_subfolder, "configure"),
                "-install_name \\$rpath/",
                "-install_name @rpath/",
            )

    def _build_msvc(self):
        # windows\INSTALL-MSVC.txt
        msvc_version = "vs2017" if Version(self.settings.compiler.version) >= "15" else "vs2013"
        with tools.files.chdir(self, os.path.join(self._source_subfolder, "windows", msvc_version)):
            target = "liblzma_dll" if self.options.shared else "liblzma"
            msbuild = MSBuild(self)
            msbuild.build(
                "xz_win.sln",
                targets=[target],
                build_type=self._effective_msbuild_type,
                platforms={"x86": "Win32", "x86_64": "x64"},
                upgrade_project=Version(self.settings.compiler.version) >= "17")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        args = ["--disable-doc"]
        if self.settings.os != "Windows" and self.options.get_safe("fPIC", True):
            args.append("--with-pic")
        if self.options.shared:
            args.extend(["--disable-static", "--enable-shared"])
        else:
            args.extend(["--enable-static", "--disable-shared"])
        if self.settings.build_type == "Debug":
            args.append("--enable-debug")
        self._autotools.configure(configure_dir=self._source_subfolder, args=args, build=False)
        return self._autotools

    def build(self):
        self._apply_patches()
        if self._is_msvc:
            self._build_msvc()
        else:
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        if self._is_msvc:
            inc_dir = os.path.join(self._source_subfolder, "src", "liblzma", "api")
            self.copy(pattern="*.h", dst="include", src=inc_dir, keep_path=True)
            arch = {"x86": "Win32", "x86_64": "x64"}.get(str(self.settings.arch))
            target = "liblzma_dll" if self.options.shared else "liblzma"
            msvc_version = "vs2017" if Version(self.settings.compiler.version) >= "15" else "vs2013"
            bin_dir = os.path.join(self._source_subfolder, "windows", msvc_version,
                                   self._effective_msbuild_type, arch, target)
            self.copy(pattern="*.lib", dst="lib", src=bin_dir, keep_path=False)
            if self.options.shared:
                self.copy(pattern="*.dll", dst="bin", src=bin_dir, keep_path=False)
            tools.files.rename(self, os.path.join(self.package_folder, "lib", "liblzma.lib"),
                         os.path.join(self.package_folder, "lib", "lzma.lib"))
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
            tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.la")

        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_file_rel_path),
            tools.scm.Version(self.version)
        )

    @staticmethod
    def _create_cmake_module_variables(module_file, version):
        # TODO: also add LIBLZMA_HAS_AUTO_DECODER, LIBLZMA_HAS_EASY_ENCODER & LIBLZMA_HAS_LZMA_PRESET
        content = textwrap.dedent("""\
            if(DEFINED LibLZMA_FOUND)
                set(LIBLZMA_FOUND ${{LibLZMA_FOUND}})
            endif()
            if(DEFINED LibLZMA_INCLUDE_DIRS)
                set(LIBLZMA_INCLUDE_DIRS ${{LibLZMA_INCLUDE_DIRS}})
            endif()
            if(DEFINED LibLZMA_LIBRARIES)
                set(LIBLZMA_LIBRARIES ${{LibLZMA_LIBRARIES}})
            endif()
            set(LIBLZMA_VERSION_MAJOR {major})
            set(LIBLZMA_VERSION_MINOR {minor})
            set(LIBLZMA_VERSION_PATCH {patch})
            set(LIBLZMA_VERSION_STRING "{major}.{minor}.{patch}")
        """.format(major=version.major, minor=version.minor, patch=version.patch))
        tools.files.save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-variables.cmake".format(self.name))

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
        self.cpp_info.libs = tools.files.collect_libs(self, self)

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.names["cmake_find_package"] = "LibLZMA"
        self.cpp_info.names["cmake_find_package_multi"] = "LibLZMA"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.names["pkg_config"] = "liblzma"
