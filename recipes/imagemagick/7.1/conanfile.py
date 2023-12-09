import os

from conan import ConanFile
from conan.tools.build import stdcpp_library
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rmdir
from conan.tools.gnu import PkgConfigDeps
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
        "hdri": [True, False],
        "quantum_depth": [8, 16, 32],
        "with_zlib": [True, False],
        "with_bzlib": [True, False],
        "with_zstd": [True, False],
        "with_lzma": [True, False],
        "with_lcms": [True, False],
        "with_openexr": [True, False],
        "with_heic": [True, False],
        "with_jbig": [True, False],
        "with_jpeg": [None, "libjpeg", "libjpeg-turbo"],
        "with_jxl": [True, False],
        "with_openjp2": [True, False],
        "with_pango": [True, False],
        "with_png": [True, False],
        "with_tiff": [True, False],
        "with_webp": [True, False],
        "with_xml2": [True, False],
        "with_freetype": [True, False],
        "with_djvu": [True, False],
        "with_raw": [True, False],
        "with_openmp": [True, False],
        "with_threads": [True, False],
        "magickpp": [True, False],
        "utilities": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "hdri": True,
        "quantum_depth": 16,
        "with_zlib": True,
        "with_bzlib": True,
        "with_zstd": False,
        "with_lzma": True,
        "with_lcms": True,
        "with_openexr": True,
        "with_heic": True,
        "with_jbig": True,
        "with_jpeg": "libjpeg",
        "with_jxl": False,
        "with_openjp2": True,
        "with_pango": False,  # FIXME: re-enable once migrated
        "with_png": True,
        "with_tiff": True,
        "with_webp": False,
        "with_xml2": True,
        "with_freetype": True,
        "with_djvu": False,
        "with_raw": False,
        "with_openmp": True,
        "with_threads": True,
        "magickpp": True,
        "utilities": True,
    }
    short_paths = True

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

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
        if self.options.with_zlib:
            self.requires("zlib/1.3")
        if self.options.with_bzlib:
            self.requires("bzip2/1.0.8")
        if self.options.with_zstd:
            self.requires("zstd/1.5.5")
        if self.options.with_lzma:
            self.requires("xz_utils/5.4.5")
        if self.options.with_lcms:
            self.requires("lcms/2.14")
        if self.options.with_openexr:
            self.requires("openexr/3.2.1")
        if self.options.with_heic:
            self.requires("libheif/1.16.2")
        if self.options.with_jbig:
            self.requires("jbig/20160605")
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/3.0.1")
        if self.options.with_jxl:
            self.requires("libjxl/0.6.1")
        if self.options.with_openjp2:
            self.requires("openjpeg/2.5.0")
        if self.options.with_pango:
            self.requires("pango/1.48.5")
        if self.options.with_png:
            self.requires("libpng/1.6.40")
        if self.options.with_tiff:
            self.requires("libtiff/4.6.0")
        if self.options.with_webp:
            self.requires("libwebp/1.3.2")
        if self.options.with_xml2:
            self.requires("libxml2/2.12.2")
        if self.options.with_freetype:
            self.requires("freetype/2.13.2")
        if self.options.with_raw:
            self.requires("libraw/0.21.1")
        if self.options.with_djvu:
            self.output.warning("Conan package for djvu is not available, this package will be used from system.")
        if self.options.with_openmp:
            if self.settings.compiler in ["clang", "apple-clang"]:
                self.requires("llvm-openmp/17.0.4")

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
        tc.variables["MAGICK_HDRI_ENABLE"] = self.options.hdri
        tc.variables["MAGICKCORE_QUANTUM_DEPTH"] = self.options.quantum_depth
        tc.variables["BUILD_MAGICKPP"] = self.options.magickpp
        tc.variables["BUILD_UTILITIES"] = self.options.utilities
        tc.variables["OPENMP_SUPPORT"] = self.options.with_openmp
        tc.variables["THREADS_SUPPORT"] = self.options.with_threads

        tc.variables["BZLIB_DELEGATE"] = self.options.with_bzlib
        tc.variables["LZMA_DELEGATE"] = self.options.with_lzma
        tc.variables["ZLIB_DELEGATE"] = self.options.with_zlib
        tc.variables["ZSTD_DELEGATE"] = self.options.with_zstd
        tc.variables["LCMS_DELEGATE"] = self.options.with_lcms
        tc.variables["FREETYPE_DELEGATE"] = self.options.with_freetype
        tc.variables["XML_DELEGATE"] = self.options.with_xml2
        tc.variables["TIFF_DELEGATE"] = self.options.with_tiff
        tc.variables["HEIC_DELEGATE"] = self.options.with_heic
        tc.variables["JBIG_DELEGATE"] = self.options.with_jbig
        tc.variables["JPEG_DELEGATE"] = self.options.with_jpeg
        tc.variables["LIBOPENJP2_DELEGATE"] = self.options.with_openjp2
        tc.variables["OPENEXR_DELEGATE"] = self.options.with_openexr
        tc.variables["PNG_DELEGATE"] = self.options.with_png
        tc.variables["RAW_R_DELEGATE"] = self.options.with_raw
        tc.variables["WEBP_DELEGATE"] = self.options.with_webp
        tc.variables["JXL_DELEGATE"] = self.options.with_jxl
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def _libname(self, library):
        suffix = "HDRI" if self.options.hdri else ""
        return f"{library}-{Version(self, self.version).major}.Q{self.options.quantum_depth}{suffix}"

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        # FIXME: fully model the official FindImageMagick https://cmake.org/cmake/help/latest/module/FindImageMagick.html

        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "ImageMagick")
        self.cpp_info.set_property("cmake_target_name", "ImageMagick::ImageMagick")

        core_requires = []
        if self.options.with_zlib:
            core_requires.append("zlib::zlib")
        if self.options.with_bzlib:
            core_requires.append("bzip2::bzip2")
        if self.options.with_zstd:
            core_requires.append("zstd::zstd")
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
        if self.options.with_jpeg == "libjpeg":
            core_requires.append("libjpeg::libjpeg")
        elif self.options.with_jpeg == "libjpeg-turbo":
            core_requires.append("libjpeg-turbo::jpeg")
        if self.options.with_jxl:
            core_requires.append("libjxl::libjxl")
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
        if self.options.with_raw:
            core_requires.append("libraw::libraw")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["MagickCore"].system_libs.append("pthread")

        self.cpp_info.components["MagickCore"].defines.append(f"MAGICKCORE_QUANTUM_DEPTH={self.options.quantum_depth}")
        self.cpp_info.components["MagickCore"].defines.append(f"MAGICKCORE_HDRI_ENABLE={int(bool(self.options.hdri))}")
        self.cpp_info.components["MagickCore"].defines.append("_MAGICKDLL_=1" if self.options.shared else "_MAGICKLIB_=1")

        include_dir_root = os.path.join("include", f"ImageMagick-{Version(self.version).major}")
        self.cpp_info.components["MagickCore"].includedirs = [include_dir_root]
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
            # TODO: check if OpenMP pargmas are used in exported headers
            # self.cpp_info.components["MagickCore"].cflags.extend(openmp_flags)
            # self.cpp_info.components["MagickCore"].cxxflags.extend(openmp_flags)
            self.cpp_info.components["MagickCore"].sharedlinkflags = openmp_flags
            self.cpp_info.components["MagickCore"].exelinkflags = openmp_flags

        self.cpp_info.components["MagickWand"].includedirs = [os.path.join(include_dir_root, "MagickWand")]
        self.cpp_info.components["MagickWand"].libs = [self._libname("MagickWand")]
        self.cpp_info.components["MagickWand"].requires = ["MagickCore"]
        self.cpp_info.components["MagickWand"].set_property("pkg_config_name", "MagickWand")

        self.cpp_info.components[self._libname("MagickWand")].requires = ["MagickWand"]
        self.cpp_info.components[self._libname("MagickWand")].set_property("pkg_config_name", "MagickWand")

        if self.options.magickpp:
            self.cpp_info.components["Magick++"].includedirs = [os.path.join(include_dir_root, "Magick++")]
            self.cpp_info.components["Magick++"].libs = [self._libname("Magick++")]
            self.cpp_info.components["Magick++"].requires = ["MagickWand"]
            self.cpp_info.components["Magick++"].set_property("pkg_config_name", ["Magick++", self._libname("Magick++")])

            self.cpp_info.components[self._libname("Magick++")].requires = ["Magick++"]
            self.cpp_info.components[self._libname("Magick++")].set_property("pkg_config_name", self._libname("Magick++"))

            if not self.options.shared:
                self.cpp_info.components["MagickCore"].defines.append("STATIC_MAGICK=1")
                self.cpp_info.components["MagickCore"].defines.append("NOAUTOLINK_MAGICK=1")

        # TODO: Legacy, to be removed on Conan 2.0
        self.cpp_info.names["cmake_find_package"] = "ImageMagick"
        self.cpp_info.names["cmake_find_package_multi"] = "ImageMagick"
        bin_path = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_path)
