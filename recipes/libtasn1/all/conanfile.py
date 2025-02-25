from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cstd
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import  copy, get, rm, rmdir, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=2.4.0"


class LibTasn1Conan(ConanFile):
    name = "libtasn1"
    homepage = "https://www.gnu.org/software/libtasn1/"
    description = "Libtasn1 is the ASN.1 library used by GnuTLS, p11-kit and some other packages."
    topics = ("ASN.1", "cryptography")
    url = "https://github.com/conan-io/conan-center-index"
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
    languages = ["C"]
    implements = ["auto_shared_fpic"]

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support Visual Studio")
        if self.settings.get_safe("compiler.cstd"):
            check_min_cstd(self, 99)

    def build_requirements(self):
        if self.settings_build.os == "Windows":
            self.tool_requires("winflexbison/2.5.25")
        else:
            self.tool_requires("bison/3.8.2")

        if self.settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)
        if not is_msvc(self):
            tc.extra_cflags.append("-std=c99")
        else:
            tc.extra_cflags.append("-std=gnu99")
        tc.configure_args.append("--disable-doc")
        # Workaround against SIP on macOS
        if self.settings.os == "Macos" and self.options.shared:
            tc.extra_ldflags.append("-Wl,-rpath,@loader_path/../lib")
        tc.generate()

    def _patch_sources(self):
        if Version(self.version) >= "4.19.0":
            replace_in_file(self, os.path.join(self.source_folder, "config.h.in"),
                            "# define _GL_EXTERN_INLINE _GL_UNUSED static",
                            "# define _GL_EXTERN_INLINE _GL_UNUSED")
        else:
            replace_in_file(self, os.path.join(self.source_folder, "config.h.in"),
                            "# define _GL_EXTERN_INLINE static _GL_UNUSED",
                            "# define _GL_EXTERN_INLINE _GL_UNUSED")

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libtasn1")
        self.cpp_info.libs = ["tasn1"]
        if not self.options.shared:
            self.cpp_info.defines = ["ASN1_STATIC"]
