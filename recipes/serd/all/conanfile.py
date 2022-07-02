import os

from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import rmdir
from conan.tools.microsoft import is_msvc

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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version]["serd"],
                  destination=self.folders.base_source,
                  strip_root=True)
        # serd comes with its own modification of the waf build system
        # It seems to be used only by serd and will be replaced in future versions with meson.
        # So it makes no sense to create a separate conan package for the build system.
        tools.get(**self.conan_data["sources"][self.version]["autowaf"],
                  destination=os.path.join(self.folders.base_source, "waflib"),
                  strip_root=True)

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if tools.cross_building(self):
            raise ConanInvalidConfiguration("Cross compiling is not supported by serd's build system Waf.")

        if is_msvc(self):
            raise ConanInvalidConfiguration("Don't know how to setup WAF for VS.")

    def build(self):
        args = ["--no-utils", " --prefix={}".format(self.folders.package_folder)]
        if not self.options.shared:
            args += ["--static", "--no-shared"]
        args = " ".join(arg for arg in args)

        cflags = []
        if self.options.get_safe("fPIC"):
            cflags += ["-fPIC"]
        if self.settings.build_type in ["Debug", "RelWithDebInfo"]:
            cflags += ["-g"]
        if self.settings.build_type in ["Release", "RelWithDebInfo"]:
            cflags += ["-O3"]
        if self.settings.build_type in ["Release", "MinSizeRel"]:
            cflags += ["-DNDEBUG"]
        if self.settings.build_type == "MinSizeRel":
            cflags += ["-Os"]
        cflags = " ".join(cflag for cflag in cflags)

        self.run(f'CFLAGS="{cflags}" ./waf configure {args}', run_environment=True)
        self.run('./waf build', run_environment=True)

    def package(self):
        self.run('./waf install', run_environment=True)
        rmdir(os.path.join(self.package_folder, "share"))
        rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
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
