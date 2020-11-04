from conans import ConanFile, tools
import os
import glob


class CuteHeadersConan(ConanFile):
    name = "cute_headers"
    description = "Various single-file cross-platform C/C++ headers implementing self-contained libraries."
    topics = ("conan", "various", "pure-c")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/RandyGaul/cute_headers"
    license = "Unlicense"  # This library (cute-headers) is public domain software, i.e. not copyrighted
    no_copy_source = True

    def _extract_license(self):
        file = os.path.join(self.package_folder, "include/cute_math2d.h")
        with open(file, 'r') as f:
            file_content = f.read()
        return file_content[file_content.rfind('/*'):]

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob(self.name + "-*/")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy(
            pattern="*.h",
            dst="include",
            src=self._source_subfolder,
            excludes=("examples_cute_*", "test_cute_*")
        )
        license_folder = os.path.join(self.package_folder, "licenses")
        tools.mkdir(license_folder)
        with open(os.path.join(license_folder, "LICENSE"), 'w') as f:
            f.write(self._extract_license())

    def package_id(self):
        self.info.header_only()
