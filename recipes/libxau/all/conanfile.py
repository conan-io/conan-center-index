from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os

class LibXauConan(ConanFile):
    name = "libxau"
    description = "A sample authorization protocol for X."
    topics = "x11"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.x.org"
    license = "MIT"

    generators = "pkg_config"

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
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

    def build_requirements(self):
        self.build_requires("automake/1.16.4")

    def requirements(self):
        self.requires("xorg-proto/2021.4")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def _configre_autotools(self):
        if self._autotools is not None:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        env_build = self._configre_autotools()
        env_build.make()

    def package(self):
        env_build = self._configre_autotools()
        env_build.install()

        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)

        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "xau"

        self.cpp_info.libs = ["Xau"]
