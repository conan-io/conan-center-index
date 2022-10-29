from conan import ConanFile
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, rename, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.52.0"


class LibSELinuxConan(ConanFile):
    name = "libselinux"
    description = (
        "Security-enhanced Linux is a patch of the Linux kernel and a number "
        "of utilities with enhanced security functionality designed to add "
        "mandatory access controls to Linux"
    )
    topics = ("selinux", "security-enhanced linux")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/SELinuxProject/selinux"
    license = "Unlicense"  # This library (libselinux) is public domain software, i.e. not copyrighted
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
            del self.options.fPIC
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def requirements(self):
        self.requires("pcre2/10.40")

    def validate(self):
        if self.info.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.ref} only supports Linux")

    def build_requirements(self):
        self.tool_requires("flex/2.6.4")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        for download in self.conan_data["sources"][self.version]:
            get(self, **download, destination=self.source_folder)

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
        pkg_config_deps = AutotoolsDeps(self)
        pkg_config_deps.generate()
        tc = AutotoolsToolchain(self)
        tc.extra_defines.append("USE_PCRE2=1")
        tc.extra_defines.append("PCRE2_CODE_UNIT_WIDTH=8")
        sepol_include_folder = os.path.join(self._sepol_source_folder, "include")
        tc.extra_cflags.append(f"-I{sepol_include_folder}")
        # Remove the "/usr" prefix from the install destination.
        tc.make_args.append("PREFIX=")
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        with chdir(self, os.path.join(self._sepol_source_folder, "src")):
            autotools.make(self._sepol_library_target)
        with chdir(self, os.path.join(self._selinux_source_folder, "src")):
            autotools.make(self._selinux_library_target)

    def package(self):
        copy(self, "LICENSE", self._selinux_source_folder, os.path.join(self.package_folder, "licenses"))
        for library in [self._sepol_source_folder, self._selinux_source_folder]:
            copy(self, "*.h", os.path.join(library, "include"), os.path.join(self.package_folder, "include"))
            copy(self, "*.so*", library, os.path.join(self.package_folder, "lib"), keep_path=False)
            copy(self, "*.a", library, os.path.join(self.package_folder, "lib"), keep_path=False)

    def package_info(self):
        self.cpp_info.components["selinux"].set_property("pkg_config_name", "libselinux")
        self.cpp_info.components["selinux"].names["pkg_config"] = "libselinux"
        self.cpp_info.components["selinux"].libs = ["selinux"]
        self.cpp_info.components["selinux"].requires = ["sepol", "pcre2::pcre2"]

        self.cpp_info.components["sepol"].set_property("pkg_config_name", "libsepol")
        self.cpp_info.components["sepol"].names["pkg_config"] = "libsepol"
        self.cpp_info.components["sepol"].libs = ["sepol"]
