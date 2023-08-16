from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, NMakeToolchain
import os

required_conan_version = ">=1.55.0"


class TinycborConan(ConanFile):
    name = "tinycbor"
    description = (
        "A small CBOR encoder and decoder library, optimized for very fast "
        "operation with very small footprint."
    )
    license = "MIT"
    topics = ("cbor", "encoder", "decoder")
    homepage = "https://github.com/intel/tinycbor"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

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
        if self.options.shared and (self.settings.os == "Windows" or is_apple_os(self)):
            raise ConanInvalidConfiguration(f"{self.ref} shared not supported on {self.settings.os}")

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not is_msvc(self):
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if is_msvc(self):
            tc = NMakeToolchain(self)
            tc.generate()
        else:
            tc = AutotoolsToolchain(self)
            env = tc.environment()
            env.define("BUILD_SHARED", "1" if self.options.shared else "0")
            env.define("BUILD_STATIC", "0" if self.options.shared else "1")
            tc.generate(env)

    def build(self):
        apply_conandata_patches(self)
        if is_msvc(self):
            with chdir(self, self.source_folder):
                self.run("nmake -f Makefile.nmake")
        else:
            autotools = Autotools(self)
            with chdir(self, self.source_folder):
                autotools.make()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            copy(self, "tinycbor.lib",
                       src=os.path.join(self.source_folder, "lib"),
                       dst=os.path.join(self.package_folder, "lib"))
            for header in ["cbor.h", "cborjson.h", "tinycbor-version.h"]:
                copy(self, header,
                           src=os.path.join(self.source_folder, "src"),
                           dst=os.path.join(self.package_folder, "include", "tinycbor"))
        else:
            autotools = Autotools(self)
            with chdir(self, self.source_folder):
                autotools.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rmdir(self, os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "tinycbor")
        self.cpp_info.libs = ["tinycbor"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
        self.cpp_info.includedirs.append(os.path.join("include", "tinycbor"))
