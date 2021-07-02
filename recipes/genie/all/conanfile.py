import os
from conans import AutoToolsBuildEnvironment, ConanFile, tools


required_conan_version = ">=1.33.0"


class GenieConan(ConanFile):
    name = "genie"
    license = "BSD-3-clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/bkaradzic/GENie"
    description = "Project generator tool"
    topics = ("conan", "genie", "project", "generator", "build", "build-systems")
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def build_requirements(self):
        if self.settings.compiler == "Visual Studio":
            self.build_requires("cccl/1.1")

        if self.settings.os == "Windows" and tools.os_info.is_windows:
            if "make" not in os.environ.get("CONAN_MAKE_PROGRAM", ""):
                self.build_requires("make/4.2.1")

            if "CONAN_BASH_PATH" not in os.environ and tools.os_info.detect_windows_subsystem() != 'msys2':
                self.build_requires("msys2/20200517")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    @property
    def _os(self):
        if tools.is_apple_os(self.settings.os):
            return "darwin"
        return {
            "Windows": "windows",
            "Linux": "linux",
            "FreeBSD": "bsd",
        }[str(self.settings.os)]

    def _patch_compiler(self, cc, cxx):
        tools.replace_in_file(os.path.join(self._source_subfolder, "build", "gmake.{}".format(self._os), "genie.make"), "CC  = gcc", "CC  = {}".format(cc))
        tools.replace_in_file(os.path.join(self._source_subfolder, "build", "gmake.{}".format(self._os), "genie.make"), "CXX = g++", "CXX = {}".format(cxx))

    @property
    def _genie_config(self):
        return "debug" if self.settings.build_type == "Debug" else "release"

    def build(self):
        if self.settings.compiler == "Visual Studio":
            self._patch_compiler("cccl", "cccl")
            with tools.vcvars(self.settings):
                with tools.chdir(self._source_subfolder):
                    self.run("make", win_bash=tools.os_info.is_windows)
        else:
            cc = tools.get_env("CC")
            cxx = tools.get_env("CXX")
            if tools.is_apple_os(self.settings.os):
                if not cc:
                    cc = "clang"
                if not cxx:
                    cxx = "clang"
            else:
                if not cc:
                    cc = "clang" if self.settings.compiler == "clang" else "gcc"
                if not cxx:
                    cxx = "clang++" if self.settings.compiler == "clang" else "g++"
            self._patch_compiler(cc, cxx)

            autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            with tools.chdir(self._source_subfolder):
                autotools.make(args=["OS={}".format(self._os), "config={}".format(self._genie_config)])

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        bin_ext = ".exe" if self.settings.os == "Windows" else ""
        self.copy("genie{}".format(bin_ext), dst="bin", src=os.path.join(self._source_subfolder, "bin", self._os))
        if self.settings.build_type == "Debug":
            self.copy("*.lua", dst="res", src=os.path.join(self._source_subfolder, "src"))

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        if self.settings.build_type == "Debug":
            resdir = os.path.join(self.package_folder, "res")
            self.output.info("Appending PREMAKE_PATH environment variable: {}".format(resdir))
            self.env_info.PREMAKE_PATH.append(resdir)
