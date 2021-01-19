from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.28.0"

class GeographiclibConan(ConanFile):
    name = "geographiclib"
    description = "Convert geographic units and solve geodesic problems"
    topics = ("conan", "geographiclib", "geodesic")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://geographiclib.sourceforge.io"
    license = "MIT"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = ["CMakeLists.txt"]
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    _cmake = None

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    @property
    def _min_compiler_version_default_cxx11(self):
        # Minimum compiler version having c++ standard >= 11
        return {
            "apple-clang": "3.3",
            "gcc": "4.9",
            "clang": "6",
            "Visual Studio": "14",  # guess
        }.get(str(self.settings.compiler), False)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if tools.Version(self.version) >= "1.51":
            if self.settings.compiler.cppstd:
                tools.min_cppstd(self, 11)

            def lazy_lt_semver(v1, v2):
                lv1 = [int(v) for v in v1.split(".")]
                lv2 = [int(v) for v in v2.split(".")]
                min_length = min(len(lv1), len(lv2))
                return lv1[:min_length] < lv2[:min_length]

            minimum_version = self._min_compiler_version_default_cxx11
            if not minimum_version:
                self.output.warn("geographiclib {} requires C++11 math functions. Your compiler is unknown. Assuming it supports this feature.".format(self.version))
            elif lazy_lt_semver(str(self.settings.compiler.version), minimum_version):
                raise ConanInvalidConfiguration("geographiclib {} requires C++11 math functions, which your compiler does not support.".format(self.version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "GeographicLib-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["GEOGRAPHICLIB_LIB_TYPE"] = "SHARED" if self.options.shared else "STATIC"
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        # it does not work on Windows but is not needed
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "add_subdirectory (js)", "")
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        for folder in ["share", os.path.join("lib", "python"), os.path.join("lib", "pkgconfig"),
                       os.path.join("lib", "cmake"), "sbin", "python", "matlab", "doc", "cmake"]:
            tools.rmdir(os.path.join(os.path.join(self.package_folder, folder)))
        if self.settings.os == "Linux" or self.settings.os == "Macos":
            tools.rmdir(os.path.join(os.path.join(self.package_folder, "bin")))
        elif self.settings.os == "Windows":
            for item in os.listdir(os.path.join(os.path.join(self.package_folder, "bin"))):
                if not item.startswith("Geographic") or item.endswith(".pdb"):
                    os.remove(os.path.join(self.package_folder, "bin", item))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "geographiclib"
        self.cpp_info.filenames["cmake_find_package_multi"] = "geographiclib"
        self.cpp_info.names["cmake_find_package"] = "GeographicLib"
        self.cpp_info.names["cmake_find_package_multi"] = "GeographicLib"
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.defines.append("GEOGRAPHICLIB_SHARED_LIB={}".format("1" if self.options.shared else "0"))
