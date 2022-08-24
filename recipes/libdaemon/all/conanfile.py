from conan import ConanFile, tools
from conans import AutoToolsBuildEnvironment
from conan.errors import ConanInvalidConfiguration
import os
import shutil

required_conan_version = ">=1.33.0"

class LibDaemonConan(ConanFile):
    name = "libdaemon"
    description = "a lightweight C library that eases the writing of UNIX daemons"
    topics = ("daemon")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://0pointer.de/lennart/projects/libdaemon/"
    license = "LGPL-2.1-or-later"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)


    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("Visual Studio not supported")

    def build_requirements(self):
        self.build_requires("gnu-config/cci.20201022")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--disable-examples",
        ]
        if tools.build.cross_building(self, self):
            args.append("ac_cv_func_setpgrp_void=yes")
        self._autotools.configure(configure_dir=self._source_subfolder, args=args)
        return self._autotools

    def build(self):
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_SUB,
                    os.path.join(self._source_subfolder, "config.sub"))
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_GUESS,
                    os.path.join(self._source_subfolder, "config.guess"))
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        autotools = self._configure_autotools()
        autotools.install()
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
        
    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libdaemon"
        self.cpp_info.libs = ["daemon"]
