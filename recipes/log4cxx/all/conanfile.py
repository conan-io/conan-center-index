from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.43.0"


class Log4cxxConan(ConanFile):
    name = "log4cxx"
    description = "Logging framework for C++ patterned after Apache log4j"
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"
    homepage = "https://logging.apache.org/log4cxx"
    topics = ("logging", "log")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake", "cmake_find_package", "pkg_config"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("apr/1.7.0")
        self.requires("apr-util/1.6.1")
        self.requires("expat/2.4.2")
        if self.settings.os != "Windows":
            self.requires("odbc/2.3.9")

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "Visual Studio": "15",
            "clang": "5",
            "apple-clang": "10",
        }

    def validate(self):
        # TODO: if compiler doesn't support C++17, boost can be used instead
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, "17")
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("log4cxx requires C++17. Your compiler is unknown. Assuming it supports C++17.")
        elif tools.scm.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("log4cxx requires a compiler that supports at least C++17")

    def build_requirements(self):
        if self.settings.os != "Windows":
            self.build_requires("pkgconf/1.7.4")

    def source(self):
        #OSError: [WinError 123] The filename, directory name, or volume label syntax is incorrect:
        #'source_subfolder\\src\\test\\resources\\output\\xyz\\:'
        pattern = "*[!:]"
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True,
                  pattern=pattern)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["BUILD_TESTING"] = False
            if self.settings.os == "Windows":
                self._cmake.definitions["LOG4CXX_INSTALL_PDB"] = False
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy("NOTICE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"log4cxx": "log4cxx::log4cxx"}
        )

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        tools.files.save(self, module_file, content)

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
