from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, replace_in_file, rm, rmdir
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class Dav1dConan(ConanFile):
    name = "dav1d"
    description = "dav1d is a new AV1 cross-platform decoder, open-source, and focused on speed, size and correctness."
    homepage = "https://www.videolan.org/projects/dav1d.html"
    topics = ("av1", "codec", "video", "decoding")
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "bit_depth": ["all", 8, 16],
        "with_tools": [True, False],
        "assembly": [True, False],
        "with_avx512": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "bit_depth": "all",
        "with_tools": True,
        "assembly": True,
        "with_avx512": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if is_msvc(self) and self.settings.build_type == "Debug":
            # debug builds with assembly often causes linker hangs or LNK1000
            self.options.assembly = False
        if Version(self.version) < "1.0.0":
            del self.options.with_avx512

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
           del self.settings.compiler.libcxx
        except Exception:
           pass
        try:
           del self.settings.compiler.cppstd
        except Exception:
           pass
        if not self.options.assembly:
            del self.options.with_avx512

    def build_requirements(self):
        self.tool_requires("meson/0.63.1")
        if self.options.assembly:
            self.tool_requires("nasm/2.15.05")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options["enable_tests"] = False
        tc.project_options["enable_asm"] = self.options.assembly
        if Version(self.version) < "1.0.0":
            tc.project_options["enable_avx512"] = self.options.get_safe("with_avx512", False)
        tc.project_options["enable_tools"] = self.options.with_tools
        if self.options.bit_depth == "all":
            tc.project_options["bitdepths"] = "8,16"
        else:
            tc.project_options["bitdepths"] = str(self.options.bit_depth)
        # TODO: fixed in conan 1.51.0?
        tc.project_options["bindir"] = "bin"
        tc.project_options["libdir"] = "lib"
        tc.generate()

        env = VirtualBuildEnv(self)
        env.generate(scope="build")

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "meson.build"),
                              "subdir('doc')", "")

    def build(self):
        self._patch_sources()
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
        fix_msvc_libname(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "dav1d")
        self.cpp_info.libs = ["dav1d"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "pthread"])

        if self.options.with_tools:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)

def fix_msvc_libname(conanfile, remove_lib_prefix=True):
    """remove lib prefix & change extension to .lib"""
    from conan.tools.files import rename
    import glob
    if not is_msvc(conanfile):
        return
    libdirs = getattr(conanfile.cpp.package, "libdirs")
    for libdir in libdirs:
        for ext in [".dll.a", ".dll.lib", ".a"]:
            full_folder = os.path.join(conanfile.package_folder, libdir)
            for filepath in glob.glob(os.path.join(full_folder, f"*{ext}")):
                libname = os.path.basename(filepath)[0:-len(ext)]
                if remove_lib_prefix and libname[0:3] == "lib":
                    libname = libname[3:]
                rename(conanfile, filepath, os.path.join(os.path.dirname(filepath), f"{libname}.lib"))
