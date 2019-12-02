
import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment


class Package7Zip(ConanFile):
    name = "7zip"
    version = "19.00"
    url = "https://github.com/conan-io/conan-center-index"
    description = "7-Zip is a file archiver with a high compression ratio"
    license = ("LGPL-2.1", "BSD-3-Clause", "Unrar")
    homepage = "https://www.7-zip.org"
    topics = ("conan", "7zip", "zip", "compression", "decompression")
    settings = "os_build", "arch_build", "compiler"
    build_requires = "lzma_sdk/9.20"

    def source(self):
        tools.download(self.conan_data["sources"][self.version]["url"], "7zip.7z")
        tools.check_sha256("7zip.7z", self.conan_data["sources"][self.version]["sha256"])
        self.run("7zDec x 7zip.7z")
        os.unlink("7zip.7z")

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
        }[str(self.settings.arch_build)]

    @property
    def _autotools_build_dirs(self):
        es = ".exe" if self.settings.os_build == "Windows" else ""
        return (
            [os.path.join("C","Util","7z"), [["7zDec{}".format(es)], []]],
            [os.path.join("CPP","7zip","Bundles","LzmaCon"), [["lzma{}".format(es)],[]]]
        )

    def _build_msvc(self):
        env_build = VisualStudioBuildEnvironment(self)
        with tools.environment_append(env_build.vars):
            vcvars = tools.vcvars_command(self.settings)
            for make_dir, _ in self._msvc_build_dirs:
                with tools.chdir(make_dir):
                    self.run("%s && nmake /f makefile NEW_COMPILER=1 CPU=%s" % (vcvars, self._msvc_cpu))

    def _build_autotools(self):
        env_build = AutoToolsBuildEnvironment(self)
        with tools.environment_append(env_build.vars):
            for make_dir, _ in self._autotools_build_dirs:
                with tools.chdir(make_dir):
                    extra_args = ""
                    if self.settings.os_build == "Windows":
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
        #self._patch_sources()
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
        del self.info.settings.compiler

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: %s' % bin_path)
        self.env_info.path.append(bin_path)
