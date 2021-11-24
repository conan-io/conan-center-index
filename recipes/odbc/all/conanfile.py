from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os
import shutil

required_conan_version = ">=1.33.0"


class OdbcConan(ConanFile):
    name = "odbc"
    description = "Package providing unixODBC"
    topics = ("odbc", "database", "dbms", "data-access")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.unixodbc.org"
    license = ("LGPL-2.1", "GPL-2.1")
    exports_sources = "patches/**"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libiconv": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libiconv": True
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_libiconv:
            self.requires("libiconv/1.16")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Windows not supported yet. Please, open an issue if you need such support")

    def build_requirements(self):
        self.build_requires("gnu-config/cci.20201022")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        self._autotools.libs = []
        static_flag = "no" if self.options.shared else "yes"
        shared_flag = "yes" if self.options.shared else "no"
        libiconv_flag = "yes" if self.options.with_libiconv else "no"
        args = ["--enable-static=%s" % static_flag,
                "--enable-shared=%s" % shared_flag,
                "--enable-ltdl-install",
                "--enable-iconv=%s" % libiconv_flag,
                "--sysconfdir=/etc"]
        if self.options.with_libiconv:
            libiconv_prefix = self.deps_cpp_info["libiconv"].rootpath
            args.append("--with-libiconv-prefix=%s" % libiconv_prefix)
        self._autotools.configure(configure_dir=self._source_subfolder, args=args)
        return self._autotools

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_SUB,
                    os.path.join(self._source_subfolder, "config.sub"))
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_GUESS,
                    os.path.join(self._source_subfolder, "config.guess"))
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "etc"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "ODBC"
        self.cpp_info.names["cmake_find_package_multi"] = "ODBC"
        # odbc
        self.cpp_info.components["_odbc"].names["pkg_config"] = "odbc"
        self.cpp_info.components["_odbc"].libs = ["odbc"]
        self.cpp_info.components["_odbc"].requires = ["odbcltdl"]
        if self.options.with_libiconv:
            self.cpp_info.components["_odbc"].requires.append("libiconv::libiconv")
        # odbcinst
        self.cpp_info.components["odbcinst"].names["pkg_config"] = "odbcinst"
        self.cpp_info.components["odbcinst"].libs = ["odbcinst"]
        self.cpp_info.components["odbcinst"].requires = ["odbcltdl"]
        # odbccr
        self.cpp_info.components["odbccr"].names["pkg_config"] = "odbccr"
        self.cpp_info.components["odbccr"].libs = ["odbccr"]

        self.cpp_info.components["odbcltdl"].libs = ["ltdl"]

        if self.settings.os == "Linux":
            self.cpp_info.components["_odbc"].system_libs = ["pthread"]
            self.cpp_info.components["odbcinst"].system_libs = ["pthread"]
            self.cpp_info.components["odbcltdl"].system_libs = ["dl"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
