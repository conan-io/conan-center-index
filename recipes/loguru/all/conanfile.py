import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, load, save
from conan.tools.build import check_min_cppstd


required_conan_version = ">=1.53.0"


class LoguruConan(ConanFile):
    name = "loguru"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = 'CMakeLists.txt'
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/emilk/loguru"
    license = "Unlicense"
    topics = ("logging", "log", "fmt")
    description = "Loguru is a C++11 logging library."

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_fmtlib": [True, False],
        "catch_sigabrt": [True, False],
        "verbose_scope_endings": [True, False],
        "redefine_assert": [True, False],
        "with_streams": [True, False],
        "with_fileabs": [True, False],
        "with_rtti": [True, False],
        "replace_glog": [True, False],

        "scope_text_size": [None, "ANY"],
        "filename_width": [None, "ANY"],
        "threadname_width": [None, "ANY"],
        "scope_time_precision": [None, "ANY"]
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "use_fmtlib": False,
        "catch_sigabrt": True,
        "verbose_scope_endings": True,
        "redefine_assert": False,
        "with_streams": False,
        "with_fileabs": False,
        "with_rtti": True,
        "replace_glog": False,
        "scope_text_size": 196,
        "filename_width": 23,
        "threadname_width": 16,
        "scope_time_precision": 3,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        if self.options.use_fmtlib:
            self.requires("fmt/9.1.0", transitive_headers=True)

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder='src')

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LOGURU_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.variables["LOGURU_USE_FMTLIB"] = self.options.use_fmtlib
        tc.variables["LOGURU_CATCH_SIGABRT"] = int(eval(self.options.catch_sigabrt.value))
        tc.variables["LOGURU_VERBOSE_SCOPE_ENDINGS"] = int(eval(self.options.verbose_scope_endings.value))
        tc.variables["LOGURU_REDEFINE_ASSERT"] = int(eval(self.options.redefine_assert.value))
        tc.variables["LOGURU_WITH_STREAMS"] = int(eval(self.options.with_streams.value))
        tc.variables["LOGURU_WITH_FILEABS"] = int(eval(self.options.with_fileabs.value))
        tc.variables["LOGURU_RTTI"] = int(eval(self.options.with_rtti.value))
        tc.variables["LOGURU_REPLACE_GLOG"] = int(eval(self.options.replace_glog.value))
        tc.variables["LOGURU_SCOPE_TEXT_SIZE"] = self.options.scope_text_size
        tc.variables["LOGURU_FILENAME_WIDTH"] = self.options.filename_width
        tc.variables["LOGURU_THREADNAME_WIDTH"] = self.options.threadname_width
        tc.variables["LOGURU_SCOPE_TIME_PRECISION"] = self.options.scope_time_precision
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

        self.cpp_info.defines.append(f"LOGURU_SCOPE_TEXT_SIZE={self.options.scope_text_size}")
        self.cpp_info.defines.append(f"LOGURU_FILENAME_WIDTH={self.options.filename_width}")
        self.cpp_info.defines.append(f"LOGURU_THREADNAME_WIDTH={self.options.threadname_width}")
        self.cpp_info.defines.append(f"LOGURU_SCOPE_TIME_PRECISION={self.options.scope_time_precision}")
        self.cpp_info.defines.append(f"LOGURU_USE_FMTLIB={int(eval(self.options.use_fmtlib.value))}")
        self.cpp_info.defines.append(f"LOGURU_CATCH_SIGABRT={int(eval(self.options.catch_sigabrt.value))}")
        self.cpp_info.defines.append(f"LOGURU_VERBOSE_SCOPE_ENDINGS={int(eval(self.options.verbose_scope_endings.value))}")
        self.cpp_info.defines.append(f"LOGURU_REDEFINE_ASSERT={int(eval(self.options.redefine_assert.value))}")
        self.cpp_info.defines.append(f"LOGURU_WITH_STREAMS={int(eval(self.options.with_streams.value))}")
        self.cpp_info.defines.append(f"LOGURU_WITH_FILEABS={int(eval(self.options.with_fileabs.value))}")
        self.cpp_info.defines.append(f"LOGURU_RTTI={int(eval(self.options.with_rtti.value))}")
        self.cpp_info.defines.append(f"LOGURU_REPLACE_GLOG={int(eval(self.options.replace_glog.value))}")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "dl"]
