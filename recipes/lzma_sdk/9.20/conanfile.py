from conans import ConanFile, tools, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment
import os

required_conan_version = ">=1.33.0"


""" This older lzma release is used to build 7zip (to extract its sources).
    That's why this lzma_sdk/9.20 conan package includes a 7zDec executable.

    Recent versions of 7zip are distributed as 7z archives.
    So we need 7zip itself to uncompress its sources.
    To break this cycle, we have 2 options:
    * download an executable and run it
    * bootstrap using a previous version (lzma_sdk/9.20) which sources are in .tar.bz2.
    Right now it would be a loop in the Conan graph (if we'ld use the same recipe name)
"""


class LzmaSdkConan(ConanFile):
    name = "lzma_sdk"
    url = "https://github.com/conan-io/conan-center-index"
    description = "LZMA provides a high compression ratio and fast decompression, so it is very suitable for embedded applications."
    license = ("LZMA-exception",)
    homepage = "https://www.7-zip.org/sdk.html"
    topics = ("lzma", "zip", "compression", "decompression")
    settings = "os", "arch", "compiler"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if self.settings.compiler != "Visual Studio" and self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder)
        os.unlink(os.path.join(self._source_subfolder, "7zr.exe"))
        os.unlink(os.path.join(self._source_subfolder, "lzma.exe"))

    @property
    def _msvc_build_dirs(self):
        return (
            (os.path.join(self._source_subfolder, "C", "Util", "7z"), "7zDec.exe"),
            (os.path.join(self._source_subfolder, "C", "Util", "Lzma"), "LZMAc.exe"),
            (os.path.join(self._source_subfolder, "CPP", "7zip", "UI", "Console"), "7z.exe"),
            (os.path.join(self._source_subfolder, "CPP", "7zip","Bundles", "Alone7z"), "7zr.exe"),
            (os.path.join(self._source_subfolder, "CPP", "7zip", "Bundles", "LzmaCon"), "lzma.exe"),
        )

    @property
    def _msvc_cpu(self):
        return {
            "x86_64": "AMD64",
            "x86": "x86",
        }[str(self.settings.arch)]

    @property
    def _autotools_build_dirs(self):
        es = ".exe" if self.settings.os == "Windows" else ""
        return (
            (os.path.join(self._source_subfolder, "C", "Util", "7z"), "7zDec{}".format(es)),
            (os.path.join(self._source_subfolder, "CPP", "7zip", "Bundles", "LzmaCon"), "lzma{}".format(es)),
        )

    def _build_msvc(self):
        for make_dir, _ in self._msvc_build_dirs:
            with tools.vcvars(self):
                with tools.environment_append(VisualStudioBuildEnvironment(self).vars):
                    with tools.chdir(make_dir):
                        self.run("nmake /f makefile NEW_COMPILER=1 CPU={}".format(self._msvc_cpu))

    def _build_autotools(self):
        env_build = AutoToolsBuildEnvironment(self)
        with tools.environment_append(env_build.vars):
            for make_dir, _ in self._autotools_build_dirs:
                with tools.chdir(make_dir):
                    args = [
                        "-f", "makefile.gcc",
                    ]
                    if self.settings.os == "Windows":
                        args.append("IS_MINGW=1")
                    autotools = AutoToolsBuildEnvironment(self)
                    autotools.make(args=args)

    def _patch_sources(self):
        if self.settings.compiler == "Visual Studio":
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "CPP", "Build.mak"),
                                  "-MT\r", "-" + str(self.settings.compiler.runtime))
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "CPP", "Build.mak"),
                                  "-MD\r", "-" + str(self.settings.compiler.runtime))
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "CPP", "Build.mak"),
                                  " -WX ", " ")

        # Patches for other build systems
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "C", "Util", "7z", "makefile.gcc"),
                              "CFLAGS = ",
                              "CFLAGS = -fpermissive ")
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "C", "Util", "7z", "makefile.gcc"),
                              ": 7zAlloc.c",
                              ": ../../7zAlloc.c")
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "C", "Util", "Lzma", "makefile.gcc"),
                              "CFLAGS = ",
                              "CFLAGS = -fpermissive ")
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "CPP", "Common", "MyString.h"),
                              "#ifdef _WIN32\r\n",
                              "#ifdef _WIN32\r\n#ifndef UNDER_CE\r\n#include <windows.h>\r\n#endif\r\n")

    def build(self):
        self._patch_sources()
        if self.settings.compiler == "Visual Studio":
            self._build_msvc()
        else:
            self._build_autotools()

    def package(self):
        self.copy("lzma.txt", src=self._source_subfolder, dst="licenses")
        self.copy("7zC.txt", src=self._source_subfolder, dst="licenses")
        if self.settings.compiler == "Visual Studio":
            for make_dir, exe in self._msvc_build_dirs:
                self.copy(exe, src=os.path.join(make_dir, self._msvc_cpu), dst="bin", keep_path=False)
        else:
            for make_dir, exe in self._autotools_build_dirs:
                self.copy(exe, src=os.path.join(make_dir), dst="bin", keep_path=False)

    def package_info(self):
        self.cpp_info.libdirs = []
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.path.append(bin_path)
