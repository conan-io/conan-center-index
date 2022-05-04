from conan.tools.microsoft import is_msvc
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.45.0"


class H5ppConan(ConanFile):
    name = "h5pp"
    description = "A C++17 wrapper for HDF5 with focus on simplicity"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/DavidAce/h5pp"
    topics = ("h5pp", "hdf5", "binary", "storage")
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"

    exports_sources = "CMakeLists.txt"
    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"

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

    def requirements(self):
        self.requires("eigen/3.4.0")
        self.requires("hdf5/1.12.1")
        self.requires("spdlog/1.10.0")

    def package_id(self):
        self.info.header_only()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 17)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("h5pp requires C++17, which your compiler does not support.")
        else:
            self.output.warn("h5pp requires C++17. Your compiler is unknown. Assuming it supports C++17.")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["H5PP_ENABLE_TESTS"] = False
        cmake.definitions["H5PP_BUILD_EXAMPLES"] = False
        cmake.definitions["H5PP_PRINT_INFO"] = False
        if tools.Version(self.version) >= "1.9.0":
            cmake.definitions["H5PP_PACKAGE_MANAGER"] = "none"
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        if tools.Version(self.version) <= "1.8.6":
            tools.rmdir(os.path.join(self.package_folder, "share"))
        else:
            tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "h5pp")
        self.cpp_info.set_property("cmake_target_name", "h5pp::h5pp")
        self.cpp_info.components["h5pp_headers"].set_property("cmake_target_name", "h5pp::headers")
        self.cpp_info.components["h5pp_deps"].set_property("cmake_target_name", "h5pp::deps")
        self.cpp_info.components["h5pp_deps"].requires = ["eigen::eigen", "spdlog::spdlog", "hdf5::hdf5"]
        self.cpp_info.components["h5pp_flags"].set_property("cmake_target_name", "h5pp::flags")
        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "9":
            self.cpp_info.components["h5pp_flags"].system_libs = ["stdc++fs"]
        if is_msvc(self):
            self.cpp_info.components["h5pp_flags"].defines = ["NOMINMAX"]
            self.cpp_info.components["h5pp_flags"].cxxflags = ["/permissive-"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "h5pp"
        self.cpp_info.names["cmake_find_package_multi"] = "h5pp"
        self.cpp_info.components["h5pp_headers"].names["cmake_find_package"] = "headers"
        self.cpp_info.components["h5pp_headers"].names["cmake_find_package_multi"] = "headers"
        self.cpp_info.components["h5pp_deps"].names["cmake_find_package"] = "deps"
        self.cpp_info.components["h5pp_deps"].names["cmake_find_package_multi"] = "deps"
        self.cpp_info.components["h5pp_flags"].names["cmake_find_package"] = "flags"
        self.cpp_info.components["h5pp_flags"].names["cmake_find_package_multi"] = "flags"
