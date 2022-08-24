from conans import CMake, ConanFile, tools
from conan.tools.microsoft import is_msvc
import functools

required_conan_version = ">=1.33.0"


class LightGBMConan(ConanFile):
    name = "lightgbm"
    description = "A fast, distributed, high performance gradient boosting (GBT, GBDT, GBRT, GBM or MART) framework based on decision tree algorithms, used for ranking, classification and many other machine learning tasks."
    topics = ("machine-learning", "boosting")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/microsoft/LightGBM"
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "cmake_find_package"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openmp": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openmp": True
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("eigen/3.4.0")
        self.requires("fast_double_parser/0.6.0")
        self.requires("fmt/9.0.0")
        if self.options.with_openmp and self.settings.compiler in ("clang", "apple-clang"):
            self.requires("llvm-openmp/11.1.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_STATIC_LIB"] = not self.options.shared
        cmake.definitions["USE_DEBUG"] = self.settings.build_type == "Debug"
        cmake.definitions["USE_OPENMP"] = self.options.with_openmp
        if self.settings.os == "Macos":
            cmake.definitions["APPLE_OUTPUT_DYLIB"] = True
        cmake.configure()
        return cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "LightGBM")
        self.cpp_info.set_property("cmake_target_name", "LightGBM::LightGBM")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "LightGBM"
        self.cpp_info.names["cmake_find_package_multi"] = "LightGBM"

        self.cpp_info.libs = ["lib_lightgbm"] if is_msvc(self) else ["_lightgbm"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32", "iphlpapi"])
        elif self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
        if not self.options.shared and self.options.with_openmp:
            if is_msvc(self):
                openmp_flags = ["-openmp"]
            elif self.settings.compiler == "gcc":
                openmp_flags = ["-fopenmp"]
            elif self.settings.compiler in ("clang", "apple-clang"):
                openmp_flags = ["-Xpreprocessor", "-fopenmp"]
            else:
                openmp_flags = []
            self.cpp_info.exelinkflags.extend(openmp_flags)
            self.cpp_info.sharedlinkflags.extend(openmp_flags)
