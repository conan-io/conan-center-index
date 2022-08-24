from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class GeographiclibConan(ConanFile):
    name = "geographiclib"
    description = "Convert geographic units and solve geodesic problems"
    topics = ("geographiclib", "geodesic")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://geographiclib.sourceforge.io"
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "precision": ["float", "double", "extended", "quadruple", "variable"],
        "tools": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "precision": "double",
        "tools": True,
    }

    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

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

    @property
    def _min_compiler_version_default_cxx11(self):
        # Minimum compiler version having C++11 math functions
        return {
            "apple-clang": "3.3",
            "gcc": "4.9",
            "clang": "6",
            "Visual Studio": "14",  # guess
        }.get(str(self.settings.compiler), False)

    def validate(self):
        if tools.scm.Version(self.version) >= "1.51":
            if self.settings.compiler.get_safe("cppstd"):
                tools.build.check_min_cppstd(self, 11)

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
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmakelists = os.path.join(self._source_subfolder, "CMakeLists.txt")
        # it does not work on Windows but is not needed
        tools.files.replace_in_file(self, cmakelists, "add_subdirectory (js)", "")
        # Don't install system libs
        tools.files.replace_in_file(self, cmakelists, "include (InstallRequiredSystemLibraries)", "")
        # Don't build tools if asked
        if not self.options.tools:
            tools.files.replace_in_file(self, cmakelists, "add_subdirectory (tools)", "")
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "cmake", "CMakeLists.txt"),
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
            tools.files.rmdir(self, os.path.join(os.path.join(self.package_folder, folder)))
        tools.files.rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "geographiclib")
        self.cpp_info.set_property("cmake_target_name", "GeographicLib::GeographicLib")
        self.cpp_info.libs = tools.files.collect_libs(self, self)
        self.cpp_info.defines.append("GEOGRAPHICLIB_SHARED_LIB={}".format("1" if self.options.shared else "0"))

        if self.options.tools:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "geographiclib"
        self.cpp_info.filenames["cmake_find_package_multi"] = "geographiclib"
        self.cpp_info.names["cmake_find_package"] = "GeographicLib"
        self.cpp_info.names["cmake_find_package_multi"] = "GeographicLib"
