import os

from conans import CMake, ConanFile, tools


class CppSortConan(ConanFile):
    name = "cpp-sort"
    description = "Additional sorting algorithms & related tools"
    topics = "conan", "cpp-sort", "sorting", "algorithms"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Morwenn/cpp-sort"
    license = "MIT"
    no_copy_source = True
    settings = "os", "compiler", "build_type", "arch"

    _source_subfolder = "source_subfolder"

    def configure(self):
        tools.check_min_cppstd(self, "14")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        # Install with CMake
        cmake = CMake(self)
        cmake.definitions["BUILD_TESTING"] = "OFF"
        cmake.configure(source_folder=self._source_subfolder)
        cmake.install()

        # Copy license files
        if tools.Version(self.version) < "1.8.0":
            license_files = ["license.txt"]
        else:
            license_files = ["LICENSE.txt", "NOTICE.txt"]
        for license_file in license_files:
            self.copy(license_file, dst="licenses", src=self._source_subfolder)

        # Remove CMake config files (only files in lib)
        tools.rmdir(os.path.join(self.package_folder, "lib"))

    def package_id(self):
        self.info.header_only()
