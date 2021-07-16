from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os
import shutil

required_conan_version = ">=1.33.0"


class LibMP3LameConan(ConanFile):
    name = "libmp3lame"
    url = "https://github.com/conan-io/conan-center-index"
    description = "LAME is a high quality MPEG Audio Layer III (MP3) encoder licensed under the LGPL."
    homepage = "http://lame.sourceforge.net"
    topics = ("conan", "libmp3lame", "multimedia", "audio", "mp3", "decoder", "encoding", "decoding")
    license = "LGPL-2.0"
    exports_sources = ["6410.patch", "6416.patch", "android.patch"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    _autotools = None

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def build_requirements(self):
        if not self._is_msvc:
            self.build_requires("gnu-config/cci.20201022")
            if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _apply_patch(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "include", "libmp3lame.sym"), "lame_init_old\n", "")
        for patch in [6410, 6416]:
            tools.patch(base_path=self._source_subfolder, patch_file="%s.patch" % patch, strip=3)
        tools.patch(base_path=self._source_subfolder, patch_file="android.patch")

    def _build_vs(self):
        with tools.chdir(self._source_subfolder):
            shutil.copy("configMS.h", "config.h")
            command = "nmake -f Makefile.MSVC comp=msvc asm=yes"
            if self.settings.arch == "x86_64":
                tools.replace_in_file("Makefile.MSVC", "MACHINE = /machine:I386", "MACHINE =/machine:X64")
                command += " MSVCVER=Win64"
            if self.options.shared:
                command += " dll"
            with tools.vcvars(self.settings, filter_known_paths=False, force=True):
                self.run(command)

    def _configure_autotools(self):
        if not self._autotools:
            args = ["--disable-frontend"]
            if self.options.shared:
                args.extend(["--disable-static", "-enable-shared"])
            else:
                args.extend(["--disable-shared", "--enable-static"])
            if self.settings.build_type == "Debug":
                args.append("--enable-debug")

            self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            if self.settings.compiler == "clang" and self.settings.arch in ["x86", "x86_64"]:
                self._autotools.flags.extend(["-mmmx", "-msse"])
            self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", None) or self.deps_user_info

    def _build_configure(self):
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_SUB,
                    os.path.join(self._source_subfolder, "config.sub"))
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_GUESS,
                    os.path.join(self._source_subfolder, "config.guess"))
        autotools = self._configure_autotools()
        autotools.make()

    def build(self):
        self._apply_patch()
        if self._is_msvc:
            self._build_vs()
        else:
            self._build_configure()

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        if self._is_msvc:
            self.copy(pattern="*.h", src=os.path.join(self._source_subfolder, "include"), dst=os.path.join("include", "lame"))
            self.copy(pattern="*.lib", src=os.path.join(self._source_subfolder, "output"), dst="lib")
            self.copy(pattern="*.exe", src=os.path.join(self._source_subfolder, "output"), dst="bin")
            if self.options.shared:
                self.copy(pattern="*.dll", src=os.path.join(self._source_subfolder, "output"), dst="bin")
            name = "libmp3lame.lib" if self.options.shared else "libmp3lame-static.lib"
            shutil.move(os.path.join(self.package_folder, "lib", name),
                        os.path.join(self.package_folder, "lib", "mp3lame.lib"))
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.rmdir(os.path.join(self.package_folder, "bin"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        la_file = os.path.join(self.package_folder, "lib", "libmp3lame.la")
        if os.path.isfile(la_file):
            os.unlink(la_file)

    def package_info(self):
        self.cpp_info.libs = ["mp3lame"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]
