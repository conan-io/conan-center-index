import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, rename, replace_in_file, save
from conan.tools.gnu import Autotools, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

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
    license = (
        # https://github.com/SELinuxProject/selinux/blob/main/libselinux/LICENSE
        # For the libselinux component: public domain with a limited liability clause
        "libselinux-1.0",
        # https://github.com/SELinuxProject/selinux/blob/main/libsepol/LICENSE
        # For the libsepol component: LGPL-2.1
        "LGPL-2.1-or-later",
    )
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
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration(f"{self.ref} only supports Linux")

    def build_requirements(self):
        self.tool_requires("flex/2.6.4")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.0.3")

    def source(self):
        for download in self.conan_data["sources"][self.version]:
            get(self, **download)

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
        for subdir in [self._sepol_source_folder, self._selinux_source_folder]:
            with chdir(self, subdir):
                # Build only .a or .so, not both
                replace_in_file(self, os.path.join("src", "Makefile"),
                                "all: $(LIBA) $(LIBSO) $(LIBPC)",
                                "all: $(LIBSO)" if self.options.shared else "all: $(LIBA)")
                # Skip utils dir by truncating its Makefile
                save(self, os.path.join("utils", "Makefile"), "all:\n")
                autotools.make()

    def _copy_licenses(self):
        copy(self, "LICENSE", self._selinux_source_folder, os.path.join(self.package_folder, "licenses"))
        rename(self, os.path.join(self.package_folder, "licenses", "LICENSE"),
               os.path.join(self.package_folder, "licenses", "LICENSE-libselinux"))
        if Version(self.version) >= "3.5":
            copy(self, "LICENSE", self._sepol_source_folder, os.path.join(self.package_folder, "licenses"))
            rename(self, os.path.join(self.package_folder, "licenses", "LICENSE"),
                   os.path.join(self.package_folder, "licenses", "LICENSE-libsepol"))
        else:
            copy(self, "COPYING", self._sepol_source_folder, os.path.join(self.package_folder, "licenses"))
            rename(self, os.path.join(self.package_folder, "licenses", "COPYING"),
                   os.path.join(self.package_folder, "licenses", "LICENSE-libsepol"))

    def package(self):
        self._copy_licenses()
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
