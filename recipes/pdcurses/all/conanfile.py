import os
import re
import textwrap

from conan import ConanFile, conan_version
from conan.errors import ConanInvalidConfiguration, ConanException
from conan.tools.apple import is_apple_os
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import chdir, copy, get, load, replace_in_file, rmdir, save, rename
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, msvc_runtime_flag, unix_path, NMakeToolchain, NMakeDeps

required_conan_version = ">=1.53.0"


class PDCursesConan(ConanFile):
    name = "pdcurses"
    description = "PDCurses - a curses library for environments that don't fit the termcap/terminfo model"
    license = ("LicenseRef-LICENSE")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://pdcurses.org/"
    topics = ("curses", "ncurses")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_widec": [True, False],
        "with_sdl": [True, False],
        "with_x11": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_widec": False,
        "with_sdl": False,
        "with_x11": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os not in ["FreeBSD", "Linux"]:
            del self.options.with_x11

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")
        if is_apple_os(self):
            # Only the sdl2 subsystem is supported on macOS
            self.options.with_sdl = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_sdl:
            self.requires(f"sdl/2.28.2")
        if self.options.get_safe("with_x11"):
            self.requires("xorg/system")

    def validate(self):
        if self.options.with_sdl and conan_version < "2.0.10":
            raise ConanInvalidConfiguration("with_sdl option requires conan >= 2.0.10")
        if self.options.with_sdl and self.settings.os == "Windows":
            raise ConanInvalidConfiguration("with_sdl option is not yet supported on Windows")
        if self.settings.os != "Windows" and not self.options.get_safe("with_x11") and not self.options.with_sdl:
            raise ConanInvalidConfiguration("At least one of with_x11 or with_sdl options must be enabled")

    def build_requirements(self):
        if not is_msvc(self):
            if not self.conf.get("tools.gnu:make_program", check_type=str):
                self.tool_requires("make/4.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if is_msvc(self):
            tc = NMakeToolchain(self)
            tc.generate()
            deps = NMakeDeps(self)
            deps.generate()
        else:
            tc = AutotoolsToolchain(self)
            tc.configure_args.append("--prefix={}".format(unix_path(self, self.package_folder)))
            tc.configure_args.append("--enable-widec" if self.options.enable_widec else "--disable-widec")
            if self.settings.os == "Windows" and self.options.shared:
                tc.make_args.append("DLL=Y")
            tc.generate()
            if self.options.with_sdl:
                from conan.tools.gnu import MakeDeps
                self.dependencies["sdl"].cpp_info.includedirs.append(os.path.join("include", "SDL2"))
                deps = MakeDeps(self)
                deps.generate()

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
        if is_msvc(self):
            self._build_msvc()
        else:
            self._build_autotools()

    def _build_autotools(self):
        if self.options.get_safe("with_x11"):
            with chdir(self, os.path.join(self.source_folder, "x11")):
                autotools = Autotools(self)
                autotools.configure(build_script_folder=os.path.join(self.source_folder, "x11"))
                autotools.make()
        if self.options.with_sdl:
            with chdir(self, os.path.join(self.source_folder, "sdl2")):
                replace_in_file(self, "Makefile",
                                "BUILD		=",
                                 textwrap.dedent(f"""\
                                    include {self.generators_folder}/conandeps.mk
                                    CFLAGS              += $(CONAN_CFLAGS)
                                    CFLAGS              += $(addprefix -I, $(CONAN_INCLUDE_DIRS))
                                    CPPFLAGS            += $(addprefix -D, $(CONAN_DEFINES))
                                    LDFLAGS             += $(addprefix -L, $(CONAN_LIB_DIRS))
                                    LDLIBS              += $(addprefix -l, $(CONAN_LIBS))
                                    EXELINKFLAGS        += $(CONAN_EXELINKFLAGS)
                                    BUILD		="""))
                autotools = Autotools(self)
                args = []
                if self.options.enable_widec:
                    args.append("WIDE=Y")
                autotools.make(args=args)


    def _build_msvc(self):
        with chdir(self, os.path.join(self.source_folder, "wincon")):
            args = []
            if self.options.shared:
                args.append("DLL=Y")
            if self.options.enable_widec:
                args.append("WIDE=Y")
            args = " ".join(args)
            if is_msvc(self):
                self.run(f"nmake -f Makefile.vc {args}")
            else:
                self.run(f"make libs {args}")

    @property
    def _license_text(self):
        readme = load(self, os.path.join(self.source_folder, "README.md"))
        match = re.search(r"Legal Stuff\n[\-]+[\r\n]+((?:.*\n)+)\n\nMaintainer", readme, re.IGNORECASE | re.MULTILINE)
        license = match.group(1).strip() + "\n"
        if self.options.get_safe("with_x11"):
            readme = load(self, os.path.join(self.source_folder, "x11", "README.md"))
            match = re.search(r"Distribution Status\n[\-]+[\r\n]+((?:[0-9a-z .,;*]+[\r\n])+)", readme, re.IGNORECASE | re.MULTILINE)
            if not match:
                raise ConanException("Cannot extract distribution status")
            license += "\n" + match.group(1).strip() + "\n"
        return license


    def package(self):
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), self._license_text)
        if self.options.get_safe("with_x11"):
            with chdir(self, os.path.join(self.source_folder, "x11")):
                autotools = Autotools(self)
                autotools.install()
                rmdir(self, os.path.join(self.package_folder, "bin"))
        copy(self, "curses.h", dst=os.path.join(self.package_folder, "include"), src=self.source_folder)
        build_folders = []
        if self.settings.os == "Windows":
            build_folders += [self.source_folder]
        if self.options.with_sdl:
            build_folders += [os.path.join(self.source_folder, "sdl2")]
        for build_folder in build_folders:
            copy(self, "*.dll", dst=os.path.join(self.package_folder, "bin"), src=build_folder, keep_path=False)
            for pattern in ["*.lib", "*.a", "*.so*", "*.dylib*"]:
                copy(self, pattern, dst=os.path.join(self.package_folder, "lib"), src=build_folder, keep_path=False)
        if (self.settings.os == "Windows" or self.options.with_sdl) and not is_msvc(self):
            rename(self, os.path.join(self.package_folder, "lib", "pdcurses.a"),
                         os.path.join(self.package_folder, "lib", "libpdcurses.a"))

    def package_info(self):
        if self.settings.os == "Windows" or self.options.with_sdl:
            self.cpp_info.libs = ["pdcurses"]
        if self.options.get_safe("with_x11"):
            self.cpp_info.includedirs.append(os.path.join("include", "xcurses"))
            self.cpp_info.libs += ["XCurses"]
