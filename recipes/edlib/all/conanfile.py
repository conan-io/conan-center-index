import os
import textwrap
import functools
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"

class EdlibConan(ConanFile):
    name = "edlib"
    description = "Lightweight, super fast C/C++ (& Python) library for " \
                  "sequence alignment using edit (Levenshtein) distance."
    topics = ("edlib", "sequence-alignment", "edit-distance", "levehnstein-distance", "alignment-path")
    license = "MIT"
    homepage = "https://github.com/Martinsos/edlib"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

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

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "5",
            "clang": "5",
            "apple-clang": "5.1",
        }

    def validate(self):
        if tools.Version(self.version) < "1.2.7":
            if self.settings.compiler.get_safe("cppstd"):
                tools.check_min_cppstd(self, 11)
            return

        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 14)

        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("{}/{} requires C++14. Your compiler is unknown. Assuming it supports C++14.".format(self.name, self.version))
        elif tools.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("{}/{} requires C++14, which your compiler does not support.".format(self.name, self.version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TESTING"] = False
        cmake.definitions["EDLIB_BUILD_EXAMPLES"] = False
        cmake.definitions["EDLIB_BUILD_UTILITIES"] = False
        if tools.Version(self.version) >= "1.2.7":
            cmake.definitions["EDLIB_ENABLE_INSTALL"] = True
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

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
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-targets.cmake".format(self.name))

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        if tools.Version(self.version) >= "1.2.7":
            self._create_cmake_module_alias_targets(
                os.path.join(self.package_folder, self._module_file_rel_path),
                {"edlib": "edlib::edlib"}
            )

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "edlib-{}".format(tools.Version(self.version).major)
        self.cpp_info.libs = ["edlib"]
        if self.options.shared:
            self.cpp_info.defines = ["EDLIB_SHARED"]
        if not self.options.shared and tools.stdcpp_library(self):
            self.cpp_info.system_libs = [tools.stdcpp_library(self)]
