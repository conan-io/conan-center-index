import os

from conan import ConanFile, tools

class QuaternionsConan(ConanFile):
    name = "quaternions"
    description = "A blazingly fast C++ library to work with quaternions."
    topics = ("conan", "quaternions", "mathematics")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ferd36/quaternions"
    license = "MIT"
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, 11)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        url = self.conan_data["sources"][self.version]["url"]
        extracted_dir = self.name + "-" + os.path.splitext(os.path.basename(url))[0]
        os.rename(extracted_dir, self._source_subfolder)
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "include", "quaternion.h"),
                              "#include <boost/mpl/bool.hpp>", "")

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))
