from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.50.0"


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
        # TODO: fixed in conan 1.51.0?
        tc.project_options["bindir"] = "bin"
        tc.project_options["libdir"] = "lib"
        tc.generate()

        env = VirtualBuildEnv(self)
        env.generate(scope="build")

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        fix_apple_shared_install_name(self)
        fix_msvc_libname(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "serd-0")
        libname = "serd"
        if not (is_msvc(self) and self.options.shared):
            libname += "-0"
        self.cpp_info.libs = [libname]
        self.cpp_info.includedirs = [os.path.join("include", "serd-0")]
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.defines.append("SERD_STATIC")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

def fix_msvc_libname(conanfile, remove_lib_prefix=True):
    """remove lib prefix & change extension to .lib"""
    from conan.tools.files import rename
    import glob
    if not is_msvc(conanfile):
        return
    libdirs = getattr(conanfile.cpp.package, "libdirs")
    for libdir in libdirs:
        for ext in [".dll.a", ".dll.lib", ".a"]:
            full_folder = os.path.join(conanfile.package_folder, libdir)
            for filepath in glob.glob(os.path.join(full_folder, f"*{ext}")):
                libname = os.path.basename(filepath)[0:-len(ext)]
                if remove_lib_prefix and libname[0:3] == "lib":
                    libname = libname[3:]
                rename(conanfile, filepath, os.path.join(os.path.dirname(filepath), f"{libname}.lib"))
