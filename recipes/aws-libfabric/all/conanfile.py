import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import chdir, collect_libs, copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import unix_path

required_conan_version = ">=1.53.0"


class LibfabricConan(ConanFile):
    name = "aws-libfabric"
    description = "AWS Libfabric"
    license = ("BSD-2-Clause", "GPL-2.0-or-later")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/aws/libfabric"
    topics = ("fabric", "communication", "framework", "service")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    _providers = ["gni", "psm", "psm2", "sockets", "rxm", "tcp", "udp", "usnic", "verbs", "bgq", "shm", "efa", "rxd", "mrail", "rstream", "perf", "hook_debug"]
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        **{ p: [True, False, "shared"] for p in _providers },
        **{
            "with_libnl": [True, False],
            "bgq_progress": ["auto", "manual"],
            "bgq_mr": ["basic", "scalable"]
        }
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        **{ p: False for p in _providers },
        **{
            "tcp": True,
            "with_libnl": False,
            "bgq_progress": "manual",
            "bgq_mr": "basic"
        }
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        elif self.settings.os == "Linux":
            self.options.efa = True

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_libnl:
            self.requires("libnl/3.2.25")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("The libfabric package cannot be built on Windows.")

    def build_requirements(self):
        self.tool_requires("libtool/2.4.7")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")
        yes_no_dl = lambda v: {"True": "yes", "False": "no", "shared": "dl"}[str(v)]
        tc = AutotoolsToolchain(self)
        tc.configure_args += [
            "--with-bgq-progress={}".format(self.options.bgq_progress),
            "--with-bgq-mr={}".format(self.options.bgq_mr),
        ]
        for p in self._providers:
            tc.configure_args.append("--enable-{}={}".format(p, yes_no_dl(getattr(self.options, p))))
        if self.options.with_libnl:
            tc.configure_args.append("--with-libnl={}".format(unix_path(self, self.dependencies["libnl"].package_folder)))
        else:
            tc.configure_args.append("--with-libnl=no")
        if self.settings.build_type == "Debug":
            tc.configure_args.append("--enable-debug")
        tc.generate()
        tc = AutotoolsDeps(self)
        tc.generate()

    def build(self):
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.autoreconf()
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, pattern="COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.la", self.package_folder, recursive=True)
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libfabric")
        self.cpp_info.libs = collect_libs(self)
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["pthread", "m"]
            if not self.options.shared:
                self.cpp_info.system_libs.extend(["dl", "rt"])
