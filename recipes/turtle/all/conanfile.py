from conans import ConanFile, tools
import os


class TurtleConan(ConanFile):
    name = "turtle"
    description = "Turtle is a C++ mock object library based on Boost with a focus on usability, simplicity and flexibility."
    topics = ("conan", "turtule", "mock", "test", "boost")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mat007/turtle"
    license = "BSL-1.0"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("boost/1.73.0")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def package(self):
        self.copy("LICENSE_1_0.txt", dst="licenses", src=self._source_subfolder)
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
