import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


required_conan_version = ">=1.33.0"


class TaoCPPTaopqConan(ConanFile):
    name = "taocpp-taopq"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/taocpp/taopq"
    description = "C++ client library for PostgreSQL"
    topics = ("cpp17", "postgresql", "libpq", "data-base", "sql")
    settings = "os", "build_type", "compiler", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = "CMakeLists.txt"
    generators = "cmake", "cmake_find_package"

    _cmake = None

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

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "17")
        min_compiler_version = self._min_compilers_version.get(str(self.settings.compiler), False)
        if min_compiler_version:
            if tools.Version(self.settings.compiler.version) < min_compiler_version:
                raise ConanInvalidConfiguration("taocpp-taopq requires C++17, which your compiler does not support.")
        else:
            self.output.warn("taocpp-taopq requires C++17. Your compiler is unknown. Assuming it supports C++17.")

    def requirements(self):
        self.requires("libpq/13.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["TAOPQ_BUILD_TESTS"] = False
            self._cmake.definitions["TAOPQ_INSTALL_DOC_DIR"] = "licenses"
            if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
                self._cmake.definitions["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = self.options.shared
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "taopq"
        self.cpp_info.filenames["cmake_find_package_multi"] = "taopq"
        self.cpp_info.names["cmake_find_package"] = "taocpp"
        self.cpp_info.names["cmake_find_package_multi"] = "taocpp"
        self.cpp_info.components["_taocpp-taopq"].names["cmake_find_package"] = "taopq"
        self.cpp_info.components["_taocpp-taopq"].names["cmake_find_package_multi"] = "taopq"
        self.cpp_info.components["_taocpp-taopq"].libs = ["taopq"]
        if self.settings.os == "Windows":
            self.cpp_info.components["_taocpp-taopq"].system_libs = ["Ws2_32"]
        self.cpp_info.components["_taocpp-taopq"].requires = ["libpq::libpq"]
