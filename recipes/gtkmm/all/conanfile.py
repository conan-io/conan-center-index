from conans import ConanFile, Meson, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class GtkConan(ConanFile):
    name = "gtkmm"
    description = "libraries used for creating graphical user interfaces for applications."
    topics = ("gtk", "widgets")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gtkmm.org"
    license = "LGPL-2.1-or-later"
    generators = "pkg_config"
    version = "4.6.1"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
        }
    default_options = {
        "shared": False,
        "fPIC": True
    }

    short_paths = True

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
        if self.options.shared:
            del self.options.fPIC

    def build_requirements(self):
        self.build_requires("meson/0.62.2")
        self.build_requires("pkgconf/1.7.4")

    def requirements(self):
        self.requires("cairomm/1.16.1")
        self.requires("glibmm/2.72.1")
        self.requires("glib/2.73.0")
        self.requires("gtk/4.7.0")
        self.requires("libsigcpp/3.0.7")
        self.requires("pangomm/2.50.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _configure_meson(self):
        meson = Meson(self)
        defs = {}
        args=[]
        args.append("--wrap-mode=nofallback")
        meson.configure(
            defs=defs,
            build_folder=self._build_subfolder,
            source_folder=self._source_subfolder,
            pkg_config_paths=[self.install_folder],
            args=args
        )
        return meson

    def build(self):
        with tools.environment_append(tools.RunEnvironment(self).vars):
            meson = self._configure_meson()
            meson.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        meson = self._configure_meson()
        with tools.environment_append({
            "PKG_CONFIG_PATH": self.install_folder,
            "PATH": [os.path.join(self.package_folder, "bin")]}):
            meson.install()

        self.copy(pattern="COPYING", src=self._source_subfolder, dst="licenses")
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*.pdb")
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.pdb")

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "gtkmm"
        self.cpp_info.libs = ["gtkmm-4"]
        self.cpp_info.includedirs.append(os.path.join("include", "gtkmm-4.0"))
