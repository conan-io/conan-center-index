from conans import AutoToolsBuildEnvironment, ConanFile, tools
import os

required_conan_version = ">=1.33.0"


class LibTomMathConan(ConanFile):
    name = "libtommath"
    description = "LibTomMath is a free open source portable number theoretic multiple-precision integer library written entirely in C."
    topics = "libtommath", "math", "multiple", "precision"
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

    exports_sources = "patches/*"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        if self._settings_build.os == "Windows" and self.settings.compiler != "Visual Studio":
            self.build_requires("make/4.3")
        if self.settings.compiler != "Visual Studio" and self.settings.os != "Windows" and self.options.shared:
            self.build_requires("libtool/2.4.6")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

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
            with tools.files.chdir(self, self._source_subfolder):
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
                        tools.cpu_count(self, ),
                    ), run_environment=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
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

        tools.files.rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        if self.settings.compiler == "Visual Studio" and self.options.shared:
            os.rename(os.path.join(self.package_folder, "lib", "tommath.dll.lib"),
                      os.path.join(self.package_folder, "lib", "tommath.lib"))

    def package_info(self):
        self.cpp_info.libs = ["tommath"]
        if not self.options.shared:
            if self.settings.os == "Windows":
                self.cpp_info.system_libs = ["advapi32", "crypt32"]

        self.cpp_info.names["pkg_config"] = "libtommath"
