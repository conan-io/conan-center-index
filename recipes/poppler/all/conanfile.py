from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy, rmdir, apply_conandata_patches, export_conandata_patches
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.gnu import PkgConfigDeps
import os

required_conan_version = ">=2"


class PopplerConan(ConanFile):
    name = "poppler"
    description = "Poppler is a PDF rendering library based on the xpdf-3.0 code base"
    homepage = "https://poppler.freedesktop.org/"
    topics = ("conan", "poppler", "pdf", "rendering")
    license = "GPL-2.0-or-later", "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libcurl": [True, False],
        "with_zlib": [True, False],
        "with_lcms": [True, False],
        "fontconfiguration": ["generic", "fontconfig", "win32", "android"],
        "with_cairo": [True, False],
        "with_glib": [True, False],
        # "with_qt": [True, False],
        # If you need control over these options, please open an issue
        # "with_openjpeg": [True, False],
        # "with_libjpeg": ["libjpeg", False],
        # "with_png": [True, False],
        # "with_gobject_introspection": [True, False],
        # "with_gtk": [True, False],
        # "with_nss": [True, False],
        # "float": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_zlib": True,
        "with_libcurl": False,
        "with_lcms": False,
        "fontconfiguration": "generic",
        "with_cairo": False,
        "with_glib": False,
        # "with_qt": False,
        # If you need control over these options, please open an issue
        # "with_openjpeg": True,
        # "with_libjpeg": "libjpeg",
        # "with_png": True,
        # "with_gtk": False,
        # "with_nss": False,
        # "with_gobject_introspection": True,
        # "float": False,
    }
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            self.options.fontconfiguration = "win32"
        elif self.settings.os == "Android":
            self.options.fontconfiguration = "android"

    def requirements(self):
        self.requires("poppler-data/0.4.11")
        self.requires("freetype/2.13.2")

        self.requires("boost/[>=1.81.0 <=1.89.0]", options={"header_only": True})
        self.requires("libiconv/1.17")
        self.requires("libpng/[>=1.6 <2]")
        self.requires("libtiff/[>=4.6.0 <5]")
        self.requires("libjpeg/[>=9e]")
        self.requires("openjpeg/[>=2.5.2 <3]")
        # zlib is always requires.
        # ENABLE_ZLIB_UNCOMPRESS just enables extra code
        self.requires("zlib/[>=1.2.11 <2]")

        if self.options.fontconfiguration == "fontconfig":
            self.requires("fontconfig/2.15.0")
        if self.options.with_libcurl:
            # Not compatible with libcurl 8 yet
            self.requires("libcurl/[>=7.78.0 <9]")
        if self.options.with_lcms:
            self.requires("lcms/[>=2.16 <3]")

        if self.options.with_cairo:
            self.requires("cairo/1.18.0")

        if self.options.with_glib:
            self.requires("glib/2.78.3")

    def validate(self):
        if self.options.fontconfiguration == "win32" and self.settings.os != "Windows":
            raise ConanInvalidConfiguration("'win32' option of fontconfig is only available on Windows")
        if self.options.fontconfiguration == "android" and self.settings.os != "Android":
            raise ConanInvalidConfiguration("'android' option of fontconfig is only available on Android")

        if self.options.with_glib and not self.options.with_cairo:
            raise ConanInvalidConfiguration("with_glib option requires with_cairo option enabled")

        check_min_cppstd(self, 20)

    def build_requirements(self):
        if self.options.with_glib:
            self.tool_requires("glib/<host_version>")
        self.tool_requires("cmake/[>=3.22]")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["ENABLE_UNSTABLE_API_ABI_HEADERS"] = True
        tc.cache_variables["BUILD_GTK_TESTS"] = False
        tc.cache_variables["BUILD_QT5_TESTS"] = False
        tc.cache_variables["BUILD_QT6_TESTS"] = False
        tc.cache_variables["BUILD_CPP_TESTS"] = False
        tc.cache_variables["BUILD_MANUAL_TESTS"] = False
        tc.cache_variables["ENABLE_UTILS"] = False

        tc.cache_variables["ENABLE_ZLIB_UNCOMPRESS"] = self.options.with_zlib

        tc.cache_variables["FONT_CONFIGURATION"] = self.options.fontconfiguration
        tc.cache_variables["ENABLE_LCMS"] = self.options.with_lcms
        tc.cache_variables["ENABLE_LIBCURL"] = self.options.with_libcurl
        # One controls the option, the other the dependency. Cairo is needed for glib
        tc.cache_variables["WITH_Cairo"] = self.options.with_cairo
        tc.cache_variables["CAIRO_FOUND"] = self.options.with_cairo
        tc.cache_variables["ENABLE_GLIB"] = self.options.with_glib
        tc.cache_variables["WITH_GLIB"] = self.options.with_glib

        tc.cache_variables["WITH_PNG"] = True
        tc.cache_variables["WITH_GTK"] = False
        tc.cache_variables["ENABLE_NSS3"] = False
        tc.cache_variables["ENABLE_GOBJECT_INTROSPECTION"] = False
        tc.cache_variables["ENABLE_GTK_DOC"] = False
        tc.cache_variables["ENABLE_GPGME"] = False  # Not available in CCI
        tc.cache_variables["POPPLER_DATADIR"] = self.dependencies["poppler-data"].conf_info.get("user.poppler-data:datadir")

        tc.cache_variables["ENABLE_QT5"] = False
        tc.cache_variables["ENABLE_QT6"] = False

        # TODO: Why?
        tc.cache_variables["RUN_GPERF_IF_PRESENT"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("freetype", "cmake_file_name", "FREETYPE")
        if self.options.fontconfiguration == "fontconfig":
            deps.set_property("fontconfig", "cmake_file_name", "FONTCONFIG")
        if self.options.with_lcms:
            deps.set_property("lcms", "cmake_file_name", "LCMS2")
        if self.options.with_cairo:
            deps.set_property("cairo", "cmake_file_name", "Cairo")
        if self.options.with_glib:
            deps.set_property("glib", "cmake_file_name", "GLIB")
        if self.options.with_libcurl:
            # They set a min of 7.81, supports libcurl 8 too
            deps.set_property("libcurl", "cmake_config_version_compat", "AnyNewerVersion")
        deps.generate()
        pkgdeps = PkgConfigDeps(self)
        pkgdeps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.components["libpoppler"].libs = ["poppler"]
        self.cpp_info.components["libpoppler"].includedirs.append(os.path.join("include", "poppler"))
        if self.settings.os == "Windows":
            self.cpp_info.components["libpoppler"].system_libs = ["gdi32"]

        self.cpp_info.components["libpoppler"].requires = [
            "freetype::freetype",
            "zlib::zlib",
            "libjpeg::libjpeg",
            "openjpeg::openjpeg",
            "libpng::libpng",
            "libtiff::libtiff",
            "boost::headers",
            "poppler-data::poppler-data",
        ]

        if self.options.fontconfiguration == "fontconfig":
            self.cpp_info.components["libpoppler"].requires.append("fontconfig::fontconfig")

        if self.options.with_libcurl:
            self.cpp_info.components["libpoppler"].requires.append("libcurl::libcurl")

        if self.options.with_lcms:
            self.cpp_info.components["libpoppler"].requires.append("lcms::lcms")

        self.cpp_info.components["libpoppler-cpp"].libs = ["poppler-cpp"]
        self.cpp_info.components["libpoppler-cpp"].includedirs.append(os.path.join("include", "poppler", "cpp"))
        self.cpp_info.components["libpoppler-cpp"].requires = ["libpoppler", "libiconv::libiconv"]

        if self.options.with_glib:
            self.cpp_info.components["libpoppler-glib"].libs = ["poppler-glib"]
            self.cpp_info.components["libpoppler-glib"].requires = ["libpoppler-cpp", "cairo::cairo", "glib::glib", "freetype::freetype"]
