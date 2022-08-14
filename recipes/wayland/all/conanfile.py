import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.files import get, mkdir, replace_in_file, rmdir, save
from conan.tools.gnu.pkgconfigdeps.pc_files_creator import get_pc_files_and_content
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.scm import Version

required_conan_version = ">=1.47.0"

class WaylandConan(ConanFile):
    name = "wayland"
    description = "Wayland is a project to define a protocol for a compositor to talk to its clients as well as a library implementation of the protocol"
    topics = ("protocol", "compositor", "display")
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

    generators = "PkgConfigDeps", "VirtualBuildEnv", "VirtualRunEnv"

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
            self.requires("libxml2/2.9.14")
        self.requires("expat/2.4.8")

    def build_requirements(self):
        self.tool_requires("meson/0.63.0")
        self.tool_requires("pkgconf/1.7.4")
        if cross_building(self):
            self.tool_requires(self.ref)

    def layout(self):
        basic_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "meson.build"),
                        "subdir('tests')", "#subdir('tests')")

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options["libdir"] = "lib"
        tc.project_options["datadir"] = "res"
        tc.project_options["libraries"] = self.options.enable_libraries
        tc.project_options["dtd_validation"] = self.options.enable_dtd_validation
        tc.project_options["documentation"] = False
        if Version(self.version) >= "1.18.91":
            tc.project_options["scanner"] = True

            # Generate PC files for the tool_requires wayland package to ensure wayland-scanner is found for build machine.
            if cross_building(self):
                native_generators_folder = os.path.join(self.generators_folder, "native")
                mkdir(self, native_generators_folder)
                for target in ["wayland", "expat", "libxml2", "libiconv"]:
                    for pc_name, pc_content in get_pc_files_and_content(self, self.dependencies.build[target]).items():
                        save(self, os.path.join(native_generators_folder, pc_name), pc_content)
                tc.project_options["build.pkg_config_path"] = native_generators_folder
        tc.generate()

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self.source_folder)
        meson = Meson(self)
        meson.install()
        pkg_config_dir = os.path.join(self.package_folder, "lib", "pkgconfig")
        rmdir(self, pkg_config_dir)

    def package_info(self):
        self.cpp_info.components["wayland-scanner"].set_property("pkg_config_name", "wayland-scanner")
        self.cpp_info.components["wayland-scanner"].names["pkg_config"] = "wayland-scanner"
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

        bindir = os.path.join(self.package_folder, "bin")
        self.buildenv_info.prepend_path("PATH", bindir)
        self.runenv_info.prepend_path("PATH", bindir)
        # TODO: Remove in Conan 2.0 where Environment class will be required.
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        if self.options.enable_libraries:
            self.cpp_info.components["wayland-server"].libs = ["wayland-server"]
            self.cpp_info.components["wayland-server"].set_property("pkg_config_name", "wayland-server")
            self.cpp_info.components["wayland-server"].names["pkg_config"] = "wayland-server"
            self.cpp_info.components["wayland-server"].requires = ["libffi::libffi"]
            self.cpp_info.components["wayland-server"].system_libs = ["pthread", "m"]
            self.cpp_info.components["wayland-server"].resdirs = ["res"]
            if self.version >= Version("1.21.0") and self.settings.os == "Linux":
                self.cpp_info.components["wayland-server"].system_libs += ["rt"]
            self.cpp_info.components["wayland-server"].set_property("component_version", self.version)

            # todo Remove in Conan version 1.50.0 where these are set by default for the PkgConfigDeps generator.
            self.cpp_info.components["wayland-server"].includedirs = ["include"]
            self.cpp_info.components["wayland-server"].libdirs = ["lib"]

            pkgconfig_variables = {
                'datarootdir': '${prefix}/res',
                'pkgdatadir': '${datarootdir}/wayland',
            }
            self.cpp_info.components["wayland-server"].set_property(
                "pkg_config_custom_content",
                "\n".join(f"{key}={value}" for key, value in pkgconfig_variables.items()))

            self.cpp_info.components["wayland-client"].libs = ["wayland-client"]
            self.cpp_info.components["wayland-client"].set_property("pkg_config_name", "wayland-client")
            self.cpp_info.components["wayland-client"].names["pkg_config"] = "wayland-client"
            self.cpp_info.components["wayland-client"].requires = ["libffi::libffi"]
            self.cpp_info.components["wayland-client"].system_libs = ["pthread", "m"]
            self.cpp_info.components["wayland-client"].resdirs = ["res"]
            if self.version >= Version("1.21.0") and self.settings.os == "Linux":
                self.cpp_info.components["wayland-client"].system_libs += ["rt"]
            self.cpp_info.components["wayland-client"].set_property("component_version", self.version)

            # todo Remove in Conan version 1.50.0 where these are set by default for the PkgConfigDeps generator.
            self.cpp_info.components["wayland-client"].includedirs = ["include"]
            self.cpp_info.components["wayland-client"].libdirs = ["lib"]

            pkgconfig_variables = {
                'datarootdir': '${prefix}/res',
                'pkgdatadir': '${datarootdir}/wayland',
            }
            self.cpp_info.components["wayland-client"].set_property(
                "pkg_config_custom_content",
                "\n".join(f"{key}={value}" for key, value in pkgconfig_variables.items()))

            self.cpp_info.components["wayland-cursor"].libs = ["wayland-cursor"]
            self.cpp_info.components["wayland-cursor"].set_property("pkg_config_name", "wayland-cursor")
            self.cpp_info.components["wayland-cursor"].names["pkg_config"] = "wayland-cursor"
            self.cpp_info.components["wayland-cursor"].requires = ["wayland-client"]
            self.cpp_info.components["wayland-cursor"].set_property("component_version", self.version)

            # todo Remove in Conan version 1.50.0 where these are set by default for the PkgConfigDeps generator.
            self.cpp_info.components["wayland-cursor"].includedirs = ["include"]
            self.cpp_info.components["wayland-cursor"].libdirs = ["lib"]

            self.cpp_info.components["wayland-egl"].libs = ["wayland-egl"]
            self.cpp_info.components["wayland-egl"].set_property("pkg_config_name", "wayland-egl")
            self.cpp_info.components["wayland-egl"].names["pkg_config"] = "wayland-egl"
            self.cpp_info.components["wayland-egl"].requires = ["wayland-client"]
            self.cpp_info.components["wayland-egl"].set_property("component_version", "18.1.0")

            # todo Remove in Conan version 1.50.0 where these are set by default for the PkgConfigDeps generator.
            self.cpp_info.components["wayland-egl"].includedirs = ["include"]
            self.cpp_info.components["wayland-egl"].libdirs = ["lib"]

            self.cpp_info.components["wayland-egl-backend"].names["pkg_config"] = "wayland-egl-backend"
            self.cpp_info.components["wayland-egl-backend"].set_property("pkg_config_name", "wayland-egl-backend")
            self.cpp_info.components["wayland-egl-backend"].set_property("component_version", "3")

            # todo Remove in Conan version 1.50.0 where these are set by default for the PkgConfigDeps generator.
            self.cpp_info.components["wayland-egl-backend"].includedirs = ["include"]
            self.cpp_info.components["wayland-egl-backend"].libdirs = ["lib"]

            bindir = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bindir))
            self.env_info.PATH.append(bindir)
