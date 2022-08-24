from from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class PopplerConan(ConanFile):
    name = "poppler"
    description = "Poppler is a PDF rendering library based on the xpdf-3.0 code base"
    homepage = "https://poppler.freedesktop.org/"
    topics = ("conan", "poppler", "pdf", "rendering")
    license = "GPL-2.0-or-later", "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "cpp": [True, False],
        "fontconfiguration": ["generic", "fontconfig", "win32"],
        "splash": [True, False],
        "float": [True, False],
        "with_cairo": [True, False],
        "with_glib": [True, False],
        "with_gobject_introspection": [True, False],
        "with_qt": [True, False],
        "with_gtk": [True, False],
        "with_libiconv": [True, False],
        "with_openjpeg": [True, False],
        "with_lcms": [True, False],
        "with_libjpeg": ["libjpeg", False],
        "with_png": [True, False],
        "with_nss": [True, False],
        "with_tiff": [True, False],
        "with_libcurl": [True, False],
        "with_zlib": [True, False],

    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "cpp": True,
        "fontconfiguration": "generic",
        "with_cairo": False,
        "splash": True,
        "with_glib": False,
        "with_gobject_introspection": True,
        "with_qt": False,
        "with_gtk": False,
        "with_libiconv": True,
        "with_openjpeg": True,
        "with_lcms": True,
        "with_libjpeg": "libjpeg",
        "with_png": True,
        "with_nss": False,
        "with_tiff": True,
        "with_libcurl": True,
        "with_zlib": True,
        "float": False,
    }

    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake", "cmake_find_package", "pkg_config"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if not self.options.with_cairo:
            del self.options.with_glib
        if not self.options.get_safe("with_glib"):
            del self.options.with_gobject_introspection
            del self.options.with_gtk
        if not self.options.cpp:
            del self.options.with_libiconv

    def requirements(self):
        self.requires("poppler-data/0.4.11")
        self.requires("freetype/2.12.1")
        if self.options.get_safe("with_libiconv"):
            self.requires("libiconv/1.17")
        if self.options.fontconfiguration == "fontconfig":
            self.requires("fontconfig/2.13.93")
        if self.options.with_cairo:
            self.requires("cairo/1.17.4")
        if self.options.get_safe("with_glib"):
            self.requires("glib/2.73.2")
        if self.options.get_safe("with_gobject_introspection"):
            self.requires("gobject-introspection/1.72.0")
        if self.options.with_qt:
            self.requires("qt/6.3.1")
        if self.options.get_safe("with_gtk"):
            self.requires("gtk/4.7.0")
        if self.options.with_openjpeg:
            self.requires("openjpeg/2.5.0")
        if self.options.with_lcms:
            self.requires("lcms/2.13.1")
        if self.options.with_libjpeg == "libjpeg":
            self.requires("libjpeg/9d")
        if self.options.with_png:
            self.requires("libpng/1.6.37")
        if self.options.with_tiff:
            self.requires("libtiff/4.3.0")
        if self.options.splash:
            self.requires("boost/1.79.0")
        if self.options.with_libcurl:
            self.requires("libcurl/7.84.0")
        if self.options.with_zlib:
            self.requires("zlib/1.2.12")

    @property
    def _minimum_compilers_version(self):
        # Poppler requires C++14
        return {
            "Visual Studio": "15",
            "gcc": "5",
            "clang": "5",
            "apple-clang": "5.1"
        }

    def validate(self):
        if self.options.fontconfiguration == "win32" and self.settings.os != "Windows":
            raise ConanInvalidConfiguration("'win32' option of fontconfig is only available on Windows")

        # C++ standard required
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, 14)

        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("C++14 support required. Your compiler is unknown. Assuming it supports C++14.")
        elif tools.scm.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("C++14 support required, which your compiler does not support.")

        if self.options.with_nss:
            # FIXME: missing nss recipe
            raise ConanInvalidConfiguration("nss is not (yet) available on cci")

    def build_requirements(self):
        self.build_requires("pkgconf/1.7.4")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @property
    def _dct_decoder(self):
        if self.options.with_libjpeg == False:
            return "none"
        else:
            return str(self.options.with_libjpeg)

    @property
    def _cppstd_required(self):
        if self.options.with_qt and tools.scm.Version(self.deps_cpp_info["qt"].version).major == "6":
            return 17
        else:
            return 14

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

        self._cmake.definitions["CMAKE_CXX_STANDARD"] = self._cppstd_required

        self._cmake.definitions["ENABLE_UNSTABLE_API_ABI_HEADERS"] = True
        self._cmake.definitions["BUILD_GTK_TESTS"] = False
        self._cmake.definitions["BUILD_QT5_TESTS"] = False
        self._cmake.definitions["BUILD_QT6_TESTS"] = False
        self._cmake.definitions["BUILD_CPP_TESTS"] = False
        self._cmake.definitions["BUILD_MANUAL_TESTS"] = False

        self._cmake.definitions["ENABLE_UTILS"] = False
        self._cmake.definitions["ENABLE_CPP"] = self.options.cpp

        self._cmake.definitions["ENABLE_SPLASH"] = self.options.splash
        self._cmake.definitions["FONT_CONFIGURATION"] = self.options.fontconfiguration
        self._cmake.definitions["ENABLE_JPEG"] = self.options.with_libjpeg
        self._cmake.definitions["WITH_PNG"] = self.options.with_png
        self._cmake.definitions["WITH_TIFF"] = self.options.with_tiff
        self._cmake.definitions["WITH_NSS3"] = self.options.with_nss
        self._cmake.definitions["WITH_Cairo"] = self.options.with_cairo
        self._cmake.definitions["ENABLE_GLIB"] = self.options.get_safe("with_glib", False)
        self._cmake.definitions["ENABLE_GOBJECT_INTROSPECTION"] = self.options.get_safe("with_gobject_introspection", False)
        self._cmake.definitions["WITH_GTK"] = self.options.get_safe("with_gtk", False)
        self._cmake.definitions["WITH_Iconv"] = self.options.get_safe("with_libiconv")
        self._cmake.definitions["ENABLE_ZLIB"] = self.options.with_zlib
        self._cmake.definitions["ENABLE_LIBOPENJPEG"] = "openjpeg2" if self.options.with_openjpeg else "none"
        if self.options.with_openjpeg:
            # FIXME: openjpeg's cmake_find_package should provide these variables
            self._cmake.definitions["OPENJPEG_MAJOR_VERSION"] = tools.scm.Version(self.requires["openjpeg"].ref.version).major
        self._cmake.definitions["ENABLE_CMS"] = "lcms2" if self.options.with_lcms else "none"
        self._cmake.definitions["ENABLE_LIBCURL"] = self.options.with_libcurl

        self._cmake.definitions["POPPLER_DATADIR"] = self.deps_user_info["poppler-data"].datadir.replace("\\", "/")
        self._cmake.definitions["FONT_CONFIGURATION"] = self.options.fontconfiguration
        self._cmake.definitions["BUILD_CPP_TESTS"] = False
        self._cmake.definitions["ENABLE_GTK_DOC"] = False
        self._cmake.definitions["ENABLE_QT5"] = self.options.with_qt and tools.scm.Version(self.deps_cpp_info["qt"].version).major == "5"
        self._cmake.definitions["ENABLE_QT6"] = self.options.with_qt and tools.scm.Version(self.deps_cpp_info["qt"].version).major == "6"

        self._cmake.definitions["ENABLE_CMS"] = "lcms2" if self.options.with_lcms else "none"
        self._cmake.definitions["ENABLE_DCTDECODER"] = self._dct_decoder
        self._cmake.definitions["USE_FLOAT"] = self.options.float
        self._cmake.definitions["RUN_GPERF_IF_PRESENT"] = False
        if self.settings.os == "Windows":
            self._cmake.definitions["ENABLE_RELOCATABLE"] = self.options.shared
        self._cmake.definitions["EXTRA_WARN"] = False

        # Workaround for cross-build to at least iOS/tvOS/watchOS,
        # when dependencies are found with find_path() and find_library()
        if tools.build.cross_building(self, self):
            self._cmake.definitions["CMAKE_FIND_ROOT_PATH_MODE_INCLUDE"] = "BOTH"
            self._cmake.definitions["CMAKE_FIND_ROOT_PATH_MODE_LIBRARY"] = "BOTH"

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        for patchdata in self.conan_data["patches"][self.version]:
            tools.files.patch(self, **patchdata)
        if tools.scm.Version(self.version) < "21.07.0" and not self.options.shared:
            poppler_global = os.path.join(self._source_subfolder, "cpp", "poppler-global.h")
            tools.files.replace_in_file(self, poppler_global, "__declspec(dllimport)", "")
            tools.files.replace_in_file(self, poppler_global, "__declspec(dllexport)", "")
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "FREETYPE_INCLUDE_DIRS",
                              "Freetype_INCLUDE_DIRS")

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING*", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.components["libpoppler"].libs = ["poppler"]
        self.cpp_info.components["libpoppler"].includedirs.append(os.path.join("include", "poppler"))
        self.cpp_info.components["libpoppler"].names["pkg_config"] = "poppler"
        if not self.options.shared:
            self.cpp_info.components["libpoppler"].defines = ["POPPLER_STATIC"]

        if self.settings.os == "Linux":
            self.cpp_info.components["libpoppler"].system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["libpoppler"].system_libs = ["gdi32"]

        self.cpp_info.components["libpoppler"].requires = ["poppler-data::poppler-data", "freetype::freetype"]
        if self.options.fontconfiguration == "fontconfig":
            self.cpp_info.components["libpoppler"].requires.append("fontconfig::fontconfig")
        if self.options.with_openjpeg:
            self.cpp_info.components["libpoppler"].requires.append("openjpeg::openjpeg")
        if self.options.with_lcms:
            self.cpp_info.components["libpoppler"].requires.append("lcms::lcms")
        if self.options.with_libjpeg == "libjpeg":
            self.cpp_info.components["libpoppler"].requires.append("libjpeg::libjpeg")
        if self.options.with_png:
            self.cpp_info.components["libpoppler"].requires.append("libpng::libpng")
        if self.options.with_nss:
            self.cpp_info.components["libpoppler"].requires.append("nss::nss")
        if self.options.with_tiff:
            self.cpp_info.components["libpoppler"].requires.append("libtiff::libtiff")
        if self.options.with_libcurl:
            self.cpp_info.components["libpoppler"].requires.append("libcurl::libcurl")
        if self.options.with_zlib:
            self.cpp_info.components["libpoppler"].requires.append("zlib::zlib")

        if self.options.cpp:
            self.cpp_info.components["libpoppler-cpp"].libs = ["poppler-cpp"]
            self.cpp_info.components["libpoppler-cpp"].includedirs.append(os.path.join("include", "poppler", "cpp"))
            self.cpp_info.components["libpoppler-cpp"].names["pkg_config"] = "poppler-cpp"
            self.cpp_info.components["libpoppler-cpp"].requires = ["libpoppler"]
            if self.options.get_safe("with_libiconv"):
                self.cpp_info.components["libpoppler-cpp"].requires.append("libiconv::libiconv")

        if self.options.splash:
            self.cpp_info.components["libpoppler-splash"].libs = []
            self.cpp_info.components["libpoppler-splash"].names["pkg_config"] = "poppler-splash"
            self.cpp_info.components["libpoppler-splash"].requires = ["libpoppler", "boost::boost"]  # FIXME: should be boost::headers, see https://github.com/conan-io/conan-center-index/pull/2097

        if self.options.with_cairo:
            self.cpp_info.components["libpoppler-cairo"].libs = []
            self.cpp_info.components["libpoppler-cairo"].names["pkg_config"] = "poppler-cairo"
            self.cpp_info.components["libpoppler-cairo"].requires = ["libpoppler", "cairo::cairo"]

        if self.options.get_safe("with_glib"):
            self.cpp_info.components["libpoppler-glib"].libs = ["poppler-glib"]
            self.cpp_info.components["libpoppler-glib"].names["pkg_config"] = "poppler-glib"
            self.cpp_info.components["libpoppler-glib"].requires = ["libpoppler-cairo", "glib::glib"]
            if self.options.get_safe("with_gtk"):
                self.cpp_info.components["libpoppler-glib"].requires.append("gtk::gtk")
            if self.options.get_safe("with_gobject_introspection"):
                self.cpp_info.components["libpoppler-glib"].requires.append("gobject-introspection::gobject-introspection")

        if self.options.with_qt:
            qt_major = tools.scm.Version(self.deps_cpp_info["qt"].version).major
            self.cpp_info.components["libpoppler-qt"].libs = ["poppler-qt{}".format(qt_major)]
            self.cpp_info.components["libpoppler-qt"].names["pkg_config"] = "poppler-qt{}".format(qt_major)
            self.cpp_info.components["libpoppler-qt"].requires = ["libpoppler", "qt::qtCore", "qt::qtGui", "qt::qtWidgets"]

        datadir = self.deps_user_info["poppler-data"].datadir
        self.output.info("Setting POPPLER_DATADIR env var: {}".format(datadir))
        self.env_info.POPPLER_DATADIR = datadir
