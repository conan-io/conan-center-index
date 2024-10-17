import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.env import VirtualBuildEnv, Environment
from conan.tools.files import copy, get, export_conandata_patches, apply_conandata_patches, collect_libs, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain

required_conan_version = ">=1.53"


class DpdkConan(ConanFile):
    name = "dpdk"
    description = "DPDK: a set of libraries and drivers for fast packet processing"
    # see https://github.com/DPDK/dpdk/blob/main/license/README
    license = "BSD-3-Clause AND LGPL-2.1-only AND GPL-2.0-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://dpdk.org"
    topics = ("networking", "packets", "drivers")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_stdatomic": [True, False],
        "with_jansson": [True, False],
        "with_libarchive": [True, False],
        "with_libbpf": [True, False],
        "with_libbsd": [True, False],
        "with_libibverbs": [True, False],
        "with_libpcap": [True, False],
        "with_openssl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_stdatomic": False,
        "with_jansson": True,
        "with_libarchive": True,
        "with_libbpf": True,
        "with_libbsd": False,  # FIXME: libbsd on Conan is outdated?
        "with_libibverbs": True,
        "with_libpcap": True,
        "with_openssl": True,
    }

    @property
    def _min_cppstd(self):
        return "11"

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libnuma/2.0.16", options={"shared": True})
        self.requires("libelf/0.8.13")
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("linux-headers-generic/5.15.128", transitive_headers=True)
        if self.options.with_jansson:
            # rte_metrics_telemetry.h
            self.requires("jansson/2.14", transitive_headers=True, transitive_libs=True)
        if self.options.with_libarchive:
            self.requires("libarchive/3.7.4")
        if self.options.with_libbpf:
            self.requires("libbpf/1.3.0")
        if self.options.with_libbsd:
            self.requires("libbsd/0.10.0")
        if self.options.with_libibverbs:
            self.requires("rdma-core/52.0")
        if self.options.with_libpcap:
            self.requires("libpcap/1.10.4")
        if self.options.with_openssl:
            self.requires("openssl/[>=1.1 <4]")
        # missing:
        # - libmusdk
        # - libxdp
        # - netcope-common
        # - libwd
        # - libisal
        # - dlpack
        # - dmlc
        # - tvmdp
        # - flexran

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("DPDK is only supported on Linux")

        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        if not self.dependencies["libnuma"].options.shared:
            # dpdk is strict about its exported symbols and fails when it encounters statically linked libnuma symbols
            raise ConanInvalidConfiguration("libnuma must be built with '-o libnuma/*:shared=True'")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        self.tool_requires("cpython/[~3.12]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = MesonToolchain(self)
        # No good way to enable only static/shared except patching?
        tc.project_options["tests"] = "false"
        tc.project_options["enable_stdatomic"] = "true" if self.options.enable_stdatomic else "false"
        tc.project_options["ibverbs_link"] = "shared"  # rdma-core is a shared-library package
        tc.project_options["disable_drivers"] = "bus"
        tc.extra_cflags.append(f"-I{self.dependencies['linux-headers-generic'].cpp_info.includedir}")
        tc.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

        VirtualBuildEnv(self).generate()

        # To install pyelftools
        env = Environment()
        env.append_path("PYTHONPATH", self._site_packages_dir)
        env.append_path("PATH", os.path.join(self._site_packages_dir, "bin"))
        env.vars(self).save_script("pythonpath")

    @property
    def _site_packages_dir(self):
        return os.path.join(self.build_folder, "site-packages")

    def _pip_install(self, packages):
        self.run(f"python -m pip install {' '.join(packages)} --no-cache-dir --target={self._site_packages_dir}")

    def build(self):
        apply_conandata_patches(self)
        self._pip_install(["pyelftools"])
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "*", os.path.join(self.source_folder, "license"), os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        if self.options.shared:
            rm(self, "*.a", os.path.join(self.package_folder, "lib"))
        else:
            rm(self, "*.so*", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libdpdk")
        self.cpp_info.libs = collect_libs(self)
