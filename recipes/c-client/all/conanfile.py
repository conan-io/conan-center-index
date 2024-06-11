from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, mkdir, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, NMakeToolchain
import glob
import os
import shutil
import stat

required_conan_version = ">=1.55.0"


class CclientConan(ConanFile):
    name = "c-client"
    description = "University of Washington IMAP toolkit"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/uw-imap/imap"
    topics = "imap", "uw-imap", "tcp-ip"
    license = "Apache-2.0"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if not is_msvc(self):
            self.requires("openssl/[>=1.1 <4]")

    def validate(self):
        if self.settings.os == "Windows" and not is_msvc(self):
            raise ConanInvalidConfiguration(
                "c-client is setup to build only with MSVC for Windows"
            )
        # FIXME: need krb5 recipe
        if self.settings.os == "Macos":
            raise ConanInvalidConfiguration(
                "c-client depends on krb5 on MacOS and it's not packaged by "
                "Conan yet"
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if is_msvc(self):
            tc = NMakeToolchain(self)
            tc.generate()
        else:
            tc = AutotoolsToolchain(self)
            tc.generate()
            deps = AutotoolsDeps(self)
            deps.generate()

    def _build_msvc(self):
        # Avoid many warnings
        makefile_w2k = os.path.join(self.source_folder, "src", "osdep", "nt", "makefile.w2k")
        warnings = "/W3 /wd4267 /wd4244 /wd4273 /wd4311 /wd4312 /wd4133 /wd4028"
        replace_in_file(self, makefile_w2k, "EXTRACFLAGS =", f"EXTRACFLAGS = {warnings}")

        nmake = "nmake /f makefile.w2k"
        self.run(f"{nmake} c-client", cwd=self.source_folder)
        self.run(nmake, cwd=os.path.join(self.source_folder, "c-client"))

    def _chmod_x(self, path):
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)

    def _touch(self, path):
        with open(path, "a", encoding=None): pass

    def _build_unix(self):
        self._touch(os.path.join(self.source_folder, "ip6"))
        self._chmod_x(os.path.join(self.source_folder, "tools", "an"))
        self._chmod_x(os.path.join(self.source_folder, "tools", "ua"))
        unix = os.path.join(self.source_folder, "src", "osdep", "unix")
        self._chmod_x(os.path.join(unix, "drivers"))
        self._chmod_x(os.path.join(unix, "mkauths"))
        ssldir = self.dependencies["openssl"].package_folder
        replace_in_file(self, os.path.join(unix, "Makefile"), "SSLDIR=/usr/local/ssl", f"SSLDIR={ssldir}")
        # This is from the Homebrew Formula
        replace_in_file(
            self, os.path.join(unix, "ssl_unix.c"),
            "#include <x509v3.h>\n#include <ssl.h>",
            "#include <ssl.h>\n#include <x509v3.h>"
        )
        target = "osx" if self.settings.os == "Macos" else "slx"
        # NOTE: only one job is used, because there are issues with dependency
        #       tracking in parallel builds
        args = ["IP=6", "-j1"]
        autotools = Autotools(self)
        with chdir(self, self.source_folder):
            autotools.make(target=target, args=args)

    def build(self):
        apply_conandata_patches(self)
        if is_msvc(self):
            self._build_msvc()
        else:
            self._build_unix()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        # Install headers (headers in build tree are symlinks)
        include_folder = os.path.join(self.package_folder, "include", "c-client")
        mkdir(self, include_folder)
        for header_path in glob.glob(os.path.join(self.source_folder, "c-client", "*.h")):
            # conan.tools.files.copy can't be used because it copies symlinks instead of real files
            shutil.copy(src=header_path, dst=os.path.join(include_folder, os.path.basename(header_path)))
        # Install libs
        for lib in ("*.a", "*.lib"):
            copy(self, lib, src=os.path.join(self.source_folder, "c-client"), dst=os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = ["cclient" if is_msvc(self) else "c-client"]
        if self.settings.os != "Windows":
            self.cpp_info.defines = ["_DEFAULT_SOURCE"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["winmm", "ws2_32", "secur32", "crypt32"]
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["crypt"]
