from conans import ConanFile, AutoToolsBuildEnvironment, MSBuild, tools
from conans.errors import ConanInvalidConfiguration
import glob
import os


class ZimgConan(ConanFile):
    name = "zimg"
    description = "Scaling, colorspace conversion, and dithering library"
    topics = ("conan", "zimg", "image", "manipulation")
    homepage = "https://github.com/sekrit-twc/zimg"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "WTFPL"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

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
        if not self.settings.build_type:
            self.settings.build_type = "Release"
        if self.settings.build_type not in ("Release", "Debug"):
            raise ConanInvalidConfiguration("Invalid build_type")

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")
        if self.settings.compiler != "Visual Studio":
            if tools.os_info.is_windows and  "CONAN_BASH_PATH" not in os.environ:
                self.build_requires("msys2/20190524")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("zimg-release-{}".format(self.version), self._source_subfolder)

    def _configure_autools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        conf_args = []
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--disable-shared", "--enable-static"])
        self._autotools.configure(configure_dir=self._source_subfolder, args=conf_args)
        return self._autotools

    def _build_autotools(self):
        with tools.chdir(self._source_subfolder):
            self.run("autoreconf -fiv", win_bash=tools.os_info.is_windows)
            # self.run("autoreconf --verbose --install --force", win_bash=tools.os_info.is_windows)
        autotools = self._configure_autools()
        autotools.make()

    _sln_platforms = {
        "x86": "Win32",
        "x86_64": "x64",
        "armv6": "ARM",
        "armv7": "ARM",
        "armv7hf": "ARM",
        "armv7s": "ARM",
        "armv7k": "ARM",
        "armv8_32": "ARM",
        "armv8": "ARM64",
        "armv8.3": "ARM64",
    }

    def _build_msvc(self):
        for root, _, files in os.walk(os.path.join(self._source_subfolder, "_msvc")):
            for file in files:
                if os.path.splitext(file) != ".vcxproj":
                    continue
                f = os.path.join(root, file)
                tools.replace_in_file(f, "<WindowsTargetPlatformVersion>10.0</WindowsTargetPlatformVersion>", "")

        msbuild = MSBuild(self)
        msbuild.build(os.path.join(self._source_subfolder, "_msvc", "zimg.sln"),
                      targets=["dll" if self.options.shared else "zimg"],
                      platforms=self._sln_platforms)

    def build(self):
        if self.settings.compiler == "Visual Studio":
            self._build_msvc()
        else:
            self._build_autotools()

    def _package_autotools(self):
        autotools = self._configure_autools()
        autotools.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

        with tools.chdir(os.path.join(self.package_folder, "lib")):
            for filename in glob.glob("*.la"):
                os.unlink(filename)

    def _package_msvc(self):
        self.copy("zimg.h", src=os.path.join(self._source_subfolder, "src", "zimg", "api"), dst="include")
        self.copy("zimg++.hpp", src=os.path.join(self._source_subfolder, "src", "zimg", "api"), dst="include")

        sln_dir = os.path.join(self._source_subfolder, "_msvc", self._sln_platforms[str(self.settings.arch)], str(self.settings.build_type))
        if self.options.shared:
            os.unlink(os.path.join(sln_dir, "z.lib"))

        self.copy("*.lib", src=sln_dir, dst="lib")
        self.copy("*.dll", src=sln_dir, dst="bin")

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        if self.settings.compiler == "Visual Studio":
            self._package_msvc()
        else:
            self._package_autotools()

    def package_info(self):
        self.cpp_info.libs = ["zimg"]
