import os

from conan import ConanFile, tools


class Djinni(ConanFile):
    name = "djinni-generator"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://djinni.xlcpp.dev"
    description = "Djinni is a tool for generating cross-language type declarations and interface bindings."
    topics = ("java", "Objective-C", "ios", "Android")
    license = "Apache-2.0"
    settings = "os", "arch"


    def source(self):
        filename = os.path.basename(self.conan_data["sources"][self.version]["url"])
        tools.files.download(self, filename=filename, **self.conan_data["sources"][self.version])
        tools.files.download(self, filename="LICENSE", url="https://raw.githubusercontent.com/cross-language-cpp/djinni-generator/main/LICENSE")

    def build(self):
        pass # avoid warning for missing build steps

    def package(self):
        if tools.detected_os() == "Windows":
            os.rename('djinni','djinni.bat')
            self.copy("djinni.bat", dst="bin", keep_path=False)
        else:
            self.copy("djinni", dst="bin", keep_path=False)
            executable = os.path.join(self.package_folder, "bin", "djinni")
            os.chmod(executable, os.stat(executable).st_mode | 0o111)
        self.copy("LICENSE", dst="licenses", keep_path=False)

    def package_info(self):
        self.cpp_info.includedirs = []
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))

