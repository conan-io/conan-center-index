import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.apple import is_apple_os, fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy, get, rmdir
from conan.tools.layout import basic_layout

required_conan_version = ">=1.53.0"

class LibBsdConan(ConanFile):
    name = "libbsd"
    description = "This library provides useful functions commonly found on BSD systems, and lacking on others like GNU systems, " \
                  "thus making it easier to port projects with strong BSD origins, without needing to embed the same code over and over again on each project."
    topics = ("conan", "libbsd", "useful", "functions", "bsd", "GNU")
    license = ("ISC", "MIT", "Beerware", "BSD-2-clause", "BSD-3-clause", "BSD-4-clause")
    homepage = "https://libbsd.freedesktop.org/wiki/"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def build_requirements(self):
        self.tool_requires("libtool/2.4.7")

    def export_sources(self):
        export_conandata_patches(self)
    
    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")
    
    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = AutotoolsToolchain(self)
        if is_apple_os(self):
            tc.extra_cflags.append("-Wno-error=implicit-function-declaration")
        tc.generate()
        deps = AutotoolsDeps(self)
        deps.generate()

    def layout(self):
        basic_layout(self, src_folder="src")
    
    def validate(self):
        if not is_apple_os(self) and self.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.ref} is only available for GNU-like operating systems (e.g. Linux)")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        autotools = Autotools(self)
        autotools.install()

        os.unlink(os.path.join(os.path.join(self.package_folder, "lib", "libbsd.la")))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.components["bsd"].libs = ["bsd"]
        self.cpp_info.components["bsd"].set_property("pkg_config_name", "libbsd")

        self.cpp_info.components["libbsd-overlay"].libs = []
        self.cpp_info.components["libbsd-overlay"].requires = ["bsd"]
        self.cpp_info.components["libbsd-overlay"].includedirs.append(os.path.join("include", "bsd"))
        self.cpp_info.components["libbsd-overlay"].defines = ["LIBBSD_OVERLAY"]
        self.cpp_info.components["libbsd-overlay"].set_property("pkg_config_name", "libbsd-overlay")

        # on apple-clang, GNU .init_array section is not supported
        if self.settings.compiler != "apple-clang":
            self.cpp_info.components["libbsd-ctor"].libs = ["bsd-ctor"]
            self.cpp_info.components["libbsd-ctor"].requires = ["bsd"]
            if self.settings.os == "Linux":
                self.cpp_info.components["libbsd-ctor"].exelinkflags = ["-Wl,-z,nodlopen", "-Wl,-u,libbsd_init_func"]
                self.cpp_info.components["libbsd-ctor"].sharedlinkflags = ["-Wl,-z,nodlopen", "-Wl,-u,libbsd_init_func"]
            self.cpp_info.components["libbsd-ctor"].set_property("pkg_config_name", "libbsd-ctor")

