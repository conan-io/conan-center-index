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
        self.copy(
            pattern="miniaudio.h", dst="include/miniaudio", src=self._source_subfolder
        )
        self.copy(
            pattern="stb_vorbis.c",
            dst="include/miniaudio/extras",
            src=os.path.join(self._source_subfolder, "extras"),
        )
        self.copy(
            pattern="README.md",
            dst="licenses",
            src=os.path.join(self._source_subfolder, "extras/speex_resampler/"),
        )
        self.copy(
            pattern="ma_speex_resampler.h",
            dst="include/miniaudio/extras/speex_resampler/",
            src=os.path.join(self._source_subfolder, "extras/speex_resampler/"),
        )
        self.copy(
            pattern="*.*",
            dst="include/miniaudio/extras/speex_resampler/thirdparty",
            src=os.path.join(
                self._source_subfolder, "extras/speex_resampler/thirdparty"
            ),
        )

    def package_info(self):
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("dl")
        if self.settings.os == "Macos":
            self.cpp_info.frameworks.extend(
                ["CoreFoundation", "CoreAudio", "AudioUnit"]
            )
            self.cpp_info.defines.append("MA_NO_RUNTIME_LINKING=1")

    def package_id(self):
        self.info.header_only()
