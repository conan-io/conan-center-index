import os
from conans import ConanFile, MSBuild, AutoToolsBuildEnvironment, tools


class NativefiledialogConan(ConanFile):
    name = "nativefiledialog"
    license = "ZLIB"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mlabbe/nativefiledialog"
    description = "A tiny, neat C library that portably invokes native file open and save dialogs."
    topics = ("conan", "dialog", "gui")
    settings = "os", "compiler", "build_type", "arch"
    
    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        if self.settings.os == "Linux":
            self.requires("gtk/system")

    def build_requirements(self):
        self.build_requires("premake/5.0.0-alpha15")

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-release_" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        if self.settings.compiler == "Visual Studio":
            generator = "vs" + {"16": "2019",
                                "15": "2017",
                                "14": "2015",
                                "12": "2013",
                                "11": "2012",
                                "10": "2010",
                                "9": "2008",
                                "8": "2005"}.get(str(self.settings.compiler.version))
        else:
            generator = "gmake2"
        subdir = os.path.join(self._source_subfolder, "build", "subdir")
        os.makedirs(subdir)
        with tools.chdir(subdir):
            os.rename(os.path.join("..", "premake5.lua"), "premake5.lua")
            self.run("premake5 %s" % generator)
            
            if self.settings.compiler == "Visual Studio":
                msbuild = MSBuild(self)
                msbuild.build("NativeFileDialog.sln")
            else:
                config = "debug" if self.settings.build_type == "Debug" else "release"
                env_build = AutoToolsBuildEnvironment(self)
                env_build.make(args=["config=%s" % config])

    def package(self):
        if self.settings.compiler == "Visual Studio":
            self.copy("*nfd.lib", dst="lib", src=self._source_subfolder, keep_path=False)
        else:
            self.copy("*nfd.a", dst="lib", src=self._source_subfolder, keep_path=False)
        self.copy("*nfd.h", dst="include", src=self._source_subfolder, keep_path=False)
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = ["nfd"]
