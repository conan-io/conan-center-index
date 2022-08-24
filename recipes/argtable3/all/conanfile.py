from from conan import ConanFile, tools
from conans import CMake
import os
import textwrap

required_conan_version = ">=1.33.0"


class Argtable3Conan(ConanFile):
    name = "argtable3"
    description = "A single-file, ANSI C, command-line parsing library that parses GNU-style command-line options."
    topics = ("conan", "argtable3", "command", "line", "argument", "parse", "parsing", "getopt")
    license = "BSD-3-clause"
    homepage = "https://www.argtable.org/"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = "CMakeLists.txt", "patches/*"
    generators = "cmake"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ARGTABLE3_ENABLE_TESTS"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        # The initial space is important (the cmake script does OFFSET 0)
        tools.save(os.path.join(self._source_subfolder, "version.tag"), " {}.0\n".format(self.version))
        cmake = self._configure_cmake()
        cmake.build()

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

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        tools.files.rmdir(self, os.path.join(self.package_folder, "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

        # These targets were for versions <= 3.2.0 (newer create argtable3::argtable3)
        target_name = "argtable3" if self.options.shared else "argtable3_static"
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {target_name: "argtable3::argtable3"}
        )

    def package_info(self):
        suffix = ""
        if not self.options.shared:
            suffix += "_static"
        if tools.Version(self.version) >= "3.2.1" and self.settings.build_type == "Debug":
            suffix += "d"
        self.cpp_info.libs = ["argtable3{}".format(suffix)]
        if not self.options.shared:
            if self.settings.os in ("FreeBSD", "Linux"):
                self.cpp_info.system_libs.append("m")

        self.cpp_info.filenames["cmake_find_package"] = "Argtable3"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Argtable3"
        self.cpp_info.names["cmake_find_package"] = "argtable3"
        self.cpp_info.names["cmake_find_package_multi"] = "argtable3"

        self.cpp_info.builddirs.append(self._module_subfolder)
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
