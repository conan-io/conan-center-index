import os

from conan.tools.build import cross_building
from conan.tools.microsoft import is_msvc
from conans import ConanFile, tools, Meson
from conan.errors import ConanInvalidConfiguration
from conans.tools import rmdir

required_conan_version = ">=1.33.0"


class Recipe(ConanFile):
    name = "serd"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://drobilla.net/software/serd.html"
    description = "A lightweight C library for RDF syntax"
    topics = "linked-data", "semantic-web", "rdf", "turtle", "trig", "ntriples", "nquads"
    settings = "build_type", "compiler", "os", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }
    license = "ISC"

    _meson = None

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self.folders.base_source,
                  strip_root=True)

    def build_requirements(self):
        self.build_requires("pkgconf/1.7.4")
        self.build_requires("meson/0.63.0")

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if cross_building(self):
            raise ConanInvalidConfiguration("Cross compiling is not working.")
        if is_msvc(self):
            raise ConanInvalidConfiguration("Meson packaging is broken for MSVC.")

    def _configure_meson(self):
        if self._meson:
            return self._meson
        self._meson = Meson(self)
        args = ["--wrap-mode=nofallback"]
        defs = {"docs": "disabled", "tests": "disabled", "tools": "disabled"}
        self._meson.configure(source_folder=self.folders.source_folder,
                              build_folder=os.path.join(self.package_folder, "build"),
                              args=args, defs=defs)
        return self._meson

    def build(self):
        meson = self._configure_meson()
        meson.build()

    def package(self):
        meson = self._configure_meson()
        meson.install()
        rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(os.path.join(self.package_folder, "build"))
        self.copy("COPYING", src=self.folders.base_source, dst="licenses")

    def package_info(self):
        libname = f"{self.name}-0"
        self.cpp_info.libs = [libname]
        self.cpp_info.includedirs = [os.path.join("include", libname)]
        self.cpp_info.set_property("pkg_config_name", libname)

        # TODO: to remove in conan v2 once pkg_config generators removed
        self.cpp_info.names["pkg_config"] = libname

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
