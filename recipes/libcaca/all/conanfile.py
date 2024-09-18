import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import stdcpp_library
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, export_conandata_patches, get, rm, rmdir, replace_in_file, save
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.54.0"


class LibcacaConan(ConanFile):
    name = "libcaca"
    description = "Graphics library that outputs text instead of pixels"
    license = "WTFTPL AND GPL-2.0 AND ISC AND LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://caca.zoy.org/wiki/libcaca"
    topics = ("text-graphics", "ascii", "cli")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_cxx": [True, False],
        "enable_network": [True, False],
        "with_imlib2": [True, False],
        "with_ncurses": [True, False],
        "with_opengl": [True, False],
        "with_slang": [True, False],
        "with_x11": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_cxx": False,
        "enable_network": True,
        "with_imlib2": False,
        "with_ncurses": True,
        "with_opengl": False,
        "with_slang": False,
        "with_x11": False,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.with_x11

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.enable_cxx:
            self.settings.rm_safe("compiler.cppstd")
            self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")
        if self.options.get_safe("with_ncurses"):
            self.requires("ncurses/6.5")
        if self.options.get_safe("with_x11"):
            self.requires("xorg/system")
        if self.options.get_safe("with_opengl"):
            self.requires("opengl/system")
            self.requires("freeglut/3.4.0")
        if self.options.get_safe("with_imlib2"):
            self.requires("imlib2/1.12.3")
        if self.options.get_safe("with_slang"):
            self.requires("slang/2024.11.1")

    def validate(self):
        if is_msvc(self):
            # Requires additional MSBuild config
            raise ConanInvalidConfiguration("MSVC is not supported by the recipe. Contributions are welcome.")
        if self.options.with_ncurses and not self.dependencies["ncurses"].options.with_tinfo:
            raise ConanInvalidConfiguration("libcaca requires ncurses with tinfo support (-o ncurses/*:with_tinfo=True)")

    def build_requirements(self):
        self.tool_requires("libtool/2.4.7")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()

        tc = AutotoolsToolchain(self)
        def yes_no(v): return "yes" if v else "no"
        tc.configure_args.extend([
            f"--enable-debug={yes_no(self.settings.build_type in ['Debug', 'RelWithDebInfo'])}",
            f"--enable-cxx={yes_no(self.options.get_safe('enable_cxx'))}",
            f"--enable-network={yes_no(self.options.get_safe('enable_network'))}",
            f"--enable-win32={yes_no(self.settings.os == 'Windows')}",
            f"--enable-cocoa=no",  # compilation fails: https://github.com/cacalabs/libcaca/issues/62
            f"--enable-slang={yes_no(self.options.get_safe('with_slang'))}",
            f"--enable-ncurses={yes_no(self.options.get_safe('with_ncurses'))}",
            f"--enable-x11={yes_no(self.options.get_safe('with_x11'))}",
            f"--enable-gl={yes_no(self.options.get_safe('with_opengl'))}",
            f"--enable-imlib2={yes_no(self.options.get_safe('with_imlib2'))}",
            "--disable-kernel",  # kernel mode (default no)
            "--disable-vga",     # VGA support for kernel mode (autodetected)
            "--disable-plugins", # make X11 and GL drivers plugins (default disabled)
            "--disable-conio",   # DOS conio.h graphics support (autodetected)
            "--disable-doc",
            "--disable-cppunit",
            "--disable-zzuf",
            "--disable-csharp",
            "--disable-java",
            "--disable-python",
            "--disable-ruby",
        ])
        tc.generate()

        deps = AutotoolsDeps(self)
        deps.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

    def _patch_sources(self):
        # Disable examples and tests
        save(self, os.path.join(self.source_folder, "examples", "Makefile.in"),
             "all:\n\t\ninstall:\n\t\n")
        save(self, os.path.join(self.source_folder, "caca", "t", "Makefile.in"),
             "all:\n\t\ninstall:\n\t\n")
        if not self.options.get_safe("with_imlib2"):
            # These fail to build if Imlib2 is not available
            replace_in_file(self, os.path.join(self.source_folder, "src", "Makefile.in"),
                            "cacaview$(EXEEXT) img2txt$(EXEEXT)", "")

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING*", self.source_folder, os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.components["caca"].set_property("pkg_config_name", "caca")
        self.cpp_info.components["caca"].libs = ["caca"]
        self.cpp_info.components["caca"].requires = ["zlib::zlib"]
        if self.options.with_opengl:
            self.cpp_info.components["caca"].requires.extend(["opengl::opengl", "freeglut::freeglut"])
        if self.options.with_ncurses:
            self.cpp_info.components["caca"].requires.extend(["ncurses::libcurses", "ncurses::tinfo"])
        if self.options.get_safe("with_x11"):
            self.cpp_info.components["caca"].requires.append("xorg::x11")
        if self.options.get_safe("with_imlib2"):
            self.cpp_info.components["caca"].requires.append("imlib2::imlib2")
        if self.options.get_safe("with_slang"):
            self.cpp_info.components["caca"].requires.append("slang::slang")

        if self.options.enable_cxx:
            self.cpp_info.components["caca++"].set_property("pkg_config_name", "caca++")
            self.cpp_info.components["caca++"].libs = ["caca++"]
            self.cpp_info.components["caca++"].requires = ["caca"]
            if not self.options.shared and stdcpp_library(self):
                self.cpp_info.components["caca++"].requires.append(stdcpp_library(self))
