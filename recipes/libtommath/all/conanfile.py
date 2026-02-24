from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.files import get, copy, rmdir, chdir
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
        env = tc.environment()
        env.define("PREFIX", self.package_folder)
        tc.generate(env)

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

    def build(self):        
        makefile = "makefile.shared" if self.options.shared else "makefile.unix"
        if is_msvc(self):
            makefile = "makefile.msvc"
        elif self.settings.os == "Windows":
            makefile = "makefile.mingw"
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.make(makefile=makefile)

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.install(args=["DESTDIR="])

    def package_info(self):
        self.cpp_info.libs = ["tommath"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["advapi32", "crypt32"]
