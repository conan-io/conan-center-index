import os

from conan import tools, ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, load, save
from conan.tools.build import check_min_cppstd

required_conan_version = ">=1.53.0"


def _int(flag):
    if flag is not None and flag:
        return "1"
    else:
        return "0"


class LoguruConan(ConanFile):
    name = "loguru"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = 'CMakeLists.txt'
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/emilk/loguru"
    license = "Unlicense"  # Public domain
    description = "Loguru is a C++11 logging library."

    options = {
        "use_fmtlib": [True, False],
        "shared": [True, False],
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
        "use_fmtlib": False,
        "shared": False,
        "catch_sigabrt": True,
        "verbose_scope_endings": True,
        "redefine_assert": False,
        "with_streams": False,
        "with_fileabs": False,
        "with_rtti": True,
        "replace_glog": False,

        "scope_text_size": None,         # default: 196
        "filename_width": None,          # default: 23
        "threadname_width": None,        # default: 16
        "scope_time_precision": None,    # 3=ms, 6=us, 9=ns, default: 3
    }

    def build_requirements(self):
        self.tool_requires("cmake/3.25.0")

    def requirements(self):
        if self.options.use_fmtlib:
            self.requires("fmt/9.1.0", transitive_headers=True)

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)

        tc.variables["LOGURU_USE_FMTLIB"] = self.options.use_fmtlib
        tc.variables["LOGURU_STATIC"] = not self.options.shared
        tc.variables["LOGURU_CATCH_SIGABRT"] = _int(self.options.catch_sigabrt)
        tc.variables["LOGURU_VERBOSE_SCOPE_ENDINGS"] = _int(self.options.verbose_scope_endings)
        tc.variables["LOGURU_REDEFINE_ASSERT"] = _int(self.options.redefine_assert)
        tc.variables["LOGURU_WITH_STREAMS"] = _int(self.options.with_streams)
        tc.variables["LOGURU_WITH_FILEABS"] = _int(self.options.with_fileabs)
        tc.variables["LOGURU_WITH_RTTI"] = _int(self.options.with_rtti)
        tc.variables["LOGURU_REPLACE_GLOG"] = _int(self.options.replace_glog)

        if self.options.scope_text_size:
            tc.variables["LOGURU_SCOPE_TEXT_SIZE"] = self.options.scope_text_size
        if self.options.filename_width:
            tc.variables["LOGURU_FILENAME_WIDTH"] = self.options.filename_width
        if self.options.threadname_width:
            tc.variables["LOGURU_THREADNAME_WIDTH"] = self.options.threadname_width
        if self.options.scope_time_precision:
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
        if self.options.use_fmtlib:
            self.cpp_info.components["libloguru"].defines.append("LOGURU_USE_FMTLIB")
            self.cpp_info.components["libloguru"].requires = ["fmt::fmt"]

        if self.options.scope_text_size:
            self.cpp_info.components["libloguru"].defines.append(f"LOGURU_SCOPE_TEXT_SIZE={self.options.scope_text_size}")
        if self.options.filename_width:
            self.cpp_info.components["libloguru"].defines.append(f"LOGURU_FILENAME_WIDTH={self.options.filename_width}")
        if self.options.threadname_width:
            self.cpp_info.components["libloguru"].defines.append(f"LOGURU_THREADNAME_WIDTH={self.options.threadname_width}")
        if self.options.scope_time_precision:
            self.cpp_info.components["libloguru"].defines.append(f"LOGURU_SCOPE_TIME_PRECISION={self.options.scope_time_precision}")

        self.cpp_info.components["libloguru"].defines.append(f"LOGURU_CATCH_SIGABRT={_int(self.options.catch_sigabrt)}")
        self.cpp_info.components["libloguru"].defines.append(f"LOGURU_VERBOSE_SCOPE_ENDINGS={_int(self.options.verbose_scope_endings)}")
        self.cpp_info.components["libloguru"].defines.append(f"LOGURU_REDEFINE_ASSERT={_int(self.options.redefine_assert)}")
        self.cpp_info.components["libloguru"].defines.append(f"LOGURU_WITH_STREAMS={_int(self.options.with_streams)}")
        self.cpp_info.components["libloguru"].defines.append(f"LOGURU_WITH_FILEABS={_int(self.options.with_fileabs)}")
        self.cpp_info.components["libloguru"].defines.append(f"LOGURU_WITH_RTTI={_int(self.options.with_rtti)}")
        self.cpp_info.components["libloguru"].defines.append(f"LOGURU_REPLACE_GLOG={_int(self.options.replace_glog)}")

        if not self.options.shared:
            self.cpp_info.components["libloguru"].defines.append("LOGURU_USE_STATIC")

        self.cpp_info.components["libloguru"].libs = ["loguru"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libloguru"].system_libs = ["pthread", "dl"]
