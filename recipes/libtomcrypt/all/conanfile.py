import os

from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rename, rm, rmdir, chdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, NMakeDeps

required_conan_version = ">=1.53.0"


class LibTomCryptConan(ConanFile):
    name = "libtomcrypt"
    description = ("LibTomCrypt is a cryptographic toolkit that provides well-known"
                   " published block ciphers, one-way hash functions, chaining modes,"
                   " pseudo-random number generators, public key cryptography and other routines.")
    license = "Unlicense"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.libtom.net/"
    topics = ("cryptography", "encryption", "libtom")

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

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, f"tomcrypt-{self.version}.def",
             self.recipe_folder,
             os.path.join(self.export_sources_folder, "src"))

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

    def requirements(self):
        self.requires("libtommath/1.2.1")

    def build_requirements(self):
        if not is_msvc(self):
            if self.options.shared:
                self.build_requires("libtool/2.4.7")
            if self._settings_build.os == "Windows":
                self.build_requires("make/4.4")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        venv = VirtualBuildEnv(self)
        venv.generate()

        if not cross_building(self):
            venv = VirtualRunEnv(self)
            venv.generate(scope="build")

        tc = AutotoolsToolchain(self)
        if self.settings.os == "Windows" and not is_msvc(self):
            tc.ldflags.append("-lcrypt32")
        if self.settings.os == "Windows":
            makefile = "makefile.mingw"
        else:
            if self.options.shared:
                makefile = "makefile.shared"
            else:
                makefile = "makefile.unix"
        tc.make_args += ["-f", makefile]
        tc.generate()

        if is_msvc(self):
            deps = NMakeDeps(self)
            deps.generate()
        else:
            deps = AutotoolsDeps(self)
            deps.generate()

    def build(self):
        apply_conandata_patches(self)
        with chdir(self, self.source_folder):
            if is_msvc(self):
                if self.options.shared:
                    target = "tomcrypt.dll"
                else:
                    target = "tomcrypt.lib"
                self.run(f"nmake -f makefile.msvc {target}")
            else:
                target = None
                if self.settings.os == "Windows":
                    if self.options.shared:
                        target = "libtomcrypt.dll"
                    else:
                        target = "libtomcrypt.a"
                autotools = Autotools(self)
                autotools.make(target=target)

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        if self.settings.os == "Windows":
            # The mingw makefile uses `cmd`, which is only available on Windows
            copy(self, "*.a", self.source_folder, os.path.join(self.package_folder, "lib"))
            copy(self, "*.lib", self.source_folder, os.path.join(self.package_folder, "lib"))
            copy(self, "*.dll", self.source_folder, os.path.join(self.package_folder, "bin"))
            copy(self, "tomcrypt*.h",
                 os.path.join(self.source_folder, "src", "headers"),
                 os.path.join(self.package_folder, "include"))
        else:
            with chdir(self, self.source_folder):
                autotools = Autotools(self)
                autotools.make(target="install", args=[f"PREFIX={self.package_folder}"])

        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        if is_msvc(self) and self.options.shared:
            rename(self, os.path.join(self.package_folder, "lib", "tomcrypt.dll.lib"),
                   os.path.join(self.package_folder, "lib", "tomcrypt.lib"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libtomcrypt")
        self.cpp_info.libs = ["tomcrypt"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["advapi32", "crypt32"]
