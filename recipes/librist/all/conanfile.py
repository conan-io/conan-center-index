from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=2.4"


class LibristConan(ConanFile):
    name = "librist"
    description = "Library implementing the Reliable Internet Stream Transport (RIST) protocol"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://code.videolan.org/rist/librist"
    topics = ("rist", "streaming", "video", "rtp", "broadcast")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_mbedtls": [True, False],
        "tools": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_mbedtls": True,
        "tools": False,
    }
    implements = ["auto_shared_fpic"]
    languages = "C"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # cJSON is used internally (stats output), not exposed in public headers
        self.requires("cjson/[>=1.7.16 <2]")
        # Optional payload compression (LZ4_compress_default/LZ4_decompress_safe in the library itself).
        self.requires("lz4/[>=1.10.0 <2]")

        if self.options.with_mbedtls:
            # Used for SRP/EAP authentication and AES; without it librist falls back to its bundled AES
            # mbedtls >= 3.6 is needed so that PkgConfigDeps provides "mbedcrypto.pc"
            self.requires("mbedtls/[>=3.6 <4]")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options["test"] = False
        tc.project_options["static_analyze"] = False
        tc.project_options["built_tools"] = bool(self.options.tools)
        # Never fall back to the copies of cJSON/LZ4/mbedtls vendored in upstream's contrib/ folder
        tc.project_options["fallback_builtin"] = False
        tc.project_options["builtin_cjson"] = False
        tc.project_options["builtin_lz4"] = False
        tc.project_options["builtin_mbedtls"] = False
        tc.project_options["use_mbedtls"] = bool(self.options.with_mbedtls)
        tc.project_options["use_gnutls"] = False
        tc.project_options["use_nettle"] = False
        tc.project_options["allow_obj_filter"] = False
        tc.generate()
        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "librist")
        # No upstream CMake config; these names are this recipe's convention
        self.cpp_info.set_property("cmake_file_name", "librist")
        self.cpp_info.set_property("cmake_target_name", "librist::librist")
        # Upstream builds the library with an empty name_prefix: librist.so / librist.a / librist.lib
        self.cpp_info.libs = ["librist" if is_msvc(self) else "rist"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32", "iphlpapi", "bcrypt"])
