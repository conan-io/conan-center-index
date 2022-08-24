from conans import ConanFile, tools
import os

required_conan_version = ">=1.36.0"


class XbyakConan(ConanFile):
    name = "xbyak"
    description = "Xbyak is a C++ header library that enables dynamically to " \
                  "assemble x86(IA32), x64(AMD64, x86-64) mnemonic."
    license = "BSD-3-Clause"
    topics = ("xbyak", "jit", "assembler")
    homepage = "https://github.com/herumi/xbyak"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("COPYRIGHT", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst=os.path.join("include", "xbyak"), src=os.path.join(self._source_subfolder, "xbyak"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "xbyak"
        self.cpp_info.names["cmake_find_package_multi"] = "xbyak"
        self.cpp_info.set_property("cmake_file_name", "xbyak")
