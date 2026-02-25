from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import get, copy, rmdir, chdir, rm
import os

required_conan_version = ">=2.4"


class LibTomMathConan(ConanFile):
    name = "libtommath"
    description = "LibTomMath is a free open source portable number theoretic multiple-precision integer library written entirely in C."
    topics = "libtommath", "math", "multiple", "precision"
    license = "Unlicense"
    package_type = "library"
    homepage = "https://www.libtom.net/LibTomMath/"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    languages = "C"
    implements = ["auto_shared_fpic"]
    
    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        if self.settings.os == "Windows":
            self.tool_requires("libtool/2.4.7")
            if not is_msvc(self):
                self.tool_requires("make/[>=4.3.0 <5]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        
    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()

    def _run_makefile(self, target=None):
        target = target or ""
        autotools = AutoToolsBuildEnvironment(self)
        autotools.libs = []
        if self.settings.os == "Windows" and self.settings.compiler != "Visual Studio":
            autotools.link_flags.append("-lcrypt32")
        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            # FIXME: should be handled by helper
            autotools.link_flags.append("-arch arm64")
        args = autotools.vars
        args.update({
            "PREFIX": self.package_folder,
        })
        if self.settings.compiler != "Visual Studio":
            if tools.get_env("CC"):
                args["CC"] = tools.get_env("CC")
            if tools.get_env("LD"):
                args["LD"] = tools.get_env("LD")
            if tools.get_env("AR"):
                args["AR"] = tools.get_env("AR")

            args["LIBTOOL"] = "libtool"
        arg_str = " ".join("{}=\"{}\"".format(k, v) for k, v in args.items())

        with tools.environment_append(args):
            with tools.chdir(self._source_subfolder):
                if self.settings.compiler == "Visual Studio":
                    if self.options.shared:
                        target = "tommath.dll"
                    else:
                        target = "tommath.lib"
                    with tools.vcvars(self):
                        self.run("nmake -f makefile.msvc {} {}".format(
                            target,
                            arg_str,
                        ), run_environment=True)
                else:
                    if self.settings.os == "Windows":
                        makefile = "makefile.mingw"
                        if self.options.shared:
                            target = "libtommath.dll"
                        else:
                            target = "libtommath.a"
                    else:
                        if self.options.shared:
                            makefile = "makefile.shared"
                        else:
                            makefile = "makefile.unix"
                    self.run("{} -f {} {} {} -j{}".format(
                        tools.get_env("CONAN_MAKE_PROGRAM", "make"),
                        makefile,
                        target,
                        arg_str,
                        tools.cpu_count(),
                    ), run_environment=True)

    @property
    def _makefile(self):
        """
        Helper method to determine the appropriate makefile based on the build options and settings.
        """
        makefile = "makefile.shared" if self.options.shared else "makefile.unix"
        if is_msvc(self):
            makefile = "makefile.msvc"
        elif self.settings.os == "Windows":
            makefile = "makefile.mingw"
        return makefile
        
    @property
    def _make_args(self):
        """ Helper method to construct the arguments for the make command based on the build options and settings.
            Environment variables have no effect because those variables are listed in the makefiles as arguments, so we need to pass them explicitly.
        """
        args = ["DESTDIR=", f"PREFIX={self.package_folder}"]
        if self.settings.os == "Windows" and not is_msvc(self):
            args.append("LDFLAGS=-lcrypt32")
        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            args.append("LDFLAGS='-arch arm64'")
        compilers_from_conf = self.conf.get("tools.build:compiler_executables", default={}, check_type=dict)
        buildenv_vars = VirtualBuildEnv(self).vars()
        cc = compilers_from_conf.get("c", buildenv_vars.get("CC", "cc"))
        if cc:
            args.append(f"CC={cc}")
        # INFO: Conan AutotoolsToolchain exports CXXFLAGS by default
        cflags = self.conf.get("tools.build:cflags", default=[], check_type=list) or buildenv_vars.get("CFLAGS") \
            or self.conf.get("tools.build:cxxflags", default=[], check_type=list) or buildenv_vars.get("CXXFLAGS")
        if cflags:
            args.append(f"CFLAGS={cflags}")
        ldflags = self.conf.get("tools.build:sharedlinkflags", default=[], check_type=list) or buildenv_vars.get("LDFLAGS")
        if ldflags:
            args.append(f"LDFLAGS={ldflags}")
        ar = buildenv_vars.get("AR")
        if ar:
            args.append(f"AR={ar}")
        ld = buildenv_vars.get("LD")
        if ld:
            args.append(f"LD={ld}")
        return args
    
    def build(self):
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.make(args=self._make_args, makefile=self._makefile)

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.install(args=self._make_args, makefile=self._makefile)
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        if self.options.shared:
            rm(self, "*.a", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = ["tommath"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["advapi32", "crypt32"]
