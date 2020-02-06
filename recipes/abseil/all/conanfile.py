import os
import glob
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class ConanRecipe(ConanFile):
    name = "abseil"

    description = "Abseil Common Libraries (C++) from Google"
    topics = ("algorithm", "container", "google", "common", "utility")

    homepage = "https://github.com/abseil/abseil-cpp"
    url = "https://github.com/conan-io/conan-center-index"

    license = "Apache-2.0"

    settings = "os", "arch", "compiler", "build_type"

    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}

    generators = "cmake"
    short_paths = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob('abseil-cpp-*/')[0]
        os.rename(extracted_dir, self._source_subfolder)
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "project(absl CXX)", """project(absl CXX)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()""")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        minimal_cpp_standard = "11"
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, minimal_cpp_standard)

        minimal_version = {
            "Visual Studio": "14",
        }

        compiler = str(self.settings.compiler)
        if compiler not in minimal_version:
            self.output.warn(
                "%s recipe lacks information about the %s compiler support" % (self.name, compiler))
            self.output.warn(
                "%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))
            return

        version = tools.Version(self.settings.compiler.version)
        if version < minimal_version[compiler]:
            raise ConanInvalidConfiguration(
                "%s requires at least %s %s" % (self.name, compiler, minimal_version[compiler]))

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TESTING"] = False
        cmake.configure(
            source_folder=self._source_subfolder
        )
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = [
            "absl_spinlock_wait",
            "absl_dynamic_annotations",
            "absl_malloc_internal",
            "absl_raw_logging_internal",
            "absl_base",
            "absl_throw_delegate",
            "absl_scoped_set_env",
            "absl_hashtablez_sampler",
            "absl_raw_hash_set",
            "absl_stacktrace",
            "absl_symbolize",
            "absl_examine_stack",
            "absl_failure_signal_handler",
            "absl_debugging_internal",
            "absl_demangle_internal",
            "absl_leak_check",
            "absl_leak_check_disable",
            "absl_flags_internal",
            "absl_flags_config",
            "absl_flags_marshalling",
            "absl_flags_registry",
            "absl_flags",
            "absl_flags_usage_internal",
            "absl_flags_usage",
            "absl_flags_parse",
            "absl_hash",
            "absl_city ",
            "absl_int128",
            "absl_strings",
            "absl_strings_internal",
            "absl_str_format_internal",
            "absl_graphcycles_internal",
            "absl_synchronization",
            "absl_time absl_civil_time",
            "absl_time_zone",
            "absl_bad_any_cast_impl",
            "absl_bad_optional_access",
            "absl_bad_variant_access",
            "absl_bad_variant_access",
            "absl_hashtablez_sampler",
            "absl_examine_stack",
            "absl_leak_check",
            "absl_flags_usage",
            "absl_flags_usage_internal",
            "absl_flags",
            "absl_flags_registry",
            "absl_flags_config",
            "absl_flags_internal",
            "absl_flags_marshalling",
            "absl_str_format_internal",
            "absl_bad_optional_access",
            "absl_synchronization",
            "absl_stacktrace",
            "absl_symbolize",
            "absl_debugging_internal",
            "absl_demangle_internal",
            "absl_graphcycles_internal",
            "absl_malloc_internal",
            "absl_time absl_strings",
            "absl_throw_delegate",
            "absl_strings_internal",
            "absl_civil_time",
            "absl_time_zone",
            "absl_int128",
            "absl_base ",
            "absl_spinlock_wait",
            "absl_dynamic_annotations",
            "absl_exponential_biased"
        ]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
        self.cpp_info.names["cmake_find_package"] = "absl"
        self.cpp_info.names["cmake_find_package_multi"] = "absl"
