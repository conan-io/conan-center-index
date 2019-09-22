from conans import ConanFile, tools
import os.path


class LyraConan(ConanFile):
    name = "Lyra"
    homepage = "https://bfgroup.github.io/Lyra/"
    description = "A simple to use, composing, header only, command line arguments parser for C++ 11 and beyond."
    topics = ("conan", "cli", "c++11")
    author = "Build Frameworks Group"

    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    settings = "os", "compiler", "arch", "build_type"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + \
            os.path.basename(self.conan_data["sources"][self.version]['url']).replace(
                ".tar.gz", "")
        os.rename(extracted_dir, "source")

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src="source")
        self.copy("*.h*", dst="include", src=os.path.join("source", "include"))

    def package_id(self):
        self.info.header_only()
