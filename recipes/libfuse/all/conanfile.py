from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rmdir
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
import os

required_conan_version = ">=1.53.0"


class LibfuseConan(ConanFile):
    name = "libfuse"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libfuse/libfuse"
    license = "LGPL-2.1"
    description = "The reference implementation of the Linux FUSE interface"
    topics = ("fuse", "filesystem", "linux")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "header_only": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "header_only": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.header_only:
            self.options.rm_safe("shared")
            self.options.rm_safe("fPIC")
        elif self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        if self.info.options.header_only:
            self.info.clear()

    def validate(self):
        if self.settings.os not in ("Linux", "FreeBSD"):
            raise ConanInvalidConfiguration("libfuse supports only Linux and FreeBSD")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.0 <2]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = MesonToolchain(self)
        tc.project_options["examples"] = False
        tc.project_options["utils"] = False
        tc.project_options["tests"] = False
        tc.project_options["useroot"] = False
        tc.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        if not self.options.header_only:
            meson.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if self.options.header_only:
            # The headers that include/meson.build installs, plus libfuse_config.h, which
            # meson configure generates in newer versions (fuse_common.h includes it)
            include_folder = os.path.join(self.package_folder, "include", "fuse3")
            for header in ("fuse.h", "fuse_common.h", "fuse_lowlevel.h", "fuse_opt.h", "cuse_lowlevel.h", "fuse_log.h"):
                copy(self, header, src=os.path.join(self.source_folder, "include"), dst=include_folder)
            copy(self, "libfuse_config.h", src=self.build_folder, dst=include_folder)
        else:
            meson = Meson(self)
            meson.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "fuse3")
        self.cpp_info.includedirs = [os.path.join("include", "fuse3")]
        if self.options.header_only:
            self.cpp_info.bindirs = []
            self.cpp_info.libdirs = []
        else:
            self.cpp_info.libs = ["fuse3"]
            self.cpp_info.system_libs = ["pthread"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.extend(["dl", "rt"])
