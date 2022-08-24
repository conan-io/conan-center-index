from conan.tools.files import rename
from conan.tools.microsoft import is_msvc
from conans import ConanFile, AutoToolsBuildEnvironment, MSBuild, tools
from conan.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.45.0"


class ZimgConan(ConanFile):
    name = "zimg"
    description = "Scaling, colorspace conversion, and dithering library"
    topics = ("zimg", "image", "manipulation")
    homepage = "https://github.com/sekrit-twc/zimg"
    url = "https://github.com/conan-io/conan-center-index"
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

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.build_type not in ("Release", "Debug"):
            raise ConanInvalidConfiguration("zimg does not support the build type '{}'.".format(self.settings.build_type))
        if self.settings.compiler == "Visual Studio" and tools.Version(self.settings.compiler.version) < "15":
            raise ConanInvalidConfiguration("zimg requires at least Visual Studio 15 2017")

    def build_requirements(self):
        if not is_msvc(self):
            self.build_requires("libtool/2.4.6")
            if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_autools(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        yes_no = lambda v: "yes" if v else "no"
        conf_args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return autotools

    def _build_autotools(self):
        with tools.chdir(self._source_subfolder):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows)
            # relocatable shared lib on macOS
            tools.replace_in_file("configure", "-install_name \\$rpath/", "-install_name @rpath/")
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
        msbuild = MSBuild(self)
        msbuild.build(os.path.join(self._source_subfolder, "_msvc", "zimg.sln"),
                      targets=["dll" if self.options.shared else "zimg"],
                      platforms=self._sln_platforms)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

        if is_msvc(self):
            self._build_msvc()
        else:
            self._build_autotools()

    def _package_autotools(self):
        autotools = self._configure_autools()
        autotools.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
        tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.la")

    def _package_msvc(self):
        self.copy("zimg.h", src=os.path.join(self._source_subfolder, "src", "zimg", "api"), dst="include")
        self.copy("zimg++.hpp", src=os.path.join(self._source_subfolder, "src", "zimg", "api"), dst="include")

        sln_dir = os.path.join(self._source_subfolder, "_msvc", self._sln_platforms[str(self.settings.arch)], str(self.settings.build_type))
        if self.options.shared:
            self.copy("z_imp.lib", src=sln_dir, dst="lib")
            self.copy("z.dll", src=sln_dir, dst="bin")
            rename(self, os.path.join(self.package_folder, "lib", "z_imp.lib"),
                         os.path.join(self.package_folder, "lib", "zimg.lib"))
        else:
            self.copy("z.lib", src=sln_dir, dst="lib")
            rename(self, os.path.join(self.package_folder, "lib", "z.lib"),
                         os.path.join(self.package_folder, "lib", "zimg.lib"))

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        if is_msvc(self):
            self._package_msvc()
        else:
            self._package_autotools()

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "zimg")
        self.cpp_info.libs = ["zimg"]
        if not self.options.shared:
            if self.settings.os in ("FreeBSD", "Linux"):
                self.cpp_info.system_libs = ["m"]
            stdcpp = tools.stdcpp_library(self)
            if stdcpp:
                self.cpp_info.system_libs.append(stdcpp)
