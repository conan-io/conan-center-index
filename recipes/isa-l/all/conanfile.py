import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import chdir, collect_libs, copy, get
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout

required_conan_version = ">=1.53.0"


class LibisalConan(ConanFile):
    name = "isa-l"
    description = "Intel's Intelligent Storage Acceleration Library"
    license = "BSD-3"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/intel/isa-l"
    topics = "compression"

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

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.arch not in ["x86", "x86_64", "armv8"]:
            raise ConanInvalidConfiguration("CPU Architecture not supported")
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("Only Linux and FreeBSD builds are supported")

    def build_requirements(self):
        self.tool_requires("libtool/2.4.7")
        self.tool_requires("nasm/2.15.05")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()

    def build(self):
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.autoreconf()
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*/isa-l.h",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "include/isa-l"),
             keep_path=False)
        copy(self, "*.h",
             dst=os.path.join(self.package_folder, "include/isa-l"),
             src=os.path.join(self.source_folder, "include"),
             keep_path=False)
        if self.options.shared:
            copy(self, "*.dll",
                 dst=os.path.join(self.package_folder, "bin"),
                 src=self.source_folder,
                 keep_path=False)
            copy(self, "*.so*",
                 dst=os.path.join(self.package_folder, "lib"),
                 src=self.source_folder,
                 keep_path=False)
            copy(self, "*.dylib",
                 dst=os.path.join(self.package_folder, "lib"),
                 src=self.source_folder,
                 keep_path=False)
        else:
            copy(self, "*.a",
                 dst=os.path.join(self.package_folder, "lib"),
                 src=self.source_folder,
                 keep_path=False)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
