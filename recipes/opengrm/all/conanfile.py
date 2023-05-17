from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.env import VirtualRunEnv
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


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

    @property
    def _min_cppstd(self):
        return "17"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "clang": "7",
        }

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.options["openfst"].enable_grm = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("openfst/1.8.2")

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("OpenGrm is only supported on linux")

        if not self.dependencies["openfst"].options.enable_grm:
            raise ConanInvalidConfiguration("OpenGrm requires OpenFst with enable_grm enabled.")

        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_compiler = self._compilers_minimum_version.get(str(self.settings.compiler))
        if minimum_compiler and Version(self.settings.compiler.version) < minimum_compiler:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

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
            "LIBS=-lpthread",
        ])
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

        # TODO: to remove in conan v2
        if self.options.enable_bin:
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
