import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration


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
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Windows not supported yet. Please, open an issue if you need such support")

    def requirements(self):
        if self.options.with_libiconv:
            self.requires("libiconv/1.16")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "unixODBC-%s" % self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        static_flag = "no" if self.options.shared else "yes"
        shared_flag = "yes" if self.options.shared else "no"
        libiconv_flag = "yes" if self.options.with_libiconv else "no"
        args = ["--enable-static=%s" % static_flag,
                "--enable-shared=%s" % shared_flag,
                "--enable-ltdl-install",
                "--enable-iconv=%s" % libiconv_flag]
        if self.options.with_libiconv:
            libiconv_prefix = self.deps_cpp_info["libiconv"].rootpath
            args.append("--with-libiconv-prefix=%s" % libiconv_prefix)
        self._autotools.configure(configure_dir=self._source_subfolder, args=args)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "etc"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        os.remove(os.path.join(self.package_folder, "lib", "libodbc.la"))
        os.remove(os.path.join(self.package_folder, "lib", "libodbccr.la"))
        os.remove(os.path.join(self.package_folder, "lib", "libodbcinst.la"))
        os.remove(os.path.join(self.package_folder, "lib", "libltdl.la"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "ODBC"
        self.cpp_info.names["cmake_find_package_multi"] = "ODBC"

        self.env_info.path.append(os.path.join(self.package_folder, "bin"))

        self.cpp_info.libs = ["odbc", "odbccr", "odbcinst", "ltdl"]
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("dl")
