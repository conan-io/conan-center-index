from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.54.0"


class AprUtilConan(ConanFile):
    name = "apr-util"
    description = (
        "The Apache Portable Runtime (APR) provides a predictable and "
        "consistent interface to underlying platform-specific implementations"
    )
    license = "Apache-2.0"
    topics = ("apache", "platform", "library")
    homepage = "https://apr.apache.org/"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openssl": [True, False],
        "with_nss": [True, False],
        "with_commoncrypto": [True, False],
        "dbm": [False, "gdbm", "ndbm", "db"],
        "with_expat": [True, False],
        "with_mysql": [True, False],
        "with_postgresql": [True, False],
        "with_sqlite3": [True, False],
        "with_lber": [True, False],
        "with_ldap": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openssl": False,
        "with_nss": False,
        "with_commoncrypto": False,
        "dbm": False,
        "with_expat": True,
        "with_mysql": False,
        "with_postgresql": False,
        "with_sqlite3": False,
        "with_lber": False,
        "with_ldap": False,
    }

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
        self.options["apr"].shared = self.options.shared

    def layout(self):
        if self.settings.os == "Windows":
            cmake_layout(self, src_folder="src")
        else:
            basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("apr/1.7.0", transitive_headers=True)
        if self.settings.os != "Windows":
            #cmake build doesn't allow injection of iconv yet
            # https://github.com/conan-io/conan-center-index/pull/16142#issuecomment-1494282164
            self.requires("libiconv/1.17", transitive_libs=True)
        if self.options.with_openssl:
            self.requires("openssl/1.1.1t")
        if self.options.with_mysql:
            self.requires("libmysqlclient/8.0.31")
        if self.options.with_sqlite3:
            self.requires("sqlite3/3.41.1")
        if self.options.with_expat:
            self.requires("expat/2.5.0")
        if self.options.with_postgresql:
            self.requires("libpq/14.5")

    def validate(self):
        if not self.options.with_expat:
            raise ConanInvalidConfiguration("expat cannot be disabled (at this time) (check back later)")
        if self.options.shared != self.dependencies["apr"].options.shared:
            raise ConanInvalidConfiguration("apr-util must be built with same shared option as apr")
        if self.options.with_nss:
            raise ConanInvalidConfiguration("CCI has no nss recipe (yet)")
        if self.options.with_commoncrypto:
            raise ConanInvalidConfiguration("CCI has no commoncrypto recipe (yet)")
        if self.options.dbm == "gdbm":
            raise ConanInvalidConfiguration("CCI has no gdbm recipe (yet)")
        elif self.options.dbm == "ndbm":
            raise ConanInvalidConfiguration("CCI has no ndbm recipe (yet)")
        elif self.options.dbm == "db":
            raise ConanInvalidConfiguration("CCI has no libdb recipe (yet)")
        if self.options.with_lber:
            raise ConanInvalidConfiguration("CCI has no lber recipe (yet)")
        if self.options.with_ldap:
            raise ConanInvalidConfiguration("CCI has no ldap recipe (yet)")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _with_crypto(self):
        return self.options.with_openssl or self.options.with_nss or self.options.with_commoncrypto

    def generate(self):
        if self.settings.os == "Windows":
            tc = CMakeToolchain(self)
            tc.variables["INSTALL_PDB"] = False
            tc.variables["APU_HAVE_CRYPTO"] = self._with_crypto
            tc.variables["APR_HAS_LDAP"] = self.options.with_ldap
            tc.generate()
            deps = CMakeDeps(self)
            deps.generate()
        else:
            if not cross_building(self):
                env = VirtualRunEnv(self)
                env.generate(scope="build")

            tc = AutotoolsToolchain(self)
            yes_no = lambda v: "yes" if v else "no"
            rootpath_no = lambda v, req: self.dependencies[req].package_folder if v else "no"
            tc.configure_args.extend([
                f"--with-apr={rootpath_no(True, 'apr')}",
                f"--with-crypto={yes_no(self._with_crypto)}",
                f"--with-iconv={rootpath_no(True, 'libiconv')}",
                f"--with-openssl={rootpath_no(self.options.with_openssl, 'openssl')}",
                f"--with-expat={rootpath_no(self.options.with_expat, 'expat')}",
                f"--with-mysql={rootpath_no(self.options.with_mysql, 'libmysqlclient')}",
                f"--with-pgsql={rootpath_no(self.options.with_postgresql, 'libpq')}",
                f"--with-sqlite3={rootpath_no(self.options.with_sqlite3, 'sqlite3')}",
                f"--with-ldap={rootpath_no(self.options.with_ldap, 'ldap')}",
                f"--with-berkeley-db={rootpath_no(self.options.dbm == 'db', 'libdb')}",
                f"--with-gdbm={rootpath_no(self.options.dbm == 'gdbm', 'gdbm')}",
                f"--with-ndbm={rootpath_no(self.options.dbm == 'ndbm', 'ndbm')}",
            ])
            if self.options.dbm:
                tc.configure_args.append(f"--with-dbm={self.options.dbm}")
            if self._with_crypto and self.settings.os in ["Linux", "FreeBSD"]:
                tc.extra_ldflags.append("-ldl")
            env = tc.environment()
            env.define_path("APR_ROOT", self.dependencies["apr"].package_folder)
            env.define_path("_APR_BUILDDIR", os.path.join(self.dependencies["apr"].package_folder, "res", "build-1"))
            tc.generate(env)

            deps = AutotoolsDeps(self)
            deps.generate()

    def build(self):
        apply_conandata_patches(self)
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.configure()
            cmake.build()
        else:
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.install()
        else:
            autotools = Autotools(self)
            autotools.install()
            rm(self, "*.la", os.path.join(self.package_folder, "lib"), recursive=True)
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "apr-util-1")
        if self.settings.os == "Windows":
            self.cpp_info.libs = ["apr_dbd_odbc-1"]
            if self._with_crypto:
                self.cpp_info.libs.append("apr_crypto_openssl-1")
            if self.options.with_ldap:
                self.cpp_info.libs.append("apr_ldap-1")
            prefix = "lib" if self.options.shared else ""
            self.cpp_info.libs.append(f"{prefix}aprutil-1")
        else:
            self.cpp_info.libs = ["aprutil-1"]
        self.cpp_info.libdirs.append(os.path.join("lib", "apr-util-1"))
        if not self.options.shared:
            self.cpp_info.defines = ["APU_DECLARE_STATIC"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs = ["crypt", "dl", "pthread", "rt"]
            elif self.settings.os == "Windows":
                self.cpp_info.system_libs = ["mswsock", "odbc32", "rpcrt4", "ws2_32"]

        self.runenv_info.define_path("APR_UTIL_ROOT", self.package_folder)

        deps = [dep for dep in reversed(self.dependencies.host.topological_sort.values())]
        libdirs = [p for dep in deps for p in dep.cpp_info.aggregated_components().includedirs]
        aprutil_ldflags = " ".join([f"-L{p}" for p in libdirs])
        self.runenv_info.define("APRUTIL_LDFLAGS", aprutil_ldflags)

        # TODO: to remove in conan v2
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.APR_UTIL_ROOT = self.package_folder
        if not is_msvc(self):
            self.env_info.APRUTIL_LDFLAGS = aprutil_ldflags
