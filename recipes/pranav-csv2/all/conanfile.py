import os
import functools
import textwrap

from conan.errors import ConanInvalidConfiguration
from conans import ConanFile, CMake, tools

required_conan_version = ">=1.33.0"

class PranavCSV2Conan(ConanFile):
    name = "pranav-csv2"
    license = "MIT"
    description = "Various header libraries mostly future std lib, replacements for(e.g. visit), or some misc"
    topics = ("csv", "iterator", "header-only", )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/p-ranav/csv2"
    settings = "os", "arch", "compiler", "build_type",
    generators = "cmake",
    no_copy_source = True

    _compiler_required_cpp11 = {
        "Visual Studio": "16",
        "gcc": "8",
        "clang": "7",
        "apple-clang": "12.0",
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            tools.check_min_cppstd(self, "11")

        minimum_version = self._compiler_required_cpp11.get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("{} requires C++11, which your compiler does not support.".format(self.name))
        else:
            self.output.warn("{0} requires C++11. Your compiler is unknown. Assuming it supports C++11.".format(self.name))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(source_folder=self._source_subfolder)
        return cmake

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
        self.copy("LICENSE*", "licenses", self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"csv2": "csv2::csv2"}
        )

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "csv2")
        self.cpp_info.set_property("cmake_target_name", "csv2::csv2")

        self.cpp_info.filenames["cmake_find_package"] = "csv2"
        self.cpp_info.filenames["cmake_find_package_multi"] = "csv2"
        self.cpp_info.names["cmake_find_package"] = "csv2"
        self.cpp_info.names["cmake_find_package_multi"] = "csv2"

        self.cpp_info.builddirs.append(self._module_subfolder)
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
