from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.54.0"


class Librasterlite2Conan(ConanFile):
    name = "librasterlite2"
    description = (
        "librasterlite2 is an open source library that stores and retrieves "
        "huge raster coverages using a SpatiaLite DBMS."
    )
    license = "MPL-1.1 OR GPL-2.0-or-later OR LGPL-2.1-or-later"
    topics = ("rasterlite", "raster", "spatialite")
    homepage = "https://www.gaia-gis.it/fossil/librasterlite2"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
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

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cairo/1.18.0")
        self.requires("freetype/2.13.2")
        self.requires("giflib/5.2.2")
        self.requires("libcurl/[>=7.78 <9]")
        self.requires("libgeotiff/1.7.1")
        self.requires("libjpeg/9e")
        self.requires("libpng/[>=1.6 <2]")
        self.requires("libspatialite/5.1.0")
        self.requires("libtiff/4.6.0")
        self.requires("libxml2/[>=2.12.0 <3]")
        # Used in rasterlite2/sqlite.h public header
        self.requires("sqlite3/3.44.2", transitive_headers=True, transitive_libs=True)
        self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_openjpeg:
            self.requires("openjpeg/2.5.2")
        if self.options.with_webp:
            self.requires("libwebp/1.3.2")
        if self.options.with_lzma:
            self.requires("xz_utils/[>=5.4.5 <6]")
        if self.options.with_lz4:
            self.requires("lz4/1.9.4")
        if self.options.with_zstd:
            self.requires("zstd/[^1.5]")

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration("Visual Studio not supported yet")

    def build_requirements(self):
        self.tool_requires("libtool/2.4.7")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args.extend([
            "--disable-gcov",
            f"--enable-openjpeg={yes_no(self.options.with_openjpeg)}",
            f"--enable-webp={yes_no(self.options.with_webp)}",
            f"--enable-lzma={yes_no(self.options.with_lzma)}",
            f"--enable-lz4={yes_no(self.options.with_lz4)}",
            f"--enable-zstd={yes_no(self.options.with_zstd)}",
        ])
        tc.generate()

        deps = AutotoolsDeps(self)
        deps.generate()
        deps = PkgConfigDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Disable tests, tools and examples
        replace_in_file(self, os.path.join(self.source_folder, "Makefile.am"),
                              "SUBDIRS = headers src test tools examples",
                              "SUBDIRS = headers src")
        # fix MinGW
        replace_in_file(
            self, os.path.join(self.source_folder, "configure.ac"),
            "AC_CHECK_LIB(z,",
            "AC_CHECK_LIB({},".format(self.dependencies["zlib"].cpp_info.aggregated_components().libs[0]),
        )

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "rasterlite2")
        self.cpp_info.libs = ["rasterlite2"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
