from conans import ConanFile, tools
import os

required_conan_version = ">=1.33.0"


class ModernCppKafkaConan(ConanFile):
    name = "modern-cpp-kafka"
    description = "A C++ API for Kafka clients (i.e. KafkaProducer, KafkaConsumer, AdminClient)"
    license = "Apache License 2.0"
    topics = ("kafka", "librdkafka", "kafkaproducer", "kafkaconsumer")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/morganstanley/modern-cpp-kafka"
    settings = "arch", "build_type", "compiler", "os"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
       self.cpp_info.set_property("cmake_target_name", "ModernCppKafka::ModernCppKafka")

       self.cpp_info.names["cmake_find_package"] = "ModernCppKafka"
       self.cpp_info.names["cmake_find_package_multi"] = "ModernCppKafka"

       if self.settings.os in ["Linux", "Macos"]:
           self.cpp_info.system_libs.append("pthread")
