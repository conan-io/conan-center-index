from conan import ConanFile, tools
from conan.tools.cmake import CMake
import os

required_conan_version = ">=1.33.0"

class NudbConan(ConanFile):
    name = "nudb"
    license = "BSL-1.0"
    description = "A fast key/value insert-only database for SSD drives in C++11"
    homepage = "https://github.com/CPPAlliance/NuDB"
    url = "https://github.com/conan-io/conan-center-index/"
    topics = ("header-only", "KVS", "insert-only")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("boost/1.78.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE*", "licenses", self._source_subfolder)
        self.copy("*.hpp", "include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("*.ipp", "include", src=os.path.join(self._source_subfolder, "include"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "NuDB"
        self.cpp_info.names["cmake_find_package_multi"] = "NuDB"
        self.cpp_info.components["core"].names["cmake_find_package"] = "nudb"
        self.cpp_info.components["core"].names["cmake_find_package_multi"] = "nudb"
        self.cpp_info.components["core"].requires = ["boost::thread", "boost::system"]
        self.cpp_info.set_property("cmake_target_name", "NuDB")
        self.cpp_info.set_property("cmake_target_module_name", "NuDB::nudb")
        self.cpp_info.set_property("cmake_find_module", "both")
