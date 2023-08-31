import os
from conan import ConanFile
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.files import copy, get, rmdir, rename, chdir, rm
from conan.tools.layout import basic_layout
from conan.tools.gnu import PkgConfigDeps
from conan.tools.microsoft import is_msvc_static_runtime
from conan.tools.apple import fix_apple_shared_install_name
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.60.0 <2 || >=2.0.6"

class LibniceConan(ConanFile):
    name = "libnice"
    homepage = "https://libnice.freedesktop.org/"
    license = ("MPL-1.1", "LGPL-2.1-only")
    url = "https://github.com/conan-io/conan-center-index"
    description = "a GLib ICE implementation"
    topics = ("ice", "stun", "turn")
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "crypto_library": ["openssl", "win32"],
        "with_gstreamer": [True, False],
        "with_gtk_doc": [True, False],
        "with_introspection": [True, False]}
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_gstreamer": False,
        "with_gtk_doc": False,
        "with_introspection": False}

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            self.options.crypto_library = "win32"
        else:
            self.options.crypto_library = "openssl"

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os != "Windows" and self.options.crypto_library == "win32":
            raise ConanInvalidConfiguration(
                f"-o {self.ref}:crypto_library=win32 is not supported on non-Windows")
        if self.settings.os == "Windows" and self.options.with_gtk_doc:
            raise ConanInvalidConfiguration(
                f"-o {self.ref}:with_gtk_doc=True is not support on Windows")
        if is_msvc_static_runtime(self) and self.dependencies["glib"].options.shared:
            raise ConanInvalidConfiguration(
                "-o glib/*:shared=True with static runtime is not supported")

    def requirements(self):
        self.requires("glib/2.77.2", transitive_headers=True, transitive_libs=True)
        if self.options.crypto_library == "openssl":
            self.requires("openssl/[>=1.1 <4]")
        if self.options.with_gstreamer:
            self.requires("gstreamer/1.22.3")

    def build_requirements(self):
        self.tool_requires("meson/1.2.1")
        self.tool_requires("pkgconf/1.9.5")
        self.tool_requires("glib/<host_version>")  # for glib-mkenums
        if self.options.with_introspection:
            self.tool_requires("gobject-introspection/1.72.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = PkgConfigDeps(self)
        tc.generate()
        tc = MesonToolchain(self)
        tc.project_options["gupnp"] = "disabled"
        tc.project_options["gstreamer"] = "enabled" if self.options.with_gstreamer else "disabled"
        tc.project_options["crypto-library"] = "auto" if self.options.crypto_library == "win32" else str(
            self.options.crypto_library)

        tc.project_options["examples"] = "disabled"
        tc.project_options["tests"] = "disabled"
        tc.project_options["gtk_doc"] = "disabled" if self.options.with_gtk_doc else "disabled"
        tc.project_options["introspection"] = "enabled" if self.options.with_introspection else "disabled"
        tc.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, pattern="COPYING*", dst=os.path.join(self.package_folder,
             "licenses"), src=self.source_folder)
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        if self.settings.os == "Windows":
            if not self.options.shared:
                with chdir(self, os.path.join(self.package_folder, "lib")):
                    rename(self, "libnice.a", "nice.lib")
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["nice"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("advapi32")
