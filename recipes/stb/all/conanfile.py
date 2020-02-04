from conans import ConanFile, tools
import os

class StbConan(ConanFile):
    name = "stb"
    description = "single-file public domain libraries for C/C++"
    topics = ("conan", "stb", "single-file")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/nothings/stb"
    license = ("Public domain", "MIT")
    no_copy_source = True
    _source_subfolder = "source_subfolder"
    _commits = {
        "20200203": "0224a44a10564a214595797b4c88323f79a5f934",
    }

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self._commits[self.version]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy("*.h", src=self._source_subfolder, dst="include")
        tools.rmdir(os.path.join(self.package_folder, "include", "tests"))

    def package_info(self):
        self.info.header_only()
        self.cpp_info.defines.append('STB_TEXTEDIT_KEYTYPE=unsigned')
