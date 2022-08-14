from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rmdir
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.47.0"


class SerdConan(ConanFile):
    name = "serd"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://drobilla.net/software/serd.html"
    description = "A lightweight C library for RDF syntax"
    topics = "linked-data", "semantic-web", "rdf", "turtle", "trig", "ntriples", "nquads"
    license = "ISC"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
           del self.settings.compiler.libcxx
        except Exception:
           pass
        try:
           del self.settings.compiler.cppstd
        except Exception:
           pass

    def validate(self):
        if cross_building(self) and hasattr(self.settings_build):
            raise ConanInvalidConfiguration("Cross compiling is not working.")
        if is_msvc(self):
            raise ConanInvalidConfiguration("Meson packaging is broken for MSVC.")

    def build_requirements(self):
        self.tool_requires("meson/0.63.1")
        self.tool_requires("pkgconf/1.7.4")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options["docs"] = "disabled"
        tc.project_options["tests"] = "disabled"
        tc.project_options["tools"] = "disabled"
        tc.generate()

        env = VirtualBuildEnv(self)
        env.generate(scope="build")

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "build"))
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        libname = "serd-0"
        self.cpp_info.set_property("pkg_config_name", libname)
        self.cpp_info.libs = [libname]
        self.cpp_info.includedirs = [os.path.join("include", libname)]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
