import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"

class StatusCodeConan(ConanFile):
    name = "status-code"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ned14/status-code"
    description = "Proposed SG14 status_code for the C++ standard"
    topics = ("c++", "platform", "sg14")
    generators = "cmake"
    exports_sources = "CMakeLists.txt"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib"))
        self.copy("Licence.txt", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "status-code")
        self.cpp_info.set_property("cmake_target_name", "status-code::hl")

        self.cpp_info.filenames["cmake_find_package"] = "status-code"
        self.cpp_info.filenames["cmake_find_package_multi"] = "status-code"
        self.cpp_info.names["cmake_find_package"] = "status-code::hl"
        self.cpp_info.names["cmake_find_package_multi"] = "status-code::hl"
