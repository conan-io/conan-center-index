from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, rm, rmdir, chdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.54.0"

class LibbpfConan(ConanFile):
    name = "libbpf"
    description = "eBPF helper library"
    license = "LGPL-2.1-only", "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libbpf/libbpf"
    topics = ("berkeley-packet-filter", "bpf", "ebpf", "network", "tracing")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_uapi_headers": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_uapi_headers": False
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

    def requirements(self):
        self.requires("linux-headers-generic/5.15.128", transitive_headers=True)
        self.requires("elfutils/0.190", transitive_headers=True, transitive_libs=True)
        self.requires("zlib/[>=1.2.11 <2]")

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
        with chdir(self, os.path.join(self.source_folder, "src")):
            autotools = Autotools(self)
            autotools.make()
            if self.options.with_uapi_headers:
                autotools.make('install_uapi_headers')

    def package(self):
        copy(self, pattern="LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        with chdir(self, os.path.join(self.source_folder, "src")):
            autotools = Autotools(self)
            autotools.install()

        if self.options.shared:
            rm(self, "libbpf.a", os.path.join(self.package_folder, "lib"))
        else:
            rm(self, "libbpf.so*", os.path.join(self.package_folder, "lib"))

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["bpf"]
        self.cpp_info.set_property("pkg_config_name", "libbpf")

        # TODO: Remove once v1 is no longer needed
        self.cpp_info.names["pkg_config"] = "libbpf"

