from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os


required_conan_version = ">=2.0.9"


class HsmcppConan(ConanFile):
    name = "hsmcpp"
    package_type = "library"
    description = (
        "C++ library for hierarchical state machines / finite state machines. "
        "Provides a code-free visual approach for defining state machine logic "
        "using GUI editors with automatic code and diagram generation."
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/igor-krechetov/hsmcpp"
    topics = ("fsm", "hsm", "state-machine", "hierarchical", "embedded", "scxml")

    settings = "os", "compiler", "build_type", "arch"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_std_dispatcher": [True, False],
        "with_glib_dispatcher": [True, False],
        "with_glibmm_dispatcher": [True, False],
        "with_qt_dispatcher": [True, False],
        "enable_thread_safety": [True, False],
        "enable_debugging": [True, False],
        "enable_structure_validation": [True, False],
        "enable_verbose_logging": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_std_dispatcher": True,
        "with_glib_dispatcher": False,
        "with_glibmm_dispatcher": False,
        "with_qt_dispatcher": False,
        "enable_thread_safety": True,
        "enable_debugging": True,
        "enable_structure_validation": True,
        "enable_verbose_logging": False,
    }

    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_glib_dispatcher or self.options.with_glibmm_dispatcher:
            self.requires("glib/2.78.3")
        if self.options.with_glibmm_dispatcher:
            self.requires("glibmm/2.66.6")
        if self.options.with_qt_dispatcher:
            self.requires("qt/[>=6.0 <7]")

    def validate(self):
        check_min_cppstd(self, 11)
        if self.options.shared:
            raise ConanInvalidConfiguration(
                f"{self.ref} does not support shared library builds yet."
            )
        if self.options.with_qt_dispatcher:
            check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["HSMBUILD_TARGET"] = "library"
        tc.variables["HSMBUILD_PLATFORM"] = self._get_platform()
        tc.variables["HSMBUILD_TESTS"] = False
        tc.variables["HSMBUILD_EXAMPLES"] = False
        tc.variables["HSMBUILD_DISPATCHER_STD"] = self.options.with_std_dispatcher
        tc.variables["HSMBUILD_DISPATCHER_GLIB"] = self.options.with_glib_dispatcher
        tc.variables["HSMBUILD_DISPATCHER_GLIBMM"] = self.options.with_glibmm_dispatcher
        tc.variables["HSMBUILD_DISPATCHER_QT"] = self.options.with_qt_dispatcher
        tc.variables["HSMBUILD_DISPATCHER_FREERTOS"] = False
        tc.variables["HSMBUILD_THREAD_SAFETY"] = self.options.enable_thread_safety
        tc.variables["HSMBUILD_DEBUGGING"] = self.options.enable_debugging
        tc.variables["HSMBUILD_STRUCTURE_VALIDATION"] = self.options.enable_structure_validation
        tc.variables["HSMBUILD_VERBOSE"] = self.options.enable_verbose_logging
        tc.variables["HSMBUILD_CODECOVERAGE"] = False
        tc.variables["HSMBUILD_CLANGTIDY"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _get_platform(self):
        if self.settings.os == "Windows":
            return "windows"
        return "posix"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        # Keep scxml2gen (code generator tool), remove only the config/version cmake files
        # that conflict with Conan-generated ones
        cmake_dir = os.path.join(self.package_folder, "lib", "cmake", "hsmcpp")
        for f in ["hsmcpp-config.cmake", "hsmcpp-configVersion.cmake",
                  "hsmcpp-std.cmake", "hsmcpp-glib.cmake", "hsmcpp-glibmm.cmake", "hsmcpp-qt.cmake"]:
            fpath = os.path.join(cmake_dir, f)
            if os.path.isfile(fpath):
                os.remove(fpath)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "hsmcpp")
        self.cpp_info.set_property("cmake_target_name", "hsmcpp::hsmcpp")
        self.cpp_info.set_property("pkg_config_name", "hsmcpp")

        # Expose scxml2gen cmake module directory so consumers can use generateHsm()
        self.cpp_info.builddirs.append(os.path.join("lib", "cmake", "hsmcpp", "scxml2gen"))

        if self.options.with_qt_dispatcher:
            self.cpp_info.libs.append("hsmcpp_qt")
        if self.options.with_glibmm_dispatcher:
            self.cpp_info.libs.append("hsmcpp_glibmm")
        if self.options.with_glib_dispatcher:
            self.cpp_info.libs.append("hsmcpp_glib")
        if self.options.with_std_dispatcher:
            self.cpp_info.libs.append("hsmcpp_std")
        self.cpp_info.libs.append("hsmcpp")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")

        if not self.options.enable_thread_safety:
            self.cpp_info.defines.append("HSM_DISABLE_THREADSAFETY")
        if self.options.enable_verbose_logging:
            self.cpp_info.defines.append("HSM_LOGGING_MODE_STRICT_VERBOSE")
        if self.options.enable_structure_validation:
            self.cpp_info.defines.append("HSM_ENABLE_SAFE_STRUCTURE")
        if self.options.enable_debugging:
            self.cpp_info.defines.append("HSMBUILD_DEBUGGING")
