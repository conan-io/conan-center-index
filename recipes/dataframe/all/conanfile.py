from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class DataFrameConan(ConanFile):
    name = "dataframe"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/hosseinmoein/DataFrame"
    description = (
        "C++ DataFrame for statistical, Financial, and ML analysis -- in modern C++ "
        "using native types, continuous memory storage, and no pointers are involved"
    )
    topics = (
        "dataframe",
        "data-science",
        "numerical-analysis",
        "multidimensional-data",
        "heterogeneous",
        "cpp",
        "statistical-analysis",
        "financial-data-analysis",
        "financial-engineering",
        "data-analysis",
        "trading-strategies",
        "machine-learning",
        "trading-algorithms",
        "financial-engineering",
        "large-data",
    )

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10.0" if tools.Version(self.version) >= "1.12.0" else "9.0",
        }

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self._is_msvc and self.options.shared and tools.Version(self.version) <= "1.19.0":
            raise ConanInvalidConfiguration(
                "dataframe {} doesn't support shared lib with Visual Studio".format(self.version)
            )

        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")

        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if minimum_version and tools.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                "{} requires C++17, which your compiler does not support.".format(self.name)
            )

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if tools.Version(self.version) >= "1.14.0":
            self._cmake.definitions["ENABLE_TESTING"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("License", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        # Remove packaging files & MS runtime files
        for dir_to_remove in [
            os.path.join("lib", "cmake"),
            os.path.join("lib", "share"),
            os.path.join("lib", "pkgconfig"),
            "CMake",
        ]:
            tools.rmdir(os.path.join(self.package_folder, dir_to_remove))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "DataFrame")
        self.cpp_info.set_property("cmake_target_name", "DataFrame::DataFrame")
        self.cpp_info.set_property("pkg_config_name", "DataFrame")
        self.cpp_info.libs = ["DataFrame"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread", "rt"])
        if self._is_msvc:
            self.cpp_info.defines.append("_USE_MATH_DEFINES")
            if tools.Version(self.version) <= "1.19.0" and not self.options.shared:
                # weird but required in those versions of dataframe
                self.cpp_info.defines.append("LIBRARY_EXPORTS")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "DataFrame"
        self.cpp_info.names["cmake_find_package_multi"] = "DataFrame"
        self.cpp_info.names["pkg_config"] = "DataFrame"
