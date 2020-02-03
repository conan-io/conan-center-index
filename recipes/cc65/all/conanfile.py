from conans import AutoToolsBuildEnvironment, ConanFile, MSBuild, tools
from conans.client.tools.win import msvs_toolset
from conans.errors import ConanInvalidConfiguration
from contextlib import contextmanager
import os


class Cc65Conan(ConanFile):
    name = "cc65"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://cc65.github.io/"
    description = "A freeware C compiler for 6502 based systems"
    license = "zlib"
    topics = ("conan", "cc65", "compiler", "cmos", "6502", "8bit")
    exports_sources = "patches/**"

    settings = "os_build", "arch_build", "compiler"

    _autotools = None
    _source_subfolder = "source_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.compiler == "Visual Studio":
            if self.settings.arch_build not in ("x86", "x86_64"):
                raise ConanInvalidConfiguration("Invalid arch_build")

    def build_requirements(self):
        if tools.os_info.is_windows and "CONAN_BASH_PATH" not in os.environ \
                and tools.os_info.detect_windows_subsystem() != "msys2":
            # msys2 provides make for MSVC and mingw + install for mingw
            self.build_requires("msys2/20190524")

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

    @contextmanager
    def _mock_settings(self):
        """
        This will temporarily copy the attributes arch_build and os_build of settings to arch and os.
        Because cc65 does not provide x86_64 support for visual studio, x86 is built instead.
        """
        mock_settings = self.settings.copy()

        if self.settings.compiler == "Visual Studio":
            if self.settings.arch_build == "x86_64":
                self.output.info("x86_64 detected: building x86 instead")
                mock_settings.arch_build = "x86"

        mock_settings._data["arch"] = mock_settings._data["arch_build"].copy()
        mock_settings._data["os"] = mock_settings._data["os_build"].copy()

        original_settings = self.settings
        self.settings = mock_settings
        yield
        self.settings = original_settings

    def _build_msvc(self):
        msbuild = MSBuild(self)
        msvc_platforms = {
            "x86": "Win32",
        }
        msbuild.build(os.path.join(self._source_subfolder, "src", "cc65.sln"),
                      build_type="Release", platforms=msvc_platforms, arch=self.settings.arch_build)
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
        return [
            "PREFIX={}".format(prefix),
            "datadir={}".format(datadir),
            "samplesdir={}".format(samplesdir),
        ]

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
                    tools.replace_in_file(fn, "v141", msvs_toolset(self.settings))
                    tools.replace_in_file(fn, "<WindowsTargetPlatformVersion>10.0.16299.0</WindowsTargetPlatformVersion>", "")

    def build(self):
        self._patch_sources()
        with self._mock_settings():
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
        self.info.include_build_settings()
        if self.settings.compiler == "Visual Studio":
            if self.settings.arch_build == "x86_64":
                self.info.settings.arch_build = "x86"
        del self.info.settings.compiler

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: %s" % bindir)
        self.env_info.PATH.append(bindir)

        self.output.info("Seting CC65_HOME environment variable: %s" % self._datadir)
        self.env_info.CC65_HOME = self._datadir

        bin_ext = ".exe" if self.settings.os_build == "Windows" else ""

        cc65_cc = os.path.join(bindir, "cc65" + bin_ext)
        self.output.info("Seting CC65 environment variable: %s" % cc65_cc)
        self.env_info.CC65 = cc65_cc

        cc65_as = os.path.join(bindir, "ca65" + bin_ext)
        self.output.info("Seting AS65 environment variable: %s" % cc65_as)
        self.env_info.AS65 = cc65_as

        cc65_ld = os.path.join(bindir, "cl65" + bin_ext)
        self.output.info("Seting LD65 environment variable: %s" % cc65_ld)
        self.env_info.LD65 = cc65_ld
