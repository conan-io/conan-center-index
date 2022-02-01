from conans import ConanFile, tools
import os

required_conan_version = ">=1.33.0"

class MiniaudioConan(ConanFile):
    name = "miniaudio"
    description = "A single file audio playback and capture library."
    topics = ("miniaudio", "header-only", "sound")
    homepage = "https://github.com/mackron/miniaudio"
    url = "https://github.com/conan-io/conan-center-index"
    license = ["Unlicense", "MIT-0"]
    settings = "os", "compiler", "build_type", "arch"

    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="miniaudio.h", dst="include", src=self._source_subfolder)
        self.copy(
            pattern="stb_vorbis.c",
            dst="include/extras",
            src=os.path.join(self._source_subfolder, "extras"),
        )
        self.copy(
            pattern="dr_*.h",
            dst="include/extras",
            src=os.path.join(self._source_subfolder, "extras"),
        )
        self.copy(
            pattern="ma_speex_resampler.h",
            dst="include/extras/speex_resampler/",
            src=os.path.join(self._source_subfolder, "extras/speex_resampler/"),
        )
        self.copy(
            pattern="*.*",
            dst="include/extras/speex_resampler/thirdparty",
            src=os.path.join(
                self._source_subfolder, "extras/speex_resampler/thirdparty"
            ),
        )
        self.copy(
            pattern="miniaudio.*",
            dst="include/extras/miniaudio_split",
            src=os.path.join(self._source_subfolder, "extras/miniaudio_split"),
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
