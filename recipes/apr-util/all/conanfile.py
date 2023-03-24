from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.microsoft import is_msvc
import os


required_conan_version = ">=1.54.0"


class AprUtilConan(ConanFile):
    name = "apr-util"
    description = (
        "The Apache Portable Runtime (APR) provides a predictable and consistent "
        "interface to underlying platform-specific implementations"
    )
    license = "Apache-2.0"
    topics = ("apr-util", "apache", "platform", "library")
    homepage = "https://apr.apache.org/"
    url = "https://github.com/conan-io/conan-center-index"

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
             self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
             self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

        if not self.options.with_expat:
            raise ConanInvalidConfiguration("expat cannot be disabled (at this time) (check back later)")

    def requirements(self):
        self.requires("apr/[>=1.7]")
        if self.settings.os != "Windows":
            #cmake build doesn't allow injection of iconv yet
            self.requires("libiconv/[>=1.16]")
        if self.options.with_openssl:
            self.requires("openssl/[>=1.1]")
        if self.options.with_nss:
            # self.requires("nss/x.y.z")
            raise ConanInvalidConfiguration("CCI has no nss recipe (yet)")
        if self.options.with_commoncrypto:
            # self.requires("commoncrypto/x.y.z")
            raise ConanInvalidConfiguration("CCI has no commoncrypto recipe (yet)")
        if self.options.dbm == "gdbm":
            # self.requires("gdbm/x.y.z")
            raise ConanInvalidConfiguration("CCI has no gdbm recipe (yet)")
        elif self.options.dbm == "ndbm":
            # self.requires("ndbm/x.y.z")
            raise ConanInvalidConfiguration("CCI has no ndbm recipe (yet)")
        elif self.options.dbm == "db":
            # self.requires("libdb/x.y.z")
            raise ConanInvalidConfiguration("CCI has no libdb recipe (yet)")
        if self.options.with_lber:
            # self.requires("lber/x.y.z")
            raise ConanInvalidConfiguration("CCI has no lber recipe (yet)")
        if self.options.with_ldap:
            # self.requires("ldap/x.y.z")
            raise ConanInvalidConfiguration("CCI has no ldap recipe (yet)")
        if self.options.with_mysql:
            self.requires("libmysqlclient/[>=8.0]")
        if self.options.with_sqlite3:
            self.requires("sqlite3/[>=3.35]")
        if self.options.with_expat:
            self.requires("expat/[>=2.4]")
        if self.options.with_postgresql:
            self.requires("libpq/[>=13.2]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def validate(self):
        if self.options.shared != self.dependencies["apr"].options.shared:
            raise ConanInvalidConfiguration("apr-util must be built with same shared option as apr")

    @property
    def _with_crypto(self):
        return self.options.with_openssl or self.options.with_nss or self.options.with_commoncrypto

    def generate(self):
        if is_msvc(self):
            tc = CMakeToolchain(self)
            tc.variables["INSTALL_PDB"] = False
            tc.variables["APR_INCLUDE_DIR"] = ";".join(self.dependencies["apr"].cpp_info.includedirs).replace("\\", "/")
            tc.variables["APU_HAVE_CRYPTO"] = self._with_crypto
            tc.variables["APR_HAS_LDAP"] = self.options.with_ldap
            tc.generate()
            cmake_deps = CMakeDeps(self)
            cmake_deps.generate()
        else:
            env = VirtualBuildEnv(self)
            env.generate()
            tc = AutotoolsToolchain(self)
            tc.configure_args.append("--with-installbuilddir=${prefix}/res/build-1")
            tc.configure_args.append("--with-apr={}".format(self.dependencies["apr"].package_folder))
            tc.configure_args.append("--with-crypto" if self._with_crypto else "--without-crypto")
            tc.configure_args.append("--with-iconv={}".format(self.dependencies["libiconv"].package_folder))
            tc.configure_args.append("--with-openssl={}".format(self.dependencies["openssl"].package_folder) if self.options.with_openssl else "--without-openssl")
            tc.configure_args.append("--with-expat={}".format(self.dependencies["expat"].package_folder) if self.options.with_expat else "--without-expat")
            tc.configure_args.append("--with-mysql={}".format(self.dependencies["libmysqlclient"].package_folder) if self.options.with_mysql else "--without-mysql")
            tc.configure_args.append("--with-pgsql={}".format(self.dependencies["libpq"].package_folder) if self.options.with_postgresql else "--without-pgsql")
            tc.configure_args.append("--with-sqlite3={}".format(self.dependencies["sqlite3"].package_folder) if self.options.with_sqlite3 else "--without-sqlite3")
            tc.configure_args.append("--with-ldap={}".format(self.dependencies["ldap"].package_folder) if self.options.with_ldap else "--without-ldap")
            tc.configure_args.append("--with-berkeley-db={}".format(self.dependencies["libdb"].package_folder) if self.options.dbm == "db" else "--without-berkeley-db")
            tc.configure_args.append("--with-gdbm={}".format(self.dependencies["gdbm"].package_folder) if self.options.dbm == "gdbm" else "--without-gdbm")
            tc.configure_args.append("--with-ndbm={}".format(self.dependencies["ndbm"].package_folder) if self.options.dbm == "ndbm" else "--without-ndbm")
            if self.options.dbm:
                tc.configure_args.append("--with-dbm={}".format(self.options.dbm))
            if cross_building(self):
                tc.configure_args.append("apr_cv_mutex_robust_shared=yes")
            tc.generate()

    def build(self):
        apply_conandata_patches(self)
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.configure()
            cmake.build()
        else:
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.install()
        else:
            autotools = Autotools(self)
            autotools.install()
            rm(self, "*.la", os.path.join(self.package_folder, "apr-util-1", "lib"))
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "apr-util-1"
        self.cpp_info.libs = ["libaprutil-1" if self.settings.os == "Windows" and self.options.shared else "aprutil-1"]
        self.cpp_info.libdirs.append(os.path.join("lib", "apr-util-1"))
        if not self.options.shared:
            self.cpp_info.defines = ["APU_DECLARE_STATIC"]
            if self.settings.os == "Linux":
                self.cpp_info.system_libs = ["dl", "pthread", "rt"]
            elif self.settings.os == "Windows":
                self.cpp_info.system_libs = ["mswsock", "rpcrt4", "ws2_32"]

        # TODO: to remove in conan v2
        binpath = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var : {}".format(binpath))
        self.env_info.PATH.append(binpath)

        apr_util_root = self.package_folder
        self.output.info("Settings APR_UTIL_ROOT environment var: {}".format(apr_util_root))
        self.env_info.APR_UTIL_ROOT = apr_util_root

        if self.settings.compiler != "msvc":
            self.env_info.APRUTIL_LDFLAGS = " ".join("-L{}".format(l) for l in self.deps_cpp_info.lib_paths)
