from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import can_run
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, replace_in_file, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import check_min_vs, is_msvc, is_msvc_static_runtime
import os

required_conan_version = ">=1.53.0"


class LibvipsConan(ConanFile):
    name = "libvips"
    description = "libvips is a demand-driven, horizontally threaded image processing library."
    license = "LGPL-2.1-or-later"
    topics = ("image", "image-processing")
    homepage = "https://www.libvips.org"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "deprecated": [True, False],
        "cpp": [True, False],
        "introspection": [True, False],
        "vapi": [True, False],
        "with_cfitsio": [True, False],
        "with_cgif": [True, False],
        "with_exif": [True, False],
        "with_fftw": [True, False],
        "with_fontconfig": [True, False],
        "with_gsf": [True, False],
        "with_heif": [True, False],
        "with_imagequant": [True, False],
        "with_jpeg": ["libjpeg", "libjpeg-turbo", "mozjpeg", False],
        "with_jpeg_xl": [True, False],
        "with_lcms": [True, False],
        "with_magick": [True, False],
        "with_matio": [True, False],
        "with_nifti": [True, False],
        "with_openexr": [True, False],
        "with_openjpeg": [True, False],
        "with_openslide": [True, False],
        "with_orc": [True, False],
        "with_pangocairo": [True, False],
        "with_pdfium": [True, False],
        "with_png": ["libpng", "libspng", False],
        "with_poppler": [True, False],
        "with_quantizr": [True, False],
        "with_rsvg": [True, False],
        "with_tiff": [True, False],
        "with_webp": [True, False],
        "with_zlib": [True, False],
        "with_nsgif": [True, False],
        "with_ppm": [True, False],
        "with_analyse": [True, False],
        "with_radiance": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "deprecated": True,
        "cpp": True,
        "introspection": False,
        "vapi": False,
        "with_cfitsio": False,
        "with_cgif": False,
        "with_exif": False,
        "with_fftw": True,
        "with_fontconfig": False,
        "with_gsf": False,
        "with_heif": False,
        "with_imagequant": False,
        "with_jpeg": "libjpeg",
        "with_jpeg_xl": False,
        "with_lcms": True,
        "with_magick": False,
        "with_matio": False,
        "with_nifti": False,
        "with_openexr": False,
        "with_openjpeg": False,
        "with_openslide": False,
        "with_orc": False,
        "with_pangocairo": False,
        "with_pdfium": False,
        "with_png": "libspng",
        "with_poppler": False,
        "with_quantizr": False,
        "with_rsvg": False,
        "with_tiff": True,
        "with_webp": True,
        "with_zlib": True,
        "with_nsgif": True,
        "with_ppm": True,
        "with_analyse": True,
        "with_radiance": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.cpp:
            self.settings.rm_safe("compiler.cppstd")
            self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("expat/2.5.0")
        self.requires("glib/2.76.3", transitive_headers=True, transitive_libs=True, run=can_run(self))
        if self.options.with_cfitsio:
            self.requires("cfitsio/4.2.0")
        if self.options.with_cgif:
            self.requires("cgif/0.3.0")
        if self.options.with_exif:
            self.requires("libexif/0.6.24")
        if self.options.with_fftw:
            self.requires("fftw/3.3.10")
        if self.options.with_fontconfig:
            self.requires("fontconfig/2.14.2")
        if self.options.with_heif:
            self.requires("libheif/1.13.0")
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.5")
        elif self.options.with_jpeg == "mozjpeg":
            self.requires("mozjpeg/4.1.1")
        if self.options.with_jpeg_xl:
            self.requires("libjxl/0.6.1")
        if self.options.with_lcms:
            self.requires("lcms/2.14")
        if self.options.with_magick:
            self.requires("imagemagick/7.0.11-14")
        if self.options.with_matio:
            self.requires("matio/1.5.23")
        if self.options.with_openexr:
            self.requires("openexr/3.1.7")
        if self.options.with_openjpeg:
            self.requires("openjpeg/2.5.0")
        if self.options.with_pangocairo:
            self.requires("pango/1.50.10")
        if self.options.with_pdfium:
            self.requires("pdfium/cci.20210730")
        if self.options.with_png == "libpng":
            self.requires("libpng/1.6.39")
        elif self.options.with_png == "libspng":
            self.requires("libspng/0.7.3")
        if self.options.with_poppler:
            self.requires("poppler/21.07.0")
        if self.options.with_tiff:
            self.requires("libtiff/4.5.0")
        if self.options.with_webp:
            self.requires("libwebp/1.3.0")
        if self.options.with_zlib:
            self.requires("zlib/1.2.13")

    def validate(self):
        if self.options.vapi and not self.options.introspection:
            raise ConanInvalidConfiguration("vapi requires introspection")
        if self.options.with_pangocairo and not self.dependencies["pango"].options.with_cairo:
            raise ConanInvalidConfiguration(f"{self.ref}:with_pangocairo=True requires pango/*:with_cairo=True")
        if self.options.with_pdfium and self.options.with_poppler:
            raise ConanInvalidConfiguration("pdf support is enabled either with pdfium or poppler")
        if self.options.with_cgif and not (self.options.with_imagequant or self.options.with_quantizr):
            raise ConanInvalidConfiguration("with_cgif requires either with_imagequant or with_quantizr")

        # Visual Studio < 2019 doesn't seem to like pointer restrict of pointer restrict in libnsgif
        check_min_vs(self, "192")

        if is_msvc(self) and is_msvc_static_runtime(self) and not self.options.shared and \
           self.dependencies["glib"].options.shared:
            raise ConanInvalidConfiguration(
                f"{self.ref} static with MT runtime not supported if glib shared due to conancenter CI limitations"
            )

        if self.options.with_gsf:
            raise ConanInvalidConfiguration("libgsf recipe not available in conancenter yet")
        if self.options.with_imagequant:
            raise ConanInvalidConfiguration("libimagequant recipe not available in conancenter yet")
        if self.options.with_nifti:
            raise ConanInvalidConfiguration("nifti recipe not available in conancenter yet")
        if self.options.with_openslide:
            raise ConanInvalidConfiguration("openslide recipe not available in conancenter yet")
        if self.options.with_orc:
            raise ConanInvalidConfiguration("orc recipe not available in conancenter yet")
        if self.options.with_quantizr:
            raise ConanInvalidConfiguration("quantizr recipe not available in conancenter yet")
        if self.options.with_rsvg:
            raise ConanInvalidConfiguration("librsvg recipe not available in conancenter yet")

    def build_requirements(self):
        self.tool_requires("meson/1.1.1")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/1.9.3")
        if self.options.introspection:
            self.tool_requires("gobject-introspection/1.72.0")
        if not can_run(self):
            self.tool_requires("glib/2.76.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if can_run(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = MesonToolchain(self)
        true_false = lambda v: "true" if v else "false"
        enabled_disabled = lambda v: "enabled" if v else "disabled"
        tc.project_options["deprecated"] = true_false(self.options.deprecated)
        tc.project_options["examples"] = "false"
        tc.project_options["cplusplus"] = true_false(self.options.cpp)
        tc.project_options["doxygen"] = "false"
        tc.project_options["gtk_doc"] = "false"
        tc.project_options["modules"] = "disabled"
        tc.project_options["introspection"] = true_false(self.options.introspection)
        tc.project_options["vapi"] = true_false(self.options.vapi)
        # External libraries
        tc.project_options["cfitsio"] = enabled_disabled(self.options.with_cfitsio)
        tc.project_options["cgif"] = enabled_disabled(self.options.with_cgif)
        tc.project_options["exif"] = enabled_disabled(self.options.with_exif)
        tc.project_options["fftw"] = enabled_disabled(self.options.with_fftw)
        tc.project_options["fontconfig"] = enabled_disabled(self.options.with_fontconfig)
        tc.project_options["gsf"] = enabled_disabled(self.options.with_gsf)
        tc.project_options["heif"] = enabled_disabled(self.options.with_heif)
        tc.project_options["heif-module"] = "disabled"
        tc.project_options["imagequant"] = enabled_disabled(self.options.with_imagequant)
        tc.project_options["jpeg"] = enabled_disabled(bool(self.options.with_jpeg))
        tc.project_options["jpeg-xl"] = enabled_disabled(self.options.with_jpeg_xl)
        tc.project_options["jpeg-xl-module"] = "disabled"
        tc.project_options["lcms"] = enabled_disabled(self.options.with_lcms)
        tc.project_options["magick"] = enabled_disabled(self.options.with_magick)
        tc.project_options["magick-module"] = "disabled"
        tc.project_options["matio"] = enabled_disabled(self.options.with_matio)
        tc.project_options["nifti"] = enabled_disabled(self.options.with_nifti)
        tc.project_options["openexr"] = enabled_disabled(self.options.with_openexr)
        tc.project_options["openjpeg"] = enabled_disabled(self.options.with_openjpeg)
        tc.project_options["openslide"] = enabled_disabled(self.options.with_openslide)
        tc.project_options["openslide-module"] = "disabled"
        tc.project_options["orc"] = enabled_disabled(self.options.with_orc)
        tc.project_options["pangocairo"] = enabled_disabled(self.options.with_pangocairo)
        tc.project_options["pdfium"] = enabled_disabled(self.options.with_pdfium)
        tc.project_options["png"] = enabled_disabled(self.options.with_png == "libpng")
        tc.project_options["poppler"] = enabled_disabled(self.options.with_poppler)
        tc.project_options["poppler-module"] = "disabled"
        tc.project_options["quantizr"] = enabled_disabled(self.options.with_quantizr)
        tc.project_options["rsvg"] = enabled_disabled(self.options.with_rsvg)
        tc.project_options["spng"] = enabled_disabled(self.options.with_png == "libspng")
        tc.project_options["tiff"] = enabled_disabled(self.options.with_tiff)
        tc.project_options["webp"] = enabled_disabled(self.options.with_webp)
        tc.project_options["zlib"] = enabled_disabled(self.options.with_zlib)
        # Other supported formats without external libs
        tc.project_options["nsgif"] = true_false(self.options.with_nsgif)
        tc.project_options["ppm"] = true_false(self.options.with_ppm)
        tc.project_options["analyze"] = true_false(self.options.with_analyse)
        tc.project_options["radiance"] = true_false(self.options.with_radiance)
        tc.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

    def _patch_sources(self):
        # Disable tests
        meson_build = os.path.join(self.source_folder, "meson.build")
        replace_in_file(self, meson_build, "subdir('test')", "")
        replace_in_file(self, meson_build, "subdir('fuzz')", "")

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        fix_apple_shared_install_name(self)
        fix_msvc_libname(self)

    def package_info(self):
        self.cpp_info.components["vips"].set_property("pkg_config_name", "vips")
        self.cpp_info.components["vips"].libs = ["vips"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["vips"].system_libs.extend(["m", "pthread"])
        self.cpp_info.components["vips"].requires = [
            "expat::expat", "glib::glib-2.0", "glib::gio-2.0", "glib::gobject-2.0",
        ]
        if self.options.with_cfitsio:
            self.cpp_info.components["vips"].requires.append("cfitsio::cfitsio")
        if self.options.with_cgif:
            self.cpp_info.components["vips"].requires.append("cgif::cgif")
        if self.options.with_exif:
            self.cpp_info.components["vips"].requires.append("libexif::libexif")
        if self.options.with_fftw:
            self.cpp_info.components["vips"].requires.append("fftw::fftw")
        if self.options.with_fontconfig:
            self.cpp_info.components["vips"].requires.append("fontconfig::fontconfig")
        if self.options.with_heif:
            self.cpp_info.components["vips"].requires.append("libheif::libheif")
        if self.options.with_jpeg == "libjpeg":
            self.cpp_info.components["vips"].requires.append("libjpeg::libjpeg")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.cpp_info.components["vips"].requires.append("libjpeg-turbo::jpeg")
        elif self.options.with_jpeg == "mozjpeg":
            self.cpp_info.components["vips"].requires.append("mozjpeg::libjpeg")
        if self.options.with_jpeg_xl:
            self.cpp_info.components["vips"].requires.append("libjxl::libjxl")
        if self.options.with_lcms:
            self.cpp_info.components["vips"].requires.append("lcms::lcms")
        if self.options.with_magick:
            self.cpp_info.components["vips"].requires.append("imagemagick::MagickCore")
        if self.options.with_matio:
            self.cpp_info.components["vips"].requires.append("matio::matio")
        if self.options.with_openexr:
            self.cpp_info.components["vips"].requires.append("openexr::openexr")
        if self.options.with_openjpeg:
            self.cpp_info.components["vips"].requires.append("openjpeg::openjpeg")
        if self.options.with_pangocairo:
            self.cpp_info.components["vips"].requires.append("pango::pangocairo")
        if self.options.with_pdfium:
            self.cpp_info.components["vips"].requires.append("pdfium::pdfium")
        if self.options.with_png == "libpng":
            self.cpp_info.components["vips"].requires.append("libpng::libpng")
        elif self.options.with_png == "libspng":
            self.cpp_info.components["vips"].requires.append("libspng::libspng")
        if self.options.with_poppler:
            self.cpp_info.components["vips"].requires.append("poppler::poppler")
        if self.options.with_tiff:
            self.cpp_info.components["vips"].requires.append("libtiff::libtiff")
        if self.options.with_webp:
            self.cpp_info.components["vips"].requires.append("libwebp::libwebp")
        if self.options.with_zlib:
            self.cpp_info.components["vips"].requires.append("zlib::zlib")

        if self.options.cpp:
            self.cpp_info.components["vips-cpp"].set_property("pkg_config_name", "vips-cpp")
            self.cpp_info.components["vips-cpp"].libs = ["vips-cpp"]
            self.cpp_info.components["vips-cpp"].requires = ["vips"]

        # TODO: to remove once conan v1 support dropped
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))

def fix_msvc_libname(conanfile, remove_lib_prefix=True):
    """remove lib prefix & change extension to .lib in case of cl like compiler"""
    from conan.tools.files import rename
    import glob
    if not conanfile.settings.get_safe("compiler.runtime"):
        return
    libdirs = getattr(conanfile.cpp.package, "libdirs")
    for libdir in libdirs:
        for ext in [".dll.a", ".dll.lib", ".a"]:
            full_folder = os.path.join(conanfile.package_folder, libdir)
            for filepath in glob.glob(os.path.join(full_folder, f"*{ext}")):
                libname = os.path.basename(filepath)[0:-len(ext)]
                if remove_lib_prefix and libname[0:3] == "lib":
                    libname = libname[3:]
                rename(conanfile, filepath, os.path.join(os.path.dirname(filepath), f"{libname}.lib"))
