from conans import ConanFile, Meson, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.36.0"

class WaylandConan(ConanFile):
    name = "wayland"
    description = "Wayland is a project to define a protocol for a compositor to talk to its clients as well as a library implementation of the protocol"
    topics = ("conan", "wayland")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://wayland.freedesktop.org"
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_libraries": [True, False],
        "enable_dtd_validation": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_libraries": True,
        "enable_dtd_validation": True,
    }

    generators = "pkg_config"
    _meson = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"
    
    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("Wayland can be built on Linux only")

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.enable_libraries:
            self.requires("libffi/3.4.2")
        if self.options.enable_dtd_validation:
            self.requires("libxml2/2.9.12")
        self.requires("expat/2.4.1")

    def build_requirements(self):
        self.build_requires("meson/0.59.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def _patch_sources(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "meson.build"),
                              "subdir('tests')", "#subdir('tests')")

    def _configure_meson(self):
        if not self._meson:
            defs = {
                "libraries": "true" if self.options.enable_libraries else "false",
                "dtd_validation": "true" if self.options.enable_dtd_validation else "false",
                "documentation": "false",
            }
            if tools.Version(self.version) >= "1.18.91":
                defs.update({"scanner": "true"})
            self._meson = Meson(self)
            self._meson.configure(
                source_folder=self._source_subfolder,
                build_folder=self._build_subfolder,
                defs=defs,
                args=["--datadir={}".format(os.path.join(self.package_folder, "res"))]
            )
        return self._meson

    def build(self):
        self._patch_sources()
        meson = self._configure_meson()
        meson.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        meson = self._configure_meson()
        meson.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.components["wayland-scanner"].names["pkg_config"] = "wayland-scanner"
        self.cpp_info.components["wayland-scanner"].requires = ["expat::expat"]
        if self.options.enable_dtd_validation:
            self.cpp_info.components["wayland-scanner"].requires.append("libxml2::libxml2")
        pkgconfig_variables = {
            'datarootdir': '${prefix}/res',
            'pkgdatadir': '${datarootdir}/wayland',
            'bindir': '${prefix}/bin',
            'wayland_scanner': '${bindir}/wayland-scanner',
        }
        self.cpp_info.components["wayland-scanner"].set_property(
            "pkg_config_custom_content",
            "\n".join("%s=%s" % (key, value) for key,value in pkgconfig_variables.items()))

        if self.options.enable_libraries:
            self.cpp_info.components["wayland-server"].libs = ["wayland-server"]
            self.cpp_info.components["wayland-server"].names["pkg_config"] = "wayland-server"
            self.cpp_info.components["wayland-server"].requires = ["libffi::libffi"]
            self.cpp_info.components["wayland-server"].system_libs = ["pthread", "m"]
            pkgconfig_variables = {
                'datarootdir': '${prefix}/res',
                'pkgdatadir': '${datarootdir}/wayland',
            }
            self.cpp_info.components["wayland-server"].set_property(
                "pkg_config_custom_content",
                "\n".join("%s=%s" % (key, value) for key,value in pkgconfig_variables.items()))

            self.cpp_info.components["wayland-client"].libs = ["wayland-client"]
            self.cpp_info.components["wayland-client"].names["pkg_config"] = "wayland-client"
            self.cpp_info.components["wayland-client"].requires = ["libffi::libffi"]
            self.cpp_info.components["wayland-client"].system_libs = ["pthread", "m"]
            pkgconfig_variables = {
                'datarootdir': '${prefix}/res',
                'pkgdatadir': '${datarootdir}/wayland',
            }
            self.cpp_info.components["wayland-client"].set_property(
                "pkg_config_custom_content",
                "\n".join("%s=%s" % (key, value) for key,value in pkgconfig_variables.items()))

            self.cpp_info.components["wayland-cursor"].libs = ["wayland-cursor"]
            self.cpp_info.components["wayland-cursor"].names["pkg_config"] = "wayland-cursor"
            self.cpp_info.components["wayland-cursor"].requires = ["wayland-client"]

            self.cpp_info.components["wayland-egl"].libs = ["wayland-egl"]
            self.cpp_info.components["wayland-egl"].names["pkg_config"] = "wayland-egl"
            self.cpp_info.components["wayland-egl"].requires = ["wayland-client"]

            self.cpp_info.components["wayland-egl-backend"].names["pkg_config"] = "wayland-egl-backend"
            self.cpp_info.components["wayland-egl-backend"].version = "3"

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
