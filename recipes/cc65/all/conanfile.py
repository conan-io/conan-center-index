import os
from conans import AutoToolsBuildEnvironment, ConanFile, MSBuild, tools


class Cc65Conan(ConanFile):
    name = "cc65"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://cc65.github.io/"
    description = "A freeware C compiler for 6502 based systems"
    license = "zlib"
    topics = ("conan", "cc65", "compiler", "cmos", "6502", "8bit", "apple", "commodore")

    settings = "os_build", "arch_build", "compiler", "arch"

    _autotools = None
    _source_subfolder = "source_subfolder"

    def configure(self):
        # FIXME: MSBuild does not respect arch_build
        self.settings.arch = self.settings.arch_build
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        # if self.settings.compiler not in ("gcc", "clang", ):
        #     raise ConanInvalidConfiguration("Only gcc and clang are supported")

    def build_requirements(self):
        if self.settings.compiler == "Visual Studio":
            self.build_requires("make/4.2.1")
        elif tools.os_info.is_windows:
            self.build_requires("msys2/20190524")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        return self._autotools

    @property
    def _datadir(self):
        return os.path.join(self.package_folder, "bin", "share", "cc65")

    @property
    def _samplesdir(self):
        return os.path.join(self.package_folder, "samples")

    @property
    def _make_args(self):
        datadir = self._datadir
        prefix = self.package_folder
        samplesdir = self._samplesdir
        if tools.os_info.is_windows:
            datadir = tools.unix_path(datadir)
            prefix = tools.unix_path(prefix)
            samplesdir = tools.unix_path(samplesdir)
        return [
            "PREFIX={}".format(prefix),
            "datadir={}".format(datadir),
            "samplesdir={}".format(samplesdir),
        ]

    def _build_msvc(self):
        msbuild = MSBuild(self)
        msvc_platforms = {
            "x86": "Win32",
        }
        msbuild.build(os.path.join(self._source_subfolder, "src", "cc65.sln"),
                      build_type="Release", platforms=msvc_platforms, arch=self.settings.arch_build)
        with tools.chdir(os.path.join(self._source_subfolder, "libsrc")):
            self.run("{}".format(os.environ["CONAN_MAKE_PROGRAM"]))

    def _build_autotools(self):
        autotools = self._configure_autotools()
        with tools.chdir(os.path.join(self._source_subfolder)):
            autotools.make(args=self._make_args)

    def build(self):
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
        del self.info.settings.arch

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: %s" % bindir)
        self.env_info.PATH.append(bindir)

        self.output.info("Seting CC65_HOME environment variable: %s" % self._datadir)
        self.env_info.CC65_HOME = self._datadir

        cc65_cc = os.path.join(bindir, "cc65")
        if self.settings.os_build == "Windows":
            cc65_cc += ".exe"
        self.output.info("Seting CC65 environment variable: %s" % cc65_cc)
        self.env_info.CC65 = cc65_cc

        cc65_as = os.path.join(bindir, "ca65")
        if self.settings.os_build == "Windows":
            cc65_as += ".exe"
        self.output.info("Seting AS65 environment variable: %s" % cc65_as)
        self.env_info.AS65 = cc65_as

        cc65_ld = os.path.join(bindir, "cl65")
        if self.settings.os_build == "Windows":
            cc65_ld += ".exe"
        self.output.info("Seting LD65 environment variable: %s" % cc65_ld)
        self.env_info.LD65 = cc65_ld
