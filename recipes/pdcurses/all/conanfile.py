import os
import re

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration, ConanException
from conan.tools.apple import is_apple_os
from conan.tools.files import chdir, copy, get, load, replace_in_file, rmdir, save
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, msvc_runtime_flag, unix_path

required_conan_version = ">=1.53.0"


class PDCursesConan(ConanFile):
    name = "pdcurses"
    description = "PDCurses - a curses library for environments that don't fit the termcap/terminfo model"
    license = ("Unlicense", "MITX", "CC-BY-4.0", "GPL", "FSFUL")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://pdcurses.org/"
    topics = ("curses", "ncurses")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "enable_widec": [True, False], "with_sdl": [None, "1", "2"]}
    default_options = {"shared": False, "fPIC": True, "enable_widec": False, "with_sdl": None}

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os not in ("FreeBSD", "Linux"):
            self.options.rm_safe("enable_widec")

    def configure(self):
        if is_apple_os(self):
            raise ConanInvalidConfiguration("pdcurses does not support Apple")
        if self.options.with_sdl:
            raise ConanInvalidConfiguration("conan-center-index has no packages for sdl (yet)")
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.settings.os in ("FreeBSD", "Linux"):
            self.requires("xorg/system")

    def build_requirements(self):
        if not is_msvc(self):
            self.tool_requires("make/4.2.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--prefix={}".format(unix_path(self, self.package_folder)))
        tc.configure_args.append("--enable-widec" if self.options.enable_widec else "--disable-widec")
        if self.settings.os == "Windows" and self.options.shared:
            tc.make_args.append("DLL=Y")
        tc.generate()

    def _patch_sources(self):
        if is_msvc(self):
            replace_in_file(self, os.path.join(self.source_folder, "wincon", "Makefile.vc"),
                            "$(CFLAGS)",
                            "$(CFLAGS) -{}".format(msvc_runtime_flag(self)))
        replace_in_file(self, os.path.join(self.source_folder, "x11", "Makefile.in"),
                        "$(INSTALL) -c -m 644 $(osdir)/libXCurses.a $(libdir)/libXCurses.a",
                        "-$(INSTALL) -c -m 644 $(osdir)/libXCurses.a $(libdir)/libXCurses.a")
        replace_in_file(self, os.path.join(self.source_folder, "x11", "Makefile.in"),
                        "\nall:\t",
                        "\nall:\t{}\t#".format("@SHL_TARGETS@" if self.options.shared else "$(LIBCURSES)"))

    def build(self):
        self._patch_sources()
        with chdir(self, os.path.join(self.source_folder, "x11")):
            autotools = Autotools(self)
            autotools.configure(build_script_folder=os.path.join(self.source_folder, "x11"))
            autotools.make()

    @property
    def _subsystem_folder(self):
        return {"Windows": "wincon"}.get(str(self.settings.os), "x11")

    @property
    def _license_text(self):
        readme = load(self, os.path.join(self.source_folder, self._subsystem_folder, "README.md"))
        match = re.search(r"Distribution Status\n[\-]+(?:[\r\n])+((?:[0-9a-z .,;*]+[\r\n])+)", readme, re.IGNORECASE | re.MULTILINE)
        if not match:
            raise ConanException("Cannot extract distribution status")
        return match.group(1).strip() + "\n"

    def package(self):
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), self._license_text)

        if self.settings.os == "Windows":
            copy(self, "curses.h", dst=os.path.join(self.package_folder, "include"), src=self.source_folder)
            copy(self, "*.dll", dst=os.path.join(self.package_folder, "bin"), src=self.source_folder, keep_path=False)
            copy(self, "*.lib", dst=os.path.join(self.package_folder, "lib"), src=self.source_folder, keep_path=False)
            copy(self, "*.a", dst=os.path.join(self.package_folder, "lib"), src=self.source_folder, keep_path=False)
            if not is_msvc(self):
                os.rename(os.path.join(self.package_folder, "lib", "pdcurses.a"),
                          os.path.join(self.package_folder, "lib", "libpdcurses.a"))
        else:
            with chdir(self, os.path.join(self.source_folder, "x11")):
                autotools = Autotools(self)
                autotools.install()
                rmdir(self, os.path.join(self.package_folder, "bin"))

    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.libs = ["pdcurses"]
        elif self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.includedirs.append(os.path.join("include", "xcurses"))
            self.cpp_info.libs = ["XCurses"]
