from conans import ConanFile, Meson, tools
from conans.errors import ConanInvalidConfiguration
import os


class XkbcommonConan(ConanFile):
    name = "xkbcommon"
    description = "keymap handling library for toolkits and window systems"
    topics = ("conan", "xkbcommon", "keyboard")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xkbcommon/libxkbcommon"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_x11": [True, False],
        "with_wayland": [True, False],
        "xkbregistry": [True, False],
        "docs": [True, False, "deprecated"]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_x11": True,
        "with_wayland": False,
        "xkbregistry": True,
        "docs": "deprecated"
    }

    generators = "pkg_config"

    _meson = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _has_xkbregistry_option(self):
        return tools.Version(self.version) >= "1.0.0"

    def config_options(self):
        if not self._has_xkbregistry_option:
            del self.options.xkbregistry

    def configure(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("This library is only compatible with Linux or FreeBSD")
        if self.options.docs != "deprecated":
            self.output.warn("'docs' option is deprecated. Do not use.")

        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("xorg/system")
        if self.options.get_safe("xkbregistry"):
            self.requires("libxml2/2.9.10")

    def build_requirements(self):
        self.build_requires("meson/0.56.2")
        self.build_requires("bison/3.7.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "libxkbcommon-" + self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_meson(self):
        if self._meson:
            return self._meson
        defs={
            "enable-wayland": self.options.with_wayland,
            "enable-docs": False,
            "enable-x11": self.options.with_x11,
            "libdir": os.path.join(self.package_folder, "lib"),
            "default_library": ("shared" if self.options.shared else "static")}
        if self._has_xkbregistry_option:
            defs["enable-xkbregistry"] = self.options.xkbregistry

        # workaround for https://github.com/conan-io/conan-center-index/issues/3377
        # FIXME: do not remove this pkg-config file once xorg recipe fixed
        xeyboard_config_pkgfile = os.path.join(self.build_folder, "xkeyboard-config.pc")
        if os.path.isfile(xeyboard_config_pkgfile):
            os.remove(xeyboard_config_pkgfile)

        self._meson = Meson(self)
        self._meson.configure(
            defs=defs,
            source_folder=self._source_subfolder,
            build_folder=self._build_subfolder,
            pkg_config_paths=self.build_folder)
        return self._meson

    def build(self):
        with tools.run_environment(self):
            meson = self._configure_meson()
            meson.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        meson = self._configure_meson()
        meson.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_id(self):
        del self.info.options.docs

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "xkbcommon_full_package" # unofficial, but required to avoid side effects (libxkbcommon component "steals" the default global pkg_config name)
        self.cpp_info.components["libxkbcommon"].names["pkg_config"] = "xkbcommon"
        self.cpp_info.components["libxkbcommon"].libs = ["xkbcommon"]
        self.cpp_info.components["libxkbcommon"].requires = ["xorg::xkeyboard-config"]
        if self.options.with_x11:
            self.cpp_info.components["libxkbcommon-x11"].names["pkg_config"] = "xkbcommon-x11"
            self.cpp_info.components["libxkbcommon-x11"].libs = ["xkbcommon-x11"]
            self.cpp_info.components["libxkbcommon-x11"].requires = ["libxkbcommon", "xorg::xcb", "xorg::xcb-xkb"]
        if self.options.get_safe("xkbregistry"):
            self.cpp_info.components["libxkbregistry"].names["pkg_config"] = "xkbregistry"
            self.cpp_info.components["libxkbregistry"].libs = ["xkbregistry"]
            self.cpp_info.components["libxkbregistry"].requires = ["libxml2::libxml2"]

        if tools.Version(self.version) >= "1.0.0":
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
