from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, replace_in_file, rm, rmdir, save
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
import os
import textwrap


required_conan_version = ">=1.53.0"


class LibdisplayInfoConan(ConanFile):
    name = "libdisplay-info"
    description = "EDID and DisplayID library."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.freedesktop.org/emersion/libdisplay-info"
    topics = ("display", "DisplayID", "EDID")
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

    @property
    def _has_build_profile(self):
        return getattr(self, "settings_build", None)

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

    def validate(self):
        if not self.settings.os in ["FreeBSD", "Linux"]:
            raise ConanInvalidConfiguration(f"{self.ref} is not supported on {self.settings.os}")

    def build_requirements(self):
        self.tool_requires("hwdata/0.376")
        self.tool_requires("meson/1.2.3")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.0.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = MesonToolchain(self)
        if cross_building(self):
            # https://mesonbuild.com/Builtin-options.html#specifying-options-per-machine
            tc.project_options["build.pkg_config_path"] = self.generators_folder
        tc.generate()

        if self._has_build_profile:
            pkg_config_deps = PkgConfigDeps(self)
            pkg_config_deps.build_context_activated = ["hwdata"]
            pkg_config_deps.generate()
        else:
            # Manually generate pkgconfig file of hwdata since
            # PkgConfigDeps.build_context_activated can't work with legacy 1 profile.
            # We must use legacy conan v1 deps_cpp_info because self.dependencies doesn't
            # contain build requirements when using 1 profile.
            hwdata_prefix = self.deps_cpp_info["hwdata"].rootpath
            hwdata_version = self.deps_cpp_info["hwdata"].version
            hwdata_pkg_content = textwrap.dedent(f"""\
                prefix={hwdata_prefix}
                datadir=${{prefix}}/res
                pkgdatadir=${{datadir}}/hwdata
                Name: hwdata
                Description: Hardware identification and configuration data
                Version: {hwdata_version}
            """)
            save(self, os.path.join(self.generators_folder, "hwdata.pc"), hwdata_pkg_content)

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "meson.build"), "subdir('test')", "# subdir('test')")

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = ["display-info"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m"])
