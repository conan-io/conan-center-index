from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.43.0"


class CjsonConan(ConanFile):
    name = "cjson"
    description = "Ultralightweight JSON parser in ANSI C."
    license = "MIT"
    topics = ("cjson", "json", "parser")
    homepage = "https://github.com/DaveGamble/cJSON"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "utils": [True, False],
        "use_locales": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "utils": False,
        "use_locales": True,
    }

    generators = "cmake"
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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.options.shared and \
           ((self.settings.compiler == "Visual Studio" and self.settings.compiler.runtime == "MTd") or \
            (str(self.settings.compiler) == "msvc" and self.settings.compiler.runtime == "MT" and self.settings.compiler.runtime_type == "Debug")):
            raise ConanInvalidConfiguration("shared cjson is not supported with MTd runtime")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_SANITIZERS"] = False
        self._cmake.definitions["ENABLE_SAFE_STACK"] = False
        self._cmake.definitions["ENABLE_PUBLIC_SYMBOLS"] = True
        self._cmake.definitions["ENABLE_HIDDEN_SYMBOLS"] = False
        self._cmake.definitions["ENABLE_TARGET_EXPORT"] = False
        self._cmake.definitions["BUILD_SHARED_AND_STATIC_LIBS"] = False
        self._cmake.definitions["CJSON_OVERRIDE_BUILD_SHARED_LIBS"] = False
        self._cmake.definitions["ENABLE_CJSON_UTILS"] = self.options.utils
        self._cmake.definitions["ENABLE_CJSON_TEST"] = False
        self._cmake.definitions["ENABLE_LOCALES"] = self.options.use_locales
        self._cmake.definitions["ENABLE_FUZZING"] = False
        self._cmake.definitions["ENABLE_CUSTOM_COMPILER_FLAGS"] = False

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        targets = {"cjson": "cJSON::cjson"}
        if self.options.utils:
            targets.update({"cjson_utils": "cJSON::cjson_utils"})
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            targets
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
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "cJSON")

        self.cpp_info.components["_cjson"].set_property("cmake_target_name", "cjson")
        self.cpp_info.components["_cjson"].set_property("pkg_config_name", "libcjson")
        self.cpp_info.components["_cjson"].libs = ["cjson"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_cjson"].system_libs = ["m"]

        if self.options.utils:
            self.cpp_info.components["cjson_utils"].set_property("cmake_target_name", "cjson_utils")
            self.cpp_info.components["cjson_utils"].set_property("pkg_config_name", "libcjson_utils")
            self.cpp_info.components["cjson_utils"].libs = ["cjson_utils"]
            self.cpp_info.components["cjson_utils"].requires = ["_cjson"]

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.names["cmake_find_package"] = "cJSON"
        self.cpp_info.names["cmake_find_package_multi"] = "cJSON"
        self.cpp_info.components["_cjson"].names["cmake_find_package"] = "cjson"
        self.cpp_info.components["_cjson"].names["cmake_find_package_multi"] = "cjson"
        self.cpp_info.components["_cjson"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["_cjson"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components["_cjson"].names["pkg_config"] = "libcjson"
        if self.options.utils:
            self.cpp_info.components["cjson_utils"].names["cmake_find_package"] = "cjson_utils"
            self.cpp_info.components["cjson_utils"].names["cmake_find_package_multi"] = "cjson_utils"
            self.cpp_info.components["cjson_utils"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components["cjson_utils"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
            self.cpp_info.components["cjson_utils"].names["pkg_config"] = "libcjson_utils"
