from conans import ConanFile, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment, tools
import os


class LibdeflateConan(ConanFile):
    name = "libdeflate"
    description = "Heavily optimized library for DEFLATE/zlib/gzip compression and decompression."
    license = "MIT"
    topics = ("conan", "libdeflate", "compression", "decompression", "deflate", "zlib", "gzip")
    homepage = "https://github.com/ebiggers/libdeflate"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

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
        if tools.os_info.is_windows and self.settings.compiler != "Visual Studio" and \
           not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/20200517")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def _build_msvc(self):
        makefile_msc_file = os.path.join(self._source_subfolder, "Makefile.msc")
        tools.replace_in_file(makefile_msc_file, "CFLAGS = /MD /O2 -I.", "CFLAGS = /nologo $(CFLAGS) -I.")
        tools.replace_in_file(makefile_msc_file, "LDFLAGS =", "")
        with tools.chdir(self._source_subfolder):
            with tools.vcvars(self.settings):
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
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        self.copy("libdeflate.h", dst="include", src=self._source_subfolder)
        self.copy("*.lib", dst="lib", src=self._source_subfolder)
        self.copy("*.dll", dst="bin", src=self._source_subfolder)
        self.copy("*.a", dst="lib", src=self._source_subfolder)
        self.copy("*.so*", dst="lib", src=self._source_subfolder, symlinks=True)
        self.copy("*.dylib", dst="lib", src=self._source_subfolder, symlinks=True)

    def package_info(self):
        prefix = "lib" if self.settings.os == "Windows" else ""
        suffix = "static" if self.settings.os == "Windows" and not self.options.shared else ""
        self.cpp_info.libs = ["{0}deflate{1}".format(prefix, suffix)]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines = ["LIBDEFLATE_DLL"]
