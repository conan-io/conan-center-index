from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import VirtualRunEnv
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=2.1"


class PsqlodbcConan(ConanFile):
    name = "psqlodbc"
    description = "The official PostgreSQL ODBC driver"
    license = "LGPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://odbc.postgresql.org/"
    topics = ("postgresql", "database", "db", "odbc", "driver")
    # psqlodbc is an ODBC driver module loaded at runtime via dlopen by the
    # unixODBC driver manager. It has no static variant (the build is hard-wired
    # shared via libtool -module), so no "shared" option is exposed.
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"

    def configure(self):
        # Pure C project, no C++ runtime settings.
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libpq/14.22")
        self.requires("odbc/2.3.11")

    def validate(self):
        # Upstream supports Windows through a separate MSVC/nmake build system.
        # This recipe only covers the autotools (Unix) build against unixODBC.
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(
                f"{self.ref} is not supported on Windows. Use the upstream MSVC build instead."
            )

    def build_requirements(self):
        self.tool_requires("autoconf/2.71")
        self.tool_requires("automake/1.16.5")
        self.tool_requires("libtool/2.4.7")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        # configure runs test executables linked against shared dependencies
        if not cross_building(self):
            VirtualRunEnv(self).generate(scope="build")

        tc = AutotoolsToolchain(self)
        # configure's AC_CHECK_LIB(ltdl, ...) and unixODBC linkage add several
        # libraries (libltdl, libodbc, libodbccr) to the link line that the
        # driver never references. --as-needed drops these unused DT_NEEDED
        # entries, leaving only libpq and libodbcinst.
        tc.extra_ldflags.append("-Wl,--as-needed")
        libpq_root = self.dependencies["libpq"].package_folder
        odbc_root = self.dependencies["odbc"].package_folder
        tc.configure_args.extend([
            f"--with-libpq={libpq_root}",
            f"--with-unixodbc={odbc_root}",
        ])
        tc.generate()

        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "license.txt",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()

        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        # psqlodbcw.so / psqlodbca.so are ODBC driver modules loaded
        # exclusively at runtime (dlopen). They are not link libraries and
        # ship no public headers, so no link interface is exposed.
        self.cpp_info.includedirs = []
        self.cpp_info.libs = []
        self.cpp_info.libdirs = ["lib"]
        # The driver modules link libpq (PQ*) and unixODBC's libodbcinst
        # (SQLGetPrivateProfileString). Declare these so the runtime
        # dependencies are propagated to consumers/generators.
        self.cpp_info.requires = ["libpq::pq", "odbc::odbcinst"]
