from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"

class PatchElfConan(ConanFile):
    name = "patchelf"
    description = "A small utility to modify the dynamic linker and RPATH of ELF executables"
    topics = ("conan", "elf", "linker", "interpreter", "RPATH", "binaries")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/NixOS/patchelf"
    license = "GPL-3.0-or-later"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": False,  # TODO justify
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")

    def configure(self):
        if not tools.is_apple_os(self.settings.os) and self.settings.os != "Linux":
            raise ConanInvalidConfiguration("PatchELF is only available for GNU-like operating systems (e.g. Linux)")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)  # TODO check if we need this win thingy
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        with tools.chdir(self._source_subfolder):
            self.run("{} -fiv --warnings=all".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows, run_environment=True)
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()

    def package_info(self):
        self.cpp_info.components["libpatchelf"].names["pkg_config"] = "patchelf"
        self.cpp_info.components["libpatchelf"].libs = ["patchelf"]
        self.cpp_info.components["libpatchelf"].includedirs.append("src")
