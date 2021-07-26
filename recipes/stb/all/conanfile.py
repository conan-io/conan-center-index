from conans import ConanFile, tools
import os

class StbConan(ConanFile):
    name = "stb"
    description = "single-file public domain libraries for C/C++"
    topics = ("conan", "stb", "single-file")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/nothings/stb"
    license = ("Unlicense", "MIT")
    no_copy_source = True
    _source_subfolder = "source_subfolder"

    def source(self):
        commit = os.path.splitext(os.path.basename(self.conan_data["sources"][self.version]["url"]))[0]
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + commit
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy("*.h", src=self._source_subfolder, dst="include")
        self.copy("stb_vorbis.c", src=self._source_subfolder, dst="include")
        tools.rmdir(os.path.join(self.package_folder, "include", "tests"))

    def package_id(self):
        self.info.header_only()
    
    def package_info(self):
        self.cpp_info.defines.append('STB_TEXTEDIT_KEYTYPE=unsigned')
