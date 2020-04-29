from conans import AutoToolsBuildEnvironment, ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import glob
import os


class AprUtilConan(ConanFile):
    name = "apr-util"
    description = "The Apache Portable Runtime (APR) provides a predictable and consistent interface to underlying platform-specific implementations"
    license = "Apache-2.0"
    topics = ("conan", "apr-util", "apache", "platform", "library")
    homepage = "https://apr.apache.org/"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "crypto": [False, "openssl", "nss", "commoncrypto"],
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
        "crypto": "openssl",
        "dbm": False,
        "with_expat": True,
        "with_mysql": True,
        "with_postgresql": True,
        "with_sqlite3": True,
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

        if self.settings.compiler == "Visual Studio":
            if self.options.crypto and self.options.crypto != "openssl":
                raise ConanInvalidConfiguration("Visual Studio only supports openssl crypto")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):
        self.requires("apr/1.7.0")
        if self.options.crypto == "openssl":
            self.requires("openssl/1.1.1g")  # FIXME: 1.1 is not supported by mysql-connector-c
        elif self.options.crypto == "nss":
            # self.requires("nss/x.y.z")
            raise ConanInvalidConfiguration("CCI has no nss recipe (yet)")
        elif self.options.crypto == "commoncrypto":
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
            self.requires("libmysqlclient/8.0.17")
        if self.options.with_sqlite3:
            self.requires("sqlite3/3.31.1")
        if self.options.with_expat:
            self.requires("expat/2.2.9")
        if self.options.with_postgresql:
            self.requires("libpq/11.5")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["APR_INCLUDE_DIR"] = ";".join(self.deps_cpp_info["apr"].include_paths)
        self._cmake.definitions["INSTALL_PDB"] = False
        self._cmake.definitions["APU_HAVE_CRYPTO"] = bool(self.options.crypto)
        self._cmake.definitions["APR_HAS_LDAP"] = self.options.with_ldap
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        my_unix_path = tools.unix_path if tools.os_info.is_windows else lambda x: x
        conf_args = [
            "--with-apr={}".format(my_unix_path(self.deps_cpp_info["apr"].rootpath)),
            "--with-crypto" if self.options.crypto else "--without-crypto",
            "--with-expat={}".format(my_unix_path(self.deps_cpp_info["expat"].rootpath)) if self.options.with_expat else "--without-expat",
            "--with-mysql={}".format(my_unix_path(self.deps_cpp_info["libmysqlclient"].rootpath)) if self.options.with_mysql else "--without-mysql",
            "--with-pgsql={}".format(my_unix_path(self.deps_cpp_info["libpq"].rootpath)) if self.options.with_postgresql else "--without-pgsql",
            "--with-sqlite3={}".format(my_unix_path(self.deps_cpp_info["sqlite3"].rootpath)) if self.options.with_sqlite3 else "--without-sqlite3",
        ]
        if self.options.dbm:
            conf_args.append("--with-dbm={}".format(self.options.dbm))
        if self.options.crypto == "openssl":
            conf_args.append("--with-openssl={}".format(my_unix_path(self.deps_cpp_info["openssl"].rootpath)))
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def build(self):
        if self.options.shared != self.options["apr"].shared:
            raise ConanInvalidConfiguration("apr-util must be built with same shared option as apr")

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

            for file in glob.glob(os.path.join(self.package_folder, "lib", "apr-util-1", "*.la")):
                os.unlink(file)
            os.unlink(os.path.join(self.package_folder, "lib", "libaprutil-1.la"))
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "apr-util-1"
        self.cpp_info.libs = ["libaprutil-1" if self.settings.os == "Windows" and self.options.shared else "aprutil-1"]
        self.cpp_info.libdirs.append(os.path.join("lib", "apr-util-1"))
        if not self.options.shared:
            self.cpp_info.defines = ["APU_DECLARE_STATIC"]
            if self.settings.os == "Linux":
                self.cpp_info.system_libs = ["dl", "pthread", "uuid"]
            elif self.settings.os == "Windows":
                self.cpp_info.system_libs = ["mswsock", "rpcrt4", "ws2_32"]

        apr_util_root = self.package_folder
        if tools.os_info.is_windows:
            apr_util_root = tools.unix_path(apr_util_root)
        self.output.info("Settings APR_UTIL_ROOT environment var: {}".format(apr_util_root))
        self.env_info.APR_UTIL_ROOT = apr_util_root
