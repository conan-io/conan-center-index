import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conan.errors import ConanInvalidConfiguration
required_conan_version = ">=1.43.0"


class OpenldapConan(ConanFile):
    name = "openldap"
    description = "OpenLDAP C++ library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.openldap.org/"
    license = "OLDAP-2.8"
    topics = ("ldap", "load-balancer", "directory-access")
    exports_sources = ["patches/*"]
    settings = settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_cyrus_sasl": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_cyrus_sasl": True

    }
    _autotools = None
    _configure_vars = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def requirements(self):
        self.requires("openssl/1.1.1q")
        if self.options.with_cyrus_sasl:
            self.requires("cyrus-sasl/2.1.27")

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(
                f"{self.name} is only supported on Linux")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools

        def yes_no(v): return "yes" if v else "no"
        self._autotools = AutoToolsBuildEnvironment(self)
        configure_args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--with-cyrus_sasl={}".format(yes_no(self.options.with_cyrus_sasl)),
            "--with-pic={}".format(yes_no(self.options.get_safe("fPIC", True))),
            "--without-fetch",
            "--with-tls=openssl",
            "--enable-auditlog"]
        self._configure_vars = self._autotools.vars
        self._configure_vars["systemdsystemunitdir"] = os.path.join(
            self.package_folder, "res")

        # Need to link to -pthread instead of -lpthread for gcc 8 shared=True
        # on CI job. Otherwise, linking fails.
        self._autotools.libs.remove("pthread")
        self._configure_vars["LIBS"] = self._configure_vars["LIBS"].replace(
            "-lpthread", "-pthread")

        self._autotools.configure(
            args=configure_args,
            configure_dir=self._source_subfolder,
            vars=self._configure_vars)
        return self._autotools

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        autotools = self._configure_autotools()

        autotools.make(vars=self._configure_vars)

    def package(self):
        autotools = self._configure_autotools()
        autotools.install(vars=self._configure_vars)
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("COPYRIGHT", dst="licenses", src=self._source_subfolder)
        for folder in ["var", "share", "etc", "lib/pkgconfig", "res"]:
            tools.rmdir(os.path.join(self.package_folder, folder))
        tools.remove_files_by_mask(
            os.path.join(
                self.package_folder,
                "lib"),
            "*.la")

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_path)
        self.output.info(
            "Appending PATH environment variable: {}".format(bin_path))

        self.cpp_info.libs = ["ldap", "lber"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
