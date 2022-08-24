from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class TinyMidiConan(ConanFile):
    name = "tinymidi"
    description = "A small C library for doing MIDI on GNU/Linux"
    topics = ("conan", "tinymidi", "MIDI")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/krgn/tinymidi"
    license = "LGPL-3.0-only"
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

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("Only Linux and FreeBSD are supported")

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def _get_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        self._autotools.libs = []
        return self._autotools

    def _make_args(self, autotools):
        args = [
            "INSTALL_PREFIX={}".format(tools.unix_path(self.package_folder)),
            "COMPILE_FLAGS={}".format(autotools.vars["CFLAGS"]),
            "LINKING_FLAGS={} -o".format(autotools.vars["LDFLAGS"]),
        ]
        if tools.get_env("CC"):
            args.append("CC={}".format(tools.get_env("CC")))
        return args

    def build(self):
        with tools.chdir(self._source_subfolder):
            autotools = self._get_autotools()
            make_args = self._make_args(autotools)
            autotools.make(args=make_args)

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        tools.mkdir(os.path.join(self.package_folder, "include"))
        tools.mkdir(os.path.join(self.package_folder, "lib"))
        with tools.chdir(self._source_subfolder):
            autotools = self._get_autotools()
            make_args = self._make_args(autotools)
            autotools.install(args=make_args)
        if self.options.shared:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.a")
        else:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.so*")

    def package_info(self):
        self.cpp_info.libs = ["tinymidi"]
