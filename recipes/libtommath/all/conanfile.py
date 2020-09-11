from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class LibTomMathConan(ConanFile):
    name = "libtommath"
    description = "LibTomMath is a free open source portable number theoretic multiple-precision integer library written entirely in C."
    topics = "conan", "libtommath", "math", "multiple", "precision"
    license = "Unlicense"
    homepage = "https://www.libtom.net/"
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
    exports_sources = "patches/**"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        if tools.os_info.is_windows and self.settings.compiler != "Visual Studio":
            self.build_requires("make/4.2.1")
        if self.settings.compiler != "Visual Studio" and self.settings.os != "Windows" and self.options.shared:
            self.build_requires("libtool/2.4.6")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("libtommath-{}".format(self.version), self._source_subfolder)

    def _run_makefile(self, target=None):
        target = target or ""
        autotools = AutoToolsBuildEnvironment(self)
        autotools.libs = []
        if self.settings.os == "Windows" and self.settings.compiler != "Visual Studio":
            autotools.link_flags.append("-lcrypt32")
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
                    with tools.vcvars(self.settings):
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
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        self._run_makefile()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        if self.settings.os == "Windows":
            # The mingw makefile uses `cmd`, which is only available on Windows
            self.copy("*.a", src=self._source_subfolder, dst="lib")
            self.copy("*.lib", src=self._source_subfolder, dst="lib")
            self.copy("*.dll", src=self._source_subfolder, dst="bin")
            self.copy("tommath.h", src=self._source_subfolder, dst="include")
        else:
            self._run_makefile("install")

        # FIXME: use tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
        la = os.path.join(self.package_folder, "lib", "libtommath.la")
        if os.path.isfile(la):
            os.unlink(la)

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        suffix = ""
        if self.settings.os == "Windows":
            suffix = ".dll" if self.options.shared else ""
        self.cpp_info.libs = ["tommath" + suffix]
        if not self.options.shared:
            if self.settings.os == "Windows":
                self.cpp_info.system_libs = ["advapi32", "crypt32"]

        self.cpp_info.names["pkg_config"] = "libtommath"
