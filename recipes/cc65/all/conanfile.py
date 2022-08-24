from conans import AutoToolsBuildEnvironment, ConanFile, MSBuild, tools
from conan.errors import ConanInvalidConfiguration
import os


class Cc65Conan(ConanFile):
    name = "cc65"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://cc65.github.io/"
    description = "A freeware C compiler for 6502 based systems"
    license = "Zlib"
    topics = ("conan", "cc65", "compiler", "cmos", "6502", "8bit")
    exports_sources = "patches/**"

    settings = "os", "arch", "compiler", "build_type"

    _autotools = None
    _source_subfolder = "source_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.compiler == "Visual Studio":
            if self.settings.arch not in ("x86", "x86_64"):
                raise ConanInvalidConfiguration("Invalid arch")
            if self.settings.arch == "x86_64":
                self.output.info("This recipe will build x86 instead of x86_64 (the binaries are compatible)")

    def build_requirements(self):
        if self.settings.compiler == "Visual Studio" and not tools.which("make"):
            self.build_requires("make/4.2.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    @property
    def _datadir(self):
        return os.path.join(self.package_folder, "bin", "share", "cc65")

    @property
    def _samplesdir(self):
        return os.path.join(self.package_folder, "samples")

    def _build_msvc(self):
        msbuild = MSBuild(self)
        msvc_platforms = {
            "x86": "Win32",
        }
        arch = str(self.settings.arch)
        if arch != "x86":
            self.output.warn("{} detected: building x86 instead".format(self.settings.arch))
            arch = "x86"

        msbuild.build(os.path.join(self._source_subfolder, "src", "cc65.sln"),
                      build_type="Debug" if self.settings.build_type == "Debug" else "Release",
                      arch=arch, platforms=msvc_platforms)
        autotools = self._configure_autotools()
        with tools.chdir(os.path.join(self._source_subfolder, "libsrc")):
            autotools.make()

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        return self._autotools

    @property
    def _make_args(self):
        datadir = self._datadir
        prefix = self.package_folder
        samplesdir = self._samplesdir
        if tools.os_info.is_windows:
            datadir = tools.unix_path(datadir)
            prefix = tools.unix_path(prefix)
            samplesdir = tools.unix_path(samplesdir)
        args = [
            "PREFIX={}".format(prefix),
            "datadir={}".format(datadir),
            "samplesdir={}".format(samplesdir),
        ]
        if self.settings.os == "Windows":
            args.append("EXE_SUFFIX=.exe")
        return args

    def _build_autotools(self):
        autotools = self._configure_autotools()
        with tools.chdir(os.path.join(self._source_subfolder)):
            autotools.make(args=self._make_args)

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        if self.settings.compiler == "Visual Studio":
            with tools.chdir(os.path.join(self._source_subfolder, "src")):
                for fn in os.listdir("."):
                    if not fn.endswith(".vcxproj"):
                        continue
                    tools.replace_in_file(fn, "v141", tools.msvs_toolset(self))
                    tools.replace_in_file(fn, "<WindowsTargetPlatformVersion>10.0.16299.0</WindowsTargetPlatformVersion>", "")
        if self.settings.os == "Windows":
            # Add ".exe" suffix to calls from cl65 to other utilities
            for fn, var in (("cc65", "CC65"), ("ca65", "CA65"), ("co65", "CO65"), ("ld65", "LD65"), ("grc65", "GRC")):
                v = "{},".format(var).ljust(5)
                tools.replace_in_file(os.path.join(self._source_subfolder, "src", "cl65", "main.c"),
                                      "CmdInit (&{v} CmdPath, \"{n}\");".format(v=v, n=fn),
                                      "CmdInit (&{v} CmdPath, \"{n}.exe\");".format(v=v, n=fn))

    def build(self):
        self._patch_sources()
        if self.settings.compiler == "Visual Studio":
            self._build_msvc()
        else:
            self._build_autotools()

    def _package_msvc(self):
        self.copy("*.exe", src=os.path.join(self._source_subfolder, "bin"), dst=os.path.join(self.package_folder, "bin"), keep_path=False)
        for dir in ("asminc", "cfg", "include", "lib", "target"):
            self.copy("*", src=os.path.join(self._source_subfolder, dir), dst=os.path.join(self._datadir, dir))

    def _package_autotools(self):
        autotools = self._configure_autotools()
        with tools.chdir(os.path.join(self.build_folder, self._source_subfolder)):
            autotools.install(args=self._make_args)

        tools.rmdir(self._samplesdir)
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        if self.settings.compiler == "Visual Studio":
            self._package_msvc()
        else:
            self._package_autotools()

    def package_id(self):
        del self.info.settings.compiler
        if self.settings.compiler == "Visual Studio":
            if self.settings.arch == "x86_64":
                self.info.settings.arch = "x86"

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: %s" % bindir)
        self.env_info.PATH.append(bindir)

        self.output.info("Seting CC65_HOME environment variable: %s" % self._datadir)
        self.env_info.CC65_HOME = self._datadir

        bin_ext = ".exe" if self.settings.os == "Windows" else ""

        cc65_cc = os.path.join(bindir, "cc65" + bin_ext)
        self.output.info("Seting CC65 environment variable: {}".format(cc65_cc))
        self.env_info.CC65 = cc65_cc

        cc65_as = os.path.join(bindir, "ca65" + bin_ext)
        self.output.info("Seting AS65 environment variable: {}".format(cc65_as))
        self.env_info.AS65 = cc65_as

        cc65_ld = os.path.join(bindir, "cl65" + bin_ext)
        self.output.info("Seting LD65 environment variable: {}".format(cc65_ld))
        self.env_info.LD65 = cc65_ld
