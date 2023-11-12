from conan import ConanFile
from conan.tools.files import get, rmdir, copy, apply_conandata_patches, chdir, export_conandata_patches, symlinks
from conan.tools.scm import Version
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.54.0"


class Liburing(ConanFile):
    name = "liburing"
    license = "GPL-2.0-or-later"
    homepage = "https://github.com/axboe/liburing"
    url = "https://github.com/conan-io/conan-center-index"
    description = ("helpers to setup and teardown io_uring instances, and also a simplified interface for "
                   "applications that don't need (or want) to deal with the full kernel side implementation.")
    topics = ("asynchronous-io", "async", "kernel")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
        "with_libc": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
        "with_libc": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def requirements(self):
        if Version(self.version) < "2.3":
            self.requires("linux-headers-generic/5.13.9")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "2.2":
            del self.options.with_libc

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def validate(self):
        # FIXME: use kernel version of build/host machine.
        # kernel version should be encoded in profile
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(
                "liburing is supported only on linux")

    def layout(self):
        basic_layout(self, src_folder='src')

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        def whether(condition):
            return "" if condition else None
        tc.update_configure_args({
            "--nolibc": whether(not self.options.get_safe("with_libc", default=True)),
            "--enable-shared": None,
            "--disable-shared": None,
            "--enable-static": None,
            "--disable-static": None,
            "--bindir": None,
            "--sbindir": None,
            "--oldincludedir": None,
        })
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        with chdir(self, self.source_folder):
            at = Autotools(self)
            at.configure()
            at.make(target="src")

    def package(self):
        copy(self, "COPYING*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        with chdir(self, self.source_folder):
            at = Autotools(self)
            at.install(
                args=[f"ENABLE_SHARED={1 if self.options.shared else 0}"]
            )

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "man"))

        if self.options.shared:
            os.remove(os.path.join(self.package_folder, "lib", "liburing.a"))
        
            # FIXME: The liburing.so symlink ends up broken. Remove and replace.
            symlinks.remove_broken_symlinks(self, self.package_folder)
            source_file_suffix = "1" if self.version < Version("2.0") else "2"
            os.symlink(src=f"liburing.so.{source_file_suffix}",
                       dst=os.path.join(self.package_folder, "lib", "liburing.so"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "liburing")
        self.cpp_info.libs = ["uring"]
