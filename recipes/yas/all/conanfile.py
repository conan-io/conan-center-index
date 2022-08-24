from conan import ConanFile, tools$
import os

required_conan_version = ">=1.33.0"


class YasConan(ConanFile):
    name = "yas"
    description = "Yet Another Serialization"
    topics = ("yas", "serialization", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/niXman/yas"
    license = "BSL-1.0"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _extract_license(self):
        header = tools.files.load(self, os.path.join(
            self.source_folder, self._source_subfolder,
            "include", "yas", "binary_oarchive.hpp"))
        license_contents = header[:header.find("#")] \
            .replace("//", "").replace("\n ", "\n").lstrip()
        tools.files.save(self, "LICENSE", license_contents)

    def package(self):
        self._extract_license()
        self.copy("LICENSE", dst="licenses")
        self.copy("*", src=os.path.join(self._source_subfolder, "include"),
                  dst="include")

    def package_id(self):
        self.info.header_only()
