# https://github.com/Alexpux/MINGW-packages/blob/master/mingw-w64-ghostscript/PKGBUILD
# https://bugs.ghostscript.com/show_bug.cgi?id=690716 --> make libgs for static libs?

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.files import copy, get, rm, rmdir, rename, apply_conandata_patches, export_conandata_patches
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
        "with_jpeg": ["libjpeg", "libjpeg-turbo"]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_jpeg": "libjpeg"
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

    def requirements(self):
        # pass
        # self.requires("fontconfig/2.13.93")
        # self.requires("freetype/2.12.1")
        # self.requires("lcms/2.13.1")
        if self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.4")
        elif self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9e")
        # self.requires("libpng/1.6.38")
        self.requires("libtiff/4.4.0")
        # self.requires("openjpeg/2.5.0")
        # self.requires("libidn/1.36")
        # self.requires("zlib/1.2.12")
        # self.requires("tesseract/5.2.0")
        # self.requires("leptonica/1.82.0")

        # self.requires("libiconv/1.17")
        # not handled: cups
        # optional:
        # cairo/1.17.4
        # gtk/system
        # gtk/4.7.0

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    # def build_requirements(self):
        # # make deps
        # freeglut/3.2.2
        # glu/system

    def source(self):
        # TODO: add the font package https://www.linuxfromscratch.org/blfs/view/svn/pst/gs.html
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)
        # 'freetype'
        # 'leptonica'
        # 'tesseract'
        # for directory in ['jpeg', 'lcms2mt', 'libpng', 'openjpeg', 'tiff', 'zlib']:
        # for directory in ['jpeg', 'openjpeg', 'tiff']:
        #     rmdir(self, os.path.join(self.source_folder, directory))
        for directory in ['jpeg', 'tiff']:
            rmdir(self, os.path.join(self.source_folder, directory))

    def generate(self):
        # https://ghostscript.readthedocs.io/en/gs10.0.0/Make.html#how-to-prepare-the-makefiles
        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--disable-compile-inits")
        tc.configure_args.append("--with-system-libtiff")
        tc.configure_args.append("--without-tesseract")
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
        # apply patches listed in conandata.yml
        # apply_conandata_patches(self)
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
        # autotools.install()
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
