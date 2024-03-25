from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class UtilLinuxLibuuidConan(ConanFile):
    name = "util-linux-libuuid"
    description = "Universally unique id library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/util-linux/util-linux.git"
    license = "BSD-3-Clause"
    topics = "id", "identifier", "unique", "uuid"
    package_type = "library"
    provides = "libuuid"
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

    def _minimum_compiler_version(self, compiler, build_type):
        min_version = {
            "gcc": {
                "Release": "4",
                "Debug": "8",
            },
            "clang": {
                "Release": "3",
                "Debug": "3",
            },
            "apple-clang": {
                "Release": "5",
                "Debug": "5",
            },
        }
        return min_version.get(str(compiler), {}).get(str(build_type), "0")

    def requirements(self):
        if self.settings.os == "Macos":
            # Required because libintl.{a,dylib} is not distributed via libc on Macos
            self.requires("libgettext/0.22")

    def validate(self):
        min_version = self._minimum_compiler_version(self.settings.compiler, self.settings.build_type)
        if Version(self.settings.compiler.version) < min_version:
            raise ConanInvalidConfiguration(f"{self.settings.compiler} {self.settings.compiler.version} does not meet the minimum version requirement of version {min_version}")
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(f"{self.ref} is not supported on Windows")

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
        tc.project_options["build-libuuid"] = "enabled"
        # Enable libutil for older versions of glibc which still provide an actual libutil library.
        tc.project_options["libutil"] = "enabled"
        tc.project_options["program-tests"] = False
        if "x86" in self.settings.arch:
            tc.c_args.append("-mstackrealign")
        tc.generate()
        pkg_config_deps = PkgConfigDeps(self)
        pkg_config_deps.generate()
        virtual_build_env = VirtualBuildEnv(self)
        virtual_build_env.generate()
        virtual_run_env = VirtualRunEnv(self)
        virtual_run_env.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Disable translations.
        replace_in_file(self, os.path.join(self.source_folder, "meson.build"), "subdir('po')", "#subdir('po')")

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING.BSD-3-Clause", os.path.join(self.source_folder, "Documentation", "licenses"), os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "sbin"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "usr"))
        # util-linux always builds both the shared and static libraries of libuuid, so delete the one that isn't needed.
        shared_library_extension = ".so"
        if self.settings.os == "Macos":
            shared_library_extension = ".dylib"
        rm(self, "libuuid.a" if self.options.shared else f"libuuid{shared_library_extension}*", os.path.join(self.package_folder, "lib"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "uuid")
        self.cpp_info.set_property("cmake_target_name", "libuuid::libuuid")
        self.cpp_info.set_property("cmake_file_name", "libuuid")
        # Maintain alias to `LibUUID::LibUUID` for previous version of the recipe
        self.cpp_info.set_property("cmake_target_aliases", ["LibUUID::LibUUID"])

        self.cpp_info.libs = ["uuid"]
        self.cpp_info.includedirs.append(os.path.join("include", "uuid"))
