import os

from conan.tools.gnu import Autotools, AutotoolsToolchain
from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class LibPciAccessConan(ConanFile):
    name = "libpciaccess"
    description = "Generic PCI access library"
    topics = ("pci", "xorg")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.freedesktop.org/xorg/lib/libpciaccess"
    license = "MIT", "X11"

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def validate(self):
        def is_supported(settings):
            if settings.os in ("Linux", "FreeBSD", "SunOS"):
                return True
            return settings.os == "Windows" and settings.get_safe("os.subsystem") == "cygwin"
        if not is_supported(self.settings):
            raise ConanInvalidConfiguration("Unsupported architecture.")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        self.build_requires("pkgconf/1.7.4")
        self.build_requires("xorg-macros/1.19.3")
        self.build_requires("libtool/2.4.6")

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.default_configure_install_args = True
        tc.generate()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def build(self):
        # autoreconf
        self.run("{} -fiv".format(tools.get_env("AUTORECONF") or "autoreconf"),
                 win_bash=tools.os_info.is_windows, run_environment=True, cwd=self._source_subfolder)

        autotools = Autotools(self)
        autotools.configure(build_script_folder=self._source_subfolder)
        autotools.make()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses",
                  src=self._source_subfolder)

        autotools = Autotools(self)
        autotools.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.remove_files_by_mask(os.path.join(
            self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.set_property("pkg_config_name", "pciaccess")
