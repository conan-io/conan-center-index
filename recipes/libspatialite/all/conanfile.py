from conans import ConanFile, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment, tools
import os

required_conan_version = ">=1.33.0"


class LibspatialiteConan(ConanFile):
    name = "libspatialite"
    description = (
        "SpatiaLite is an open source library intended to extend the SQLite "
        "core to support fully fledged Spatial SQL capabilities."
    )
    license = ("MPL-1.1", "GPL-2.0-or-later", "LGPL-2.1-or-later")
    topics = ("spatialite", "database", "sql", "sqlite", "ogc")
    homepage = "https://www.gaia-gis.it/fossil/libspatialite"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "mathsql": [True, False],
        "geocallbacks": [True, False],
        "knn": [True, False],
        "epsg": [True, False],
        "geopackage": [True, False],
        "gcp": [True, False],
        "with_proj": [True, False],
        "with_iconv": [True, False],
        "with_freexl": [True, False],
        "with_geos": [True, False],
        "with_rttopo": [True, False],
        "with_libxml2": [True, False],
        "with_minizip": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "mathsql": True,
        "geocallbacks": True,
        "knn": True,
        "epsg": True,
        "geopackage": True,
        "gcp": True,
        "with_proj": True,
        "with_iconv": True,
        "with_freexl": True,
        "with_geos": True,
        "with_rttopo": True,
        "with_libxml2": True,
        "with_minizip": True,
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
        if not self.options.with_geos:
            del self.options.with_rttopo
            del self.options.gcp

    def requirements(self):
        self.requires("sqlite3/3.36.0")
        self.requires("zlib/1.2.11")
        if self.options.with_proj:
            self.requires("proj/8.1.0")
        if self.options.with_iconv:
            self.requires("libiconv/1.16")
        if self.options.with_freexl:
            self.requires("freexl/1.0.6")
        if self.options.with_geos:
            self.requires("geos/3.9.1")
        if self.options.get_safe("with_rttopo"):
            self.requires("librttopo/1.1.0")
        if self.options.with_libxml2:
            self.requires("libxml2/2.9.12")
        if self.options.with_minizip:
            self.requires("minizip/1.2.11")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if self.settings.compiler != "Visual Studio":
            self.build_requires("libtool/2.4.6")
            self.build_requires("pkgconf/1.7.4")
            if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _build_msvc(self):
        # Visual Studio build doesn't provide options, we need to manually edit gaiaconfig-msvc.h
        gaiaconfig_msvc = os.path.join(self._source_subfolder, "src", "headers", "spatialite", "gaiaconfig-msvc.h")
        if not self.options.mathsql:
            tools.replace_in_file(gaiaconfig_msvc, "/* #undef OMIT_MATHSQL */", "#define OMIT_MATHSQL 1")
        if self.options.geocallbacks:
            tools.replace_in_file(gaiaconfig_msvc, "#define OMIT_GEOCALLBACKS 1", "")
        if not self.options.knn:
            tools.replace_in_file(gaiaconfig_msvc, "/* #undef OMIT_KNN */", "#define OMIT_KNN 1")
        if not self.options.epsg:
            tools.replace_in_file(gaiaconfig_msvc, "/* #undef OMIT_EPSG */", "#define OMIT_EPSG 1")
        if not self.options.geopackage:
            tools.replace_in_file(gaiaconfig_msvc, "#define ENABLE_GEOPACKAGE 1", "")
        if not self.options.get_safe("gcp", False):
            tools.replace_in_file(gaiaconfig_msvc, "#define ENABLE_GCP 1", "")
        if not self.options.with_proj:
            tools.replace_in_file(gaiaconfig_msvc, "/* #undef OMIT_PROJ */", "#define OMIT_PROJ 1")
        if not self.options.with_iconv:
            tools.replace_in_file(gaiaconfig_msvc, "/* #undef OMIT_ICONV */", "#define OMIT_ICONV 1")
        if not self.options.with_freexl:
            tools.replace_in_file(gaiaconfig_msvc, "/* #undef OMIT_FREEXL */", "#define OMIT_FREEXL 1")
        if not self.options.with_geos:
            tools.replace_in_file(gaiaconfig_msvc, "/* #undef OMIT_GEOS */", "#define OMIT_GEOS 1")
        if not self.options.get_safe("with_rttopo", False):
            tools.replace_in_file(gaiaconfig_msvc, "#define ENABLE_RTTOPO 1", "")
        if not self.options.with_libxml2:
            tools.replace_in_file(gaiaconfig_msvc, "#define ENABLE_LIBXML2 1", "")
        if not self.options.with_minizip:
            tools.replace_in_file(gaiaconfig_msvc, "#define ENABLE_MINIZIP 1", "")

        target = "spatialite_i.lib" if self.options.shared else "spatialite.lib"
        optflags = ["-DYY_NO_UNISTD_H"]
        system_libs = [lib + ".lib" for lib in self.deps_cpp_info.system_libs]
        if self.options.shared:
            optflags.append("-DDLL_EXPORT")
        with tools.chdir(self._source_subfolder):
            with tools.vcvars(self):
                with tools.environment_append(VisualStudioBuildEnvironment(self).vars):
                    self.run("nmake -f makefile.vc {} OPTFLAGS=\"{}\" SYSTEM_LIBS=\"{}\"".format(target,
                                                                                                 " ".join(optflags),
                                                                                                 " ".join(system_libs)))

    def _build_autotools(self):
        # fix MinGW
        tools.replace_in_file(os.path.join(self._source_subfolder, "configure.ac"),
                              "AC_CHECK_LIB(z,",
                              "AC_CHECK_LIB({},".format(self.deps_cpp_info["zlib"].libs[0]))
        # Disable tests
        tools.replace_in_file(os.path.join(self._source_subfolder, "Makefile.am"),
                              "SUBDIRS = src test $(EXAMPLES)",
                              "SUBDIRS = src $(EXAMPLES)")

        with tools.chdir(self._source_subfolder):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows)
            with tools.run_environment(self):
                autotools = self._configure_autotools()
                autotools.make()

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools

        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-mathsql={}".format(yes_no(self.options.mathsql)),
            "--enable-geocallbacks={}".format(yes_no(self.options.geocallbacks)),
            "--enable-knn={}".format(yes_no(self.options.knn)),
            "--enable-proj={}".format(yes_no(self.options.with_proj)),
            "--enable-iconv={}".format(yes_no(self.options.with_iconv)),
            "--enable-freexl={}".format(yes_no(self.options.with_freexl)),
            "--enable-epsg={}".format(yes_no(self.options.epsg)),
            "--enable-geos={}".format(yes_no(self.options.with_geos)),
            "--enable-libxml2={}".format(yes_no(self.options.with_libxml2)),
            "--enable-minizip={}".format(yes_no(self.options.with_minizip)),
            "--enable-geopackage={}".format(yes_no(self.options.geopackage)),
            "--disable-gcov",
            "--disable-examples",
            "--disable-module-only",
        ]
        if self.options.with_geos:
            args.extend([
                "--enable-gcp={}".format(yes_no(self.options.gcp)),
                "--enable-geosadvanced=yes",
                "--enable-geosreentrant=yes",
                "--enable-geosonlyreentrant=no",
                "--enable-geos370=yes",
                "--enable-rttopo={}".format(yes_no(self.options.with_rttopo)),
            ])

        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.configure(args=args)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        if self.settings.compiler == "Visual Studio":
            self._build_msvc()
        else:
            self._build_autotools()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        if self.settings.compiler == "Visual Studio":
            self.copy("spatialite.h", dst="include", src=os.path.join(self._source_subfolder, "src", "headers"))
            self.copy("*.h", dst=os.path.join("include", "spatialite"), src=os.path.join(self._source_subfolder, "src", "headers", "spatialite"))
            self.copy("*.lib", dst="lib", src=self._source_subfolder)
            self.copy("*.dll", dst="bin", src=self._source_subfolder)
        else:
            with tools.chdir(self._source_subfolder):
                with tools.run_environment(self):
                    autotools = self._configure_autotools()
                    autotools.install()
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "spatialite"
        suffix = "_i" if self.settings.compiler == "Visual Studio" and self.options.shared else ""
        self.cpp_info.libs = ["spatialite{}".format(suffix)]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])
