from conans import ConanFile, tools

required_conan_version = ">=1.43.0"

class CircularBufferConan(ConanFile):
    name = "circularbuffer"
    description = "Arduino circular buffer library"
    topics = ("circular buffer", "arduino", "data-structures")
    license = "LGPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rlogiacco/CircularBuffer"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE*", "licenses", self._source_subfolder)
        self.copy("CircularBuffer.h", "include", self._source_subfolder)
        self.copy("CircularBuffer.tpp", "include", self._source_subfolder)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "CircularBuffer")
        self.cpp_info.set_property("cmake_target_name", "CircularBuffer::CircularBuffer")

        self.cpp_info.filenames["cmake_find_package"] = "CircularBuffer"
        self.cpp_info.filenames["cmake_find_package_multi"] = "CircularBuffer"
        self.cpp_info.names["cmake_find_package"] = "CircularBuffer"
        self.cpp_info.names["cmake_find_package_multi"] = "CircularBuffer"
