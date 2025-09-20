from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class GumboParserConan(ConanFile):
    name = "gumbo-parser"
    description = "HTML parser library implemented in C99"
    topics = ("parser", "html")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://codeberg.org/gumbo-parser/gumbo-parser"
    package_type = "library"
    license = "Apache-2.0"

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
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration("gumbo-parser recipe does not support Visual Studio yet")

    def build_requirements(self):
        if Version(self.version) >= "0.13.2":
            self.tool_requires("meson/[>=1.4.1]")
        else:
            self.tool_requires("libtool/2.4.7")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if Version(self.version) >= "0.13.2":
            tc = MesonToolchain(self)
            tc.project_options["tests"] = False
            tc.generate()
        else:
            tc = AutotoolsToolchain(self)
            tc.generate()

    def build(self):
        if Version(self.version) >= "0.13.2":
            meson = Meson(self)
            meson.configure()
            meson.build()
        else:
            autotools = Autotools(self)
            autotools.autoreconf()
            autotools.configure()
            autotools.make()

    def package(self):
        if Version(self.version) >= "0.13.2":
            meson = Meson(self)
            meson.install()
            copy(self, "COPYING", src=os.path.join(self.source_folder, "doc"), dst=os.path.join(self.package_folder, "licenses"))
        else:
            autotools = Autotools(self)
            autotools.install()
            copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "gumbo")
        self.cpp_info.libs = ["gumbo"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
