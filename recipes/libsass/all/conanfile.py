from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class LibsassConan(ConanFile):
    name = "libsass"
    license = "MIT"
    homepage = "libsass.org"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A C/C++ implementation of a Sass compiler"
    topics = ("Sass", "LibSass", "compiler")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler == "Visual Studio":
            # TODO: add Visual Studio support
            raise ConanInvalidConfiguration("Visual Studio not yet supported in libsass recipe")

    def build_requirements(self):
        if self.settings.os != "Windows":
            self.build_requires("libtool/2.4.6")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
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
        with tools.chdir(self._source_subfolder):
            tools.save(path="VERSION", content="%s" % self.version)
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")))
            autotools = self._configure_autotools()
            autotools.make()

    @property
    def _make_program(self):
        return tools.get_env("CONAN_MAKE_PROGRAM", tools.which("make") or tools.which("mingw32-make"))

    def _build_mingw(self):
        makefile = os.path.join(self._source_subfolder, "Makefile")
        tools.replace_in_file(makefile, "CFLAGS   += -O2", "")
        tools.replace_in_file(makefile, "CXXFLAGS += -O2", "")
        tools.replace_in_file(makefile, "LDFLAGS  += -O2", "")
        with tools.chdir(self._source_subfolder):
            env_vars = AutoToolsBuildEnvironment(self).vars
            env_vars.update({
                "BUILD": "shared" if self.options.shared else "static",
                "PREFIX": tools.unix_path(os.path.join(self.package_folder)),
                # Don't force static link to mingw libs, leave this decision to consumer (through LDFLAGS in env)
                "STATIC_ALL": "0",
                "STATIC_LIBGCC": "0",
                "STATIC_LIBSTDCPP": "0",
            })
            with tools.environment_append(env_vars):
                self.run("{} -f Makefile".format(self._make_program))

    def build(self):
        if self._is_mingw:
            self._build_mingw()
        else:
            self._build_autotools()

    def _install_autotools(self):
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.remove_files_by_mask(self.package_folder, "*.la")

    def _install_mingw(self):
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("*.dll", dst="bin", src=os.path.join(self._source_subfolder, "lib"))
        self.copy("*.a", dst="lib", src=os.path.join(self._source_subfolder, "lib"))

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        if self._is_mingw:
            self._install_mingw()
        else:
            self._install_autotools()

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libsass"
        self.cpp_info.libs = ["sass"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "m"])
        if not self.options.shared and tools.stdcpp_library(self):
            self.cpp_info.system_libs.append(tools.stdcpp_library(self))
