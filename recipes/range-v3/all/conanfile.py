import os
from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class Rangev3Conan(ConanFile):
    name = "range-v3"
    license = "BSL-1.0"
    homepage = "https://github.com/ericniebler/range-v3"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Experimental range library for C++11/14/17"
    topics = ("range", "range-library", "proposal", "iterator", "header-only")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _compilers_minimum_version(self):
        rangev3_version = tools.Version(self.version)
        return {
            "gcc": "5" if rangev3_version < "0.10.0" else "6.5",
            "Visual Studio": "16",
            "clang": "3.6" if rangev3_version < "0.10.0" else "3.9"
        }

    @property
    def _min_cppstd(self):
        if self.settings.compiler == "Visual Studio":
            return "17"
        else:
            return "14"

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("{0} {1} support for range-v3 is unknown, assuming it is supported."
                             .format(self.settings.compiler, self.settings.compiler.version))
        elif tools.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("range-v3 {0} requires C++{1} with {2}, which is not supported by {2} {3}"
                                            .format(self.version,
                                                    self._min_cppstd,
                                                    self.settings.compiler,
                                                    self.settings.compiler.version))

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = self.name + "-" + self.version
        os.rename(extracted_folder, self._source_subfolder)

    def package(self):
        self.copy(pattern="*", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.components["range-v3-meta"].names["cmake_find_package"] = "meta"
        self.cpp_info.components["range-v3-meta"].names["cmake_find_package_multi"] = "meta"
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.components["range-v3-meta"].cxxflags = ["/permissive-"]
            version = tools.Version(self.version)
            if "0.9.0" <= version and version < "0.11.0":
                self.cpp_info.components["range-v3-meta"].cxxflags.append("/experimental:preprocessor")
        self.cpp_info.components["range-v3-concepts"].names["cmake_find_package"] = "concepts"
        self.cpp_info.components["range-v3-concepts"].names["cmake_find_package_multi"] = "concepts"
        self.cpp_info.components["range-v3-concepts"].requires = ["range-v3-meta"]
