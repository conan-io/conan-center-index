import os
import glob
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration, ConanException


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

        try:
            tools.check_min_cppstd(self, minimal_cpp_standard)
        except ConanInvalidConfiguration:
            raise
        except ConanException:
            # FIXME: We need to handle the case when Conan doesn't know
            # about a user defined compiler's default standard version
            self.output.warn(
                "Unnable to determine the default standard version of the compiler")

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
            "absl_flags_parse",
            "absl_flags_usage",
            "absl_flags_usage_internal",
            "absl_flags",
            "absl_flags_internal",
            "absl_flags_registry",
            "absl_flags_config",
            "absl_flags_program_name",
            "absl_flags_marshalling",
            "absl_raw_hash_set",
            "absl_random_seed_sequences",
            "absl_hashtablez_sampler",
            "absl_synchronization",
            "absl_time",
            "absl_civil_time",
            "absl_time_zone",
            "absl_failure_signal_handler",
            "absl_random_internal_distribution_test_util",
            "absl_examine_stack",
            "absl_symbolize",
            "absl_str_format_internal",
            "absl_graphcycles_internal",
            "absl_stacktrace",
            "absl_malloc_internal",
            "absl_demangle_internal",
            "absl_debugging_internal",
            "absl_periodic_sampler",
            "absl_exponential_biased",
            "absl_random_internal_pool_urbg",
            "absl_random_distributions",
            "absl_random_internal_seed_material",
            "absl_random_seed_gen_exception",
            "absl_hash",
            "absl_strings",
            "absl_strings_internal",
            "absl_bad_variant_access",
            "absl_throw_delegate",
            "absl_city",
            "absl_base",
            "absl_dynamic_annotations",
            "absl_bad_any_cast_impl",
            "absl_scoped_set_env",
            "absl_bad_optional_access",
            "absl_raw_logging_internal",
            "absl_log_severity",
            "absl_spinlock_wait",
            "absl_random_internal_randen",
            "absl_random_internal_randen_hwaes",
            "absl_random_internal_randen_slow",
            "absl_random_internal_randen_hwaes_impl",
            "absl_leak_check",
            "absl_leak_check_disable",
            "absl_int128"
        ]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
        if self.settings.os == "Macos":
            self.cpp_info.frameworks.append("CoreFoundation")
        self.cpp_info.names["cmake_find_package"] = "absl"
        self.cpp_info.names["cmake_find_package_multi"] = "absl"
