from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conan.errors import ConanInvalidConfiguration
import functools
import os
import shutil

required_conan_version = ">=1.36.0"


class LibmetalinkConan(ConanFile):
    name = "libmetalink"
    description = (
        "Libmetalink is a library to read Metalink XML download description format. "
        "It supports both Metalink version 3 and Metalink version 4 (RFC 5854)."
    )
    license = "MIT"
    topics = ("libmetalink", "metalink", "xml")
    homepage = "https://launchpad.net/libmetalink"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "xml_backend": ["expat", "libxml2"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "xml_backend": "expat",
    }

    generators = "pkg_config"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.xml_backend == "expat":
            self.requires("expat/2.4.6")
        if self.options.xml_backend == "libxml2":
            self.requires("libxml2/2.9.12")

    def validate(self):
        if self._is_msvc:
            raise ConanInvalidConfiguration("libmetalink does not support Visual Studio yet")

    def build_requirements(self):
        self.build_requires("gnu-config/cci.20201022")
        self.build_requires("pkgconf/1.7.4")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        # Support more configurations
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_SUB,
                    os.path.join(self._source_subfolder, "config.sub"))
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_GUESS,
                    os.path.join(self._source_subfolder, "config.guess"))
        # Relocatable shared lib for Apple platforms
        tools.files.replace_in_file(self, 
            os.path.join(self._source_subfolder, "configure"),
            "-install_name \\$rpath/",
            "-install_name @rpath/",
        )

    @functools.lru_cache(1)
    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.libs = []
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--with-libexpat={}".format(yes_no(self.options.xml_backend == "expat")),
            "--with-libxml2={}".format(yes_no(self.options.xml_backend == "libxml2")),
            "ac_cv_func_malloc_0_nonnull=yes",
        ]
        autotools.configure(configure_dir=self._source_subfolder, args=args)
        return autotools

    def build(self):
        self._patch_sources()
        with tools.run_environment(self):
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        with tools.run_environment(self):
            autotools = self._configure_autotools()
            autotools.install()
        tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.la")
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libmetalink")
        self.cpp_info.libs = ["metalink"]
