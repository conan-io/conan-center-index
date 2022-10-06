from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.layout import basic_layout
from conan.tools.build import cross_building
from conan.tools.gnu import (Autotools, AutotoolsDeps, PkgConfigDeps,
                             AutotoolsToolchain)
from conan.tools.env import VirtualRunEnv, VirtualBuildEnv
from conan.tools import files, microsoft, scm
import os

required_conan_version = ">=1.50.0"


class ImageMagicConan(ConanFile):
    name = "imagemagick"
    description = (
        "ImageMagick is a free and open-source software suite for displaying, "
        "converting, and editing raster image and vector image files")
    topics = ("imagemagick", "images", "manipulating")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://imagemagick.org"
    license = "ImageMagick"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "hdri": [True, False],
        "quantum_depth": [8, 16, 32],
        "with_zlib": [True, False],
        "with_bzlib": [True, False],
        "with_lzma": [True, False],
        "with_lcms": [True, False],
        "with_openexr": [True, False],
        "with_heic": [True, False],
        "with_jbig": [True, False],
        "with_jpeg": [None, "libjpeg", "libjpeg-turbo"],
        "with_openjp2": [True, False],
        "with_pango": [True, False],
        "with_png": [True, False],
        "with_tiff": [True, False],
        "with_webp": [True, False],
        "with_xml2": [True, False],
        "with_freetype": [True, False],
        "with_zstd": [True, False],
        "with_fftw": [True, False],
        "with_gdi32": [True, False],
        "with_raw": [True, False],
        "with_jxl": [True, False],
        "with_openmp": [True, False],
        "with_djvu": [True, False],
        "with_rsvg": [True, False],
        "with_autotrace": [True, False],
        "with_dps": [True, False],
        "with_flif": [True, False],
        "with_fpx": [True, False],
        "with_gslib": [True, False],
        "with_gvc": [True, False],
        "with_lqr": [True, False],
        "with_raqm": [True, False],
        "with_wmf": [True, False],
        "utilities": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "hdri": True,
        "quantum_depth": 16,
        "with_zlib": True,
        "with_bzlib": True,
        "with_lzma": True,
        "with_lcms": True,
        "with_openexr": True,
        "with_heic": True,
        "with_jbig": True,
        "with_jpeg": "libjpeg",
        "with_openjp2": True,
        "with_pango": True,
        "with_png": True,
        "with_tiff": True,
        "with_webp": False,
        "with_xml2": True,
        "with_freetype": True,
        "with_zstd": True,
        "with_fftw": True,
        "with_gdi32": True,
        "with_raw": False,
        "with_jxl": False,
        "with_openmp": False,
        "with_djvu": False,
        "with_rsvg": False,
        "with_autotrace": False,
        "with_dps": False,
        "with_flif": False,
        "with_fpx": False,
        "with_gslib": False,
        "with_gvc": False,
        "with_lqr": False,
        "with_raqm": False,
        "with_wmf": False,
        "utilities": True,
    }
    exports_sources = "patches/*"

    def layout(self):
        basic_layout(self, src_folder="src")

    @property
    def _modules(self):
        return ["Magick++", "MagickWand", "MagickCore"]

    def validate(self):
        if self.settings.os == "Windows" and scm.Version(
                self.version) < "7.1.0-45":
            raise ConanInvalidConfiguration(
                "This version of ImageMagick can't be built on Windows!")

        # TODO: Add support to these libraries with ImageMagick
        unsupported_libs = {
            "raw": self.options.with_raw,
            "jxl": self.options.with_jxl,
            "djvu": self.options.with_djvu,
            "rsvg": self.options.with_rsvg,
            "autotrace": self.options.with_autotrace,
            "dps": self.options.with_dps,
            "flif": self.options.with_flif,
            "fpx": self.options.with_fpx,
            "gslib": self.options.with_gslib,
            "gvc": self.options.with_gvc,
            "lqr": self.options.with_lqr,
            "raqm": self.options.with_raqm,
            "wmf": self.options.with_wmf,
        }

        for lib, is_required in unsupported_libs.items():
            if is_required:
                raise ConanInvalidConfiguration(
                    f"Building ImageMagick with '{lib}' package is not supported (yet)."
                )

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

        if microsoft.is_msvc(self):
            self.options.with_openmp = False
        if self.settings.os != "Windows":
            self.options.with_gdi32 = False

        if self.settings.os == "Windows":
            self.win_bash = True

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if hasattr(self, "settings_build"):
            self.tool_requires("automake/1.16.5")
        if self._settings_build.os == "Windows" and not self.conf.get(
                "tools.microsoft.bash:path", default=False, check_type=str):
            self.tool_requires("msys2/cci.latest")
        self.tool_requires("pkgconf/1.7.4")

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.12")
        if self.options.with_bzlib:
            self.requires("bzip2/1.0.8")
        if self.options.with_lzma:
            self.requires("xz_utils/5.2.5")
        if self.options.with_lcms:
            self.requires("lcms/2.13.1")
        if self.options.with_openexr:
            self.requires("openexr/3.1.5")
        if self.options.with_heic:
            self.requires("libheif/1.13.0")
        if self.options.with_jbig:
            self.requires("jbig/20160605")
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.4")
        if self.options.with_openjp2:
            self.requires("openjpeg/2.5.0")
        if self.options.with_pango:
            self.requires("pango/1.50.10")
        if self.options.with_png:
            self.requires("libpng/1.6.38")
        if self.options.with_tiff:
            self.requires("libtiff/4.4.0")
        if self.options.with_webp:
            self.requires("libwebp/1.2.4")
        if self.options.with_xml2:
            self.requires("libxml2/2.9.14")
        if self.options.with_freetype:
            self.requires("freetype/2.12.1")
        if self.options.with_zstd:
            self.requires("zstd/1.5.2")
        if self.options.with_fftw:
            self.requires("fftw/3.3.9")

    def source(self):
        files.get(self,
                  **self.conan_data["sources"][self.version],
                  destination=self.source_folder,
                  strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        env = tc.environment()

        if microsoft.is_msvc(self):
            # FIXME: it seems that PKG_CONFIG_PATH is added as a unix style path
            env.unset("PKG_CONFIG_PATH")
            env.define("PKG_CONFIG_PATH", self.generators_folder)

            # FIXME: otherwise configure reports "ld" as its linker
            env.define("LD", "link")
            # use "compile" script as a compiler driver for cl, since autotools
            # doesn't work well with cl
            compile_script = microsoft.unix_path(
                self, os.path.join(self.source_folder, "config", "compile"))
            env.define("CC", f'{compile_script} cl.exe -nologo')
            env.define("CXX", f"{compile_script} cl.exe -nologo")

            env.append("CXXFLAGS", "-FS")
            env.append("CFLAGS", "-FS")

        tc.generate(env)

        # FIXME: without this, AutotoolsDeps generates unix style path
        self.win_bash = None
        td = AutotoolsDeps(self)

        # AutotoolsDeps uses /LIBPATH: which is a linker argument that
        # will be pased incorrectly to the msvc compiler by autotools
        # this replaces /LIBPATH: by  -L, which the "compile" script will
        # fix for us, and replaces /I by -I, which works with the compile script
        env = td.environment
        if microsoft.is_msvc(self):
            ldflags = env.vars(self)["LDFLAGS"].replace("/LIBPATH:", "-L").replace("\\", "/")
            cppflags = env.vars(self)["CPPFLAGS"].replace("/I", "-I").replace("\\", "/")
            env.define("LDFLAGS", ldflags)
            env.define("CPPFLAGS", cppflags)

        # AutotoolsDeps adds all dependencies in the libs variable.
        # all these libs make `libtool` do the extra work of finding where they
        # are, which seems to fail on Windows (and macOS as well, due to
        # different reasons). this variable is not needed anyways, since
        # autotools will link against the required libraries by itself
        env.unset("LIBS")

        td.generate()

        self.win_bash = True

        pd = PkgConfigDeps(self)
        pd.generate()

        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

    def build(self):
        files.apply_conandata_patches(self)

        if microsoft.is_msvc(self):
            # jpeg library is named as libjpeg in Windows
            files.replace_in_file(
                self, os.path.join(self.source_folder, "configure"), "-ljpeg",
                "-llibjpeg")

            if self.options.with_gdi32:
                # emf.c is a c++ source code utilizing the c++ header gdiplus.h
                # we change emf.c extension to cpp so that msvc compiles it as
                # c++ code
                files.replace_in_file(
                    self, os.path.join(self.source_folder, "Makefile.in"), "emf.c",
                    "emf.cpp")

                files.rename(
                    self, os.path.join(self.source_folder, "coders", "emf.c"),
                    os.path.join(self.source_folder, "coders", "emf.cpp"))

        # FIXME: change pangocairo pkg-config component name in the pango recipe
        if os.path.exists(
                os.path.join(self.generators_folder, "pango-pangocairo.pc")):
            files.rename(
                self,
                os.path.join(self.generators_folder, "pango-pangocairo.pc"),
                os.path.join(self.generators_folder, "pangocairo.pc"))

        autotools = Autotools(self)

        def yes_no(o):
            return "yes" if o else "no"

        args = [
            "--disable-docs",
            "--with-perl=no",
            "--with-x=no",
            "--with-fontconfig=no",
            f"--enable-shared={format(yes_no(self.options.shared))}",
            f"--enable-static={format(yes_no(not self.options.shared))}",
            f"--enable-hdri={format(yes_no(self.options.hdri))}",
            f"--with-quantum-depth={format(self.options.quantum_depth)}",
            f"--with-zlib={format(yes_no(self.options.with_zlib))}",
            f"--with-bzlib={format(yes_no(self.options.with_bzlib))}",
            f"--with-lzma={format(yes_no(self.options.with_lzma))}",
            f"--with-lcms={format(yes_no(self.options.with_lcms))}",
            f"--with-openexr={format(yes_no(self.options.with_openexr))}",
            f"--with-heic={format(yes_no(self.options.with_heic))}",
            f"--with-jbig={format(yes_no(self.options.with_jbig))}",
            f"--with-jpeg={format(yes_no(self.options.with_jpeg))}",
            f"--with-openjp2={format(yes_no(self.options.with_openjp2))}",
            f"--with-pango={format(yes_no(self.options.with_pango))}",
            f"--with-png={format(yes_no(self.options.with_png))}",
            f"--with-tiff={format(yes_no(self.options.with_tiff))}",
            f"--with-webp={format(yes_no(self.options.with_webp))}",
            f"--with-xml={format(yes_no(self.options.with_xml2))}",
            f"--with-freetype={format(yes_no(self.options.with_freetype))}",
            f"--with-djvu={format(yes_no(self.options.with_djvu))}",
            f"--with-utilities={format(yes_no(self.options.utilities))}",
            f"--with-zstd={format(yes_no(self.options.with_zstd))}",
            f"--with-fftw={format(yes_no(self.options.with_fftw))}",
            f"--with-gdi32={format(yes_no(self.options.with_gdi32))}",
            f"--with-rsvg={format(yes_no(self.options.with_rsvg))}",
            f"--with-autotrace={format(yes_no(self.options.with_autotrace))}",
            f"--with-dps={format(yes_no(self.options.with_dps))}",
            f"--with-flif={format(yes_no(self.options.with_flif))}",
            f"--with-fpx={format(yes_no(self.options.with_fpx))}",
            f"--with-gslib={format(yes_no(self.options.with_gslib))}",
            f"--with-gvc={format(yes_no(self.options.with_gvc))}",
            f"--with-jxl={format(yes_no(self.options.with_jxl))}",
            f"--with-lqr={format(yes_no(self.options.with_lqr))}",
            f"--with-raqm={format(yes_no(self.options.with_raqm))}",
            f"--with-wmf={format(yes_no(self.options.with_wmf))}",
            f"--with-raw={format(yes_no(self.options.with_raw))}"
        ]
        if not self.options.with_openmp:
            args.append("--disable-openmp")

        autotools.configure(args=args)
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        if microsoft.is_msvc(self):
            # FIXME: On Windows, Autotools sets DESTDIR as a Windows path
            autotools.install(
                [f"DESTDIR={microsoft.unix_path(self, self.package_folder)}"])
        else:
            autotools.install()

        # remove undesired files
        files.rmdir(self, os.path.join(self.package_folder, "lib",
                                       "pkgconfig"))  # pc files
        files.rmdir(self, os.path.join(self.package_folder, "etc"))
        files.rmdir(self, os.path.join(self.package_folder, "share"))
        files.rm(self, "*.la", os.path.join(self.package_folder, "lib"))

        if microsoft.is_msvc(self) and self.options.shared:
            for m in self._modules:
                files.rename(
                    self,
                    os.path.join(self.package_folder, "lib",
                                 f"{self._libname(m)}.dll.lib"),
                    os.path.join(self.package_folder, "lib",
                                 f"{self._libname(m)}.lib"))

        files.copy(self,
                   pattern="LICENSE",
                   dst=os.path.join(self.package_folder, "licenses"),
                   src=self.source_folder)

    def _libname(self, library):
        suffix = "HDRI" if self.options.hdri else ""
        return "{}-{}.Q{}{}".format(
            library,
            scm.Version(self.version).major,
            self.options.quantum_depth,
            suffix,
        )

    def package_info(self):
        # FIXME model official FindImageMagick https://cmake.org/cmake/help/latest/module/FindImageMagick.html
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.PATH.append(bin_path)

        self.cpp_info.names["cmake_find_package_multi"] = "ImageMagick"
        self.cpp_info.set_property("cmake_file_name", "ImageMagick")
        self.cpp_info.set_property("cmake_target_name", "ImageMagick")

        core_requires = []
        if self.options.with_zlib:
            core_requires.append("zlib::zlib")
        if self.options.with_bzlib:
            core_requires.append("bzip2::bzip2")
        if self.options.with_lzma:
            core_requires.append("xz_utils::xz_utils")
        if self.options.with_lcms:
            core_requires.append("lcms::lcms")
        if self.options.with_openexr:
            core_requires.append("openexr::openexr")
        if self.options.with_heic:
            core_requires.append("libheif::libheif")
        if self.options.with_jbig:
            core_requires.append("jbig::jbig")
        if self.options.with_jpeg:
            core_requires.append("{0}::{0}".format(self.options.with_jpeg))
        if self.options.with_openjp2:
            core_requires.append("openjpeg::openjpeg")
        if self.options.with_pango:
            core_requires.append("pango::pango")
        if self.options.with_png:
            core_requires.append("libpng::libpng")
        if self.options.with_tiff:
            core_requires.append("libtiff::libtiff")
        if self.options.with_webp:
            core_requires.append("libwebp::libwebp")
        if self.options.with_xml2:
            core_requires.append("libxml2::libxml2")
        if self.options.with_freetype:
            core_requires.append("freetype::freetype")
        if self.options.with_zstd:
            core_requires.append("zstd::zstdlib")
        if self.options.with_fftw:
            core_requires.append("fftw::fftwlib")

        self.cpp_info.components["MagickCore"].names[
            "cmake_find_package_multi"] = "MagickCore"
        self.cpp_info.components["MagickCore"].set_property(
            "cmake_target_name", "ImageMagick::MagickCore")

        if self.settings.os == "Linux":
            self.cpp_info.components["MagickCore"].system_libs.append(
                "pthread")

        self.cpp_info.components["MagickCore"].defines.append(
            f"MAGICKCORE_QUANTUM_DEPTH={self.options.quantum_depth}")
        self.cpp_info.components["MagickCore"].defines.append(
            f"MAGICKCORE_HDRI_ENABLE={int(bool(self.options.hdri))}")
        self.cpp_info.components["MagickCore"].defines.append(
            "_MAGICKDLL_=1" if self.options.shared else "_MAGICKLIB_=1")

        imagemagick_include_dir = (
            f"include/ImageMagick-{scm.Version(self.version).major}")

        self.cpp_info.components["MagickCore"].includedirs = [
            imagemagick_include_dir
        ]
        self.cpp_info.components["MagickCore"].libs.append(
            self._libname("MagickCore"))
        self.cpp_info.components["MagickCore"].requires = core_requires
        self.cpp_info.components["MagickCore"].names["pkg_config"] = [
            "MagicCore"
        ]
        self.cpp_info.components["MagickCore"].set_property(
            "pkg_config_name", "MagickCore")

        if self.options.with_openmp:
            self.cpp_info.components["MagickCore"].cflags.append("-fopenmp")
            self.cpp_info.components["MagickCore"].cxxflags.append("-fopenmp")
            self.cpp_info.components["MagickCore"].sharedlinkflags.append("-fopenmp")

        if self.settings.os == "Windows":
            self.cpp_info.components["MagickCore"].system_libs.append("urlmon")

        if self.options.with_gdi32:
            self.cpp_info.components["MagickCore"].system_libs.append("gdi32")

        self.cpp_info.components["MagickWand"].names[
            "cmake_find_package_multi"] = "MagickWand"
        self.cpp_info.components["MagickWand"].set_property(
            "cmake_target_name", "ImageMagick::MagickWand")

        self.cpp_info.components["MagickWand"].includedirs = [
            imagemagick_include_dir + "/MagickWand"
        ]
        self.cpp_info.components["MagickWand"].libs = [
            self._libname("MagickWand")
        ]
        self.cpp_info.components["MagickWand"].requires = ["MagickCore"]
        self.cpp_info.components["MagickWand"].names["pkg_config"] = [
            "MagickWand"
        ]
        self.cpp_info.components["MagickWand"].set_property(
            "pkg_config_name", "MagickWand")

        self.cpp_info.components["Magick++"].names[
            "cmake_find_package_multi"] = "Magick++"
        self.cpp_info.components["Magick++"].set_property(
            "cmake_target_name", "ImageMagick::Magick++")
        self.cpp_info.components["Magick++"].includedirs = [
            imagemagick_include_dir + "/Magick++"
        ]
        self.cpp_info.components["Magick++"].libs = [self._libname("Magick++")]
        self.cpp_info.components["Magick++"].requires = ["MagickWand"]
        self.cpp_info.components["Magick++"].names["pkg_config"] = ["Magick++"]
        self.cpp_info.components["Magick++"].set_property(
            "pkg_config_name", "Magick++")
