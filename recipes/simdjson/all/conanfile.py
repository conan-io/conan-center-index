from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class SimdjsonConan(ConanFile):
    name = "simdjson"
    description = "Parsing gigabytes of JSON per second"
    topics = ("json", "parser", "simd", "format")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lemire/simdjson"
    license = "Apache-2.0"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "threads": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "threads": True
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

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "Visual Studio": "16",
            "clang": "6",
            "apple-clang": "9.4",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("{} requires C++17. Your compiler is unknown. Assuming it supports C++17.".format(self.name))
        elif lazy_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration("{} requires C++17, which your compiler does not fully support.".format(self.name))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        if tools.Version(self.version) < "1.0.0":
            # Those flags are not set in 1.0.0 since SIMDJSON_DEVELOPER_MODE is disabled in non-top project
            simd_flags_file = os.path.join(self._source_subfolder, "cmake", "simdjson-flags.cmake")
            tools.replace_in_file(simd_flags_file, "target_compile_options(simdjson-internal-flags INTERFACE -fPIC)", "")
            tools.replace_in_file(simd_flags_file, "-Werror", "")
            tools.replace_in_file(simd_flags_file, "/WX", "")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["SIMDJSON_ENABLE_THREADS"] = self.options.threads
        if tools.Version(self.version) < "1.0.0":
            self._cmake.definitions["SIMDJSON_BUILD_STATIC"] = not self.options.shared
            self._cmake.definitions["SIMDJSON_SANITIZE"] = False
            self._cmake.definitions["SIMDJSON_JUST_LIBRARY"] = True
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        self.cpp_info.libs = ["simdjson"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]
        if self.options.threads:
            self.cpp_info.defines = ["SIMDJSON_THREADS_ENABLED=1"]
            if self.settings.os == "Linux":
                self.cpp_info.system_libs.append("pthread")
        if self.options.shared:
            self.cpp_info.defines.append("SIMDJSON_USING_LIBRARY=1")
            if tools.Version(self.version) >= "0.9.0" and self.settings.compiler == "Visual Studio":
                self.cpp_info.defines.append("SIMDJSON_USING_WINDOWS_DYNAMIC_LIBRARY=1")
