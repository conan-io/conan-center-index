import os

from conan import ConanFile
from conan.error import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, load, save
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
        cmake = CMake(self)
        cmake.install()

        copy(self, pattern='loguru.hpp', src=self.source_folder, dst=os.path.join(self.package_folder, 'include'))
        save(self, os.path.join(self.package_folder, 'licenses', 'LICENSE'), self._extracted_license)

    def package_info(self):
        self.cpp_info.libs = ["loguru"]
        # https://github.com/emilk/loguru/blob/4adaa185883e3c04da25913579c451d3c32cfac1/CMakeLists.txt#L301
        self.cpp_info.set_property("cmake_file_name", "loguru")
        self.cpp_info.set_property("cmake_target_name", "loguru::loguru")

        self.cpp_info.defines.append(f"LOGURU_SCOPE_TEXT_SIZE={self.options.scope_text_size}")
        self.cpp_info.defines.append(f"LOGURU_FILENAME_WIDTH={self.options.filename_width}")
        self.cpp_info.defines.append(f"LOGURU_THREADNAME_WIDTH={self.options.threadname_width}")
        self.cpp_info.defines.append(f"LOGURU_SCOPE_TIME_PRECISION={self.options.scope_time_precision}")
        self.cpp_info.defines.append(f"LOGURU_USE_FMTLIB={self.options.with_fmt.value}")
        self.cpp_info.defines.append(f"LOGURU_CATCH_SIGABRT={self.options.catch_sigabrt.value}")
        self.cpp_info.defines.append(f"LOGURU_VERBOSE_SCOPE_ENDINGS={self.options.verbose_scope_endings.value}")
        self.cpp_info.defines.append(f"LOGURU_REDEFINE_ASSERT={self.options.redefine_assert.value}")
        self.cpp_info.defines.append(f"LOGURU_WITH_STREAMS={self.options.enable_streams.value}")
        self.cpp_info.defines.append(f"LOGURU_WITH_FILEABS={self.options.enable_fileabs.value}")
        self.cpp_info.defines.append(f"LOGURU_RTTI={self.options.with_rtti.value}")
        self.cpp_info.defines.append(f"LOGURU_REPLACE_GLOG={self.options.replace_glog.value}")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "dl"]
