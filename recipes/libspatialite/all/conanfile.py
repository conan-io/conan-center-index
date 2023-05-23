from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import (
    apply_conandata_patches, chdir, copy, export_conandata_patches, get,
    replace_in_file, rm, rmdir
)
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, NMakeDeps, NMakeToolchain
import os

required_conan_version = ">=1.58.0"


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
    package_type = "library"
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

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")
        if not self.options.with_geos:
            del self.options.with_rttopo
            del self.options.gcp

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("sqlite3/3.41.1")
        self.requires("zlib/1.2.13")
        if self.options.with_proj:
            self.requires("proj/9.1.1")
        if self.options.with_iconv:
            self.requires("libiconv/1.17")
        if self.options.with_freexl:
            self.requires("freexl/1.0.6")
        if self.options.with_geos:
            self.requires("geos/3.11.1")
        if self.options.get_safe("with_rttopo"):
            self.requires("librttopo/1.1.0")
        if self.options.with_libxml2:
            self.requires("libxml2/2.10.3")
        if self.options.with_minizip:
            self.requires("minizip/1.2.13")

    def build_requirements(self):
        if not is_msvc(self):
            self.tool_requires("libtool/2.4.7")
            if not self.conf.get("tools.gnu:pkg_config", check_type=str):
                self.tool_requires("pkgconf/1.9.3")
            if self._settings_build.os == "Windows":
                self.win_bash = True
                if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                    self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if is_msvc(self):
            tc = NMakeToolchain(self)
            tc.generate()
            deps = NMakeDeps(self)
            deps.generate()
        else:
            env = VirtualBuildEnv(self)
            env.generate()
            if not cross_building(self):
                env = VirtualRunEnv(self)
                env.generate(scope="build")

            tc = AutotoolsToolchain(self)
            yes_no = lambda v: "yes" if v else "no"
            tc.configure_args.extend([
                f"--enable-mathsql={yes_no(self.options.mathsql)}",
                f"--enable-geocallbacks={yes_no(self.options.geocallbacks)}",
                f"--enable-knn={yes_no(self.options.knn)}",
                f"--enable-proj={yes_no(self.options.with_proj)}",
                f"--enable-iconv={yes_no(self.options.with_iconv)}",
                f"--enable-freexl={yes_no(self.options.with_freexl)}",
                f"--enable-epsg={yes_no(self.options.epsg)}",
                f"--enable-geos={yes_no(self.options.with_geos)}",
                f"--enable-libxml2={yes_no(self.options.with_libxml2)}",
                f"--enable-minizip={yes_no(self.options.with_minizip)}",
                f"--enable-geopackage={yes_no(self.options.geopackage)}",
                "--disable-gcov",
                "--disable-examples",
                "--disable-module-only",
            ])
            if self.options.with_geos:
                tc.configure_args.extend([
                    f"--enable-gcp={yes_no(self.options.gcp)}",
                    "--enable-geosadvanced=yes",
                    "--enable-geosreentrant=yes",
                    "--enable-geosonlyreentrant=no",
                    "--enable-geos370=yes",
                    f"--enable-rttopo={yes_no(self.options.with_rttopo)}",
                ])
            tc.generate()

            deps = AutotoolsDeps(self)
            deps.generate()
            deps = PkgConfigDeps(self)
            deps.generate()

    def _build_msvc(self):
        # Visual Studio build doesn't provide options, we need to manually edit gaiaconfig-msvc.h
        gaiaconfig_msvc = os.path.join(self.source_folder, "src", "headers", "spatialite", "gaiaconfig-msvc.h")
        if not self.options.mathsql:
            replace_in_file(self, gaiaconfig_msvc, "/* #undef OMIT_MATHSQL */", "#define OMIT_MATHSQL 1")
        if self.options.geocallbacks:
            replace_in_file(self, gaiaconfig_msvc, "#define OMIT_GEOCALLBACKS 1", "")
        if not self.options.knn:
            replace_in_file(self, gaiaconfig_msvc, "/* #undef OMIT_KNN */", "#define OMIT_KNN 1")
        if not self.options.epsg:
            replace_in_file(self, gaiaconfig_msvc, "/* #undef OMIT_EPSG */", "#define OMIT_EPSG 1")
        if not self.options.geopackage:
            replace_in_file(self, gaiaconfig_msvc, "#define ENABLE_GEOPACKAGE 1", "")
        if not self.options.get_safe("gcp", False):
            replace_in_file(self, gaiaconfig_msvc, "#define ENABLE_GCP 1", "")
        if not self.options.with_proj:
            replace_in_file(self, gaiaconfig_msvc, "/* #undef OMIT_PROJ */", "#define OMIT_PROJ 1")
        if not self.options.with_iconv:
            replace_in_file(self, gaiaconfig_msvc, "/* #undef OMIT_ICONV */", "#define OMIT_ICONV 1")
        if not self.options.with_freexl:
            replace_in_file(self, gaiaconfig_msvc, "/* #undef OMIT_FREEXL */", "#define OMIT_FREEXL 1")
        if not self.options.with_geos:
            replace_in_file(self, gaiaconfig_msvc, "/* #undef OMIT_GEOS */", "#define OMIT_GEOS 1")
        if not self.options.get_safe("with_rttopo", False):
            replace_in_file(self, gaiaconfig_msvc, "#define ENABLE_RTTOPO 1", "")
        if not self.options.with_libxml2:
            replace_in_file(self, gaiaconfig_msvc, "#define ENABLE_LIBXML2 1", "")
        if not self.options.with_minizip:
            replace_in_file(self, gaiaconfig_msvc, "#define ENABLE_MINIZIP 1", "")

        target = "spatialite_i.lib" if self.options.shared else "spatialite.lib"
        optflags = ["-DYY_NO_UNISTD_H"]
        if self.options.shared:
            optflags.append("-DDLL_EXPORT")
        with chdir(self, self.source_folder):
            self.run(f"nmake -f makefile.vc {target} OPTFLAGS=\"{' '.join(optflags)}\"")

    def _build_autotools(self):
        # fix MinGW
        replace_in_file(
            self, os.path.join(self.source_folder, "configure.ac"),
            "AC_CHECK_LIB(z,",
            "AC_CHECK_LIB({},".format(self.dependencies["zlib"].cpp_info.aggregated_components().libs[0]),
        )
        # Disable tests
        replace_in_file(self, os.path.join(self.source_folder, "Makefile.am"),
                              "SUBDIRS = src test $(EXAMPLES)",
                              "SUBDIRS = src $(EXAMPLES)")

        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def build(self):
        apply_conandata_patches(self)
        if is_msvc(self):
            self._build_msvc()
        else:
            self._build_autotools()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            copy(self, "spatialite.h", src=os.path.join(self.source_folder, "src", "headers"),
                                       dst=os.path.join(self.package_folder, "include"))
            copy(self, "*.h", src=os.path.join(self.source_folder, "src", "headers", "spatialite"),
                              dst=os.path.join(self.package_folder, "include", "spatialite"))
            copy(self, "*.lib", src=self.source_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            copy(self, "*.dll", src=self.source_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
        else:
            autotools = Autotools(self)
            autotools.install()
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "spatialite")
        suffix = "_i" if is_msvc(self) and self.options.shared else ""
        self.cpp_info.libs = [f"spatialite{suffix}"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])
