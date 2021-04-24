import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.29.1"

class ResiprocateConan(ConanFile):
    name = "resiprocate"
    description = "The project is dedicated to maintaining a complete, correct, and commercially usable implementation of SIP and a few related protocols. "
    topics = ("sip", "voip", "communication", "signaling")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.resiprocate.org"
    license = "VSL-1.0"
    exports_sources = "patches/*"
    settings = "os", "compiler", "build_type", "arch"
    options = {"fPIC": [True, False],
               "shared": [True, False],
               "with_ssl": [True, False],
               "with_postgresql": [True, False],
               "with_mysql": [True, False],
               "with_repro": [True, False]}
    default_options = {"fPIC": True,
                       "shared": False,
                       "with_ssl": True,
                       "with_postgresql": True,
                       "with_mysql": True,
                       "with_repro": True}
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.settings.os in ("Windows", "Macos"):
            # FIXME: Visual Studio project & Mac support seems available in resiprocate
            raise ConanInvalidConfiguration("reSIProcate recipe does not currently support {}.".format(self.settings.os))
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.with_ssl:
            self.requires("openssl/1.1.1j")
        if self.options.with_postgresql:
            self.requires("libpq/11.9")
        if self.options.with_mysql:
            self.requires("libmysqlclient/8.0.17")
        if self.options.with_repro:
            self.requires("libdb/4.8.30")
            self.options["libdb"].with_cxx = True

    def build_requirements(self):
        if self.options.with_repro:
            self.build_requires("cajun-jsonapi/2.0.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        yes_no = lambda v: "yes" if v else "no"
        configure_args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--with-pic={}".format(yes_no(self.options.get_safe("fPIC", True)))
        ]

        # These options do not support yes/no
        if self.options.with_ssl:
            configure_args.append("--with-ssl")
        if self.options.with_mysql:
            configure_args.append("--with-mysql")
        if self.options.with_postgresql:
            configure_args.append("--with-postgresql")
        if self.options.with_repro:
            configure_args.append("--with-repro")

        self._autotools.configure(configure_dir=self._source_subfolder, args=configure_args)
        return self._autotools

    def build(self):
        self._patch_sources()
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()
        tools.rmdir(os.path.join(os.path.join(self.package_folder, "share")))
        tools.remove_files_by_mask(os.path.join(self.package_folder), "*.la")

    def package_info(self):
        if(self.options.with_repro):
            self.cpp_info.libs += ["repro"]
        self.cpp_info.libs += ["dum","resip", "rutil", "resipares"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs = ["pthread"]
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
