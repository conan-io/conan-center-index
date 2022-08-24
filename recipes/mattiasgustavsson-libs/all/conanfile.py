from conan import ConanFile, tools
import os.path
import glob

class MattiasgustavssonLibsConan(ConanFile):
    name = "mattiasgustavsson-libs"
    description = "Single-file public domain libraries for C/C++"
    homepage = "https://github.com/mattiasgustavsson/libs"
    url = "https://github.com/conan-io/conan-center-index"
    license = ("Unlicense", "MIT")
    topics = ("utilities", "mattiasgustavsson", "libs")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = glob.glob('libs-*/')[0]
        os.rename(extracted_dir, self._source_subfolder)

    def _extract_licenses(self):
        header = tools.files.load(self, os.path.join(self._source_subfolder, "thread.h"))
        mit_content = header[header.find("ALTERNATIVE A - "):header.find("ALTERNATIVE B -")]
        tools.files.save(self, "LICENSE_MIT", mit_content)
        unlicense_content = header[header.find("ALTERNATIVE B - "):header.rfind("*/", 1)]
        tools.files.save(self, "LICENSE_UNLICENSE", unlicense_content)

    def package(self):
        self.copy(pattern="*.h", dst="include", src=self._source_subfolder)
        self._extract_licenses()
        self.copy("LICENSE_MIT", dst="licenses")
        self.copy("LICENSE_UNLICENSE", dst="licenses")

    def package_id(self):
        self.info.header_only()
