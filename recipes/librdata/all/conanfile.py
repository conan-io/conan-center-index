import os

from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, rm, rmdir
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Git

required_conan_version = ">=2.0.0"

class Libreadstat(ConanFile):
    name = "librdata"
    version = "0.1"
    description = "librdata is a library for read and write R data frames from C"
    license = "CDDL-1.0", "LGPL-2.1-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/WizardMac/librdata"
    topics = ("r", "rdata", "rds", "data-frames")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_zip": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_zip": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_zip:
            self.requires("bzip2/1.0.8")
            self.requires("zlib/1.2.13")
            self.requires("xz_utils/5.6.3")

    def source(self):
        git = Git(self)
        git.clone(url="https://github.com/WizardMac/librdata.git", target=".")

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = AutotoolsToolchain(self)
        tc.generate()
        tc = AutotoolsDeps(self)
        if self.options.with_zip:
            tc.variables["with_zip"] = True
        tc.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, pattern="LICENSE*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        if is_msvc(self):
            copy(self, "rdata.h", src=os.path.join(self.source_folder, "headers"), dst=os.path.join(self.package_folder, "include"))
            copy(self, "*.a", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            copy(self, "*.so", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            copy(self, "*.lib", src=self.source_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            copy(self, "*.dll", src=self.source_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
        else:
            autotools = Autotools(self)
            autotools.install()
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rmdir(self, os.path.join(self.package_folder, "share"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "readstat")
        suffix = "_i" if is_msvc(self) and self.options.shared else ""
        self.cpp_info.libs = [f"librdata{suffix}"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs.append("m")