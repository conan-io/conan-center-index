from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, rm, rmdir, chdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.54.0"

class LibbpfConan(ConanFile):
    name = "libxdp"
    description = "XDP tools"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xdp-project/xdp-tools"
    topics = ("berkeley-packet-filter", "bpf", "ebpf", "xdp", "network", "tracing")

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
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.ref} is only available on Linux")

    def build_requirements(self):
        self.tool_requires("make/4.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.make_args.extend([
            "PREFIX={}".format(""),
            "DESTDIR={}".format(self.package_folder),
            "LIBSUBDIR={}".format("lib"),
        ])
        if not self.options.shared:
            tc.configure_args.append("BUILD_STATIC_ONLY={}".format(1))
        tc.generate()

        pkgdeps = PkgConfigDeps(self)
        pkgdeps.generate()

        autotoolsdeps = AutotoolsDeps(self)
        autotoolsdeps.generate()

    def build(self):
        with chdir(self, os.path.join(self.source_folder)):
            autotools = Autotools(self)
            autotools.configure()
            with chdir(self, os.path.join(self.source_folder, "lib")):
                autotools.make()

    def package(self):
        with chdir(self, os.path.join(self.source_folder, "lib")):
            autotools = Autotools(self)
            autotools.install()
        if self.options.shared:
            rm(self, "libxdp.a", os.path.join(self.package_folder, "lib"))
        else:
            rm(self, "libxdp.so*", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = ["xdp"]

