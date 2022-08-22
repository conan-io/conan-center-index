from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rmdir
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.50.0"


class G3logConan(ConanFile):
    name = "g3log"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/KjellKod/g3log"
    license = "The Unlicense"
    description = (
        "G3log is an asynchronous, \"crash safe\", logger that is easy to use "
        "with default logging sinks or you can add your own."
    )
    topics = ("g3log", "log")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_dynamic_logging_levels": [True, False],
        "change_debug_to_dbug": [True, False],
        "use_dynamic_max_message_size": [True, False],
        "log_full_filename": [True, False],
        "enable_fatal_signal_handling": [True, False],
        "enable_vectored_exception_handling": [True, False],
        "debug_break_at_fatal_signal": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_dynamic_logging_levels": False,
        "change_debug_to_dbug": False,
        "use_dynamic_max_message_size": True,
        "log_full_filename": False,
        "enable_fatal_signal_handling": True,
        "enable_vectored_exception_handling": True,
        "debug_break_at_fatal_signal": False,
    }

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "6.1",
            "clang": "3.4",
            "apple-clang": "5.1",
            "Visual Studio": "15",
        }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not is_msvc(self):
            del self.options.enable_vectored_exception_handling
            del self.options.debug_break_at_fatal_signal

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, "14")

        def loose_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.info.settings.compiler), False)
        if minimum_version and loose_lt_semver(str(self.info.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(
                "{} requires C++14, which your compiler does not support.".format(self.name)
            )

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["VERSION"] = self.version
        tc.variables["G3_SHARED_LIB"] = self.options.shared
        tc.variables["USE_DYNAMIC_LOGGING_LEVELS"] = self.options.use_dynamic_logging_levels
        tc.variables["CHANGE_G3LOG_DEBUG_TO_DBUG"] = self.options.change_debug_to_dbug
        tc.variables["USE_G3_DYNAMIC_MAX_MESSAGE_SIZE"] = self.options.use_dynamic_max_message_size
        tc.variables["G3_LOG_FULL_FILENAME"] = self.options.log_full_filename
        tc.variables["ENABLE_FATAL_SIGNALHANDLING"] = self.options.enable_fatal_signal_handling
        if is_msvc(self):
            tc.variables["ENABLE_VECTORED_EXCEPTIONHANDLING"] = self.options.enable_vectored_exception_handling
            tc.variables["DEBUG_BREAK_AT_FATAL_SIGNAL"] = self.options.debug_break_at_fatal_signal
        tc.variables["ADD_FATAL_EXAMPLE"] = "OFF"
        tc.variables["ADD_G3LOG_PERFORMANCE"] = "OFF"
        tc.variables["ADD_G3LOG_UNIT_TEST"] = "OFF"
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["g3logger"]
        if self.settings.os in ["Linux", "Android"]:
            self.cpp_info.system_libs.append("pthread")
