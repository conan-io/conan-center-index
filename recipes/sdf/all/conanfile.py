import os
import glob
from conan import ConanFile, tools$


class SdfConan(ConanFile):
    name = "sdf"
    description = "Signed Distance Field Builder for Contour Texturing"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/memononen/SDF"
    topics = ("conan", "sdf", "signed", "distance", "field", "contour")
    settings = "os"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = glob.glob('SDF-*/')[0]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE.txt", src=self._source_subfolder, dst="licenses")
        self.copy("*.h", src=os.path.join(self._source_subfolder, "src"), dst="include")

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]
