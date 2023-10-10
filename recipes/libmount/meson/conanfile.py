from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
import os

required_conan_version = ">=1.53.0"


class LibmountConan(ConanFile):
    name = "libmount"
    description = (
        "The libmount library is used to parse /etc/fstab, /etc/mtab and "
        "/proc/self/mountinfo files, manage the mtab file, evaluate mount options, etc"
    )
    topics = ("mount", "linux", "util-linux")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://git.kernel.org/pub/scm/utils/util-linux/util-linux.git"
    license = "LGPL-2.1-or-later"
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

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.ref} only supports Linux")

    def build_requirements(self):
        self.tool_requires("bison/3.8.2")
        self.tool_requires("flex/2.6.4")
        self.tool_requires("meson/1.3.2")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.1.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options["auto_features"] = "disabled"
        tc.project_options["build-libblkid"] = "enabled"
        tc.project_options["build-libmount"] = "enabled"
        # Enable libutil for older versions of glibc which still provide an actual libutil library.
        tc.project_options["libutil"] = "enabled"
        tc.project_options["program-tests"] = False
        tc.generate()
        virtual_build_env = VirtualBuildEnv(self)
        virtual_build_env.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Disable translations.
        replace_in_file(self, os.path.join(self.source_folder, "meson.build"), "subdir('po')", "#subdir('po')")
        # Disable tests for libmount.
        replace_in_file(self, os.path.join(self.source_folder, "libmount", "meson.build"), "foreach libmount_test: libmount_tests", "foreach libmount_test: []")

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING", os.path.join(self.source_folder, "libmount"), os.path.join(self.package_folder, "licenses"))
        copy(self, "COPYING.LGPL-2.1-or-later", os.path.join(self.source_folder, "Documentation", "licenses"), os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "sbin"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "usr"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        # util-linux always builds both the shared and static libraries of libblkid, so delete the one that isn't needed.
        rm(self, "libblkid.a" if self.options.shared else "libblkid.so*", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.components["libblkid"].libs = ["blkid"]
        self.cpp_info.components["libblkid"].set_property("pkg_config_name", "blkid")

        self.cpp_info.components["libmount"].libs = ["mount"]
        self.cpp_info.components["libmount"].system_libs = ["rt"]
        self.cpp_info.components["libmount"].includedirs.append(os.path.join("include", "libmount"))
        self.cpp_info.components["libmount"].set_property("pkg_config_name", "mount")
        self.cpp_info.components["libmount"].requires = ["libblkid"]
