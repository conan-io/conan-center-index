from conans import ConanFile, tools
import glob
import os


class FxdivConan(ConanFile):
    name = "fxdiv"
    description = "C99/C++ header-only library for division via fixed-point " \
                  "multiplication by inverse."
    license = "MIT"
    topics = ("conan", "fxdiv", "integer-division")
    homepage = "https://github.com/Maratyszcza/FXdiv"
    url = "https://github.com/conan-io/conan-center-index"

    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("FXdiv-*")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst="include", src=os.path.join(self._source_subfolder, "include"))
