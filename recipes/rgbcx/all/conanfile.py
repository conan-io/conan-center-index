import os
import glob
from conans import ConanFile, tools


class RgbcxConan(ConanFile):
    name = "rgbcx"
    description = "High-performance scalar BC1-5 encoders."
    homepage = "https://github.com/richgel999/bc7enc"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "BC1", "BC5", "BCx", "encoding")
    license = "MIT", "Unlicense"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = glob.glob('bc7enc-*/')[0]
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "rgbcx.h"),
                              "#include <stdlib.h>",
                              "#include <stdlib.h>\n#include <string.h>")

    def package(self):
        self.copy("rgbcx.h", dst="include", src=self._source_subfolder)
        self.copy("rgbcx_table4.h", dst="include", src=self._source_subfolder)
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
