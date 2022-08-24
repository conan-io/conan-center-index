from conans import AutoToolsBuildEnvironment, ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration
import os


required_conan_version = ">=1.33.0"


class AprUtilConan(ConanFile):
    name = "apr-util"
    description = "The Apache Portable Runtime (APR) provides a predictable and consistent interface to underlying platform-specific implementations"
    license = "Apache-2.0"
    topics = ("apr-util", "apache", "platform", "library")
    homepage = "https://apr.apache.org/"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake", "cmake_find_package"
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

    _autotools = None
    _cmake = None

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

        if not self.options.with_expat:
            raise ConanInvalidConfiguration("expat cannot be disabled (at this time) (check back later)")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):
        self.requires("apr/1.7.0")
        if self.settings.os != "Windows":
            #cmake build doesn't allow injection of iconv yet
            self.requires("libiconv/1.16")
        if self.options.with_openssl:
            self.requires("openssl/1.1.1k")
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
            self.requires("libmysqlclient/8.0.25")
        if self.options.with_sqlite3:
            self.requires("sqlite3/3.35.5")
        if self.options.with_expat:
            self.requires("expat/2.4.1")
        if self.options.with_postgresql:
            self.requires("libpq/13.2")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def validate(self):
        if self.options.shared != self.options["apr"].shared:
            raise ConanInvalidConfiguration("apr-util must be built with same shared option as apr")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["APR_INCLUDE_DIR"] = ";".join(self.deps_cpp_info["apr"].include_paths)
        self._cmake.definitions["INSTALL_PDB"] = False
        self._cmake.definitions["APU_HAVE_CRYPTO"] = self._with_crypto
        self._cmake.definitions["APR_HAS_LDAP"] = self.options.with_ldap
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    @property
    def _with_crypto(self):
        return self.options.with_openssl or self.options.with_nss or self.options.with_commoncrypto

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        self._autotools.libs = []
        self._autotools.include_paths = []
        if self._with_crypto:
            if self.settings.os == "Linux":
                self._autotools.libs.append("dl")
        conf_args = [
            "--with-apr={}".format(tools.unix_path(self.deps_cpp_info["apr"].rootpath)),
            "--with-crypto" if self._with_crypto else "--without-crypto",
            "--with-iconv={}".format(tools.unix_path(self.deps_cpp_info["libiconv"].rootpath)),
            "--with-openssl={}".format(tools.unix_path(self.deps_cpp_info["openssl"].rootpath)) if self.options.with_openssl else "--without-openssl",
            "--with-expat={}".format(tools.unix_path(self.deps_cpp_info["expat"].rootpath)) if self.options.with_expat else "--without-expat",
            "--with-mysql={}".format(tools.unix_path(self.deps_cpp_info["libmysqlclient"].rootpath)) if self.options.with_mysql else "--without-mysql",
            "--with-pgsql={}".format(tools.unix_path(self.deps_cpp_info["libpq"].rootpath)) if self.options.with_postgresql else "--without-pgsql",
            "--with-sqlite3={}".format(tools.unix_path(self.deps_cpp_info["sqlite3"].rootpath)) if self.options.with_sqlite3 else "--without-sqlite3",
            "--with-ldap={}".format(tools.unix_path(self.deps_cpp_info["ldap"].rootpath)) if self.options.with_ldap else "--without-ldap",
            "--with-berkeley-db={}".format(tools.unix_path(self.deps_cpp_info["libdb"].rootpath)) if self.options.dbm == "db" else "--without-berkeley-db",
            "--with-gdbm={}".format(tools.unix_path(self.deps_cpp_info["gdbm"].rootpath)) if self.options.dbm == "gdbm" else "--without-gdbm",
            "--with-ndbm={}".format(tools.unix_path(self.deps_cpp_info["ndbm"].rootpath)) if self.options.dbm == "ndbm" else "--without-ndbm",
        ]
        if self.options.dbm:
            conf_args.append("--with-dbm={}".format(self.options.dbm))
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        if self.settings.os == "Windows":
            cmake = self._configure_cmake()
            cmake.build()
        else:
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        if self.settings.os == "Windows":
            cmake = self._configure_cmake()
            cmake.install()
        else:
            autotools = self._configure_autotools()
            autotools.install()

            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib", "apr-util-1"), "*.la")
            os.unlink(os.path.join(self.package_folder, "lib", "libaprutil-1.la"))
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

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

        binpath = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var : {}".format(binpath))
        self.env_info.PATH.append(binpath)

        apr_util_root = tools.unix_path(self.package_folder)
        self.output.info("Settings APR_UTIL_ROOT environment var: {}".format(apr_util_root))
        self.env_info.APR_UTIL_ROOT = apr_util_root

        if self.settings.compiler != "Visual Studio":
            self.env_info.APRUTIL_LDFLAGS = " ".join(tools.unix_path("-L{}".format(l)) for l in self.deps_cpp_info.lib_paths)
