import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import get, rmdir, replace_in_file, export_conandata_patches, apply_conandata_patches, copy, move_folder_contents, mkdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class ImageMagicConan(ConanFile):
    name = "imagemagick"
    description = ("ImageMagick is a free and open-source software suite for displaying, "
                   "converting, and editing raster image and vector image files")
    license = "ImageMagick"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://imagemagick.org"
    topics = ("images", "manipulating")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],

        "cipher_support": [True, False],
        "dpc_support": [True, False],
        "exclude_deprecated": [True, False],
        "hdri": [True, False],
        "magickpp": [True, False],
        "quantum_depth": [8, 16, 32],
        "security_policy": ["open", "limited", "secure", "websafe"],
        "utilities": [True, False],
        "with_64bit_channel_mask_support": [True, False],

        "with_bzlib": [True, False],
        "with_cairo": [True, False],
        "with_djvu": [True, False],
        "with_fftw": [True, False],
        "with_fontconfig": [True, False],
        "with_freetype": [True, False],
        "with_heic": [True, False],
        "with_jbig": [True, False],
        "with_jpeg": [None, "libjpeg", "libjpeg-turbo"],
        "with_jxl": [True, False],
        "with_lcms": [True, False],
        "with_lzma": [True, False],
        "with_opencl": [True, False],
        "with_openexr": [True, False],
        "with_openjp2": [True, False],
        "with_openmp": [True, False],
        "with_pango": [True, False],
        "with_png": [True, False],
        "with_raw": [True, False],
        "with_threads": [True, False],
        "with_tiff": [True, False],
        "with_webp": [True, False],
        "with_x11": [True, False],
        "with_xml2": [True, False],
        "with_zlib": [True, False],
        "with_zstd": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,

        "cipher_support": True,
        "dpc_support": True,
        "exclude_deprecated": True,
        "hdri": True,
        "magickpp": True,
        "quantum_depth": 16,
        "security_policy": "open",
        "utilities": True,
        "with_64bit_channel_mask_support": False,

        "with_bzlib": True,
        "with_cairo": True,
        "with_djvu": False,
        "with_fftw": True,
        "with_fontconfig": True,
        "with_freetype": True,
        "with_heic": True,
        "with_jbig": True,
        "with_jpeg": "libjpeg",
        "with_jxl": False,  # FIXME: re-enable once migrated
        "with_lcms": True,
        "with_lzma": True,
        "with_opencl": True,
        "with_openexr": True,
        "with_openjp2": True,
        "with_openmp": True,
        "with_pango": False,  # FIXME: re-enable once migrated
        "with_png": True,
        "with_raw": True,
        "with_threads": True,
        "with_tiff": True,
        "with_webp": True,
        "with_x11": True,
        "with_xml2": True,
        "with_zlib": True,
        "with_zstd": True,
    }

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
        if not self.options.magickpp:
            self.settings.rm_safe("compiler.cppstd")
            self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # None of the dependencies need transitive_headers=True
        if self.options.with_bzlib:
            self.requires("bzip2/1.0.8")
        if self.options.with_cairo:
            self.requires("cairo/1.18.0")
        if self.options.with_fftw:
            self.requires("fftw/3.3.10")
        if self.options.with_fontconfig:
            self.requires("fontconfig/2.14.2")
        if self.options.with_freetype:
            self.requires("freetype/2.13.2")
        if self.options.with_heic:
            self.requires("libheif/1.16.2")
        if self.options.with_jbig:
            self.requires("jbig/20160605")
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/3.0.1")
        if self.options.with_jxl:
            self.requires("libjxl/0.8.2")
        if self.options.with_lcms:
            self.requires("lcms/2.14")
        if self.options.with_lzma:
            self.requires("xz_utils/5.4.5")
        if self.options.with_opencl:
            self.requires("opencl-headers/2023.04.17")
        if self.options.with_openexr:
            self.requires("openexr/3.2.1")
        if self.options.with_openjp2:
            self.requires("openjpeg/2.5.0")
        if self.options.with_openmp:
            if self.settings.compiler in ["clang", "apple-clang"]:
                self.requires("llvm-openmp/17.0.4")
        if self.options.with_pango:
            self.requires("pango/1.48.5")
        if self.options.with_png:
            self.requires("libpng/1.6.40")
        if self.options.with_raw:
            self.requires("libraw/0.21.1")
        if self.options.with_tiff:
            self.requires("libtiff/4.6.0")
        if self.options.with_webp:
            self.requires("libwebp/1.3.2")
        if self.options.with_xml2:
            self.requires("libxml2/2.12.2")
        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_zstd:
            self.requires("zstd/1.5.5")
        if self.options.with_djvu:
            self.output.warning("Conan package for djvu is not available, this package will be used from system.")
        if self.options.get_safe("with_x11"):
            self.requires("xorg/system")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.19 <4]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.1.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["source"], strip_root=True)

        # Copy CMake build scripts from https://github.com/Cyriuz/ImageMagick
        cmake_sources = self.source_path.joinpath("_cmake")
        get(self, **self.conan_data["sources"][self.version]["cmake"], strip_root=True, destination=cmake_sources)
        for path in sorted(cmake_sources.rglob("CMakeLists.txt")) + sorted(cmake_sources.rglob("*.cmake")):
            new_path = self.source_path.joinpath(path.relative_to(cmake_sources))
            new_path.parent.mkdir(parents=True, exist_ok=True)
            path.rename(new_path)
        rmdir(self, cmake_sources)

    def generate(self):
        venv = VirtualBuildEnv(self)
        venv.generate()

        tc = CMakeToolchain(self)
        tc.variables["MAGICK_BUILD_STATIC"] = not self.options.shared
        tc.variables["BUILD_MAGICKPP"] = self.options.magickpp
        tc.variables["BUILD_UTILITIES"] = self.options.utilities
        tc.variables["BUILD_TESTS"] = False

        tc.variables["CIPHER_SUPPORT"] = self.options.cipher_support
        tc.variables["DPC_SUPPORT"] = self.options.dpc_support
        tc.variables["EXCLUDE_DEPRECATED"] = self.options.exclude_deprecated
        tc.variables["MAGICKCORE_QUANTUM_DEPTH"] = self.options.quantum_depth
        tc.variables["MAGICK_HDRI_ENABLE"] = self.options.hdri
        tc.variables["SECURITY_POLICY"] = self.options.security_policy
        tc.variables["WITH_64BIT_CHANNEL_MASK_SUPPORT"] = self.options.with_64bit_channel_mask_support

        tc.variables["AUTOTRACE_DELEGATE"] = False
        tc.variables["BZLIB_DELEGATE"] = self.options.with_bzlib
        tc.variables["CAIRO_DELEGATE"] = self.options.with_cairo
        tc.variables["DJVU_DELEGATE"] = self.options.with_djvu
        tc.variables["DPS_DELEGATE"] = False
        tc.variables["FFTW_DELEGATE"] = self.options.with_fftw
        tc.variables["FLIF_DELEGATE"] = False
        tc.variables["FONTCONFIG_DELEGATE"] = self.options.with_fontconfig
        tc.variables["FPX_DELEGATE"] = False
        tc.variables["FREETYPE_DELEGATE"] = self.options.with_freetype
        tc.variables["GS_DELEGATE"] = False
        tc.variables["GVC_DELEGATE"] = False
        tc.variables["HasJEMALLOC"] = False
        tc.variables["HasUMEM"] = False
        tc.variables["HEIC_DELEGATE"] = self.options.with_heic
        tc.variables["JBIG_DELEGATE"] = self.options.with_jbig
        tc.variables["JPEG_DELEGATE"] = self.options.with_jpeg
        tc.variables["JXL_DELEGATE"] = self.options.with_jxl
        tc.variables["LCMS_DELEGATE"] = self.options.with_lcms
        tc.variables["LIBOPENJP2_DELEGATE"] = self.options.with_openjp2
        tc.variables["LQR"] = False
        tc.variables["LTDL_DELEGATE"] = False
        tc.variables["LZMA_DELEGATE"] = self.options.with_lzma
        tc.variables["OPENCLLIB_DELEGATE"] = self.options.with_opencl
        tc.variables["OPENEXR_DELEGATE"] = self.options.with_openexr
        tc.variables["OPENMP_SUPPORT"] = self.options.with_openmp
        tc.variables["PANGO_DELEGATE"] = self.options.with_pango
        tc.variables["PANGOCAIRO_DELEGATE"] = self.options.with_pango and self.dependencies["pango"].options.with_cairo
        tc.variables["PNG_DELEGATE"] = self.options.with_png
        tc.variables["RAQM_DELEGATE"] = False
        tc.variables["RAW_R_DELEGATE"] = self.options.with_raw
        tc.variables["RSVG_DELEGATE"] = False
        tc.variables["THREADS_SUPPORT"] = self.options.with_threads
        tc.variables["TIFF_DELEGATE"] = self.options.with_tiff
        tc.variables["WEBP_DELEGATE"] = self.options.with_webp
        tc.variables["WEBPMUX_DELEGATE"] = False
        tc.variables["WMF_DELEGATE"] = False
        tc.variables["X11_DELEGATE"] = self.options.get_safe("with_x11", False)
        tc.variables["XML_DELEGATE"] = self.options.with_xml2
        tc.variables["ZLIB_DELEGATE"] = self.options.with_zlib
        tc.variables["ZSTD_DELEGATE"] = self.options.with_zstd
        tc.generate()

        # TODO: fix this bug in the libheif recipe
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.dependencies["libheif"].cpp_info.components["heif"].system_libs.append("dl")

        if self.options.with_raw:
            self.dependencies["libraw"].cpp_info.includedirs.append(
                os.path.join(self.dependencies["libraw"].cpp_info.includedir, "libraw")
            )

        cmake_names = {
            "autotrace": "AUTOTRACE",
            "bzip2": "BZip2",
            "cairo": "Cairo",
            "djvu": "DJVU",
            "dps": "DPS",
            "fftw": "FFTW",
            "flashpix": "FlashPIX",
            "flif": "FLIF",
            "fontconfig": "Fontconfig",
            "freetype": "Freetype",
            "ghostscript": "Ghostscript",
            "gvc": "GVC",
            "jbig": "JBIG",
            "jemalloc": "Jemalloc",
            "jpeg": "JPEG",
            "lcms": "lcms",
            "libheif": "libheif",
            "libjxl": "libjxl",
            "libpng": "PNG",
            "libraw": "libraw",
            "libtiff": "TIFF",
            "libwebp": "WebP",
            "libxml2": "LibXml2",
            "lqr": "Lqr",
            "ltdl": "LTDL",
            "opencl-headers": "OpenCL",
            "openexr": "OpenEXR",
            "openjpeg": "OpenJPEG",
            "pango": "Pango",
            "raqm": "RAQM",
            "rsvg": "Rsvg",
            "umem": "UMEM",
            "webpmux": "WEBPMUX",
            "wmf": "WMF",
            "xz_utils": "LibLZMA",
            "zlib": "ZLIB",
            "zstd": "zstd",
        }
        deps = CMakeDeps(self)
        for dep, cmake_name in cmake_names.items():
            deps.set_property(dep, "cmake_file_name", cmake_name)
            deps.set_property(dep, "cmake_target_name", f"{cmake_name}::{cmake_name}")
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # PangoCairo is provided by Pango
        replace_in_file(self, os.path.join(self.source_folder, "cmake", "delegates.cmake"),
                        "magick_find_delegate(DELEGATE PANGOCAIRO_DELEGATE NAME PangoCairo DEFAULT FALSE)\n",
                        "magick_find_delegate(DELEGATE PANGOCAIRO_DELEGATE NAME Pango DEFAULT FALSE TARGETS Pango::Pango)\n")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        # License files are installed by the project
        cmake = CMake(self)
        cmake.install()
        # Copy data and config files
        mkdir(self, os.path.join(self.package_folder, "res", "share"))
        mkdir(self, os.path.join(self.package_folder, "res", "etc"))
        v = Version(self.version)
        move_folder_contents(self, os.path.join(self.package_folder, "share", f"ImageMagick-{v.major}"),
                             os.path.join(self.package_folder, "res", "share"))
        move_folder_contents(self, os.path.join(self.package_folder, "etc", f"ImageMagick-{v.major}"),
                             os.path.join(self.package_folder, "res", "etc"))
        copy(self, "*/configure.xml",
             os.path.join(self.package_folder, "lib"),
             os.path.join(self.package_folder, "res", "share"),
             keep_path=False)
        rmdir(self, os.path.join(self.package_folder, "lib", f"ImageMagick-{v.major}.{v.minor}.{v.patch}"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "etc"))

    def _libname(self, library):
        suffix = "HDRI" if self.options.hdri else ""
        major_version = Version(self.version).major
        return f"{library}-{major_version}.Q{self.options.quantum_depth}{suffix}"

    def package_info(self):
        # FIXME: fully model the official FindImageMagick https://cmake.org/cmake/help/latest/module/FindImageMagick.html

        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "ImageMagick")
        self.cpp_info.set_property("cmake_target_name", "ImageMagick::ImageMagick")

        core_requires = []
        if self.options.with_bzlib:
            core_requires.append("bzip2::bzip2")
        if self.options.with_cairo:
            core_requires.append("cairo::cairo")
        if self.options.with_fftw:
            core_requires.append("fftw::fftw")
        if self.options.with_fontconfig:
            core_requires.append("fontconfig::fontconfig")
        if self.options.with_freetype:
            core_requires.append("freetype::freetype")
        if self.options.with_heic:
            core_requires.append("libheif::libheif")
        if self.options.with_jbig:
            core_requires.append("jbig::jbig")
        if self.options.with_jpeg == "libjpeg":
            core_requires.append("libjpeg::libjpeg")
        elif self.options.with_jpeg == "libjpeg-turbo":
            core_requires.append("libjpeg-turbo::jpeg")
        if self.options.with_jxl:
            core_requires.append("libjxl::libjxl")
        if self.options.with_lcms:
            core_requires.append("lcms::lcms")
        if self.options.with_lzma:
            core_requires.append("xz_utils::xz_utils")
        if self.options.with_opencl:
            core_requires.append("opencl-headers::opencl-headers")
        if self.options.with_openexr:
            core_requires.append("openexr::openexr")
        if self.options.with_openjp2:
            core_requires.append("openjpeg::openjpeg")
        if self.options.with_openmp and self.settings.compiler in ["clang", "apple-clang"]:
            core_requires.append("llvm-openmp::llvm-openmp")
        if self.options.with_pango:
            core_requires.append("pango::pango")
        if self.options.with_png:
            core_requires.append("libpng::libpng")
        if self.options.with_raw:
            core_requires.append("libraw::libraw")
        if self.options.with_tiff:
            core_requires.append("libtiff::libtiff")
        if self.options.with_webp:
            core_requires.append("libwebp::libwebp")
        if self.options.with_xml2:
            core_requires.append("libxml2::libxml2")
        if self.options.with_zlib:
            core_requires.append("zlib::zlib")
        if self.options.with_zstd:
            core_requires.append("zstd::zstd")
        if self.options.get_safe("with_x11"):
            core_requires.append("xorg::xorg")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["MagickCore"].system_libs.append("pthread")

        self.cpp_info.components["MagickCore"].defines.append(f"MAGICKCORE_QUANTUM_DEPTH={self.options.quantum_depth}")
        self.cpp_info.components["MagickCore"].defines.append(f"MAGICKCORE_HDRI_ENABLE={int(bool(self.options.hdri))}")
        self.cpp_info.components["MagickCore"].defines.append("_MAGICKDLL_=1" if self.options.shared else "_MAGICKLIB_=1")

        include_dir_root = os.path.join("include", f"ImageMagick-{Version(self.version).major}")
        self.cpp_info.components["MagickCore"].includedirs = [include_dir_root]
        self.cpp_info.components["MagickCore"].resdirs = ["res"]
        self.cpp_info.components["MagickCore"].libs.append(self._libname("MagickCore"))
        self.cpp_info.components["MagickCore"].requires = core_requires
        self.cpp_info.components["MagickCore"].set_property("pkg_config_name", "MagicCore")

        self.cpp_info.components[self._libname("MagickCore")].requires = ["MagickCore"]
        self.cpp_info.components[self._libname("MagickCore")].set_property("pkg_config_name", self._libname("MagickCore"))

        if not self.options.shared and self.options.with_openmp:
            openmp_flags = []
            if is_msvc(self):
                openmp_flags = ["-openmp"]
            elif self.settings.compiler == "gcc":
                openmp_flags = ["-fopenmp"]
            elif self.settings.compiler in ["clang", "apple-clang"]:
                openmp_flags = ["-Xpreprocessor", "-fopenmp"]
            self.cpp_info.components["MagickCore"].sharedlinkflags = openmp_flags
            self.cpp_info.components["MagickCore"].exelinkflags = openmp_flags

        self.cpp_info.components["MagickWand"].includedirs = [os.path.join(include_dir_root, "MagickWand")]
        self.cpp_info.components["MagickWand"].resdirs = ["res"]
        self.cpp_info.components["MagickWand"].libs = [self._libname("MagickWand")]
        self.cpp_info.components["MagickWand"].requires = ["MagickCore"]
        self.cpp_info.components["MagickWand"].set_property("pkg_config_name", "MagickWand")

        self.cpp_info.components[self._libname("MagickWand")].requires = ["MagickWand"]
        self.cpp_info.components[self._libname("MagickWand")].set_property("pkg_config_name", "MagickWand")

        if self.options.magickpp:
            self.cpp_info.components["Magick++"].includedirs = [os.path.join(include_dir_root, "Magick++")]
            self.cpp_info.components["Magick++"].resdirs = ["res"]
            self.cpp_info.components["Magick++"].libs = [self._libname("Magick++")]
            self.cpp_info.components["Magick++"].requires = ["MagickWand"]
            self.cpp_info.components["Magick++"].set_property("pkg_config_name", ["Magick++", self._libname("Magick++")])

            self.cpp_info.components[self._libname("Magick++")].requires = ["Magick++"]
            self.cpp_info.components[self._libname("Magick++")].set_property("pkg_config_name", self._libname("Magick++"))

            if not self.options.shared:
                self.cpp_info.components["MagickCore"].defines.append("STATIC_MAGICK=1")
                self.cpp_info.components["MagickCore"].defines.append("NOAUTOLINK_MAGICK=1")

        resdir = os.path.join(self.package_folder, "res")
        self.runenv_info.append_path("MAGICK_CONFIGURE_PATH", os.path.join(resdir, "etc"))
        self.runenv_info.append_path("MAGICK_CONFIGURE_PATH", os.path.join(resdir, "share"))

        # TODO: Legacy, to be removed on Conan 2.0
        self.cpp_info.names["cmake_find_package"] = "ImageMagick"
        self.cpp_info.names["cmake_find_package_multi"] = "ImageMagick"
        bin_path = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_path)
