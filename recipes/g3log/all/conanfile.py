from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import export_conandata_patches, apply_conandata_patches, copy, get, rmdir, save
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.53.0"


class G3logConan(ConanFile):
    name = "g3log"
    description = (
        "G3log is an asynchronous, \"crash safe\", logger that is easy to use "
        "with default logging sinks or you can add your own."
    )
    license = "The Unlicense"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/KjellKod/g3log"
    topics = ("logging", "log", "asynchronous")
    package_type = "library"
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
    def _min_cppstd(self):
        return "14" if Version(self.version) < "2.0" else "17"

    @property
    def _compilers_minimum_version(self):
        return {
            "14": {
                "gcc": "6.1",
                "clang": "3.4",
                "apple-clang": "5.1",
                "Visual Studio": "15",
                "msvc": "191",
            },
            "17": {
                "gcc": "8",
                "clang": "7",
                "apple-clang": "12",
                "Visual Studio": "16",
                "msvc": "192",
            },
        }.get(self._min_cppstd, {})

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not is_msvc(self):
            del self.options.enable_vectored_exception_handling
            del self.options.debug_break_at_fatal_signal

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        def loose_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and loose_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

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

        # TODO: to remove in conan v2 once legacy generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"g3log": "g3log::g3log"},
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "g3log")
        self.cpp_info.set_property("cmake_target_name", "g3log")
        self.cpp_info.libs = ["g3logger" if Version(self.version) < "1.3.4" else "g3log"]

        if self.settings.os in ["Linux", "FreeBSD", "Android"]:
            self.cpp_info.system_libs.extend(["m", "pthread", "rt"])
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("dbghelp")

        # TODO: to remove in conan v2 once legacy generators removed
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
