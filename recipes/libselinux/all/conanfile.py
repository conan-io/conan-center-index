from conan import ConanFile
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get
from conan.tools.gnu import Autotools, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.53.0"


class LibSELinuxConan(ConanFile):
    name = "libselinux"
    description = (
        "Security-enhanced Linux is a patch of the Linux kernel and a number "
        "of utilities with enhanced security functionality designed to add "
        "mandatory access controls to Linux"
    )
    topics = ("linux", "selinux", "security", "security-enhanced")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/SELinuxProject/selinux"
    license = "Unlicense"
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

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("pcre2/10.42")

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.ref} only supports Linux")

    def build_requirements(self):
        self.tool_requires("flex/2.6.4")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/1.9.3")

    def source(self):
        for download in self.conan_data["sources"][self.version]:
            get(self, **download)

    @property
    def _sepol_soversion(self):
        return "2" if Version(self.version) >= "3.2" else "1"

    @property
    def _selinux_soversion(self):
        return "1"

    @property
    def _sepol_library_target(self):
        return f"libsepol.so.{self._sepol_soversion}" if self.options.shared else "libsepol.a"

    @property
    def _selinux_library_target(self):
        return f"libselinux.so.{self._selinux_soversion}" if self.options.shared else "libselinux.a"

    @property
    def _sepol_source_folder(self):
        return os.path.join(self.source_folder, f"libsepol-{self.version}")

    @property
    def _selinux_source_folder(self):
        return os.path.join(self.source_folder, f"libselinux-{self.version}")

    def generate(self):
        virtual_build_env = VirtualBuildEnv(self)
        virtual_build_env.generate()
        pkg_config_deps = PkgConfigDeps(self)
        pkg_config_deps.generate()
        tc = AutotoolsToolchain(self)
        sepol_include_folder = os.path.join(self._sepol_source_folder, "include")
        tc.extra_cflags.append(f"-I{sepol_include_folder}")
        sepol_lib_folder = os.path.join(self._sepol_source_folder, "src")
        tc.extra_ldflags.append(f"-L{sepol_lib_folder}")
        tc.make_args.append("USE_PCRE2=y")
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        with chdir(self, os.path.join(self._sepol_source_folder, "src")):
            autotools.make(self._sepol_library_target)
        with chdir(self, os.path.join(self._selinux_source_folder)):
            autotools.make()

    def package(self):
        copy(self, "LICENSE", self._selinux_source_folder, os.path.join(self.package_folder, "licenses"))
        for library in [self._sepol_source_folder, self._selinux_source_folder]:
            copy(self, "*.h", os.path.join(library, "include"), os.path.join(self.package_folder, "include"))
            if self.options.shared:
                copy(self, "*.so*", library, os.path.join(self.package_folder, "lib"), keep_path=False)
            else:
                copy(self, "*.a", library, os.path.join(self.package_folder, "lib"), keep_path=False)

    def package_info(self):
        self.cpp_info.components["selinux"].set_property("pkg_config_name", "libselinux")
        self.cpp_info.components["selinux"].libs = ["selinux"]
        self.cpp_info.components["selinux"].requires = ["sepol", "pcre2::pcre2"]
        if self.options.shared:
            self.cpp_info.components["selinux"].system_libs = ["dl"]

        self.cpp_info.components["sepol"].set_property("pkg_config_name", "libsepol")
        self.cpp_info.components["sepol"].libs = ["sepol"]
