import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout

required_conan_version = ">=2.0"


class DqliteConan(ConanFile):
    name = "dqlite"
    description = "Embeddable and replicated SQL database engine with high availability and automatic failover"
    license = "LGPL-3.0-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/canonical/dqlite"
    topics = ("database", "sqlite", "raft", "replication")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_lz4": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_lz4": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("sqlite3/[>=3.34.0 <4]")
        self.requires("libuv/[>=1.34.0 <2]")
        if self.options.with_lz4:
            self.requires("lz4/[>=1.7.1 <2]")

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.ref} only supports Linux")

    def build_requirements(self):
        self.tool_requires("autoconf/2.71")
        self.tool_requires("automake/1.16.5")
        self.tool_requires("libtool/2.4.7")
        self.tool_requires("pkgconf/2.5.1")
        self.tool_requires("gnu-config/cci.20210814")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            "--disable-dependency-tracking",
            "--disable-backtrace",
            "--enable-build-raft",
        ])
        # dqlite 1.18.7 builds with -Werror and keeps several variables alive through assert().
        tc.extra_cflags.append("-UNDEBUG")
        if self.options.with_lz4:
            tc.configure_args.extend(["--with-lz4", "--enable-lz4"])
        else:
            tc.configure_args.append("--without-lz4")
        tc.generate()

        deps = AutotoolsDeps(self)
        deps.generate()

        pkg_config = PkgConfigDeps(self)
        pkg_config.set_property("libuv", "pkg_config_name", "libuv")
        pkg_config.generate()

    def _patch_sources(self):
        for gnu_config in [
            self.conf.get("user.gnu-config:config_guess", check_type=str),
            self.conf.get("user.gnu-config:config_sub", check_type=str),
        ]:
            if gnu_config:
                copy(self, os.path.basename(gnu_config), src=os.path.dirname(gnu_config), dst=os.path.join(self.source_folder, "ac"))

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rm(self, "*.la", self.package_folder, recursive=True)
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "dqlite")
        self.cpp_info.set_property("cmake_target_name", "dqlite::dqlite")
        self.cpp_info.set_property("pkg_config_name", "dqlite")
        self.cpp_info.libs = ["dqlite"]
        self.cpp_info.requires = ["sqlite3::sqlite3", "libuv::libuv"]
        if self.options.with_lz4:
            self.cpp_info.requires.append("lz4::lz4")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")