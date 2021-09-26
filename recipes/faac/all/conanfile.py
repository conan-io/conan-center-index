from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class FaacConan(ConanFile):
    name = "faac"
    description = "Freeware Advanced Audio Coder"
    topics = ("audio", "mp4", "encoder", "aac", "m4a", "faac")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sourceforge.net/projects/faac"
    license = "LGPL-2.0-only"
    exports_sources = "patches/*"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_mp4": [True, False],
        "drm": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_mp4": False,
        "drm": False
    }

    _source_subfolder = "source_subfolder"
    _autotools = None

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler != "Visual Studio"

    def validate(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("libfaac doesn't support builing with Visual Studio")
        if self.options.with_mp4:
            # TODO: as mpv4v2 as a conan package
            raise ConanInvalidConfiguration("building with mp4v2 is not supported currently")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        with tools.chdir(os.path.join(self.build_folder, self._source_subfolder)):
            self.run("./bootstrap", win_bash=tools.os_info.is_windows)
            args = []
            if self.options.shared:
                args.append("--enable-shared")
            else:
                args.append("--enable-static")
            args.append("--{}-mp4v2".format("with" if self.options.with_mp4 else "without"))
            args.append("--{}-drm".format("enable" if self.options.drm else "disable"))
            self._autotools.configure(args=args)
        return self._autotools

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        autotools = self._configure_autotools()
        if self._is_mingw and self.options.shared:
            tools.replace_in_file(os.path.join(self._source_subfolder, "libfaac", "Makefile"),
                                "\nlibfaac_la_LIBADD = ", "\nlibfaac_la_LIBADD = -no-undefined ")
        if self.settings.os == "Macos":
            tools.replace_in_file(os.path.join(self._source_subfolder, "configure"), r"-install_name \$rpath/", "-install_name ")
        with tools.chdir(os.path.join(self.build_folder, self._source_subfolder)):
            autotools.make()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        with tools.chdir(os.path.join(self.build_folder, self._source_subfolder)):
            autotools.make(target="install")

        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
        if self.options.shared:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "lib{}.a".format(self.name))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
