from conans import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get
from conan.tools.build import check_min_cppstd
from conans.errors import ConanInvalidConfiguration
from conan.tools.scm import Version


class OctoLoggerCPPConan(ConanFile):
    name = "octo-logger-cpp"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ofiriluz/octo-logger-cpp"
    description = "Octo logger library"
    topics = ("logging", "cpp")
    settings = "os", "compiler", "build_type", "arch"

    @property
    def _source_subfolder(self):
        return "source"

    @property
    def _build_subfolder(self):
        return "build"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "clang": "9",
            "apple-clang": "11",
            "Visual Studio": "16",
        }

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()  

    def layout(self):
        cmake_layout(self, src_folder=self._source_subfolder)

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, "17")

        minimum_version = self._compilers_minimum_version.get(str(self.info.settings.compiler), False)
        if minimum_version and Version(self.info.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.name} requires C++17, which your compiler does not support."
            )
        else:
            self.output.warn(f"{self.name} requires C++17. Your compiler is unknown. Assuming it supports C++17.")
        if self.settings.compiler == "clang" and self.settings.compiler.get_safe("libcxx") == "libc++":
            raise ConanInvalidConfiguration(f"{self.name} does not support clang with libc++. Use libstdc++ instead.")
        if self.settings.compiler == "Visual Studio" and self.settings.compiler.runtime in ["MTd", "MT"]:
            raise ConanInvalidConfiguration(f"{self.name} does not support MSVC MT/MTd configurations, only MD/MDd is supported")

    def source(self):
        get(self, **self.conan_data["sources"][str(self.version)], strip_root=True, destination=self._source_subfolder)

    def requirements(self):
        self.requires("fmt/9.0.0")

    def build_requirements(self):
        self.build_requires("cmake/3.16.9")

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder=self._source_subfolder, 
                        build_folder=self._build_subfolder,
                        defs={"DISABLE_TESTS": "ON",
                              "DISABLE_EXAMPLES": "ON"})
        cmake.build(build_dir=self._build_subfolder)

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = CMake(self)
        cmake.install(build_dir=self._build_subfolder)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "octo-logger-cpp")
        self.cpp_info.set_property("cmake_target_name", "octo::octo-logger-cpp")
        self.cpp_info.set_property("pkg_config_name", "octo-logger-cpp")
        self.cpp_info.components["libocto-logger-cpp"].libs = ["octo-logger-cpp"]
        self.cpp_info.components["libocto-logger-cpp"].requires = ["fmt::fmt"]
        self.cpp_info.filenames["cmake_find_package"] = "octo-logger-cpp"
        self.cpp_info.filenames["cmake_find_package_multi"] = "octo-logger-cpp"
        self.cpp_info.names["cmake_find_package"] = "octo-logger-cpp"
        self.cpp_info.names["cmake_find_package_multi"] = "octo-logger-cpp"
        self.cpp_info.names["pkg_config"] = "octo-logger-cpp"
        self.cpp_info.components["libocto-logger-cpp"].names["cmake_find_package"] = "octo-logger-cpp"
        self.cpp_info.components["libocto-logger-cpp"].names["cmake_find_package_multi"] = "octo-logger-cpp"
        self.cpp_info.components["libocto-logger-cpp"].set_property("cmake_target_name", "octo::octo-logger-cpp")
        self.cpp_info.components["libocto-logger-cpp"].set_property("pkg_config_name", "octo-logger-cpp")
