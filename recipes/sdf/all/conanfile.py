import os
import glob
from conans import ConanFile, tools


class SdfConan(ConanFile):
    name = "sdf"
    description = "Signed Distance Field Builder for Contour Texturing"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/p-ranav/argparse"
    topics = ("conan", "sdf", "signed", "distance", "field", "contour")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob('sdf-*/')[0]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE.txt", src=self._source_subfolder, dst="licenses")
        self.copy("*.h", src=os.path.join(self._source_subfolder, "src"), dst="include")

    def package_id(self):
        self.info.header_only()
