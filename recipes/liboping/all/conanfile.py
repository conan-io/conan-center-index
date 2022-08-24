from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class LibopingConan(ConanFile):
    name = "liboping"
    description = "A multi server ping library"
    topics = ("oping", "ping", "icmp")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://noping.cc"
    license = ["LGPL-2.1", "GPL-2.0"]
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ["patches/**"]
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("liboping is not supported by Visual Studio")
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Liboping could not be built on {} as shared library".format(self.settings.os))
        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            # Build error - NO Access to a Mac/M1 - please fix when possible - see issue 8634
            raise ConanInvalidConfiguration("Liboping cannot be built on a Mac/M1 at this time")

    def build_requirements(self):
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
            "--without-ncurses",
            "--without-perl-bindings",
        ]
        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

    def build(self):
        self._patch_sources()
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()

        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
        tools.files.rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
        self.cpp_info.libs = ["oping"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")
