from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.32.1"

class HsmConan(ConanFile):
    name = "hsm"
    license = "MIT"
    homepage = "https://github.com/erikzenker/hsm.git"
    url = "https://github.com/conan-io/conan-center-index"
    description = "The hana state machine (hsm) is a finite state machine library based on the boost hana meta programming library. It follows the principles of the boost msm and boost sml libraries, but tries to reduce own complex meta programming code to a minimum."
    topics = ("state machine", "template meta programming")
    requires = "boost/1.72.0"
    no_copy_source = True
    generators = "cmake"
    settings = "os", "arch", "build_type", "compiler"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder)

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder=os.path.join(self._source_subfolder, "hsm-" + self.version))

    def package(self):
        cmake = CMake(self)    
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "hsm"
        self.cpp_info.names["cmake_find_package_multi"] = "hsm"
