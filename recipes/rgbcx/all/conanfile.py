import os
import glob
from conans import ConanFile, tools


class RgbcxConan(ConanFile):
    name = "rgbcx"
    description = "High-performance scalar BC1-5 encoders."
    homepage = "https://github.com/richgel999/bc7enc/blob/master/rgbcx.h"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "BC1", "BC5", "BCx", "encoding")
    license = "MIT", "Unlicense"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob('bc7enc-*/')[0]
        os.rename(extracted_dir, self._source_subfolder)

    def _extract_licenses(self):
        header = tools.load(os.path.join(self.source_folder, self._source_subfolder, "rgbcx.h"))
        mit_content = header[header.find("ALTERNATIVE A - "):header.find("ALTERNATIVE B -")]
        tools.save("LICENSE_MIT", mit_content)
        unlicense_content = header[header.find("ALTERNATIVE B - "):header.rfind("*/", 1)]
        tools.save("LICENSE_UNLICENSE", unlicense_content)

    def package(self):
        self.copy("rgbcx.h", dst="include", src=self._source_subfolder)
        self.copy("rgbcx_table4.h", dst="include", src=self._source_subfolder)
        self._extract_licenses()
        self.copy("LICENSE_MIT", dst="licenses")
        self.copy("LICENSE_UNLICENSE", dst="licenses")

    def package_id(self):
        self.info.header_only()
