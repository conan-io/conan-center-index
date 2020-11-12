import os
import shutil
from conans import ConanFile, AutoToolsBuildEnvironment, tools

class ResiprocateConan(ConanFile):
    name = "resiprocate"
    description = "The project is dedicated to maintaining a complete, correct, and commercially usable implementation of SIP and a few related protocols. "
    topics = ("sip", "voip", "communication", "signaling")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.resiprocate.org"
    license = "VSL-1.0"
    settings = "os", "compiler", "build_type", "arch"
    options = {"fPIC": [True, False],
               "shared": [True, False],
               "with_ssl": [True, False],
               "with_postgresql": [True, False],
               "with_mysql": [True, False]}
    default_options = {"fPIC": True,
                       "shared": False,
                       "with_ssl": True,
                       "with_postgresql": True,
                       "with_mysql": True}
    _autotools = None


    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    @property
    def _is_mingw_windows(self):
        return self.settings.os == "Windows" and (self.settings.compiler == 'gcc' or tools.cross_building(self.settings))

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def build_requirements(self):
        if self._is_mingw_windows and not self._is_msvc:
            if "CONAN_BASH_PATH" not in os.environ and tools.os_info.detect_windows_subsystem() != 'msys2':
                self.build_requires("msys2/20190524")

    def requirements(self):
        if self.options.with_ssl:
            self.requires("openssl/1.1.1h")
        if self.options.with_postgresql:
            self.requires("libpq/11.5")
        if self.options.with_mysql:
            self.requires("libmysqlclient/8.0.17")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        shutil.rmtree(self._source_subfolder, ignore_errors=True)
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash = self._is_msvc or self._is_mingw_windows)
        yes_no = lambda v: "yes" if v else "no"
        configure_args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--with-ssl={}".format(yes_no(not self.options.with_ssl)),
            "--with-mysql={}".format(yes_no(not self.options.with_mysql)),
            "--with-postgresql={}".format(yes_no(not self.options.with_postgresql)),
            "--prefix={}".format(tools.unix_path(self.package_folder))
        ]

        if self.settings.os == "Linux":
            configure_args.extend(["--with-pic={}".format(yes_no(not self.options.get_safe("fPIC", False)))])

        self._autotools.configure(configure_dir=self._source_subfolder, args=configure_args)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()
        tools.rmdir(os.path.join(os.path.join(self.package_folder, "share")))
        tools.remove_files_by_mask(os.path.join(self.package_folder), "*.la")

    def package_info(self):
        self.cpp_info.libs = ["resip", "rutil", "dum", "resipares"]
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
