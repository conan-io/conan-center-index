import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import chdir, copy, get
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout

required_conan_version = ">=1.53.0"


class OfeliConan(ConanFile):
    name = "ofeli"
    description = "An Object Finite Element Library"
    license = "LGPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://ofeli.org/index.html"
    topics = ("finite-element", "finite-element-library", "finite-element-analysis", "finite-element-solver")

    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("Ofeli only supports Linux")
        if self.settings.compiler != "gcc":
            raise ConanInvalidConfiguration("Ofeli only supports GCC")
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)
        if self.settings.compiler.libcxx != "libstdc++11":
            raise ConanInvalidConfiguration("Ofeli only supports libstdc++'s new ABI")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        config = 'release' if self.settings.build_type == 'Release' else 'debug'
        tc.configure_args.append(f"--enable-{config}")
        tc.generate()

    def build(self):
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "*.h",
             dst=os.path.join(self.package_folder, "include"),
             src=os.path.join(self.source_folder, "include"))
        copy(self, "*libofeli.a",
             dst=os.path.join(self.package_folder, "lib"),
             src=os.path.join(self.source_folder, "src"))
        copy(self, "*.md",
             dst=os.path.join(self.package_folder, "res"),
             src=os.path.join(self.source_folder, "material"))
        copy(self, "COPYING",
             dst=os.path.join(self.package_folder, "licenses"),
             src=os.path.join(self.source_folder, "doc"))

    def package_info(self):
        self.cpp_info.libs = ["ofeli"]
        res_path = os.path.join(self.package_folder, "res")
        self.runenv_info.define("OFELI_PATH_MATERIAL", res_path)

        # TODO: Legacy, to be removed on Conan 2.0
        self.env_info.OFELI_PATH_MATERIAL.append(res_path)
