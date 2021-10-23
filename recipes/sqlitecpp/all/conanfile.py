from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.33.0"


class SQLiteCppConan(ConanFile):
    name = "sqlitecpp"
    description = "SQLiteCpp is a smart and easy to use C++ sqlite3 wrapper"
    topics = ("sqlitecpp", "sqlite3")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/SRombauts/SQLiteCpp"
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "lint": [True, False, "deprecated"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "lint": "deprecated",
    }

    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.options.lint != "deprecated":
            self.output.warn("lint option is deprecated, do not use anymore")

    def requirements(self):
        self.requires("sqlite3/3.36.0")

    def validate(self):
        if tools.Version(self.version) >= "3.0.0" and self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("SQLiteCpp can not be built as shared lib on Windows")

    def package_id(self):
        del self.info.options.lint

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        if self.settings.compiler == "clang" and \
           tools.Version(self.settings.compiler.version) < "6.0" and \
           self.settings.compiler.libcxx == "libc++" and \
           tools.Version(self.version) < "3":
            tools.replace_in_file(
                os.path.join(self._source_subfolder, "include", "SQLiteCpp", "Utils.h"),
                "const nullptr_t nullptr = {};",
                "")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["SQLITECPP_INTERNAL_SQLITE"] = False
        self._cmake.definitions["SQLITECPP_RUN_CPPLINT"] = False
        self._cmake.definitions["SQLITECPP_RUN_CPPCHECK"] = False
        self._cmake.definitions["SQLITECPP_RUN_DOXYGEN"] = False
        self._cmake.definitions["SQLITECPP_BUILD_EXAMPLES"] = False
        self._cmake.definitions["SQLITECPP_BUILD_TESTS"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"SQLiteCpp": "SQLiteCpp::SQLiteCpp"}
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
        tools.save(module_file, content)

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file_rel_path(self):
        return os.path.join(self._module_subfolder,
                            "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "SQLiteCpp"
        self.cpp_info.names["cmake_find_package_multi"] = "SQLiteCpp"
        self.cpp_info.builddirs.append(self._module_subfolder)
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.libs = ["SQLiteCpp"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "dl", "m"]
