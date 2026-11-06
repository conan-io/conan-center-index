from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, load, apply_conandata_patches
from conan.tools.scm import Version
import os
import re

required_conan_version = ">=2.0.9"

class QtLoggerConan(ConanFile):
    name = "qtlogger"
    description = "Advanced Qt logging library with configurable pipelines, formatters, and sinks"
    license = "MIT"
    url = "https://github.com/yamixst/qtlogger"
    homepage = "https://github.com/yamixst/qtlogger"
    topics = ("qt", "logging", "logger", "qt6")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_network": [True, False],
        "with_thread": [True, False],
        "with_journal": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_network": False,
        "with_thread": True,
        "with_journal": False,
    }

    @property
    def _min_qt_version(self):
        return "6.0"

    def set_version(self):
        version_h = load(self, os.path.join(self.recipe_folder, "src", "qtlogger", "version.h"))
        match = re.search(r"#define\s+QTLOGGER_VERSION\s+([0-9]+\.[0-9]+\.[0-9]+)", version_h)
        if not match:
            raise ConanInvalidConfiguration("Unable to determine version from src/qtlogger/version.h")
        self.version = match.group(1)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

        self.options["qt"].gui = False
        self.options["qt"].widgets = False

    def layout(self):
        cmake_layout(self, src_folder=".")

    def requirements(self):
        qt_ref = f"qt/[>={self._min_qt_version} <7]"
        self.requires(qt_ref, transitive_headers=True, transitive_libs=True)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 17)

        qt = self.dependencies["qt"]
        if Version(str(qt.ref.version)) < self._min_qt_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires qt version >= {self._min_qt_version}"
            )

        if self.options.with_journal:
            raise ConanInvalidConfiguration(
                "with_journal is not supported in this Conan recipe because it requires the system libsystemd"
            )

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["QTLOGGER_NO_EXAMPLES"] = True
        tc.variables["QTLOGGER_NO_TESTS"] = True
        tc.variables["QTLOGGER_LIBRARY"] = self.options.shared
        tc.variables["QTLOGGER_NETWORK"] = self.options.with_network
        tc.variables["QTLOGGER_NO_THREAD"] = not self.options.with_thread
        tc.variables["QTLOGGER_JOURNAL"] = self.options.with_journal
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["qtlogger"]
        self.cpp_info.requires = ["qt::qtCore"]
        self.cpp_info.set_property("cmake_file_name", "qtlogger")
        self.cpp_info.set_property("cmake_target_name", "qtlogger::qtlogger")

        if self.options.with_network:
            self.cpp_info.requires.append("qt::qtNetwork")

        if not self.options.with_thread:
            self.cpp_info.defines.append("QTLOGGER_NO_THREAD")

        if self.options.with_network:
            self.cpp_info.defines.append("QTLOGGER_NETWORK")

        if not self.options.shared:
            self.cpp_info.defines.append("QTLOGGER_STATIC")

        if self.settings.os == "Macos":
            self.cpp_info.defines.append("QTLOGGER_OSLOG")
        elif self.settings.os == "Android":
            self.cpp_info.defines.append("QTLOGGER_ANDROIDLOG")
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.defines.append("QTLOGGER_SYSLOG")
