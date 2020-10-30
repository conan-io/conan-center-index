import os
from conans import ConanFile, CMake, AutoToolsBuildEnvironment, tools
from conans.tools import os_info, SystemPackageTool, download, untargz, replace_in_file, unzip

class ConanRecipe(ConanFile):
    name = "portaudio"
    version = "v190600.2020-10-29"
    settings = "os", "compiler", "build_type", "arch"
    generators = ["cmake", "txt"]
    description = "Conan package for the Portaudio library"
    homepage = "http://www.portaudio.com"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("audio")
    license = "http://www.portaudio.com/license.html"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    commit = "88c71a6ec478ed693adf86d1ff08134273c1e5e7"
    portaudio_folder = "source"

    def configure(self):
        del self.settings.compiler.libcxx
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tarball = self.conan_data["sources"][self.version]
        tools.get(tarball['url'], destination=".")
        tools.rename("portaudio-{}".format(self.commit), "source")

    def build(self):
        cmake = CMake(self)
        if self.settings.os == "Windows":
            cmake.definitions["MSVS"] = self.settings.compiler == "Visual Studio"

        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            cmake.definitions["PA_USE_WDMKS"] = "OFF"
            cmake.definitions["PA_USE_WDMKS_DEVICE_INFO"] = "OFF"
            cmake.definitions["PA_USE_WASAPI"] = "OFF"

        if self.options.shared:
            cmake.definitions["PA_BUILD_SHARED"] = "ON"
            cmake.definitions["PA_BUILD_STATIC"] = "OFF"
        else:
            cmake.definitions["PA_BUILD_SHARED"] = "OFF"
            cmake.definitions["PA_BUILD_STATIC"] = "ON"

        if self.settings.os == "Linux":
            cmake.definitions["PA_USE_ALSA"] = "ON"
            cmake.definitions["PA_USE_JACK"] = "ON"

        cmake.configure(source_folder=self.portaudio_folder)
        cmake.build()

    def package(self):
        self.copy("*.h", dst="include", src=os.path.join(self.portaudio_folder, "include"))
        self.copy(pattern="LICENSE*", dst="licenses", src=self.portaudio_folder,  ignore_case=True, keep_path=False)

        if self.settings.os == "Windows":
            if self.settings.compiler == "Visual Studio":
                self.copy(pattern="*.lib", dst="lib", keep_path=False)
                if self.options.shared:
                    self.copy(pattern="*.dll", dst="bin", keep_path=False)
                self.copy(pattern="*.pdb", dst="bin", keep_path=False)
            else:
                if self.options.shared:
                    self.copy(pattern="*.dll.a", dst="lib", keep_path=False)
                    self.copy(pattern="*.dll", dst="bin", keep_path=False)
                else:
                    self.copy(pattern="*static.a", dst="lib", keep_path=False)

        else:
            if self.options.shared:
                if self.settings.os == "Macos":
                    self.copy(pattern="*.dylib", dst="lib", keep_path=False)
                else:
                    self.copy(pattern="*.so*", dst="lib", keep_path=False)
            else:
                self.copy("*.a", dst="lib", keep_path=False)


    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if self.settings.os == "Macos":
            self.cpp_info.frameworks = ["CoreAudio", "AudioToolbox", "AudioUnit", "CoreServices", "Carbon"]

        if self.settings.os == "Windows" and self.settings.compiler == "gcc" and not self.options.shared:
            self.cpp_info.system_libs = ['winmm']

        if self.settings.os == "Linux" and not self.options.shared:
            self.cpp_info.system_libs = ['jack', "asound", "m", "pthread"]

