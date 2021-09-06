from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class Librasterlite2Conan(ConanFile):
    name = "librasterlite2"
    description = (
        "librasterlite2 is an open source library that stores and retrieves "
        "huge raster coverages using a SpatiaLite DBMS."
    )
    license = ("MPL-1.1", "GPL-2.0-or-later", "LGPL-2.1-or-later")
    topics = ("rasterlite", "raster", "spatialite")
    homepage = "https://www.gaia-gis.it/fossil/librasterlite2"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openjpeg": [True, False],
        "with_webp": [True, False],
        "with_lzma": [True, False],
        "with_lz4": [True, False],
        "with_zstd": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openjpeg": True,
        "with_webp": True,
        "with_lzma": True,
        "with_lz4": True,
        "with_zstd": True,
    }

    exports_sources = "patches/**"
    generators = "pkg_config"
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("cairo/1.17.4")
        self.requires("freetype/2.10.4")
        self.requires("giflib/5.2.1")
        self.requires("libcurl/7.78.0")
        self.requires("libgeotiff/1.7.0")
        self.requires("libjpeg/9d")
        self.requires("libpng/1.6.37")
        self.requires("libspatialite/5.0.1")
        self.requires("libtiff/4.3.0")
        self.requires("libxml2/2.9.12")
        self.requires("sqlite3/3.36.0")
        self.requires("zlib/1.2.11")
        if self.options.with_openjpeg:
            self.requires("openjpeg/2.4.0")
        if self.options.with_webp:
            self.requires("libwebp/1.2.0")
        if self.options.with_lzma:
            self.requires("xz_utils/5.2.5")
        if self.options.with_lz4:
            self.requires("lz4/1.9.3")
        if self.options.with_zstd:
            self.requires("zstd/1.5.0")

    def validate(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("Visual Studio not supported yet")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")
        self.build_requires("pkgconf/1.7.4")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        # Disable tests, tools and examples
        tools.replace_in_file(os.path.join(self._source_subfolder, "Makefile.am"),
                              "SUBDIRS = headers src test tools examples",
                              "SUBDIRS = headers src")
        # fix MinGW
        tools.replace_in_file(os.path.join(self._source_subfolder, "configure.ac"),
                              "AC_CHECK_LIB(z,",
                              "AC_CHECK_LIB({},".format(self.deps_cpp_info["zlib"].libs[0]))

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--disable-gcov",
            "--enable-openjpeg={}".format(yes_no(self.options.with_openjpeg)),
            "--enable-webp={}".format(yes_no(self.options.with_webp)),
            "--enable-lzma={}".format(yes_no(self.options.with_lzma)),
            "--enable-lz4={}".format(yes_no(self.options.with_lz4)),
            "--enable-zstd={}".format(yes_no(self.options.with_zstd)),
        ]
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.configure(args=args)
        return self._autotools

    def build(self):
        self._patch_sources()
        with tools.chdir(self._source_subfolder):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows)
            with tools.run_environment(self):
                autotools = self._configure_autotools()
                autotools.make()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        with tools.chdir(self._source_subfolder):
            with tools.run_environment(self):
                autotools = self._configure_autotools()
                autotools.install()
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "rasterlite2"
        self.cpp_info.libs = ["rasterlite2"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
