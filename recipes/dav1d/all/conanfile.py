from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=2.4"


class Dav1dConan(ConanFile):
    name = "dav1d"
    description = "dav1d is a new AV1 cross-platform decoder, open-source, and focused on speed, size and correctness."
    homepage = "https://www.videolan.org/projects/dav1d.html"
    topics = ("av1", "codec", "video", "decoding")
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
    languages = "C"
    implements = ["auto_shared_fpic"]
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "bit_depth": ["all", 8, 16],
        "with_tools": [True, False],
        "assembly": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "bit_depth": "all",
        "with_tools": True,
        "assembly": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if is_msvc(self) and self.settings.build_type == "Debug":
            # debug builds with assembly often causes linker hangs or LNK1000
            self.options.assembly = False

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.4.0 <2]")
        if self.options.assembly and self.settings.arch in ("x86", "x86_64"):
            self.tool_requires("nasm/[*]")
        if is_msvc(self) and self.settings.arch == "armv8":
            self.tool_requires("gas-preprocessor/[*]")
            self.tool_requires("strawberryperl/[*]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = MesonToolchain(self)
        tc.project_options["enable_tests"] = False
        tc.project_options["enable_asm"] = self.options.assembly
        tc.project_options["enable_tools"] = self.options.with_tools
        if self.options.bit_depth == "all":
            tc.project_options["bitdepths"] = "8,16"
        else:
            tc.project_options["bitdepths"] = str(self.options.bit_depth)
        tc.generate()


    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "dav1d")
        self.cpp_info.libs = ["dav1d"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "pthread"])
