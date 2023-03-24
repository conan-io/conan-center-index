from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
from conan.tools.microsoft import check_min_vs, is_msvc
import os

required_conan_version = ">=1.52.0"

class ModernCppKafkaConan(ConanFile):
    name = "modern-cpp-kafka"
    description = "A C++ API for Kafka clients (i.e. KafkaProducer, KafkaConsumer, AdminClient)"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/morganstanley/modern-cpp-kafka"
    topics = ("kafka", "librdkafka", "kafkaproducer", "kafkaconsumer", "header-only")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "clang": "7",
            "apple-clang": "12",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("librdkafka/2.0.2")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 192)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)


    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.h",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ModernCppKafka")
        self.cpp_info.set_property("cmake_target_name", "ModernCppKafka::ModernCppKafka")

        self.cpp_info.names["cmake_find_package"] = "ModernCppKafka"
        self.cpp_info.names["cmake_find_package_multi"] = "ModernCppKafka"

        if self.settings.os in ["Linux", "Macos"]:
            self.cpp_info.system_libs.append("pthread")
