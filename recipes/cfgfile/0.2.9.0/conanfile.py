from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import textwrap


class CfgfileConan(ConanFile):
    name = "cfgfile"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/igormironchik/cfgfile.git"
    license = "MIT"
    description = "Header-only library for reading/saving configuration files with schema defined in sources."
    exports_sources = "CMakeLists.txt"
    generators = "cmake", "cmake_find_package"
    topics = ("conan", "cfgfile", "configuration")
    settings = "os", "arch", "compiler", "build_type"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "5",
            "clang": "3.5",
            "apple-clang": "10"
        }

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file_rel_path(self):
        return os.path.join(self._module_subfolder,
                            "conan-official-{}-targets.cmake".format(self.name))

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

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_EXAMPLES"] = False
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["USE_INTERNAL_ARGS_PARSER"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "14")

        compiler = str(self.settings.compiler)
        if compiler not in self._compilers_minimum_version:
            self.output.warn("Unknown compiler, assuming it supports at least C++14")
            return

        version = tools.Version(self.settings.compiler.version)
        if version < self._compilers_minimum_version[compiler]:
            raise ConanInvalidConfiguration("cfgfile requires a compiler that supports at least C++14")

    def requirements(self):
        self.requires("args-parser/6.0.1.0")

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        self.copy("*.hpp", src=os.path.join(self._source_subfolder, "cfgfile"), dst=os.path.join("include", "cfgfile"))
        cmake = self._configure_cmake()
        cmake.install()
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"cfgfile": "cfgfile::cfgfile"}
        )

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with : {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
        self.cpp_info.names["cmake_find_package"] = "cfgfile"
        self.cpp_info.names["cmake_find_package_multi"] = "cfgfile"
        self.cpp_info.builddirs.append(self._module_subfolder)
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.includedirs.append(os.path.join("include", "cfgfile"))

    def package_id(self):
        del self.info.settings.compiler
