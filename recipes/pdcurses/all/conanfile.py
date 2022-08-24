from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanException, ConanInvalidConfiguration
import os
import re


class PDCursesConan(ConanFile):
    name = "pdcurses"
    description = "PDCurses - a curses library for environments that don't fit the termcap/terminfo model"
    topics = ("conan", "pdcurses", "curses", "ncurses")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://pdcurses.org/"
    license = "Unlicense", "MITX", "CC-BY-4.0", "GPL", "FSFUL"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_widec": [True, False],
        "with_sdl": [None, "1", "2"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_widec": False,
        "with_sdl": None,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os not in ("FreeBSD", "Linux"):
            del self.options.enable_widec

    def configure(self):
        if tools.is_apple_os(self.settings.os):
            raise ConanInvalidConfiguration("pdcurses does not support Apple")
        if self.options.with_sdl:
            raise ConanInvalidConfiguration("conan-center-index has no packages for sdl (yet)")
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def requirements(self):
        if self.settings.os in ("FreeBSD", "Linux"):
            self.requires("xorg/system")

    def build_requirements(self):
        if self.settings.compiler != "Visual Studio":
            self.build_requires("make/4.2.1")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("PDCurses-{}".format(self.version), self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        conf_args = [
            "--enable-shared" if self.options.shared else "--disable-shared",
            "--enable-widec" if self.options.enable_widec else "--disable-widec",
        ]
        self._autotools.configure(args=conf_args)
        return self._autotools

    def _build_windows(self):
        with tools.chdir(os.path.join(self._source_subfolder, "wincon")):
            args = []
            if self.options.shared:
                args.append("DLL=Y")
            args = " ".join(args)
            if self.settings.compiler == "Visual Studio":
                with tools.vcvars(self):
                    self.run("nmake -f Makefile.vc {}".format(args))
            else:
                self.run("{} libs {}".format(os.environ["CONAN_MAKE_PROGRAM"], args))

    def _patch_sources(self):
        if self.settings.compiler == "Visual Studio":
            tools.replace_in_file(os.path.join(self._source_subfolder, "wincon", "Makefile.vc"),
                                  "$(CFLAGS)",
                                  "$(CFLAGS) -{}".format(self.settings.compiler.runtime))
        tools.replace_in_file(os.path.join(self._source_subfolder, "x11", "Makefile.in"),
                              "$(INSTALL) -c -m 644 $(osdir)/libXCurses.a $(libdir)/libXCurses.a",
                              "-$(INSTALL) -c -m 644 $(osdir)/libXCurses.a $(libdir)/libXCurses.a")
        tools.replace_in_file(os.path.join(self._source_subfolder, "x11", "Makefile.in"),
                              "\nall:\t",
                              "\nall:\t{}\t#".format("@SHL_TARGETS@" if self.options.shared else "$(LIBCURSES)"))

    def build(self):
        self._patch_sources()
        if self.settings.os == "Windows":
            self._build_windows()
        else:
            with tools.chdir(os.path.join(self._source_subfolder, "x11")):
                autotools = self._configure_autotools()
                autotools.make()

    @property
    def _subsystem_folder(self):
        return {
            "Windows": "wincon",
        }.get(str(self.settings.os), "x11")

    @property
    def _license_text(self):
        readme = tools.files.load(self, os.path.join(self._source_subfolder, self._subsystem_folder, "README.md"))
        match = re.search(r"Distribution Status\n[\-]+(?:[\r\n])+((?:[0-9a-z .,;*]+[\r\n])+)", readme,
                          re.IGNORECASE | re.MULTILINE)
        if not match:
            raise ConanException("Cannot extract distribution status")
        return match.group(1).strip() + "\n"

    def package(self):
        tools.save(os.path.join(self.package_folder, "licenses", "LICENSE"), self._license_text)

        if self.settings.os == "Windows":
            self.copy(pattern="curses.h", src=self._source_subfolder, dst="include")
            self.copy(pattern="*.dll", dst="bin", keep_path=False)
            self.copy(pattern="*.lib", dst="lib", keep_path=False)
            self.copy(pattern="*.a", dst="lib", keep_path=False)

            if self.settings.compiler != "Visual Studio":
                os.rename(os.path.join(self.package_folder, "lib", "pdcurses.a"),
                          os.path.join(self.package_folder, "lib", "libpdcurses.a"))
        else:
            with tools.chdir(os.path.join(self._source_subfolder, "x11")):
                autotools = self._configure_autotools()
                autotools.install()
                tools.files.rmdir(self, os.path.join(self.package_folder, "bin"))

    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.libs = ["pdcurses"]
        elif self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.includedirs.append(os.path.join("include", "xcurses"))
            self.cpp_info.libs = ["XCurses"]
