from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version
import os

required_conan_version = ">=1.33.0"

class HsmConan(ConanFile):
    name = "erikzenker-hsm"
    license = "MIT"
    homepage = "https://github.com/erikzenker/hsm.git"
    url = "https://github.com/conan-io/conan-center-index"
    description = "The hana state machine (hsm) is a finite state machine library based on the boost hana meta programming library. It follows the principles of the boost msm and boost sml libraries, but tries to reduce own complex meta programming code to a minimum."
    topics = ("state-machine", "template-meta-programming")
    requires = "boost/1.77.0"
    no_copy_source = True
    generators = "cmake"
    settings = "os", "arch", "build_type", "compiler"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        # https://github.com/erikzenker/hsm#dependencies
        if self.settings.compiler == "clang" and Version(self.settings.compiler.version) < 8:
            raise ConanInvalidConfiguration("clang 8+ is required")
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < 8:
            raise ConanInvalidConfiguration("GCC 8+ is required")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder=self._source_subfolder)

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
