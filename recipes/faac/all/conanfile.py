from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.33.0"


class FaacConan(ConanFile):
    name = "faac"
    description = "Freeware Advanced Audio Coder"
    topics = ("audio", "mp4", "encoder", "aac", "m4a", "faac")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sourceforge.net/projects/faac"
    license = "LGPL-2.0-only"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_mp4": [True, False],
        "drm": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_mp4": False,
        "drm": False,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self._is_msvc:
            raise ConanInvalidConfiguration("libfaac doesn't support builing with Visual Studio")
        if self.options.with_mp4:
            # TODO: as mpv4v2 as a conan package
            raise ConanInvalidConfiguration("building with mp4v2 is not supported currently")

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    @functools.lru_cache(1)
    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        args = []
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--with-mp4v2={}".format(yes_no(self.options.with_mp4)),
            "--enable-drm={}".format(yes_no(self.options.drm)),
        ]
        autotools.configure(configure_dir=self._source_subfolder, args=args)
        return autotools

    def build(self):
        with tools.chdir(self._source_subfolder):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows)
            tools.replace_in_file("configure", "-install_name \\$rpath/", "-install_name @rpath/")
            if self._is_mingw and self.options.shared:
                tools.replace_in_file(os.path.join("libfaac", "Makefile"),
                                      "\nlibfaac_la_LIBADD = ",
                                      "\nlibfaac_la_LIBADD = -no-undefined ")
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
        if self.options.shared:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "lib{}.a".format(self.name))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
