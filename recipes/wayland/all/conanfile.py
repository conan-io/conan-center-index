from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, replace_in_file, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class WaylandConan(ConanFile):
    name = "wayland"
    description = (
        "Wayland is a project to define a protocol for a compositor to talk to "
        "its clients as well as a library implementation of the protocol"
    )
    topics = "protocol", "compositor", "display"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://wayland.freedesktop.org"
    license = "MIT"
    package_type = "library"
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

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.enable_libraries:
            self.requires("libffi/3.4.4")
        if self.options.enable_dtd_validation:
            self.requires("libxml2/2.10.4")
        self.requires("expat/2.5.0")

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.ref} only supports Linux")

    def build_requirements(self):
        self.tool_requires("meson/1.1.0")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/1.9.3")
        if cross_building(self):
            self.tool_requires(str(self.ref))

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        pkg_config_deps = PkgConfigDeps(self)
        if cross_building(self):
            pkg_config_deps.build_context_activated = ["wayland"]
        elif self.dependencies["expat"].is_build_context:  # wayland is being built as build_require
            # If wayland is the build_require, all its dependencies are treated as build_requires
            pkg_config_deps.build_context_activated = [dep.ref.name for _, dep in self.dependencies.host.items()]
        pkg_config_deps.generate()
        tc = MesonToolchain(self)
        tc.project_options["libdir"] = "lib"
        tc.project_options["datadir"] = "res"
        tc.project_options["libraries"] = self.options.enable_libraries
        tc.project_options["dtd_validation"] = self.options.enable_dtd_validation
        tc.project_options["documentation"] = False
        if cross_building(self):
            tc.project_options["build.pkg_config_path"] = self.generators_folder
        if Version(self.version) >= "1.18.91":
            tc.project_options["scanner"] = True
        tc.generate()

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "meson.build"),
                        "subdir('tests')", "#subdir('tests')")

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        pkg_config_dir = os.path.join(self.package_folder, "lib", "pkgconfig")
        rmdir(self, pkg_config_dir)

    def package_info(self):
        self.cpp_info.components["wayland-scanner"].set_property("pkg_config_name", "wayland-scanner")
        self.cpp_info.components["wayland-scanner"].resdirs = ["res"]
        self.cpp_info.components["wayland-scanner"].includedirs = []
        self.cpp_info.components["wayland-scanner"].libdirs = []
        self.cpp_info.components["wayland-scanner"].set_property("component_version", self.version)
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
            "\n".join(f"{key}={value}" for key,value in pkgconfig_variables.items()))

        if self.options.enable_libraries:
            self.cpp_info.components["wayland-server"].libs = ["wayland-server"]
            self.cpp_info.components["wayland-server"].set_property("pkg_config_name", "wayland-server")
            self.cpp_info.components["wayland-server"].requires = ["libffi::libffi"]
            self.cpp_info.components["wayland-server"].system_libs = ["pthread", "m"]
            self.cpp_info.components["wayland-server"].resdirs = ["res"]
            if self.version >= Version("1.21.0") and self.settings.os == "Linux":
                self.cpp_info.components["wayland-server"].system_libs += ["rt"]
            self.cpp_info.components["wayland-server"].set_property("component_version", self.version)
            pkgconfig_variables = {
                'datarootdir': '${prefix}/res',
                'pkgdatadir': '${datarootdir}/wayland',
            }
            self.cpp_info.components["wayland-server"].set_property(
                "pkg_config_custom_content",
                "\n".join(f"{key}={value}" for key, value in pkgconfig_variables.items()))

            self.cpp_info.components["wayland-client"].libs = ["wayland-client"]
            self.cpp_info.components["wayland-client"].set_property("pkg_config_name", "wayland-client")
            self.cpp_info.components["wayland-client"].requires = ["libffi::libffi"]
            self.cpp_info.components["wayland-client"].system_libs = ["pthread", "m"]
            self.cpp_info.components["wayland-client"].resdirs = ["res"]
            if self.version >= Version("1.21.0") and self.settings.os == "Linux":
                self.cpp_info.components["wayland-client"].system_libs += ["rt"]
            self.cpp_info.components["wayland-client"].set_property("component_version", self.version)
            pkgconfig_variables = {
                'datarootdir': '${prefix}/res',
                'pkgdatadir': '${datarootdir}/wayland',
            }
            self.cpp_info.components["wayland-client"].set_property(
                "pkg_config_custom_content",
                "\n".join(f"{key}={value}" for key, value in pkgconfig_variables.items()))

            self.cpp_info.components["wayland-cursor"].libs = ["wayland-cursor"]
            self.cpp_info.components["wayland-cursor"].set_property("pkg_config_name", "wayland-cursor")
            self.cpp_info.components["wayland-cursor"].requires = ["wayland-client"]
            self.cpp_info.components["wayland-cursor"].set_property("component_version", self.version)

            self.cpp_info.components["wayland-egl"].libs = ["wayland-egl"]
            self.cpp_info.components["wayland-egl"].set_property("pkg_config_name", "wayland-egl")
            self.cpp_info.components["wayland-egl"].requires = ["wayland-client"]
            self.cpp_info.components["wayland-egl"].set_property("component_version", "18.1.0")

            self.cpp_info.components["wayland-egl-backend"].set_property("pkg_config_name", "wayland-egl-backend")
            self.cpp_info.components["wayland-egl-backend"].set_property("component_version", "3")

            # TODO: to remove in conan v2
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
