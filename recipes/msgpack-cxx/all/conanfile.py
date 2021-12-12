from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.36.0"

class MsgpackCXXConan(ConanFile):
    name = "msgpack-cxx"
    description = "The official C++ library for MessagePack"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/msgpack/msgpack-c"
    topics = ("msgpack", "message-pack", "serialization")
    license = "BSL-1.0"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def configure(self):
        self.options["boost"].header_only = False
        self.options["boost"].without_chrono = False
        self.options["boost"].without_context = False
        self.options["boost"].without_system = False
        self.options["boost"].without_timer = False

    def requirements(self):
        self.requires("boost/1.77.0")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE_1_0.txt", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "msgpack-cxx"
        self.cpp_info.filenames["cmake_find_package_multi"] = "msgpack-cxx"
        self.cpp_info.set_property("cmake_file_name", "msgpack-cxx")
        self.cpp_info.names["cmake_find_package"] = "msgpack"
        self.cpp_info.names["cmake_find_package_multi"] = "msgpack"
        self.cpp_info.set_property("cmake_target_name", "msgpack")
        self.cpp_info.components["msgpack"].names["cmake_find_package"] = "msgpack-cxx"
        self.cpp_info.components["msgpack"].names["cmake_find_package_multi"] = "msgpack-cxx"
        self.cpp_info.components["msgpack"].set_property("cmake_target_name", "msgpack-cxx")
        self.cpp_info.components["msgpack"].set_property("pkg_config_name", "msgpack-cxx")
        self.cpp_info.components["msgpack"].defines = ["MSGPACK_USE_BOOST"]
        self.cpp_info.components["msgpack"].requires = ["boost::boost"]
