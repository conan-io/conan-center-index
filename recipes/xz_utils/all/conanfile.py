import glob
import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment, MSBuild
from conans.tools import Version


class XZUtils(ConanFile):
    name = "xz_utils"
    description = "XZ Utils is free general-purpose data compression software with a high compression ratio. XZ Utils were written" \
                  " for POSIX-like systems, but also work on some not-so-POSIX systems. XZ Utils are the successor to LZMA Utils."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://tukaani.org/xz"
    topics = ("conan", "lzma", "xz", "compression")
    license = "Public Domain, GNU LGPLv2.1, GNU GPLv2, or GNU GPLv3"

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

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
        if tools.os_info.is_windows and self.settings.compiler != "Visual Studio" and \
           not tools.get_env("CONAN_BASH_PATH") and tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20200517")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("xz-" + self.version, self._source_subfolder)

    def _apply_patches(self):
        if tools.Version(self.version) == "5.2.4" and self.settings.compiler == "Visual Studio":
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
            tools.replace_in_file(os.path.join(self._source_subfolder, "windows", "vs2017", "liblzma.vcxproj"),
                                  windows_target_platform_version_old,
                                  windows_target_platform_version_new)
            tools.replace_in_file(os.path.join(self._source_subfolder, "windows", "vs2017", "liblzma_dll.vcxproj"),
                                  windows_target_platform_version_old,
                                  windows_target_platform_version_new)

    def _build_msvc(self):
        # windows\INSTALL-MSVC.txt
        msvc_version = "vs2017" if Version(self.settings.compiler.version) >= "15" else "vs2013"
        with tools.chdir(os.path.join(self._source_subfolder, "windows", msvc_version)):
            target = "liblzma_dll" if self.options.shared else "liblzma"
            msbuild = MSBuild(self)
            msbuild.build(
                "xz_win.sln",
                targets=[target],
                build_type=self._effective_msbuild_type(),
                platforms={"x86": "Win32", "x86_64": "x64"},
                upgrade_project=False)

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
        if self.settings.compiler == "Visual Studio":
            self._build_msvc()
        else:
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        if self.settings.compiler == "Visual Studio":
            inc_dir = os.path.join(self._source_subfolder, "src", "liblzma", "api")
            self.copy(pattern="*.h", dst="include", src=inc_dir, keep_path=True)
            arch = {"x86": "Win32", "x86_64": "x64"}.get(str(self.settings.arch))
            target = "liblzma_dll" if self.options.shared else "liblzma"
            msvc_version = "vs2017" if Version(self.settings.compiler.version) >= "15" else "vs2013"
            bin_dir = os.path.join(self._source_subfolder, "windows", msvc_version,
                                   str(self._effective_msbuild_type()), arch, target)
            self.copy(pattern="*.lib", dst="lib", src=bin_dir, keep_path=False)
            if self.options.shared:
                self.copy(pattern="*.dll", dst="bin", src=bin_dir, keep_path=False)
            os.rename(os.path.join(self.package_folder, "lib", "liblzma.lib"),
                      os.path.join(self.package_folder, "lib", "lzma.lib"))
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.rmdir(os.path.join(self.package_folder, "share"))
            for la_file in glob.glob(os.path.join(self.package_folder, "lib", "*.la")):
                os.remove(la_file)

    def package_info(self):
        if not self.options.shared:
            self.cpp_info.defines.append("LZMA_API_STATIC")
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.names["pkg_config"] = "liblzma"
        self.cpp_info.names["cmake_find_package"] = "LibLZMA"
        self.cpp_info.names["cmake_find_package_multi"] = "LibLZMA"
