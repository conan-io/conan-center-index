from conan import ConanFile
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import get, chdir, copy, replace_in_file, rm
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, NMakeToolchain
import os

required_conan_version = ">=1.55.0"


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
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if not is_msvc(self) and self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.build_requires("msys2/cci.latest")

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.build_type
        del self.info.settings.compiler

    def source(self):
        get(self, **self.conan_data["sources"][self.version])
        rm(self, "7zr.exe", self.source_folder)
        rm(self, "lzma.exe", self.source_folder)

    def generate(self):
        if is_msvc(self):
            tc = NMakeToolchain(self)
            tc.generate()
        else:
            env = VirtualBuildEnv(self)
            env.generate()            
            tc = AutotoolsToolchain(self)
            tc.generate()
            deps = AutotoolsDeps(self)
            deps.generate()

    @property
    def _msvc_build_dirs(self):
        return (
            (os.path.join(self.source_folder, "C", "Util", "7z"), "7zDec.exe"),
            (os.path.join(self.source_folder, "C", "Util", "Lzma"), "LZMAc.exe"),
            (os.path.join(self.source_folder, "CPP", "7zip", "UI", "Console"), "7z.exe"),
            (os.path.join(self.source_folder, "CPP", "7zip","Bundles", "Alone7z"), "7zr.exe"),
            (os.path.join(self.source_folder, "CPP", "7zip", "Bundles", "LzmaCon"), "lzma.exe"),
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
            (os.path.join(self.source_folder, "C", "Util", "7z"), f"7zDec{es}"),
            (os.path.join(self.source_folder, "CPP", "7zip", "Bundles", "LzmaCon"), f"lzma{es}"),
        )

    def _build_msvc(self):
        for make_dir, _ in self._msvc_build_dirs:
            self.run(f"nmake /f makefile NEW_COMPILER=1 CPU={self._msvc_cpu} NO_BUFFEROVERFLOWU=1", cwd=make_dir)

    def _build_autotools(self):
        autotools = Autotools(self)
        for make_dir, _ in self._autotools_build_dirs:
            with chdir(self, make_dir):
                args = [
                    "-f", "makefile.gcc",
                ]
                if self.settings.os == "Windows":
                    args.append("IS_MINGW=1")
                autotools.make(args=args)

    def _patch_sources(self):
        if is_msvc(self):
            replace_in_file(self, os.path.join(self.source_folder, "CPP", "Build.mak"),
                                  "-MT\r", "-" + str(self.settings.compiler.runtime))
            replace_in_file(self, os.path.join(self.source_folder, "CPP", "Build.mak"),
                                  "-MD\r", "-" + str(self.settings.compiler.runtime))
            replace_in_file(self, os.path.join(self.source_folder, "CPP", "Build.mak"),
                                  " -WX ", " ")

        # Patches for other build systems
        replace_in_file(self, os.path.join(self.source_folder, "C", "Util", "7z", "makefile.gcc"),
                              "CFLAGS = ",
                              "CFLAGS = -fpermissive ")
        replace_in_file(self, os.path.join(self.source_folder, "C", "Util", "7z", "makefile.gcc"),
                              ": 7zAlloc.c",
                              ": ../../7zAlloc.c")
        replace_in_file(self, os.path.join(self.source_folder, "C", "Util", "Lzma", "makefile.gcc"),
                              "CFLAGS = ",
                              "CFLAGS = -fpermissive ")
        replace_in_file(self, os.path.join(self.source_folder, "CPP", "Common", "MyString.h"),
                              "#ifdef _WIN32\r\n",
                              "#ifdef _WIN32\r\n#ifndef UNDER_CE\r\n#include <windows.h>\r\n#endif\r\n")

    def build(self):
        self._patch_sources()
        if is_msvc(self):
            self._build_msvc()
        else:
            self._build_autotools()

    def package(self):
        copy(self, "lzma.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "7zC.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        if is_msvc(self):
            for make_dir, exe in self._msvc_build_dirs:
                copy(self, exe, dst=os.path.join(self.package_folder, "bin"), src=os.path.join(make_dir, self._msvc_cpu), keep_path=False)
        else:
            for make_dir, exe in self._autotools_build_dirs:
                copy(self, exe, dst=os.path.join(self.package_folder, "bin"), src=os.path.join(make_dir), keep_path=False)

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.path.append(bin_path)
