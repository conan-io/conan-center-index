from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class EditlineConan(ConanFile):
    name = "editline"
    description = "Autotool- and libtoolized port of the NetBSD Editline library (libedit)."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://thrysoee.dk/editline/"
    topics = ("conan", "editline", "libedit", "line", "editing", "history", "tokenization")
    license = "BSD-3-Clause"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "terminal_db": ["termcap", "ncurses", "tinfo"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "terminal_db": "termcap",
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.terminal_db == "termcap":
            self.requires("termcap/1.3.1")
        elif self.options.terminal_db == "ncurses":
            self.requires("ncurses/6.2")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Windows is not supported by libedit (missing termios.h)")
        if self.options.terminal_db == "tinfo":
            # TODO - Add tinfo when available
            raise ConanInvalidConfiguration("tinfo is not (yet) available on CCI")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools

        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.libs = []

        configure_args = ["--disable-examples"]
        if self.options.shared:
            configure_args.extend(["--disable-static", "--enable-shared"])
        else:
            configure_args.extend(["--enable-static", "--disable-shared"])

        self._autotools.configure(args=configure_args, configure_dir=self._source_subfolder)
        return self._autotools

    def _patch_sources(self):
        for patchdata in self.conan_data.get("patches",{}).get(self.version, []):
            tools.patch(**patchdata)

    def build(self):
        self._patch_sources()
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        os.unlink(os.path.join(self.package_folder, "lib", "libedit.la"))

    def package_info(self):
        self.cpp_info.libs = ["edit"]
        self.cpp_info.includedirs.append(os.path.join("include", "editline"))
