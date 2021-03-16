from conans import ConanFile, tools
import os
import glob


class MiniaudioConan(ConanFile):
    name = "miniaudio"
    description = "A single file audio playback and capture library."
    topics = ("conan", "miniaudio", "header-only", "sound")
    homepage = "https://github.com/mackron/miniaudio"
    url = "https://github.com/conan-io/conan-center-index"
    license = "Unlicense"
    settings = "os", "compiler", "build_type", "arch"

    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob(self.name + "-*/")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="miniaudio.h", dst="include", src=self._source_subfolder)

    def package_info(self):
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("dl")

    def package_id(self):
        self.info.header_only()
