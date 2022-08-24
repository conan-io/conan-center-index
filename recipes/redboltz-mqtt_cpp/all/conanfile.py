from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"

class MqttCPPConan(ConanFile):
    name = "redboltz-mqtt_cpp"
    description = "MQTT client/server for C++14 based on Boost.Asio"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/redboltz/mqtt_cpp"
    topics = ("mqtt", "boost", "asio")
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("boost/1.79.0")

    def package_id(self):
        self.info.header_only()

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "6",
            "Visual Studio": "15.0",
            "clang": "5",
            "apple-clang": "10",
        }
    
    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, 14)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.scm.Version(self, self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("{} requires C++14, which your compiler does not support.".format(self.name))
        else:
            self.output.warn("{} requires C++14. Your compiler is unknown. Assuming it supports C++14.".format(self.name))
            
    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy(pattern="LICENSE_1_0.txt", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "mqtt_cpp")
        self.cpp_info.set_property("cmake_target_name", "mqtt_cpp::mqtt_cpp")

        #  TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "mqtt_cpp"
        self.cpp_info.filenames["cmake_find_package_multi"] = "mqtt_cpp"
        self.cpp_info.names["cmake_find_package"] = "mqtt_cpp"
        self.cpp_info.names["cmake_find_package_multi"] = "mqtt_cpp"
