from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.env import VirtualRunEnv
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=2.0"


class OpenGrmConan(ConanFile):
    name = "opengrm"
    description = (
        "The OpenGrm Thrax tools compile grammars expressed as regular expressions "
        "and context-dependent rewrite rules into weighted finite-state transducers."
    )
    topics = ("fst", "wfst", "opengrm", "thrax")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.opengrm.org/twiki/bin/view/GRM/Thrax"
    license = "Apache-2.0"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_bin": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_bin": True,
    }

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.options["openfst"].enable_grm = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # Used in thrax/grm-manager.h public header
        self.requires("openfst/1.8.2", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("OpenGrm is only supported on linux")

        if not self.dependencies["openfst"].options.enable_grm:
            raise ConanInvalidConfiguration("OpenGrm requires OpenFst with enable_grm enabled.")

        check_min_cppstd(self, 17)

        # Check stdlib ABI compatibility
        if self.settings.compiler == "gcc" and self.settings.compiler.libcxx != "libstdc++11":
            raise ConanInvalidConfiguration(f'Using {self.name} with GCC requires "compiler.libcxx=libstdc++11"')

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args.extend([
            f"--enable-bin={yes_no(self.options.enable_bin)}",
        ])
        tc.ldflags.append("-lpthread")
        tc.make_args.append("-j1")
        tc.generate()

        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = ["thrax"]
        self.cpp_info.resdirs = ["res"]
        self.cpp_info.system_libs = ["pthread", "dl", "m"]
