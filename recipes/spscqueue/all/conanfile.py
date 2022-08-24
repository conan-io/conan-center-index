from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class SpscqueueConan(ConanFile):
    name = "spscqueue"
    description = "A bounded single-producer single-consumer wait-free and lock-free queue written in C++11."
    license = "MIT"
    topics = ("spscqueue", "thread", "queue")
    homepage = "https://github.com/rigtorp/SPSCQueue"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, 11)
        if self.settings.compiler == "gcc" and tools.scm.Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration("gcc < 5 not supported")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "SPSCQueue")
        self.cpp_info.set_property("cmake_target_name", "SPSCQueue::SPSCQueue")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "SPSCQueue"
        self.cpp_info.names["cmake_find_package_multi"] = "SPSCQueue"
