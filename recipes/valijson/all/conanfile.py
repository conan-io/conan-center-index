from conans import ConanFile, tools
import os
import glob


class ValijsonConan(ConanFile):
    name = "valijson"
    description = "Valijson is a header-only JSON Schema Validation library for C++11."
    topics = ("conan", "valijson", "json", "validator")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tristanpenman/valijson"
    license = "BSD-2-Clause"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob(self.name + "-*/")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        include_folder = os.path.join(self._source_subfolder, "include")
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="include", src=include_folder)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        # self.cpp_info.filenames["cmake_find_package"] = "valijson" # TBA: There's no installed config file
        # self.cpp_info.filenames["cmake_find_package_multi"] = "valijson" # TBA: There's no installed config file
        self.cpp_info.names["cmake_find_package"] = "ValiJSON"
        self.cpp_info.names["cmake_find_package_multi"] = "ValiJSON"

        self.cpp_info.components["libvalijson"].names["cmake_find_package"] = "valijson"
        self.cpp_info.components["libvalijson"].names["cmake_find_package_multi"] = "valijson"
