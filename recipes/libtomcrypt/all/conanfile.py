from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import chdir, copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import NMakeDeps, NMakeToolchain, is_msvc
import os

required_conan_version = ">=2.19"  # Autotools.make()/install() accept "makefile" since 2.19


class LibtomcryptConan(ConanFile):
    name = "libtomcrypt"
    description = "A comprehensive, modular and portable cryptographic toolkit."
    license = "WTFPL"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.libtom.net/LibTomCrypt/"
    topics = ("cryptography", "encryption", "security")
    package_type = "library"
    languages = "C"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def config_options(self):
        if self.settings.os == "Windows":
            # INFO: makefile.msvc only builds a static library
            del self.options.fPIC
            del self.options.shared

    def configure(self):
        if self.options.get_safe("shared"):
            self.options.rm_safe("fPIC")
        if self.settings.os == "Windows":
            self.package_type = "static-library"

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libtommath/1.3.0")

    def build_requirements(self):
        if self.options.get_safe("shared"):
            # INFO: makefile.shared drives the build through GNU libtool. On Macos it looks for "glibtool",
            # which is not installed by default (and Apple's own /usr/bin/libtool is a different tool).
            self.tool_requires("libtool/2.4.7")

    def validate(self):
        if self.settings.os == "Windows":
            if not is_msvc(self):
                raise ConanInvalidConfiguration(f"{self.ref} only supports MSVC on Windows (makefile.msvc)")
            if self.settings.arch == "armv8":
                # INFO: tomcrypt_cfg.h (a public header) does not know _M_ARM64 and stops with "Cannot detect endianness"
                raise ConanInvalidConfiguration(f"{self.ref} does not support Windows on ARM64")

    def validate_build(self):
        if cross_building(self) and self.options.get_safe("shared") and self.settings.os != "Macos":
            # INFO: libtool runs the compiler it was configured with (the build machine's) to link the library
            raise ConanInvalidConfiguration("Cross-building a shared library is only supported on Macos")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _defines(self):
        # INFO: USE_LTM/LTM_DESC select LibTomMath as math backend, LTM_DESC declares "ltm_desc" in the public headers
        return ["USE_LTM", "LTM_DESC"]

    def generate(self):
        buildenv = VirtualBuildEnv(self)
        buildenv.generate()
        if is_msvc(self):
            tc = NMakeToolchain(self)
            tc.extra_defines.extend(self._defines)
            tc.generate()
            NMakeDeps(self).generate()
        else:
            tc = AutotoolsToolchain(self)
            tc.extra_defines.extend(self._defines)
            env = tc.vars()
            deps_env = AutotoolsDeps(self).vars()
            # INFO: The makefiles assign CC, CFLAGS, LDFLAGS... unconditionally, so exported variables are ignored.
            #       Forward what AutotoolsToolchain/AutotoolsDeps computed as make arguments instead of rebuilding it.
            cflags = [env.get("CFLAGS"), env.get("CPPFLAGS"), deps_env.get("CPPFLAGS")]  # makefile.unix has no CPPFLAGS
            ldflags = [env.get("LDFLAGS"), deps_env.get("LDFLAGS")]
            tc.make_args += [
                "PREFIX=",
                f"CFLAGS={' '.join(filter(None, cflags))}",
                f"LDFLAGS={' '.join(filter(None, ldflags))}",
                f"EXTRALIBS={deps_env.get('LIBS', '')}",
            ]
            build_env = buildenv.vars()
            for var in ("CC", "AR", "RANLIB"):
                value = env.get(var) or build_env.get(var)
                if value:
                    tc.make_args.append(f"{var}={value}")
            if self.options.get_safe("shared"):
                libtool = os.path.join(self.dependencies.build["libtool"].cpp_info.bindirs[0], "libtool")
                tc.make_args.append(f"LIBTOOL={libtool}")
            tc.generate()

    @property
    def _makefile(self):
        if is_msvc(self):
            return "makefile.msvc"
        return "makefile.shared" if self.options.get_safe("shared") else "makefile.unix"

    @property
    def _nmake_args(self):
        # INFO: CL, _LINK_ and LIB come from NMakeToolchain/NMakeDeps. An empty CFLAGS drops the makefile's
        #       default "/Ox /I../libtommath".
        return ["CFLAGS=", f'PREFIX="{self.package_folder}"'.replace("\\", "/")]

    def build(self):
        with chdir(self, self.source_folder):
            if is_msvc(self):
                self.run(f"nmake -f {self._makefile} {' '.join(self._nmake_args)}")
            else:
                autotools = Autotools(self)
                autotools.make(makefile=self._makefile)

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        with chdir(self, self.source_folder):
            if is_msvc(self):
                self.run(f"nmake -f {self._makefile} install {' '.join(self._nmake_args)}")
            else:
                autotools = Autotools(self)
                autotools.install(makefile=self._makefile)
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        # INFO: the bin folder is created (empty) by makefile.msvc install
        rmdir(self, os.path.join(self.package_folder, "bin"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        if self.options.get_safe("shared"):
            rm(self, "*.a", os.path.join(self.package_folder, "lib"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libtomcrypt")
        self.cpp_info.libs = ["tomcrypt"]
        # INFO: the public headers must see the same defines the library was built with
        self.cpp_info.defines = self._defines
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["advapi32"]  # rng_get_bytes() uses CryptGenRandom
