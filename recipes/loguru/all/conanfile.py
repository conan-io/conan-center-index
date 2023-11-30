import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.microsoft import is_msvc
from conan.tools.files import get, load, save, rmdir, rm
from conan.tools.build import check_min_cppstd


required_conan_version = ">=1.53.0"


class LoguruConan(ConanFile):
    name = "loguru"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/emilk/loguru"
    license = "Unlicense"
    topics = ("logging", "log", "fmt")
    description = "Loguru is a C++11 logging library."
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_fmt": [True, False],
        "verbose_scope_endings": [True, False],
        "redefine_assert": [True, False],
        "enable_streams": [True, False],
        "enable_fileabs": [True, False],
        "replace_glog": [True, False],

        "scope_text_size": [None, "ANY"],
        "scope_time_precision": [None, "ANY"],
        "filename_width": [None, "ANY"],
        "threadname_width": [None, "ANY"],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "with_fmt": False,
        "verbose_scope_endings": True,
        "redefine_assert": False,
        "enable_streams": False,
        "enable_fileabs": False,
        "replace_glog": False,
        "scope_text_size": 196,
        "scope_time_precision": 3,
        "filename_width": 23,
        "threadname_width": 16,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        if self.options.with_fmt:
            self.requires("fmt/9.1.0", transitive_headers=True)

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

        if self.options.replace_glog and not self.options.enable_streams:
            # https://github.com/emilk/loguru/blob/4adaa185883e3c04da25913579c451d3c32cfac1/docs/index.html#L692
            raise ConanInvalidConfiguration(f"{self.ref}:replace_glog needs {self.ref}:enable_streams=True")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder='src')

    def generate(self):
        tc = CMakeToolchain(self)

        tc.variables["LOGURU_USE_FMTLIB"] = self.options.with_fmt
        tc.variables["LOGURU_VERBOSE_SCOPE_ENDINGS"] = self.options.verbose_scope_endings
        tc.variables["LOGURU_REDEFINE_ASSERT"] = self.options.redefine_assert
        tc.variables["LOGURU_WITH_STREAMS"] = self.options.enable_streams
        tc.variables["LOGURU_WITH_FILEABS"] = self.options.enable_fileabs
        tc.variables["LOGURU_REPLACE_GLOG"] = self.options.replace_glog

        tc.variables["LOGURU_SCOPE_TEXT_SIZE"] = self.options.scope_text_size
        tc.variables["LOGURU_SCOPE_TIME_PRECISION"] = self.options.scope_time_precision
        tc.variables["LOGURU_FILENAME_WIDTH"] = self.options.filename_width
        tc.variables["LOGURU_THREADNAME_WIDTH"] = self.options.threadname_width

        if is_msvc(self) and self.options.shared:
            tc.preprocessor_definitions["LOGURU_EXPORT"] = "__declspec(dllexport)"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    @property
    def _extracted_license(self):
        tmp = load(self, os.path.join(self.source_folder, 'loguru.hpp'))
        return tmp[2:tmp.find("# Inspiration", 0)].strip()

    def package(self):
        save(self, os.path.join(self.package_folder, 'licenses', 'LICENSE'), self._extracted_license)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        suffix = "d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = [f"loguru{suffix}"]
        self.cpp_info.includedirs = [os.path.join("include", "loguru")]
        # https://github.com/emilk/loguru/blob/4adaa185883e3c04da25913579c451d3c32cfac1/CMakeLists.txt#L301
        self.cpp_info.set_property("cmake_file_name", "loguru")
        self.cpp_info.set_property("cmake_target_name", "loguru::loguru")

        # render each option as either 0 or 1 for loguru's #if preprocessor commands
        self.cpp_info.defines.append(f"LOGURU_USE_FMTLIB={bool(self.options.with_fmt)*1}")
        self.cpp_info.defines.append(f"LOGURU_VERBOSE_SCOPE_ENDINGS={bool(self.options.verbose_scope_endings)*1}")
        self.cpp_info.defines.append(f"LOGURU_REDEFINE_ASSERT={bool(self.options.redefine_assert)*1}")
        self.cpp_info.defines.append(f"LOGURU_WITH_STREAMS={bool(self.options.enable_streams)*1}")
        self.cpp_info.defines.append(f"LOGURU_WITH_FILEABS={bool(self.options.enable_fileabs)*1}")
        self.cpp_info.defines.append(f"LOGURU_REPLACE_GLOG={bool(self.options.replace_glog)*1}")

        self.cpp_info.defines.append(f"LOGURU_SCOPE_TEXT_SIZE={self.options.scope_text_size}")
        self.cpp_info.defines.append(f"LOGURU_SCOPE_TIME_PRECISION={self.options.scope_time_precision}")
        self.cpp_info.defines.append(f"LOGURU_FILENAME_WIDTH={self.options.filename_width}")
        self.cpp_info.defines.append(f"LOGURU_THREADNAME_WIDTH={self.options.threadname_width}")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "dl", "m"]
