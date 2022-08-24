from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conan.errors import ConanInvalidConfiguration
import functools
import os
import shutil

required_conan_version = ">=1.43.0"


class OdbcConan(ConanFile):
    name = "odbc"
    description = "Package providing unixODBC"
    topics = ("odbc", "database", "dbms", "data-access")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.unixodbc.org"
    license = ("LGPL-2.1", "GPL-2.1")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libiconv": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libiconv": True,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_libiconv:
            self.requires("libiconv/1.17")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("odbc is a system lib on Windows")

    def build_requirements(self):
        self.build_requires("gnu-config/cci.20201022")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_SUB,
                    os.path.join(self._source_subfolder, "config.sub"))
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_GUESS,
                    os.path.join(self._source_subfolder, "config.guess"))
        # relocatable shared libs on macOS
        for configure in [
            os.path.join(self._source_subfolder, "configure"),
            os.path.join(self._source_subfolder, "libltdl", "configure"),
        ]:
            tools.files.replace_in_file(self, configure, "-install_name \\$rpath/", "-install_name @rpath/")

    @functools.lru_cache(1)
    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.libs = []
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--enable-ltdl-install",
            "--enable-iconv={}".format(yes_no(self.options.with_libiconv)),
            "--sysconfdir=/etc",
        ]
        if self.options.with_libiconv:
            libiconv_prefix = self.deps_cpp_info["libiconv"].rootpath
            args.append("--with-libiconv-prefix={}".format(libiconv_prefix))
        autotools.configure(configure_dir=self._source_subfolder, args=args)
        return autotools

    def build(self):
        self._patch_sources()
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "etc"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "ODBC")
        self.cpp_info.set_property("cmake_target_name", "ODBC::ODBC")
        # to avoid conflict with pkgconfig file of _odbc component
        self.cpp_info.set_property("pkg_config_name", "odbc_full_package")

        self.cpp_info.names["cmake_find_package"] = "ODBC"
        self.cpp_info.names["cmake_find_package_multi"] = "ODBC"

        # odbc
        self.cpp_info.components["_odbc"].set_property("pkg_config_name", "odbc")
        self.cpp_info.components["_odbc"].libs = ["odbc"]
        self.cpp_info.components["_odbc"].requires = ["odbcltdl"]
        if self.options.with_libiconv:
            self.cpp_info.components["_odbc"].requires.append("libiconv::libiconv")

        # odbcinst
        self.cpp_info.components["odbcinst"].set_property("pkg_config_name", "odbcinst")
        self.cpp_info.components["odbcinst"].libs = ["odbcinst"]
        self.cpp_info.components["odbcinst"].requires = ["odbcltdl"]

        # odbccr
        self.cpp_info.components["odbccr"].set_property("pkg_config_name", "odbccr")
        self.cpp_info.components["odbccr"].libs = ["odbccr"]

        self.cpp_info.components["odbcltdl"].libs = ["ltdl"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_odbc"].system_libs = ["pthread"]
            self.cpp_info.components["odbcinst"].system_libs = ["pthread"]
            self.cpp_info.components["odbcltdl"].system_libs = ["dl"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
