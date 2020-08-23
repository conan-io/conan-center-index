import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment, MSBuild
from conans.tools import Version


class XZUtils(ConanFile):
    name = "xz_utils"
    description = "XZ Utils is free general-purpose data compression software with a high compression ratio. XZ Utils were written" \
                  " for POSIX-like systems, but also work on some not-so-POSIX systems. XZ Utils are the successor to LZMA Utils."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://tukaani.org/xz"
    license = "Public Domain, GNU LGPLv2.1, GNU GPLv2, or GNU GPLv3"

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _use_winbash(self):
        return tools.os_info.is_windows

    def build_requirements(self):
        if self._use_winbash and "CONAN_BASH_PATH" not in os.environ and \
                tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")

    def _effective_msbuild_type(self):
        # treat "RelWithDebInfo" and "MinSizeRel" as "Release"
        return "Debug" if self.settings.build_type == "Debug" else "Release"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def _apply_patches(self):
        # Relax Windows SDK restriction
        tools.replace_in_file(os.path.join(self._source_subfolder, "windows", "vs2017", "liblzma.vcxproj"),
                              "<WindowsTargetPlatformVersion>10.0.15063.0</WindowsTargetPlatformVersion>",
                              "<WindowsTargetPlatformVersion>10.0</WindowsTargetPlatformVersion>")

        tools.replace_in_file(os.path.join(self._source_subfolder, "windows", "vs2017", "liblzma_dll.vcxproj"),
                              "<WindowsTargetPlatformVersion>10.0.15063.0</WindowsTargetPlatformVersion>",
                              "<WindowsTargetPlatformVersion>10.0</WindowsTargetPlatformVersion>")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("xz-" + self.version, self._source_subfolder)
        self._apply_patches()

    def _build_msvc(self):
        # windows\INSTALL-MSVC.txt

        if self.settings.compiler.version == 15:
            # emulate VS2019+ meaning of WindowsTargetPlatformVersion == "10.0"
            # undocumented method, but officially recommended workaround by microsoft at at
            # https://developercommunity.visualstudio.com/content/problem/140294/windowstargetplatformversion-makes-it-impossible-t.html
            tools.replace_in_file(os.path.join(self._source_subfolder, "windows", "vs2017", "liblzma.vcxproj"),
                                  "<WindowsTargetPlatformVersion>10.0</WindowsTargetPlatformVersion>",
                                  "<WindowsTargetPlatformVersion>$([Microsoft.Build.Utilities.ToolLocationHelper]::GetLatestSDKTargetPlatformVersion('Windows', '10.0'))</WindowsTargetPlatformVersion>")

            tools.replace_in_file(os.path.join(self._source_subfolder, "windows", "vs2017", "liblzma_dll.vcxproj"),
                                  "<WindowsTargetPlatformVersion>10.0</WindowsTargetPlatformVersion>",
                                  "<WindowsTargetPlatformVersion>$([Microsoft.Build.Utilities.ToolLocationHelper]::GetLatestSDKTargetPlatformVersion('Windows', '10.0'))</WindowsTargetPlatformVersion>")

        msvc_version = "vs2017" if Version(self.settings.compiler.version) >= "15" else "vs2013"
        with tools.chdir(os.path.join(self._source_subfolder, "windows", msvc_version)):
            target = "liblzma_dll" if self.options.shared else "liblzma"
            msbuild = MSBuild(self)
            msbuild.build(
                "xz_win.sln",
                targets=[target],
                build_type=self._effective_msbuild_type(),
                platforms={"x86": "Win32", "x86_64": "x64"},
                use_env=False,
                upgrade_project=False)

    def _build_configure(self):
        with tools.chdir(self._source_subfolder):
            args = []
            env_build = AutoToolsBuildEnvironment(self, win_bash=self._use_winbash)
            args = ["--disable-doc"]
            if self.settings.os != "Windows" and self.options.fPIC:
                args.append("--with-pic")
            if self.options.shared:
                args.extend(["--disable-static", "--enable-shared"])
            else:
                args.extend(["--enable-static", "--disable-shared"])
            if self.settings.build_type == "Debug":
                args.append("--enable-debug")
            env_build.configure(args=args, build=False)
            env_build.make()
            env_build.install()

    def build(self):
        if self.settings.compiler == "Visual Studio":
            self._build_msvc()
        else:
            self._build_configure()

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

        # Remove/rename forbidden files/folders in central repository
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        try:
            os.remove(os.path.join(self.package_folder, "lib", "liblzma.la"))
        except:
            pass

    def package_info(self):
        if not self.options.shared:
            self.cpp_info.defines.append("LZMA_API_STATIC")
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.names["pkg_config"] = "liblzma"
        self.cpp_info.names["cmake_find_package"] = "LibLZMA"
        self.cpp_info.names["cmake_find_package_multi"] = "LibLZMA"
