import os

from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.files import copy, rm, rmdir, get
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Git
from conan.tools.layout import basic_layout

required_conan_version = ">=2.0.0"

class Libreadstat(ConanFile):
    name = "librdata"
    description = "librdata is a library for read and write R data frames from C"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/WizardMac/librdata"
    topics = ("r", "rdata", "rds", "data-frames")
    package_type = "library"
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

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("bzip2/1.0.8")
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("xz_utils/[>=5.4.5 <6]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)


    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()
        dep = AutotoolsDeps(self)
        dep.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, pattern="LICENSE*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        if is_msvc(self):
            copy(self, "rdata.h", src=os.path.join(self.source_folder, "headers"), dst=os.path.join(self.package_folder, "include"))
            copy(self, "*.a", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            copy(self, "*.so", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            copy(self, "*.dll", src=self.source_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
        else:
            autotools = Autotools(self)
            autotools.install()
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rmdir(self, os.path.join(self.package_folder, "share"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        suffix = "_i" if is_msvc(self) and self.options.shared else ""
        self.cpp_info.libs = [f"rdata{suffix}"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs.append("m")