from conans import ConanFile, tools
import os.path


class LyraConan(ConanFile):
    name = "lyra"
    homepage = "https://bfgroup.github.io/Lyra/"
    description = "A simple to use, composing, header only, command line arguments parser for C++ 11 and beyond."
    topics = ("conan", "cli", "c++11")
    author = "Build Frameworks Group"
    no_copy_source = True

    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "Lyra-" + \
            os.path.basename(self.conan_data["sources"][self.version]['url']).replace(
                ".tar.gz", "")
        os.rename(extracted_dir, "source")

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src="source")
        self.copy("*.h*", dst="include", src=os.path.join("source", "include"))

    def package_id(self):
        self.info.header_only()
