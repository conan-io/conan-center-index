from conans import ConanFile, CMake, tools
from conans.tools import os_info
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

    _cmake = None


    def requirements(self):
        self.requires("boost/1.73.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination = self._source_subfolder)

    def package(self):
        self.copy("**/*.hpp", dst=".", src=self._source_subfolder, keep_path=True)
        tools.download(
          "https://www.boost.org/LICENSE_1_0.txt",
          filename=os.path.join(self.package_folder, "licenses", "LICENSE_1_0.txt"),
          sha256="c9bff75738922193e67fa726fa225535870d2aa1059f91452c411736284ad566"
        )
    def package_id(self):
        self.info.header_only()
        
    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "TURTLE"
        self.cpp_info.names["cmake_find_package_multi"] = "TURTLE"
