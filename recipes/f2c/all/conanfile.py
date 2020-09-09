from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class F2cConan(ConanFile):
    name = "f2c"
    description = "Fortran to C99 compiler"
    topics = ["conan", "f2c", "fortran", "c", "compiler", "transpiler", "netlib"]
    homepage = "http://www.netlib.org/f2c/"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
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
    def _source_subfolder_f2c(self):
        return "source_subfolder_f2c"

    @property
    def _source_subfolder_libf2c(self):
        return "source_subfolder_libf2c"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.shared
            del self.options.fPIC

    def configure(self):
        if self.options.get_safe("shared"):
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.compiler == "Visual Studio" and self.settings.arch == "x86_64":
            raise ConanInvalidConfiguration("64-bit MSVC builds are not working")

    def build_requirements(self):
        if tools.os_info.is_windows:
            if self.settings.compiler != "Visual Studio":
                self.build_requires("msys2/20200517")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version][0])
        os.rename("src", self._source_subfolder_f2c)

        tools.mkdir(self._source_subfolder_libf2c)
        with tools.chdir(self._source_subfolder_libf2c):
            tools.get(**self.conan_data["sources"][self.version][1])

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        autotools = AutoToolsBuildEnvironment(self)
        if self.settings.os == "Windows" and self.settings.compiler != "Visual Studio":
            autotools.defines.append("NO_MKDTEMP")
        if self.settings.os == "Windows":
            autotools.defines.extend(["STRICT", "WIN32_LEAN_AND_MEAN", "NOMINMAX", "MSDOS"])
        if self.settings.compiler == "Visual Studio":
            if self.settings.build_type == "Debug":
                autotools.link_flags.append("-debug")
        vars = autotools.vars
        vars["CFLAGS"] += " " + vars["CPPFLAGS"]
        with tools.environment_append(vars):
            with tools.chdir(self._source_subfolder_f2c):
                if self.settings.compiler == "Visual Studio":
                    with tools.vcvars(self.settings):
                        self.run("nmake f2c.exe -f makefile.vc", run_environment=True)
                else:
                    self.run("make f2c -f makefile.u", run_environment=True, win_bash=tools.os_info.is_windows)

            with tools.chdir(self._source_subfolder_libf2c):
                if self.settings.compiler == "Visual Studio":
                    with tools.vcvars(self.settings):
                        self.run("nmake all -f makefile.vc", run_environment=True)
                else:
                    tgt = "libf2c.so" if self.options.get_safe("shared") else "libf2c.a"
                    self.run("make TARGET={} -f makefile.u".format(tgt), run_environment=True, win_bash=tools.os_info.is_windows)

    def package(self):
        self.copy("Notice", src=self._source_subfolder_f2c, dst="licenses")

        # Copy f2c executable
        self.copy("f2c.exe", src=self._source_subfolder_f2c, dst="bin")
        self.copy("f2c", src=self._source_subfolder_f2c, dst="bin")

        # Copy f2c header
        self.copy("f2c.h", src=self._source_subfolder_f2c, dst="include")

        # Copy libf2c libraries (=support libraries for f2c)
        self.copy("vcf2c.lib", src=self._source_subfolder_libf2c, dst="lib")
        self.copy("libf2c.a", src=self._source_subfolder_libf2c, dst="lib")
        self.copy("libf2c.so", src=self._source_subfolder_libf2c, dst="lib")

    def package_info(self):
        libname = "vcf2c" if self.settings.compiler == "Visual Studio" else "f2c"
        self.cpp_info.libs = [libname]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
