from conans import ConanFile, tools, AutoToolsBuildEnvironment, MSBuild
from conan.errors import ConanInvalidConfiguration
import glob
import os
import re


class PremakeConan(ConanFile):
    name = "premake"
    topics = ("conan", "premake", "build", "build-systems")
    description = "Describe your software project just once, using Premake's simple and easy to read syntax, and build it everywhere"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://premake.github.io"
    license = "BSD-3-Clause"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "patches/**"
    options = {
        "lto": [True, False],
    }
    default_options = {
        "lto": False,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def config_options(self):
        if self.settings.os != "Windows" or self.settings.compiler == "Visual Studio":
            del self.options.lto

    def validate(self):
        if hasattr(self, 'settings_build') and tools.cross_building(self, skip_x64_x86=True):
            raise ConanInvalidConfiguration("Cross-building not implemented")

    @property
    def _msvc_version(self):
        return {
            "12": "2013",
            "14": "2015",
            "15": "2017",
            "16": "2019",
        }.get(str(self.settings.compiler.version), "2017")

    @property
    def _msvc_build_dirname(self):
        return "vs{}".format(self._msvc_version)

    def _version_info(self, version):
        res = []
        for p in re.split("[.-]|(alpha|beta)", version):
            if p is None:
                continue
            try:
                res.append(int(p))
                continue
            except ValueError:
                res.append(p)
        return tuple(res)

    @property
    def _gmake_directory_name_prefix(self):
        if self._version_info(self.version) <= self._version_info("5.0.0-alpha14"):
            return "gmake"
        else:
            return "gmake2"

    @property
    def _gmake_platform(self):
        return {
            "FreeBSD": "bsd",
            "Windows": "windows",
            "Linux": "unix",
            "Macos": "macosx",
        }[str(self.settings.os)]

    @property
    def _gmake_build_dirname(self):
        return "{}.{}".format(self._gmake_directory_name_prefix, self._gmake_platform)

    @property
    def _gmake_config(self):
        build_type = "debug" if self.settings.build_type == "Debug" else "release"
        if self.settings.os == "Windows":
            arch = {
                "x86": "x86",
                "x86_64": "x64",
            }[str(self.settings.arch)]
            config = "{}_{}".format(build_type, arch)
        else:
            config = build_type
        return config

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        if self.options.get_safe("lto", None) == False:
            for fn in glob.glob(os.path.join(self._source_subfolder, "build", self._gmake_build_dirname, "*.make")):
                tools.files.replace_in_file(self, fn, "-flto", "", strict=False)

    def build(self):
        self._patch_sources()
        if self.settings.compiler == "Visual Studio":
            with tools.files.chdir(self, os.path.join(self._source_subfolder, "build", self._msvc_build_dirname)):
                msbuild = MSBuild(self)
                msbuild.build("Premake5.sln", platforms={"x86": "Win32", "x86_64": "x64"})
        else:
            with tools.files.chdir(self, os.path.join(self._source_subfolder, "build", self._gmake_build_dirname)):
                env_build = AutoToolsBuildEnvironment(self)
                env_build.make(target="Premake5", args=["verbose=1", "config={}".format(self._gmake_config)])

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*premake5.exe", dst="bin", keep_path=False)
        self.copy(pattern="*premake5", dst="bin", keep_path=False)

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
