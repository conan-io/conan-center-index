from conans import ConanFile, CMake, tools
import os

class TslRobinMapConan(ConanFile):
    name = "tsl-robin-map"
    license = "MIT"
    description = "C++ implementation of a fast hash map and hash set using robin hood hashing."
    homepage = "https://github.com/Tessil/robin-map"
    url = "https://github.com/conan-io/conan-center-index"
    
    no_copy_source = True
    
    _source_subfolder = "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])

        os.rename("robin-map-{}".format(self.version), self._source_subfolder)

    def build(self):
        pass

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_id(self):
        self.info.header_only()
