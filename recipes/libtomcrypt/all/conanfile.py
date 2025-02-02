import os

from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.env import VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rename, rm, rmdir, chdir, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsDeps, GnuToolchain, PkgConfigDeps
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
                self.tool_requires("libtool/2.4.7")
            if self.settings_build.os == "Windows":
                self.tool_requires("make/4.4")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "makefile_include.mk"),
                        "PKG_CONFIG_PATH=$(LIBPATH)/pkgconfig pkg-config",
                        self.conf.get("tools.gnu:pkg_config", default="pkgconf", check_type=str))


    def generate(self):
        if not cross_building(self):
            venv = VirtualRunEnv(self)
            venv.generate(scope="build")

        tc = GnuToolchain(self)
        if self.settings.os == "Windows" and not is_msvc(self):
            tc.ldflags.append("-lcrypt32")
        cflags = tc.cflags + ["-DUSE_LTM", "-DLTM_DESC"] + [f"-D{d}" for d in tc.defines]
        ldflags = list(tc.ldflags)
        deps = AutotoolsDeps(self)
        dep_vars = deps.environment.vars(self)
        cflags.append(dep_vars.get("CFLAGS", ""))
        cflags.append(dep_vars.get("CPPFLAGS", ""))
        ldflags.append(dep_vars.get("LDFLAGS", ""))
        tc.make_args["CFLAGS"] = " ".join(cflags)
        tc.make_args["LDFLAGS"] = " ".join(ldflags)
        tc_vars = tc.extra_env.vars(self)
        tc.make_args["CC"] = tc_vars["CC"]
        if cross_building(self):
            tc.make_args["CROSS_COMPILE"] = tc_vars["STRIP"].replace("-strip", "-")
        tc.extra_env.prepend_path("PKG_CONFIG_PATH", self.generators_folder)
        tc.generate()

        if is_msvc(self):
            deps = NMakeDeps(self)
            deps.generate()
        else:
            deps = PkgConfigDeps(self)
            deps.generate()

    def build(self):
        with chdir(self, self.source_folder):
            if is_msvc(self):
                if self.options.shared:
                    target = "tomcrypt.dll"
                else:
                    target = "tomcrypt.lib"
                self.run(f"nmake -f makefile.msvc {target}")
            else:
                if self.options.shared:
                    if self.settings.os == "Windows":
                        target = "libtomcrypt.dll"
                    else:
                        target = "libtomcrypt.la"
                else:
                    target = "libtomcrypt.a"
                autotools = Autotools(self)
                if self.settings.os == "Windows":
                    makefile = "makefile.mingw"
                else:
                    if self.options.shared:
                        makefile = "makefile.shared"
                    else:
                        makefile = "makefile.unix"
                autotools.make(target=target, args=[f"-f {makefile}"])

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
