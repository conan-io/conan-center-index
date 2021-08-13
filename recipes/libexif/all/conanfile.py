from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os

required_conan_version = ">=1.33.0"

class LibexifConan(ConanFile):
    name = "libexif"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libexif.github.io/"
    license = "LGPL-2.1"
    description = "libexif is a library for parsing, editing, and saving EXIF data."
    topics = ("exif", "metadata", "parse", "edit")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
    }
    default_options = {
        "shared": False,
    }
    
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        self.build_requires("gettext/0.20.1")
        self.build_requires("automake/1.16.3")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=self._settings_build.os == "Windows")
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        with tools.chdir(self._source_subfolder):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")), run_environment=True, win_bash=self._settings_build.os == "Windows")
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()
        tools.remove_files_by_mask(self.package_folder, "*.la")
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["exif"]
        self.cpp_info.names["pkg_config"] = "libexif"
        self.cpp_info.system_libs = ["m"]
