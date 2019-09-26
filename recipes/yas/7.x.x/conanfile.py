from conans import ConanFile, tools
import os


class LibnameConan(ConanFile):
    name = "yas"
    description = "Yet Another Serialization"
    topics = ("conan", "yas", "serialization")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/niXman/yas"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "BSL-1.0"
    no_copy_source = True
    _source_subfolder = "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _extract_license(self):
        header = tools.load(os.path.join(self.source_folder,
                                         self._source_subfolder,
                                         "include", "yas", "binary_oarchive.hpp"))
        license_contents = header[:header.find("#", 1)].replace("//", "")
        tools.save("LICENSE", license_contents)

    def package(self):
        self._extract_license()
        self.copy(pattern="*", dst="include",
                  src=os.path.join(self._source_subfolder, "include"))
        self.copy("LICENSE", dst="licenses")

    def package_id(self):
        self.info.header_only()

