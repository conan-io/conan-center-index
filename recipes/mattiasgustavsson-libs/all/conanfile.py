from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version
import os.path
import glob

class MattiasgustavssonLibsConan(ConanFile):
    name = "mattiasgustavsson-libs"
    description = "Single-file public domain libraries for C/C++"
    homepage = "https://github.com/mattiasgustavsson/libs"
    url = "https://github.com/conan-io/conan-center-index"
    license = ("Public domain", "MIT")
    topics = ("utilities", "mattiasgustavsson", "libs")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob('libs-*/')[0]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy(pattern="*.h", dst="include", src=self._source_subfolder)

        with open(os.path.join(self.source_folder, self._source_subfolder, "thread.h")) as f:
            content_lines = f.readlines()
        license_content = []
        for i in range(1449, 1498):
            license_content.append(content_lines[i][:-1])

        tools.save(os.path.join(self.package_folder, "licenses", "license.txt"), "\n".join(license_content))

    def package_id(self):
        self.info.header_only()
