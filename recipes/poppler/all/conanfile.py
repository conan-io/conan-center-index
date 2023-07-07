from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualRunEnv, VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, rm
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os
import functools

# For CMakeDeps.set_property
required_conan_version = ">=1.55.0"


class PopplerConan(ConanFile):
    name = "poppler"
    description = "Poppler is a PDF rendering library based on the xpdf-3.0 code base"
    homepage = "https://poppler.freedesktop.org/"
    topics = "pdf", "rendering"
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
        "with_libiconv": [True, False],
        "with_openjpeg": [True, False],
        "with_lcms": [True, False],
        "with_libjpeg": ["libjpeg", "libjpeg-turbo", False],
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

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.with_cairo:
            self.options.rm_safe("with_glib")
        if not self.options.get_safe("with_glib"):
            self.options.rm_safe("with_gobject_introspection")
        if self.options.cpp:
            if is_apple_os(self):
                self.options.with_libiconv = True
        else:
            self.options.rm_safe("with_libiconv")

    def requirements(self):
        self.requires("poppler-data/0.4.11")
        self.requires("freetype/2.13.0")
        if self.options.get_safe("with_libiconv"):
            self.requires("libiconv/1.17")
        if self.options.fontconfiguration == "fontconfig":
            self.requires("fontconfig/2.13.93")
        if self.options.with_cairo:
            self.requires("cairo/1.17.4")
        if self.options.get_safe("with_glib"):
            self.requires("glib/2.74.1")
        if self.options.get_safe("with_gobject_introspection"):
            self.requires("gobject-introspection/1.72.0")
        if self.options.with_qt:
            self.requires("qt/6.5.1")
        if self.options.with_openjpeg:
            self.requires("openjpeg/2.5.0")
        if self.options.with_lcms:
            self.requires("lcms/2.14")
        if self.options.with_libjpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.5")
        elif self.options.with_libjpeg == "libjpeg":
            self.requires("libjpeg/9e")
        if self.options.with_png:
            self.requires("libpng/1.6.39")
        if self.options.with_tiff:
            self.requires("libtiff/4.5.1")
        if self.options.splash:
            self.requires("boost/1.82.0")
        if self.options.with_libcurl:
            self.requires("libcurl/8.1.2")
        if self.options.with_zlib:
            self.requires("zlib/1.2.13")

    @property
    def _minimum_compilers_version(self):
        # Poppler requires C++14
        return {"Visual Studio": "16", "gcc": "9", "clang": "10", "apple-clang": "11"}

    @property
    @functools.lru_cache(1)
    def _poppler_data_datadir(self):
        poppler_data_conf = self.dependencies["poppler-data"].conf_info
        return poppler_data_conf.get("user.poppler-data:datadir", check_type=str)

    def validate(self):
        if self.options.fontconfiguration == "win32" and self.settings.os != "Windows":
            raise ConanInvalidConfiguration("'win32' option of fontconfig is only available on Windows")

        # C++ standard required
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._cppstd_required)

        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warning("C++14 support required. Your compiler is unknown. Assuming it supports C++14.")
        elif Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("C++14 support required, which your compiler does not support.")

        if self.options.with_nss:
            # FIXME: missing nss recipe
            raise ConanInvalidConfiguration("nss is not (yet) available on cci")

        if self.settings.os == "Windows" and self.options.with_libjpeg == "libjpeg":
            raise ConanInvalidConfiguration(
                "Build with libjpeg isn't supported on Windows (see https://gitlab.freedesktop.org/poppler/poppler/-/issues/1180)"
            )

    def build_requirements(self):
        self.tool_requires("pkgconf/1.9.3")
        self.tool_requires("cmake/[>=3.18 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    @property
    def _dct_decoder(self):
        if self.options.with_libjpeg:
            return "libjpeg"

        return "none"

    @property
    @functools.lru_cache(1)
    def _qt_major(self):
        return Version(self.dependencies["qt"].ref.version).major

    @property
    def _uses_qt6(self):
        return self._qt_major == "6"

    @property
    def _cppstd_required(self):
        if self.options.with_qt and self._uses_qt6:
            return 17

        return 14

    def generate(self):
        tc = CMakeToolchain(self)

        tc.variables["ENABLE_UNSTABLE_API_ABI_HEADERS"] = True
        tc.variables["BUILD_GTK_TESTS"] = False
        tc.variables["BUILD_QT5_TESTS"] = False
        tc.variables["BUILD_QT6_TESTS"] = False
        tc.variables["BUILD_CPP_TESTS"] = False
        tc.variables["BUILD_MANUAL_TESTS"] = False

        tc.variables["ENABLE_UTILS"] = False
        tc.variables["ENABLE_CPP"] = self.options.cpp
        tc.variables["ENABLE_BOOST"] = self.options.splash
        tc.variables["FONT_CONFIGURATION"] = self.options.fontconfiguration
        tc.variables["WITH_JPEG"] = bool(self.options.with_libjpeg)
        tc.variables["WITH_PNG"] = self.options.with_png
        tc.variables["WITH_TIFF"] = self.options.with_tiff
        tc.variables["WITH_NSS3"] = self.options.with_nss
        tc.variables["WITH_Cairo"] = self.options.with_cairo
        tc.variables["ENABLE_GLIB"] = self.options.get_safe("with_glib", False)
        tc.variables["ENABLE_GOBJECT_INTROSPECTION"] = self.options.get_safe("with_gobject_introspection", False)
        tc.variables["WITH_Iconv"] = self.options.get_safe("with_libiconv", False)
        tc.variables["ENABLE_ZLIB"] = self.options.with_zlib
        tc.variables["ENABLE_LIBOPENJPEG"] = "openjpeg2" if self.options.with_openjpeg else "none"
        tc.variables["ENABLE_CMS"] = "lcms2" if self.options.with_lcms else "none"
        tc.variables["ENABLE_LIBCURL"] = self.options.with_libcurl

        tc.variables["POPPLER_DATADIR"] = self._poppler_data_datadir.replace("\\", "/")
        tc.variables["FONT_CONFIGURATION"] = self.options.fontconfiguration
        tc.variables["BUILD_CPP_TESTS"] = False
        tc.variables["ENABLE_GTK_DOC"] = False
        tc.variables["ENABLE_QT5"] = self.options.with_qt and not self._uses_qt6
        tc.variables["ENABLE_QT6"] = self.options.with_qt and self._uses_qt6

        tc.variables["ENABLE_DCTDECODER"] = self._dct_decoder
        tc.variables["USE_FLOAT"] = self.options.float
        tc.variables["RUN_GPERF_IF_PRESENT"] = False
        if self.settings.os == "Windows":
            tc.variables["ENABLE_RELOCATABLE"] = self.options.shared
        tc.variables["EXTRA_WARN"] = False
        tc.variables["WITH_Gpgmepp"] = False

        # Workaround for cross-build to at least iOS/tvOS/watchOS,
        # when dependencies are found with find_path() and find_library()
        if cross_building(self):
            tc.variables["CMAKE_FIND_ROOT_PATH_MODE_INCLUDE"] = "BOTH"
            tc.variables["CMAKE_FIND_ROOT_PATH_MODE_LIBRARY"] = "BOTH"
        tc.generate()

        vbe = VirtualBuildEnv(self)
        vbe.generate()
        if not cross_building(self):
            vre = VirtualRunEnv(self)
            vre.generate(scope="build")

        deps = CMakeDeps(self)
        deps.set_property("freetype", "cmake_target_name", "Freetype::Freetype")
        # conan-io/conan#12600
        if is_msvc(self):
            deps.set_property("libjpeg", "cmake_find_mode", "module")
            deps.set_property("libiconv", "cmake_find_mode", "module")
        deps.generate()

    def build(self):
        apply_conandata_patches(self)

        # Use CMake's built-in version of FindIconv.cmake to fix the build on MacOS
        rm(self, "FindIconv.cmake", os.path.join(self.source_folder, "cmake", "modules"))

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
        if self.options.with_libjpeg == "libjpeg-turbo":
            self.cpp_info.components["libpoppler"].requires.append("libjpeg-turbo::libjpeg-turbo")
        elif self.options.with_libjpeg == "libjpeg":
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
            self.cpp_info.components["libpoppler-splash"].requires = [
                "libpoppler",
                "boost::boost",
            ]  # FIXME: should be boost::headers, see https://github.com/conan-io/conan-center-index/pull/2097

        if self.options.with_cairo:
            self.cpp_info.components["libpoppler-cairo"].libs = []
            self.cpp_info.components["libpoppler-cairo"].names["pkg_config"] = "poppler-cairo"
            self.cpp_info.components["libpoppler-cairo"].requires = ["libpoppler", "cairo::cairo"]

        if self.options.get_safe("with_glib"):
            self.cpp_info.components["libpoppler-glib"].libs = ["poppler-glib"]
            self.cpp_info.components["libpoppler-glib"].names["pkg_config"] = "poppler-glib"
            self.cpp_info.components["libpoppler-glib"].requires = ["libpoppler-cairo", "glib::glib"]
            if self.options.get_safe("with_gobject_introspection"):
                self.cpp_info.components["libpoppler-glib"].requires.append(
                    "gobject-introspection::gobject-introspection"
                )

        if self.options.with_qt:
            qt_major = self._qt_major
            self.cpp_info.components["libpoppler-qt"].libs = [f"poppler-qt{qt_major}"]
            self.cpp_info.components["libpoppler-qt"].names["pkg_config"] = f"poppler-qt{qt_major}"
            self.cpp_info.components["libpoppler-qt"].requires = [
                "libpoppler",
                "qt::qtCore",
                "qt::qtGui",
                "qt::qtWidgets",
            ]

        datadir = self._poppler_data_datadir
        self.output.info(f"Setting POPPLER_DATADIR env var: {datadir}")
        self.env_info.POPPLER_DATADIR = datadir
