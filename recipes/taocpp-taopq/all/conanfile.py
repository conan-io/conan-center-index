from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.43.0"


class TaoCPPTaopqConan(ConanFile):
    name = "taocpp-taopq"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/taocpp/taopq"
    description = "C++ client library for PostgreSQL"
    topics = ("cpp17", "postgresql", "libpq", "data-base", "sql")

    settings = "os", "build_type", "compiler", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake", "cmake_find_package"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _min_compilers_version(self):
        return {
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10",
            "Visual Studio": "15"
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("libpq/14.2")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, "17")
        min_compiler_version = self._min_compilers_version.get(str(self.settings.compiler), False)
        if min_compiler_version:
            if tools.scm.Version(self, self.settings.compiler.version) < min_compiler_version:
                raise ConanInvalidConfiguration("taocpp-taopq requires C++17, which your compiler does not support.")
        else:
            self.output.warn("taocpp-taopq requires C++17. Your compiler is unknown. Assuming it supports C++17.")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["TAOPQ_BUILD_TESTS"] = False
        cmake.definitions["TAOPQ_INSTALL_DOC_DIR"] = "licenses"
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "taopq")
        self.cpp_info.set_property("cmake_target_name", "taocpp::taopq")
        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["_taocpp-taopq"].libs = ["taopq"]
        if self.settings.os == "Windows":
            self.cpp_info.components["_taocpp-taopq"].system_libs = ["Ws2_32"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "taopq"
        self.cpp_info.filenames["cmake_find_package_multi"] = "taopq"
        self.cpp_info.names["cmake_find_package"] = "taocpp"
        self.cpp_info.names["cmake_find_package_multi"] = "taocpp"
        self.cpp_info.components["_taocpp-taopq"].names["cmake_find_package"] = "taopq"
        self.cpp_info.components["_taocpp-taopq"].names["cmake_find_package_multi"] = "taopq"
        self.cpp_info.components["_taocpp-taopq"].set_property("cmake_target_name", "taocpp::taopq")
        self.cpp_info.components["_taocpp-taopq"].requires = ["libpq::libpq"]
