import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version

class h5ppConan(ConanFile):
    name = "h5pp"
    description = "A C++17 wrapper for HDF5 with focus on simplicity"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/DavidAce/h5pp"
    topics = ("conan","h5pp","hdf5", "binary", "storage")
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package","cmake_find_package_multi"
    requires = "eigen/3.3.9", "spdlog/1.8.5", "hdf5/1.12.0"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7.4",
            "Visual Studio": "15.7",
            "clang": "6",
            "apple-clang": "10",
        }

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["H5PP_ENABLE_TESTS"]         = False
            self._cmake.definitions["H5PP_BUILD_EXAMPLES"]       = False
            self._cmake.definitions["H5PP_PRINT_INFO"]           = False
            if Version(self.version) >= "1.9.0":
                self._cmake.definitions["H5PP_PACKAGE_MANAGER"]  = "none"
            self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 17)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("h5pp requires C++17, which your compiler does not support.")
        else:
            self.output.warn("h5pp requires C++17. Your compiler is unknown. Assuming it supports C++17.")

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        if Version(self.version) <= "1.8.6":
            tools.rmdir(os.path.join(self.package_folder, "share"))
        else:
            tools.rmdir(os.path.join(self.package_folder, "lib/cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "h5pp"
        self.cpp_info.names["cmake_find_package_multi"] = "h5pp"
        self.cpp_info.components["h5pp_headers"].names["cmake_find_package"] = "headers"
        self.cpp_info.components["h5pp_headers"].names["cmake_find_package_multi"] = "headers"
        self.cpp_info.components["h5pp_deps"].names["cmake_find_package"] = "deps"
        self.cpp_info.components["h5pp_deps"].names["cmake_find_package_multi"] = "deps"
        self.cpp_info.components["h5pp_deps"].requires = ["eigen::eigen", "spdlog::spdlog", "hdf5::hdf5"]
        self.cpp_info.components["h5pp_flags"].names["cmake_find_package"] = "flags"
        self.cpp_info.components["h5pp_flags"].names["cmake_find_package_multi"] = "flags"
        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "9":
            self.cpp_info.components["h5pp_flags"].system_libs = ["stdc++fs"]
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.components["h5pp_flags"].defines = ["NOMINMAX"]
            self.cpp_info.components["h5pp_flags"].cxxflags = ["/permissive-"]

    def package_id(self):
        self.info.header_only()
