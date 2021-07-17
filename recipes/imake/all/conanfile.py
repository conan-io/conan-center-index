from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os

required_conan_version = ">=1.33.0"


class ImakeConan(ConanFile):
    name = "imake"
    description = "Obsolete C preprocessor interface to the make utility"
    topics = ("conan", "imake", "xmkmf", "preprocessor", "build", "system")
    license = "MIT"
    homepage = "https://gitlab.freedesktop.org/xorg/util/imake"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "ccmakedep": [True, False],
        "cleanlinks": [True, False],
        "makeg": [True, False],
        "mergelib": [True, False],
        "mkdirhier": [True, False],
        "mkhtmlindex": [True, False],
        "revpath": [True, False],
        "xmkmf": [True, False],
    }
    default_options = {
        "ccmakedep": True,
        "cleanlinks": True,
        "makeg": True,
        "mergelib": True,
        "mkdirhier": True,
        "mkhtmlindex": True,
        "revpath": True,
        "xmkmf": True,
    }

    generators = "pkg_config"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return self.settings_build if hasattr(self, "settings_build") else self.settings

    def requirements(self):
        self.requires("xorg-proto/2021.4")

    def build_requirements(self):
        self.build_requires("pkgconf/1.7.4")

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def package_id(self):
        del self.settings.compiler

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=self._settings_build == "Windows")
        yes_no = lambda v: "yes" if v else "no"
        conf_args = [
            "--enable-ccmakedep={}".format(yes_no(self.options.ccmakedep)),
            "--enable-cleanlinks={}".format(yes_no(self.options.cleanlinks)),
            "--enable-makeg={}".format(yes_no(self.options.makeg)),
            "--enable-mergelib={}".format(yes_no(self.options.mergelib)),
            "--enable-mkdirhier={}".format(yes_no(self.options.mkdirhier)),
            "--enable-mkhtmlindex={}".format(yes_no(self.options.mkhtmlindex)),
            "--enable-revpath={}".format(yes_no(self.options.revpath)),
            "--enable-xmkmf={}".format(yes_no(self.options.xmkmf)),
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
