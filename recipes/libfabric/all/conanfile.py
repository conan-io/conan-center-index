import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class LibfabricConan(ConanFile):
    name = "libfabric"
    description = ("Libfabric, also known as Open Fabrics Interfaces (OFI), "
                   "defines a communication API for high-performance parallel and distributed applications.")
    license = ("BSD-2-Clause", "GPL-2.0-or-later")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://libfabric.org"
    topics = ("fabric", "communication", "framework", "service")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    _providers = [
        "bgq",
        "dmabuf_peer_mem",
        "efa",
        "gni",
        "hook_debug",
        "hook_hmem",
        "mrail",
        "opx",
        "perf",
        "psm",
        "psm2",
        "psm3",
        "rstream",
        "rxd",
        "rxm",
        "shm",
        "sm2",
        "sockets",
        "tcp",
        "trace",
        "ucx",
        "udp",
        "usnic",
        "verbs",
    ]
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_bgq_progress": [None, "auto", "manual"],
        "with_bgq_mr": [None, "basic", "scalable"],
        **{ p: ["yes", "no", "dl", "auto", "ANY"] for p in _providers },
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_bgq_progress": None,
        "with_bgq_mr": None,
        "bgq": "no",
        "dmabuf_peer_mem": "yes",
        "efa": "no",
        "gni": "no",
        "hook_debug": "yes",
        "hook_hmem": "yes",
        "mrail": "yes",
        "opx": "no",
        "perf": "yes",
        "psm": "no",
        "psm2": "no",
        "psm3": "no",
        "rstream": "yes",
        "rxd": "yes",
        "rxm": "yes",
        "shm": "yes",
        "sm2": "yes",
        "sockets": "yes",
        "tcp": "yes",
        "trace": "yes",
        "ucx": "no",
        "udp": "yes",
        "usnic": "no",
        "verbs": "no",  # TODO: this and others can be enabled once rdma-core is available
    }

    def config_options(self):
        if is_apple_os(self):
            # Requires libnl, which is not available on macOS
            del self.options.usnic
            # shm2 and sm2 due to missing Linux-specific process_vm_readv syscall
            del self.options.shm
            del self.options.sm2
        if Version(self.version) < "1.18.1":
            del self.options.dmabuf_peer_mem
            del self.options.hook_hmem
            del self.options.opx
            del self.options.trace
            del self.options.ucx
            self.options.rm_safe("sm2")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def requirements(self):
        def is_enabled(opt):
            return self.options.get_safe(opt) in ["yes", "dl", "auto"]

        if is_enabled("usnic"):
            self.requires("libnl/3.8.0")
        if is_enabled("efa") or is_enabled("opx") or is_enabled("usnic") or is_enabled("verbs"):
            self.requires("rdma-core/49.0")
        if is_enabled("opx"):
            self.requires("libnuma/2.0.14")
            self.requires("util-linux-libuuid/2.39")
        # TODO: bgq, gni, psm, psm2, psm3, ucx each require a corresponding library

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        if not self.info.options.bgq:
            del self.info.options.with_bgq_progress
            del self.info.options.with_bgq_mr

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("libfabric is not available on Windows")

        for opt, value in self.options.items():
            if opt in self._providers and self.options.get_safe(opt) not in ["auto", "yes", "no", "dl"]:
                path = str(self.options.get_safe(opt))
                if path.startswith("dl:"):
                    path = path[3:]
                if not os.path.isdir(path):
                    raise ConanInvalidConfiguration(
                        f"Option {opt} can only be 'yes', 'no', 'dl', 'auto' or a directory path "
                        "(optionally with a 'dl:' prefix to build as a dynamic library)"
                    )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        def yes_no_opt(opt):
            return "yes" if self.options.get_safe(opt) else "no"

        tc = AutotoolsToolchain(self)
        for p in self._providers:
            tc.configure_args.append(f"--enable-{p}={self.options.get_safe(p, 'no')}")
        tc.configure_args.append("--with-libnl=yes")
        tc.configure_args.append("--with-numa=yes")
        tc.configure_args.append(f"--with-bgq-progress={yes_no_opt('with_bgq_progress')}")
        tc.configure_args.append(f"--with-bgq-mr={yes_no_opt('with_bgq_mr')}")
        tc.generate()

        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.la", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libfabric")
        self.cpp_info.libs = ["fabric"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "m", "rt", "dl"]
        self.cpp_info.system_libs.append("atomic")
