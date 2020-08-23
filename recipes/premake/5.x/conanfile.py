from conans import ConanFile, tools, AutoToolsBuildEnvironment, MSBuild
from conans.errors import ConanInvalidConfiguration
import os


class PremakeConan(ConanFile):
    name = "premake"
    topics = ("conan", "premake", "build", "build-systems")
    description = "Describe your software project just once, using Premake's simple and easy to read syntax, and build it everywhere"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://premake.github.io"
    license = "BSD-3-Clause"
    settings = "os", "arch", "compiler", "build_type"
    _source_subfolder = "source_subfolder"

    def configure(self):
        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            raise ConanInvalidConfiguration("Building with MinGW isn't supported currently by the recipe")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    @property
    def _platform(self):
        if self.version == "5.0.0-alpha14":
            return {"Windows": "vs2017",
                    "Linux": "gmake.unix",
                    "Macos": "gmake.macosx"}.get(str(self.settings.os))
        else:
            return {"Windows": "vs2017",
                    "Linux": "gmake2.unix",
                    "Macos": "gmake2.macosx"}.get(str(self.settings.os))

    def build(self):
        with tools.chdir(os.path.join(self._source_subfolder, "build", self._platform)):
            if self.settings.os == "Windows":
                msbuild = MSBuild(self)
                msbuild.build("Premake5.sln", platforms={"x86": "Win32", "x86_64": "x64"})
            elif self.settings.os == "Linux" or self.settings.os == "Macos":
                env_build = AutoToolsBuildEnvironment(self)
                env_build.make(args=["config=release"])

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*premake5.exe", dst="bin", keep_path=False)
        self.copy(pattern="*premake5", dst="bin", keep_path=False)


    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

    def package_id(self):
        del self.info.settings.compiler
