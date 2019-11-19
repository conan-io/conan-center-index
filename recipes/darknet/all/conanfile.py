import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment


class DarknetConan(ConanFile):
    name = "darknet"
    license = "YOLO"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://pjreddie.com/darknet/"
    description = "Darknet is a neural network frameworks written in C"
    topics = ("darknet", "neural network", "deep learning")
    settings = "os", "compiler", "build_type", "arch", "arch_build"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "OpenCV": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "OpenCV": False,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _commit(self):
        url = self.conan_data["sources"][self.version]["url"]
        return url[url.rfind("/")+1:url.rfind(".")]

    def _activate_makefile(self, option):
        makefileName = option.upper()
        with tools.chdir(self._source_subfolder):
            if getattr(self.options, option) == True:
                tools.replace_in_file('Makefile', makefileName + '=0', makefileName + '=1')

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.OpenCV:
            self.requires("opencv/3.4.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = self.name + "-" + self._commit
        os.rename(extracted_folder, self._source_subfolder)

    def build(self):
        self._activate_makefile("OpenCV")
        with tools.chdir(self._source_subfolder):
            tools.replace_in_file('Makefile', "CFLAGS=", "CFLAGS+=${CPPFLAGS} ")
            tools.replace_in_file('Makefile', "LDFLAGS=", "LDFLAGS+=${LIBS} ")
            env_build = AutoToolsBuildEnvironment(self)
            env_build.make()

    def package(self):
        self.copy("LICENSE*", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))
        if self.options.shared:
            self.copy("*.dll", dst="bin", keep_path=False)
            self.copy("*.so", dst="lib", keep_path=False)
            self.copy("*.dylib", dst="lib", keep_path=False)
        else:
            self.copy("*.a", dst="lib", keep_path=False)
            self.copy("*.lib", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["darknet"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m", "pthread"]
