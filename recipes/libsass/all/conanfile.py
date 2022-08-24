from conans import ConanFile, AutoToolsBuildEnvironment, MSBuild, tools
from conan.errors import ConanInvalidConfiguration
import os
import re

required_conan_version = ">=1.33.0"


class LibsassConan(ConanFile):
    name = "libsass"
    license = "MIT"
    homepage = "libsass.org"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A C/C++ implementation of a Sass compiler"
    topics = ("Sass", "LibSass", "compiler")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    @property
    def _is_msvc(self):
        return self.settings.os == "Windows" and self.settings.compiler == "Visual Studio"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def build_requirements(self):
        if self.settings.os != "Windows":
            self.build_requires("libtool/2.4.6")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        args = []
        args.append("--disable-tests")
        args.append("--enable-%s" % ("shared" if self.options.shared else "static"))
        args.append("--disable-%s" % ("static" if self.options.shared else "shared"))
        self._autotools.configure(args=args)
        return self._autotools

    def _build_autotools(self):
        with tools.files.chdir(self, self._source_subfolder):
            tools.files.save(self, path="VERSION", content="%s" % self.version)
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")))
            autotools = self._configure_autotools()
            autotools.make()

    @property
    def _make_program(self):
        return tools.get_env("CONAN_MAKE_PROGRAM", tools.which("make") or tools.which("mingw32-make"))

    def _build_mingw(self):
        makefile = os.path.join(self._source_subfolder, "Makefile")
        tools.files.replace_in_file(self, makefile, "CFLAGS   += -O2", "")
        tools.files.replace_in_file(self, makefile, "CXXFLAGS += -O2", "")
        tools.files.replace_in_file(self, makefile, "LDFLAGS  += -O2", "")
        with tools.files.chdir(self, self._source_subfolder):
            env_vars = AutoToolsBuildEnvironment(self).vars
            env_vars.update({
                "BUILD": "shared" if self.options.shared else "static",
                "PREFIX": tools.microsoft.unix_path(self, os.path.join(self.package_folder)),
                # Don't force static link to mingw libs, leave this decision to consumer (through LDFLAGS in env)
                "STATIC_ALL": "0",
                "STATIC_LIBGCC": "0",
                "STATIC_LIBSTDCPP": "0",
            })
            with tools.environment_append(env_vars):
                self.run("{} -f Makefile".format(self._make_program))

    def _build_visual_studio(self):
        with tools.files.chdir(self, self._source_subfolder):
            properties = {
                "LIBSASS_STATIC_LIB": "" if self.options.shared else "true",
                "WholeProgramOptimization": "true" if any(re.finditer("(^| )[/-]GL($| )", tools.get_env("CFLAGS", ""))) else "false",
            }
            platforms = {
                "x86": "Win32",
                "x86_64": "Win64"
            }
            msbuild = MSBuild(self)
            msbuild.build(os.path.join("win", "libsass.sln"), platforms=platforms, properties=properties)

    def build(self):
        if self._is_mingw:
            self._build_mingw()
        elif self._is_msvc:
            self._build_visual_studio()
        else:
            self._build_autotools()

    def _install_autotools(self):
        with tools.files.chdir(self, self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rm(self, "*.la", self.package_folder)

    def _install_mingw(self):
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("*.dll", dst="bin", src=os.path.join(self._source_subfolder, "lib"))
        self.copy("*.a", dst="lib", src=os.path.join(self._source_subfolder, "lib"))

    def _install_visual_studio(self):
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("*.dll", dst="bin", src=os.path.join(self._source_subfolder, "win", "bin"), keep_path=False)
        self.copy("*.lib", dst="lib", src=os.path.join(self._source_subfolder, "win", "bin"), keep_path=False)

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        if self._is_mingw:
            self._install_mingw()
        elif self._is_msvc:
            self._install_visual_studio()
        else:
            self._install_autotools()

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libsass"
        self.cpp_info.libs = ["libsass" if self._is_msvc else "sass"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "m"])
        if not self.options.shared and tools.stdcpp_library(self):
            self.cpp_info.system_libs.append(tools.stdcpp_library(self))
