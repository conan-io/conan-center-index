from conans import ConanFile, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment, tools
import os

required_conan_version = ">=1.33.0"


class LibdeflateConan(ConanFile):
    name = "libdeflate"
    description = "Heavily optimized library for DEFLATE/zlib/gzip compression and decompression."
    license = "MIT"
    topics = ("libdeflate", "compression", "decompression", "deflate", "zlib", "gzip")
    homepage = "https://github.com/ebiggers/libdeflate"
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
        if self._settings_build.os == "Windows" and self.settings.compiler != "Visual Studio" and \
                not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _build_msvc(self):
        makefile_msc_file = os.path.join(self._source_subfolder, "Makefile.msc")
        tools.replace_in_file(makefile_msc_file, "CFLAGS = /MD /O2 -I.", "CFLAGS = /nologo $(CFLAGS) -I.")
        tools.replace_in_file(makefile_msc_file, "LDFLAGS =", "")
        with tools.chdir(self._source_subfolder):
            with tools.vcvars(self):
                with tools.environment_append(VisualStudioBuildEnvironment(self).vars):
                    target = "libdeflate.dll" if self.options.shared else "libdeflatestatic.lib"
                    self.run("nmake /f Makefile.msc {}".format(target))

    @property
    def _make_program(self):
        return tools.unix_path(tools.get_env("CONAN_MAKE_PROGRAM", tools.which("make") or tools.which("mingw32-make")))

    def _build_make(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "Makefile"), "-O2", "")
        with tools.chdir(self._source_subfolder):
            with tools.environment_append(AutoToolsBuildEnvironment(self).vars):
                if self.settings.os == "Windows":
                    suffix = ".dll" if self.options.shared else "static.lib"
                elif tools.is_apple_os(self.settings.os):
                    suffix = ".dylib" if self.options.shared else ".a"
                else:
                    suffix = ".so" if self.options.shared else ".a"
                target = "libdeflate{}".format(suffix)
                self.run("{0} -f Makefile {1}".format(self._make_program, target), win_bash=tools.os_info.is_windows)

    def build(self):
        if self.settings.compiler == "Visual Studio":
            self._build_msvc()
        else:
            self._build_make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        self.copy("libdeflate.h", src=self._source_subfolder, dst="include")
        self.copy("*.lib", src=self._source_subfolder, dst="lib")
        self.copy("*.dll", src=self._source_subfolder, dst="bin")
        self.copy("*.a", src=self._source_subfolder, dst="lib")
        self.copy("*.so*", src=self._source_subfolder, dst="lib", symlinks=True)
        self.copy("*.dylib", src=self._source_subfolder, dst="lib", symlinks=True)

    def package_info(self):
        prefix = "lib" if self.settings.os == "Windows" else ""
        suffix = "static" if self.settings.os == "Windows" and not self.options.shared else ""
        self.cpp_info.libs = ["{0}deflate{1}".format(prefix, suffix)]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines = ["LIBDEFLATE_DLL"]
