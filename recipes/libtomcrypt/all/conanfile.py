from conan import ConanFile
from conan.tools.files import copy, chdir, get, rmdir, rm
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, NMakeToolchain, NMakeDeps, msvc_runtime_flag
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
import os

conan_minimum_required = ">=2.4.0"

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
            del self.options.fPIC
            del self.options.shared

    def configure(self):
        if self.options.get_safe("shared"):
            self.options.rm_safe("fPIC")
        if self.settings.os == "Windows":
            self.package_type = "static-library"

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build_requirements(self):
        if self.settings_build.os == "Windows":
            if not self.conf_info.get("tools.gnu:make_program", check_type=str):
                self.tool_requires("make/4.4.1")

    def requirements(self):
        self.requires("libtommath/1.3.0")

    def generate(self):
        if is_msvc(self):
            tc = NMakeToolchain(self)
            tc.generate()
            tc = NMakeDeps(self)
            tc.generate()
        else:
            tc = AutotoolsDeps(self)
            tc.generate()
            tc = AutotoolsToolchain(self)
            tc.make_args = self._make_args()
            tc.generate()

    @property
    def _makefile(self):
        """
        Helper method to determine the appropriate makefile based on the build options and settings.
        """
        makefile = "makefile.shared" if self.options.get_safe("shared") else "makefile.unix"
        if is_msvc(self):
            makefile = "makefile.msvc"
        elif self.settings.os == "Windows":
            makefile = "makefile.mingw"
        return makefile

    def _make_args(self):
        """ Helper method to construct the arguments for the make command based on the build options and settings.
            Environment variables have no effect because those variables are listed in the makefiles as arguments, so we need to pass them explicitly.
        """
        args = ["PREFIX=", f"DESTDIR={self.package_folder}"]

        compilers_from_conf = self.conf.get("tools.build:compiler_executables", default={}, check_type=dict)
        autotools_vars = AutotoolsToolchain(self).vars()
        autotoolsdeps_vars = AutotoolsDeps(self).vars()

        cc = compilers_from_conf.get("c", autotools_vars.get("CC", "cc"))
        if cc:
            args.append(f"CC={cc}")

        defs = self.conf.get("tools.build:defines", default=[], check_type=list)
        defs.extend(["USE_LTM", "LTM_DESC"])

        cflags = self.conf.get("tools.build:cflags", default=[], check_type=list)
        cppflags = self.conf.get("tools.build:cxxflags", default=[], check_type=list)

        # Combine cflags and cppflags, prioritizing autotools_vars and autotoolsdeps_vars if conf is empty
        cflags_str = " ".join(cflags) if cflags else autotools_vars.get("CFLAGS", "")
        cppflags_str = " ".join(cppflags) if cppflags else autotoolsdeps_vars.get("CPPFLAGS", "")

        if defs:
            cppflags_str = f"{cppflags_str} {' '.join(f'-D{d}' for d in defs)}".strip()

        if cppflags_str:
            cflags_str = f"{cflags_str} {cppflags_str}".strip()

        if cflags_str:
            args.append(f"CFLAGS={cflags_str}")

        ldflags = self.conf.get("tools.build:sharedlinkflags", default=[], check_type=list)
        ldflags_str = " ".join(ldflags) if ldflags else autotoolsdeps_vars.get("LDFLAGS", "")
        if ldflags_str:
            args.append(f"LDFLAGS={ldflags_str}")

        args.append(f"EXTRALIBS={autotoolsdeps_vars.get('LIBS', '')}")

        ar = autotools_vars.get("AR")
        if ar:
            args.append(f"AR={ar}")

        ld = autotools_vars.get("LD")
        if ld:
            args.append(f"LD={ld}")

        return args

    def _nmake_args(self):
        prefix = self.package_folder.replace("\\", "/")
        args = [f"PREFIX={prefix}"]

        compilers_from_conf = self.conf.get("tools.build:compiler_executables", default={}, check_type=dict)
        cc = compilers_from_conf.get("c", "cl")
        if cc:
            args.append(f"CC={cc}")

        tommath_include = os.path.join(self.dependencies["libtommath"].cpp_info.includedirs[0]).replace("\\", "/")
        tommath_libdir = os.path.join(self.dependencies["libtommath"].cpp_info.libdirs[0]).replace("\\", "/")
        tommath_lib = self.dependencies["libtommath"].cpp_info.libs[0]

        defs = self.conf.get("tools.build:defines", default=[], check_type=list)
        defs.extend(["USE_LTM", "LTM_DESC"])

        cflags = self.conf.get("tools.build:cflags", default=[], check_type=list)
        cflags.append(f"/I'{tommath_include}'")
        if self.settings.build_type == "Release":
            cflags.append("/Ox /DNDEBUG")
        cflags.append(f"/{msvc_runtime_flag(self)}")
        cflags.extend(f"/D{d}" for d in defs)
        args.append(f"CFLAGS=\"{' '.join(cflags)}\"")

        extralibs = f"EXTRALIBS=\"/link /LIBPATH:'{tommath_libdir}' {tommath_lib}.lib\""
        args.append(extralibs)

        ldflags = self.conf.get("tools.build:sharedlinkflags", default=[], check_type=list)
        if ldflags:
            args.append(f"LDFLAGS=\"{' '.join(ldflags)}\"")

        return args

    def build(self):
        with chdir(self, self.source_folder):
            if is_msvc(self):
                make_args = self._nmake_args()
                self.run(f"nmake -f {self._makefile} {' '.join(make_args)}")
            else:
                autotools = Autotools(self)
                autotools.make(makefile=self._makefile)

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        with chdir(self, self.source_folder):
            if is_msvc(self):
                make_args = self._nmake_args()
                self.run(f"nmake -f {self._makefile} install {' '.join(make_args)}")
            else:
                autotools = Autotools(self)
                autotools.install(makefile=self._makefile)
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        # INFO: bin dir is empty by created during the install step
        rmdir(self, os.path.join(self.package_folder, "bin"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        if self.options.get_safe("shared"):
            rm(self, "*.a", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = ["tomcrypt"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
