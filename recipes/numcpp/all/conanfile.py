from conans import ConanFile, tools
import os
import glob


class NumCppConan(ConanFile):
    name = "numcpp"
    description = "A Templatized Header Only C++ Implementation of the Python NumPy Library"
    topics = ("python", "numpy", "numeric")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/dpilger26/NumCpp"
    license = "MIT"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("boost/1.75.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("NumCpp-*/")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        include_folder = os.path.join(self._source_subfolder, "include")
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="include", src=include_folder)

    def package_id(self):
        self.info.header_only()
