from conan import ConanFile
from conan.tools.files import get, rmdir, copy, chdir, rm, replace_in_file
from conan.tools.scm import Version
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=2"


class Liburing(ConanFile):
    name = "liburing"
    description = ("helpers to setup and teardown io_uring instances, and also a simplified interface for "
                   "applications that don't need (or want) to deal with the full kernel side implementation.")
    license = ("GPL-2.0-or-later", "MIT", "LGPL-2.1-or-later")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/axboe/liburing"
    topics = ("asynchronous-io", "async", "kernel")
    settings = "os", "arch", "compiler", "build_type"
    package_type = "library"
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def validate(self):
        # FIXME: use kernel version of build/host machine.
        # kernel version should be encoded in profile
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.ref} is supported only on linux")

    def layout(self):
        basic_layout(self, src_folder='src')

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        replace_in_file(self, "Makefile", "@$(MAKE) -C test", "")
        replace_in_file(self, "Makefile", "@$(MAKE) -C examples", "")

    def generate(self):
        tc = AutotoolsToolchain(self)

        if Version(self.version) >= "2.5":
            if self.options.with_libc:
                tc.configure_args.append("--use-libc")
        elif not self.options.with_libc:
            tc.configure_args.append("--nolibc")

        tc.update_configure_args({
            "--host": None,
            "--build": None,
            "--enable-shared": None,
            "--disable-shared": None,
            "--enable-static": None,
            "--disable-static": None,
            "--bindir": None,
            "--sbindir": None,
            "--oldincludedir": None,
            "--libdevdir": "${prefix}/lib",  # pointing to libdir
        })
        tc.generate()

    def build(self):
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
            rm(self, "*.a", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "liburing")
        self.cpp_info.libs = ["uring"]
