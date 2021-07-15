from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os
import fnmatch

required_conan_version = ">=1.33.0"


class FDKAACConan(ConanFile):
    name = "libfdk_aac"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A standalone library of the Fraunhofer FDK AAC code from Android"
    license = "https://github.com/mstorsjo/fdk-aac/blob/master/NOTICE"
    settings = "os", "arch", "compiler", "build_type"
    homepage = "https://sourceforge.net/projects/opencore-amr/"
    topics = ("conan", "libfdk_aac", "multimedia", "audio", "fraunhofer", "aac", "decoder", "encoding", "decoding")
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def build_requirements(self):
        if self.settings.compiler != "Visual Studio":
            self.build_requires("libtool/2.4.6")
            if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _build_vs(self):
        with tools.chdir(self._source_subfolder):
            with tools.vcvars(self.settings, force=True):
                with tools.remove_from_path("mkdir"):
                    tools.replace_in_file("Makefile.vc",
                                          "CFLAGS   = /nologo /W3 /Ox /MT",
                                          "CFLAGS   = /nologo /W3 /Ox /%s" % str(self.settings.compiler.runtime))
                    tools.replace_in_file("Makefile.vc",
                                          "MKDIR_FLAGS = -p",
                                          "MKDIR_FLAGS =")
                    self.run("nmake -f Makefile.vc")
                    self.run("nmake -f Makefile.vc prefix=\"%s\" install" % os.path.abspath(self.package_folder))

    def _build_autotools(self):
        with tools.chdir(self._source_subfolder):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows)
            if self.settings.os == "Android" and tools.os_info.is_windows:
                # remove escape for quotation marks, to make ndk on windows happy
                tools.replace_in_file("configure",
                    "s/[	 `~#$^&*(){}\\\\|;'\\\''\"<>?]/\\\\&/g", "s/[	 `~#$^&*(){}\\\\|;<>?]/\\\\&/g")
        autotools = self._configure_autotools()
        autotools.make()

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        args = []
        if self.options.shared:
            args.extend(["--disable-static", "--enable-shared"])
        else:
            args.extend(["--disable-shared", "--enable-static"])
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        if self.settings.compiler == "Visual Studio":
            self._build_vs()
        else:
            self._build_autotools()

    def package(self):
        self.copy(pattern="NOTICE", src=self._source_subfolder, dst="licenses")
        if self.settings.compiler == "Visual Studio":
            if self.options.shared:
                exts = ["fdk-aac.lib"]
            else:
                exts = ["fdk-aac.dll.lib", "fdk-aac-1.dll"]
            for root, _, filenames in os.walk(self.package_folder):
                for ext in exts:
                    for filename in fnmatch.filter(filenames, ext):
                        os.unlink(os.path.join(root, filename))
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            self.cpp_info.libs = ["fdk-aac.dll.lib"]
        else:
            self.cpp_info.libs = ["fdk-aac"]
        if self.settings.os == "Linux" or self.settings.os == "Android":
            self.cpp_info.system_libs.append("m")
        self.cpp_info.names["pkg_config"] = "fdk-aac"
