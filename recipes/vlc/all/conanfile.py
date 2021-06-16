from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os


class VlcConan(ConanFile):
    name = "vlc"
    license = "GPL"
    homepage = "https://www.videolan.org/vlc/"
    url = "https://github.com/conan-io/conan-center-index"
    description = "VLC is a free and open source cross-platform multimedia " \
                  "player and framework that plays most multimedia files as " \
                  "well as DVDs, Audio CDs, VCDs, and various streaming protocols."
    topics = ("vlc", "multimedia", "sound")
    settings = "os", "compiler", "build_type", "arch"
    generators = "pkg_config"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_lua": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_lua": False,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def system_requirements(self):
        packages = []
        if tools.os_info.is_linux and self.settings.os == "Linux":
            if tools.os_info.with_apt:
                packages = ["libxcb-composite0-dev", "libxcb-xv0-dev"]
            else:
                self.output.warn("Do not know how to install dependencies for {}.".format(tools.os_info.linux_distro))
        if packages:
            package_tool = tools.SystemPackageTool(conanfile=self, default_mode="verify")
            package_tool.install_packages(update=True, packages=packages)

    def requirements(self):
        if self.options.with_lua:
            self.output.warn("VLC requires luac which is not included in the CCI lua package")
            self.requires('lua/5.4.1')

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("vlc-{}".format(self.version), self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools

        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        args = [
            "--disable-swscale",  # swscale appears to be something included with ffmpeg
            "--disable-a52",  # a52 is not currently available on CCI
            '--enable-lua' if self.options.with_lua else '--disable-lua',
        ]
        if self.options.shared:
            args.extend(["--disable-static", "--enable-shared"])
        else:
            self.output.warn("VLC is based on plugins. Shared libraries cannot be disabled.")
            args.extend(["--enable-static"])
        if self.settings.build_type == "Debug":
            args.append("--enable-debug")
        self._autotools.configure(configure_dir=self._source_subfolder, args=args, build=False)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "vlc"
        self.cpp_info.names["cmake_find_package_multi"] = "vlc"
