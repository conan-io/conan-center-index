from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.29.1"


class GeographiclibConan(ConanFile):
    name = "geographiclib"
    description = "Convert geographic units and solve geodesic problems"
    topics = ("conan", "geographiclib", "geodesic")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://geographiclib.sourceforge.io"
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "precision": ["float", "double", "extended", "quadruple", "variable"],
        "tools": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "precision": "double",
        "tools": True
    }

    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    @property
    def _min_compiler_version_default_cxx11(self):
        # Minimum compiler version having C++11 math functions
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

        if self.options.precision not in ["float", "double"]:
            # FIXME: add support for extended, quadruple and variable precisions
            # (may require external libs: boost multiprecision for quadruple, mpfr for variable)
            raise ConanInvalidConfiguration("extended, quadruple and variable precisions not yet supported in this recipe")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "GeographicLib-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _patch_sources(self):
        cmakelists = os.path.join(self._source_subfolder, "CMakeLists.txt")
        # it does not work on Windows but is not needed
        tools.replace_in_file(cmakelists, "add_subdirectory (js)", "")
        # Don't install system libs
        tools.replace_in_file(cmakelists, "include (InstallRequiredSystemLibraries)", "")
        # Don't build tools if asked
        if not self.options.tools:
            tools.replace_in_file(cmakelists, "add_subdirectory (tools)", "")
            tools.replace_in_file(os.path.join(self._source_subfolder, "cmake", "CMakeLists.txt"),
                                  "${TOOLS}", "")

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["GEOGRAPHICLIB_LIB_TYPE"] = "SHARED" if self.options.shared else "STATIC"
            self._cmake.definitions["GEOGRAPHICLIB_PRECISION"] = self._cmake_option_precision
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    @property
    def _cmake_option_precision(self):
        return {
            "float": 1,
            "double": 2,
            "extended": 3,
            "quadruple": 4,
            "variable": 5,
        }.get(str(self.options.precision))

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        for folder in ["share", os.path.join("lib", "python"), os.path.join("lib", "pkgconfig"),
                       os.path.join("lib", "cmake"), "sbin", "python", "matlab", "doc", "cmake"]:
            tools.rmdir(os.path.join(os.path.join(self.package_folder, folder)))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*.pdb")

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "geographiclib"
        self.cpp_info.filenames["cmake_find_package_multi"] = "geographiclib"
        self.cpp_info.names["cmake_find_package"] = "GeographicLib"
        self.cpp_info.names["cmake_find_package_multi"] = "GeographicLib"
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.defines.append("GEOGRAPHICLIB_SHARED_LIB={}".format("1" if self.options.shared else "0"))

        if self.options.tools:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
