import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment


""" This older lzma release is used to build 7zip (to extract its sources).
    That's why this lzma_sdk/9.20 conan package includes a 7zDec executable.

    Recent versions of 7zip are distributed as 7z archives.
    So we need 7zip itself to uncompress its sources.
    To break this cycle, we have 2 options:
    * download an executable and run it
    * bootstrap using a previous version (lzma_sdk/9.20) which sources are in .tar.bz2.
    Right now it would be a loop in the Conan graph (if we'ld use the same recipe name)
"""


class PackageLzmaSdk(ConanFile):
    name = "lzma_sdk"
    version = "9.20"
    url = "https://github.com/conan-io/conan-center-index"
    description = "LZMA provides a high compression ratio and fast decompression, so it is very suitable for embedded applications."
    license = ("LZMA-exception",)
    homepage = "https://www.7-zip.org/sdk.html"
    topics = ("conan", "lzma", "zip", "compression", "decompression")
    settings = "os", "arch", "compiler"

    def build_requirements(self):
        if self.settings.compiler != "Visual Studio" and tools.os_info.is_windows and os.environ.get("CONAN_BASH_PATH", None) is None:
            self.build_requires("msys2/20190524")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.unlink(os.path.join(self.source_folder, "7zr.exe"))
        os.unlink(os.path.join(self.source_folder, "lzma.exe"))

    @property
    def _msvc_build_dirs(self):
        return (
            [os.path.join("C","Util","7z"), [["7zDec.exe"], []]],
            [os.path.join("C","Util","Lzma"), [["LZMAc.exe"], []]],
            [os.path.join("CPP","7zip","UI","Console"), [["7z.exe"], []]],
            [os.path.join("CPP","7zip","Bundles","Alone7z"), [["7zr.exe"], []]],
            [os.path.join("CPP","7zip","Bundles","LzmaCon"), [["lzma.exe"], []]],
        )

    @property
    def _msvc_cpu(self):
        return {
            'x86_64': 'AMD64',
            'x86': 'x86',
        }[str(self.settings.arch)]

    @property
    def _autotools_build_dirs(self):
        es = ".exe" if self.settings.os == "Windows" else ""
        return (
            [os.path.join("C","Util","7z"), [["7zDec{}".format(es)], []]],
            [os.path.join("CPP","7zip","Bundles","LzmaCon"), [["lzma{}".format(es)],[]]]
        )

    def _build_msvc(self):
        for make_dir, _ in self._msvc_build_dirs:
            with tools.vcvars(self.settings):
                with tools.chdir(make_dir):
                    self.run("nmake /f makefile NEW_COMPILER=1 CPU=%s" % self._msvc_cpu)

    def _build_autotools(self):
        env_build = AutoToolsBuildEnvironment(self)
        with tools.environment_append(env_build.vars):
            for make_dir, _ in self._autotools_build_dirs:
                with tools.chdir(make_dir):
                    extra_args = ""
                    if self.settings.os == "Windows":
                        extra_args += " IS_MINGW=1"
                    self.run("make -f makefile.gcc all%s" % extra_args)

    def _patch_sources(self):
        if self.settings.compiler == "Visual Studio":
            tools.replace_in_file(os.path.join(self.build_folder, "CPP", "Build.mak"),
                                  "-MT\r", "-" + str(self.settings.compiler.runtime))
            tools.replace_in_file(os.path.join(self.build_folder, "CPP", "Build.mak"),
                                  "-MD\r", "-" + str(self.settings.compiler.runtime))
            tools.replace_in_file(os.path.join(self.build_folder, "CPP", "Build.mak"),
                                  " -WX ", " ")

        # Patches for other build systems
        tools.replace_in_file(os.path.join(self.build_folder, "C", "Util", "7z", "makefile.gcc"),
                              "CFLAGS = ",
                              "CFLAGS = -fpermissive ")
        tools.replace_in_file(os.path.join(self.build_folder, "C", "Util", "7z", "makefile.gcc"),
                              ": 7zAlloc.c",
                              ": ../../7zAlloc.c")
        tools.replace_in_file(os.path.join(self.build_folder, "C", "Util", "Lzma", "makefile.gcc"),
                              "CFLAGS = ",
                              "CFLAGS = -fpermissive ")
        tools.replace_in_file(os.path.join(self.build_folder, "CPP", "Common", "MyString.h"),
                              "#ifdef _WIN32\r\n",
                              "#ifdef _WIN32\r\n#ifndef UNDER_CE\r\n#include <windows.h>\r\n#endif\r\n")

    def build(self):
        self._patch_sources()
        if self.settings.compiler == "Visual Studio":
            self._build_msvc()
        else:
            self._build_autotools()

    def package(self):
        self.copy("lzma.txt", src=self.source_folder, dst="licenses")
        self.copy("7zC.txt", src=self.source_folder, dst="licenses")
        if self.settings.compiler == "Visual Studio":
            for make_dir, [exes, libs] in self._msvc_build_dirs:
                for exe in exes:
                    self.copy(exe, src=os.path.join(make_dir, self._msvc_cpu), dst="bin", keep_path=False)
                for lib in libs:
                    self.copy(lib, src=os.path.join(make_dir, self._msvc_cpu), dst="lib", keep_path=False)
        else:
            for make_dir, [exes, libs] in self._autotools_build_dirs:
                for exe in exes:
                    self.copy(exe, src=os.path.join(make_dir), dst="bin", keep_path=False)
                for lib in libs:
                    self.copy(lib, src=os.path.join(make_dir), dst="lib", keep_path=False)

    def package_id(self):
        self.info.include_build_settings()
        del self.info.settings.compiler

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: %s' % bin_path)
        self.env_info.path.append(bin_path)
