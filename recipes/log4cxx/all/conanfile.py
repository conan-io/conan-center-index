from conan import ConanFile
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, save
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.scm import Version
from conan.tools.build import check_min_cppstd
from conan.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.54.0"


class Log4cxxConan(ConanFile):
    name = "log4cxx"
    description = "Logging framework for C++ patterned after Apache log4j"
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"
    homepage = "https://logging.apache.org/log4cxx"
    topics = ("logging")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "char_type": ["utf-8", "wchar_t", "unichar"],
        "char_encoding": ["utf-8", "locale"],
        "with_networking": [True, False],
        "with_wchar_t": [True, False],
        "with_fmt_layout": [True, False],
        "with_odbc_appender": [True, False],
        "with_multiprocess_rolling_file_appender": [True, False],
        "with_smtp_appender": [True, False],
        "with_qt": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "char_type": "utf-8",
        "char_encoding": "utf-8",
        "with_networking": True,
        "with_wchar_t": False,
        "with_fmt_layout": False,
        "with_odbc_appender": False,
        "with_multiprocess_rolling_file_appender": False,
        "with_smtp_appender": False,
        "with_qt": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")
            self.options.rm_safe("with_smtp_appender") # *nix only
        elif Version(self.version) <= "1.0.0": # SMTP appender is broken in version 0.12 through 1.0.0
            self.options.rm_safe("with_smtp_appender")
        if Version(self.version) < "1.0.0":
            self.options.rm_safe("with_multiprocess_rolling_file_appender")
            self.options.rm_safe("with_networking")
            self.options.rm_safe("with_fmt_layout")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("apr/1.7.0")
        self.requires("apr-util/1.6.1")
        if self.options.get_safe("with_odbc_appender") and self.settings.os != "Windows":
            self.requires("odbc/2.3.11")
        if self.options.get_safe("with_smtp_appender"):
            self.requires("libesmtp/1.1.0")
        if self.options.get_safe("with_fmt_layout"):
            self.requires("fmt/9.1.0")
        if self.options.get_safe("with_qt"):
            self.requires("qt/5.15")

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "Visual Studio": "15",
            "msvc": "191",
            "clang": "5",
            "apple-clang": "10",
        }

    def validate(self):
        if Version(self.version) < "1.0.0" or self.options.get_safe("with_multiprocess_rolling_file_appender"):
            # TODO: if compiler doesn't support C++17, boost can be used instead
            if Version(self.version) < "1.0.0":
                self.output.info(f"Version {self.version} requires C++17. log4cxx version 1.1.0 does not.")
            else:
                self.output.info("multiprocess rolling file appender requires C++17.")
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            compiler_version = Version(self.settings.compiler.version)
            if not minimum_version:
                self.output.warning("Your compiler is unknown. Assuming it supports C++17.")
            elif compiler_version < minimum_version:
                raise ConanInvalidConfiguration(f"{self.settings.compiler} {compiler_version} does not support C++17: {minimum_version} required.")
            if self.settings.compiler.get_safe("cppstd"):
                check_min_cppstd(self, "17")
        elif self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, "11")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _patch_sources(self):
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        if Version(self.version) >= "1.0.0":
            tc.variables["LOG4CXX_NETWORKING_SUPPORT"] = self.options.with_networking
            tc.variables["LOG4CXX_MULTIPROCESS_ROLLING_FILE_APPENDER"] = self.options.with_multiprocess_rolling_file_appender
            tc.variables["ENABLE_FMT_LAYOUT"] = self.options.with_fmt_layout
        if Version(self.version) > "1.0.0" and self.settings.os != "Windows":
            tc.variables["LOG4CXX_ENABLE_ESMTP"] = self.options.with_smtp_appender
        tc.variables["LOG4CXX_ENABLE_ODBC"] = self.options.with_odbc_appender
        tc.variables["LOG4CXX_CHAR"] = self.options.char_type
        tc.variables["LOG4CXX_CHARSET"] = self.options.char_encoding
        tc.variables["LOG4CXX_WCHAR_T"] = self.options.with_wchar_t
        tc.variables["LOG4CXX_QT_SUPPORT"] = self.options.with_qt
        if self.settings.os == "Windows":
            tc.variables["LOG4CXX_INSTALL_PDB"] = False
        tc.generate()

        tc = CMakeDeps(self)
        if Version(self.version) < "0.13.0":
            tc.set_property("expat", "cmake_target_name", "EXPAT::EXPAT")
        tc.generate()

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "NOTICE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"log4cxx": "log4cxx::log4cxx"}
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "log4cxx")
        self.cpp_info.set_property("cmake_target_name", "log4cxx")
        self.cpp_info.set_property("pkg_config_name", "liblog4cxx")
        if not self.options.shared:
            self.cpp_info.defines = ["LOG4CXX_STATIC"]
        self.cpp_info.libs = ["log4cxx"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["odbc32"]

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.names["pkg_config"] = "liblog4cxx"
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
