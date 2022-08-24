import os
from conan import ConanFile, tools


class PanziPortableEndian(ConanFile):
    name = "panzi-portable-endian"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gist.github.com/panzi/6856583"
    description = "This provides the endian conversion functions form endian.h on Windows, Linux, *BSD, and Mac OS X"
    topics = ("conan", "endian")
    license = "Unlicense"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _extract_license(self):
        header = tools.files.load(self, os.path.join(
            self._source_subfolder, "portable_endian.h"))
        license_contents = header[0:(header.find("#ifndef", 1))]
        tools.files.save(self, "LICENSE", license_contents)

    def package(self):
        self._extract_license()
        self.copy("LICENSE", dst="licenses")
        self.copy(pattern="*.h", dst="include",
                  src=self._source_subfolder, keep_path=False)

    def package_id(self):
        self.info.header_only()
