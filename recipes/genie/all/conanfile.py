import os, glob
from conans import ConanFile, tools


class GenieConan(ConanFile):
    name = "genie"
    license = "BSD-3-clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/bkaradzic/GENie"
    description = "Project generator tool"
    topics = ("conan", "genie", "project", "generator", "build")
    settings = "os", "arch", "compiler"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def build_requirements(self):
        if self.settings.compiler == "Visual Studio":
            self.build_requires("cccl/1.1")

        if self.settings.os == "Windows" and tools.os_info.is_windows:
            if "make" not in os.environ.get("CONAN_MAKE_PROGRAM", ""): # or not tools.which("make"):
                self.build_requires("make/4.2.1")

            if "CONAN_BASH_PATH" not in os.environ and tools.os_info.detect_windows_subsystem() != 'msys2':
                self.build_requires("msys2/20200517")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("GENie-*")[0]
        os.rename(extracted_dir, self._source_subfolder)

    @property
    def _os(self):
        return {
            "Windows": "windows",
            "Linux": "linux",
            "Macos": "darwin",
            "FreeBSD": "freebsd",
        }[str(self.settings.os)]

    def _patch_compiler(self, cc, cxx):
        tools.replace_in_file(os.path.join(self._source_subfolder, "build", "gmake.{}".format(self._os), "genie.make"), "CC  = gcc", "CC  = {}".format(cc))
        tools.replace_in_file(os.path.join(self._source_subfolder, "build", "gmake.{}".format(self._os), "genie.make"), "CXX = g++", "CXX = {}".format(cxx))

    def build(self):
        if self.settings.compiler == "Visual Studio":
            self._patch_compiler(self, "cccl", "cccl")
            with tools.vcvars(self.settings):
                with tools.chdir(self._source_subfolder):
                    self.run("make", win_bash=tools.os_info.is_windows)
        else:
            self._patch_compiler(self, tools.get_env("CC"), tools.get_env("CXX"))
            with tools.chdir(self._source_subfolder):
                self.run("make", win_bash=tools.os_info.is_windows)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        bin_ext = ".exe" if self.settings.os == "Windows" else ""
        self.copy("genie{}".format(bin_ext), dst="bin", src=os.path.join(self._source_subfolder, "bin", self._os))

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
