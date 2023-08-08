from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
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

    @property
    def _has_sys_file_header(self):
        return self.settings.os in ["FreeBSD", "Linux", "Macos"]

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

    def validate(self):
        min_version = self._minimum_compiler_version(self.settings.compiler, self.settings.build_type)
        if Version(self.settings.compiler.version) < min_version:
            raise ConanInvalidConfiguration(f"{self.settings.compiler} {self.settings.compiler.version} does not meet the minimum version requirement of version {min_version}")
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(f"{self.ref} is not supported on Windows")

    def requirements(self):
        if self.settings.os == "Macos":
            # Required because libintl.{a,dylib} is not distributed via libc on Macos
            self.requires("libgettext/0.21")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--disable-all-programs")
        tc.configure_args.append("--enable-libuuid")
        if self._has_sys_file_header:
            tc.extra_defines.append("HAVE_SYS_FILE_H")
        if "x86" in self.settings.arch:
            tc.extra_cflags.append("-mstackrealign")
        tc.generate()

        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING.BSD-3-Clause", src=os.path.join(self.source_folder, "Documentation", "licenses"), dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "sbin"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "uuid")
        self.cpp_info.set_property("cmake_target_name", "libuuid::libuuid")
        self.cpp_info.set_property("cmake_file_name", "libuuid")
        # Maintain alias to `LibUUID::LibUUID` for previous version of the recipe
        self.cpp_info.set_property("cmake_target_aliases", ["LibUUID::LibUUID"])

        self.cpp_info.libs = ["uuid"]
        self.cpp_info.includedirs.append(os.path.join("include", "uuid"))
