# https://github.com/Alexpux/MINGW-packages/blob/master/mingw-w64-ghostscript/PKGBUILD
# https://bugs.ghostscript.com/show_bug.cgi?id=690716 --> make libgs for static libs?

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.files import copy, get, rm, rmdir, rename
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
from conan.tools.layout import basic_layout
import os


required_conan_version = ">=1.52.0"

class PackageConan(ConanFile):
    name = "ghostscript"
    description = "Ghostscript is an interpreter for the PostScript®  language and PDF files."
    license = "AGPL-3.0"
    # licence refrences from LICENCE file description and home page documentation as one of the two sides of the dual licensing model:
    # https://artifex.com/licensing/agpl/
    # http://git.ghostscript.com/?p=ghostpdl.git;a=blob;f=LICENSE;h=52e83a2ac365dba3fb6aa5b677625504fa3004ae;hb=HEAD
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.ghostscript.com/"
    topics = ("ghostscript", "postscript", "interpreter", "pdf", "ps", "pdl", "print")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_jpeg": ["native", "libjpeg", "libjpeg-turbo"],
        "with_tiff": ["native", "libtiff"],
        "with_openjpeg": ["native", "openjpeg"],
        "width_zlib": ["native", "zlib"],
        "with_freetype": ["native", "freetype"],
        "with_lcms": ["native", "lcms"],
        "with_png": ["native", "libpng"],
        "with_leptonica": ["native", "leptonica"],
        "with_tesseract": [False, "native", "tesseract"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_jpeg": "libjpeg",
        "with_tiff": "libtiff",
        "with_openjpeg": "openjpeg",
        "width_zlib": "zlib",
        "with_freetype": "native",
        "with_lcms": "native",
        "with_png": "native",
        "with_leptonica": "native",
        "with_tesseract": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        self.options["libtiff"].jpeg = self.options.with_jpeg
        # TODO: update leptonica with_jpeg interface to switch used jpeg dependency
        # self.options["leptonica"].with_jpeg = self.options.with_jpeg
        self.options["leptonica"].with_jpeg = True
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("autoconf/2.71")
        self.tool_requires("automake/1.16.5")
        self.tool_requires("libtool/2.4.7")

    def requirements(self):
        if self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.4")
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9e")
        if self.options.with_tiff == "libtiff":
            self.requires("libtiff/4.4.0")
        if self.options.with_openjpeg == "openjpeg":
            self.requires("openjpeg/2.5.0")
        if self.options.width_zlib == "zlib":
            self.requires("zlib/1.2.12")
        if self.options.with_freetype == "freetype":
            self.requires("freetype/2.12.1")
        if self.options.with_lcms == "lcms":
            self.requires("lcms/2.13.1")
        if self.options.with_png == "libpng":
            self.requires("libpng/1.6.38")
        if self.options.with_leptonica == "leptonica":
            self.requires("leptonica/1.82.0")
        if self.options.with_tesseract == "tesseract":
            self.requires("tesseract/5.2.0")

        # TODO: handle optional dependencies
        # self.requires("libiconv/1.17")
        # self.requires("libidn/1.36")
        # not handled: cups
        # cairo/1.17.4
        # gtk/system
        # gtk/4.7.0

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, 11)
        # TODO: makefile patching is nedded to enable those dependencies from conan,
        # since there are not found linker statements
        options_currently_only_supported_as_native = ['with_freetype', 'with_lcms', 'with_png', 'with_leptonica']
        for option in options_currently_only_supported_as_native:
            if self.options.get_safe(option) != "native":
                raise ConanInvalidConfiguration("option "+option+" is at the moment only supported as \"native\"")
        if self.options.with_tesseract == "tesseract":
            raise ConanInvalidConfiguration("option with_tesseract is at the moment only supported as \"False\" or \"native\"")
        if self.options.with_jpeg == "libjpeg-turbo":
            raise ConanInvalidConfiguration("libjpeg turbo is not supported at the mement. \
                Transitive dependency leptonica needs to be able to handle it as well. \
                Waiting here for PR: https://github.com/conan-io/conan-center-index/pull/13344")

    def source(self):
        # TODO: add the font package https://www.linuxfromscratch.org/blfs/view/svn/pst/gs.html
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)
        native_deps_to_remove = []
        if self.options.with_jpeg != "native":
            native_deps_to_remove.append('jpeg')
        if self.options.with_tiff != "native":
            native_deps_to_remove.append('tiff')
        if self.options.with_openjpeg != "native":
            native_deps_to_remove.append('openjpeg')
        if self.options.width_zlib != "native":
            native_deps_to_remove.append('zlib')
        if self.options.with_freetype != "native":
            native_deps_to_remove.append('freetype')
        if self.options.with_lcms != "native":
            native_deps_to_remove.append('lcms2mt')
        if self.options.with_png != "native":
            native_deps_to_remove.append('libpng')
        if self.options.with_leptonica != "native":
            native_deps_to_remove.append('leptonica')
        if self.options.with_tesseract != "native":
            native_deps_to_remove.append('tesseract')
        for directory in native_deps_to_remove:
            rmdir(self, os.path.join(self.source_folder, directory))

    def generate(self):
        # https://ghostscript.readthedocs.io/en/gs10.0.0/Make.html#how-to-prepare-the-makefiles
        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--disable-compile-inits")
        if self.options.with_tiff != "native":
            tc.configure_args.append("--with-system-libtiff")
        if self.options.with_tesseract == False:
            tc.configure_args.append("--without-tesseract")

        # we configure our install prefix, since `make soinstall` (which is not part of make all) is used to install headers,
        # which are not install during `make install`
        tc.configure_args.append("--prefix="+self.package_folder)
        tc.generate()
        tc = PkgConfigDeps(self)
        tc.generate()
        tc = AutotoolsDeps(self)
        tc.generate()
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

    def build(self):
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        # https://bugs.ghostscript.com/show_bug.cgi?id=705960
        autotools.make()
        if self.options.shared == True:
            autotools.make(target="so")
        if self.options.shared == False:
            autotools.make(target="libgs")

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        autotools = Autotools(self)
        autotools.make(target="soinstall")
        if self.options.shared == False:
            copy(self, pattern="gs.a", dst=os.path.join(self.package_folder, "lib"), src=os.path.join(self.build_folder, "bin"))
            rename(self, os.path.join(self.package_folder, "lib", "gs.a"), os.path.join(self.package_folder, "lib", "libgs.a"))
            rm(self, "*.so*", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = ["gs"]
        self.cpp_info.set_property("pkg_config_name", "libgs")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
            self.cpp_info.system_libs.append("dl")
