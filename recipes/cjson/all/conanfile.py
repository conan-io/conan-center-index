from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rmdir, save
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
import os
import textwrap

required_conan_version = ">=1.50.0"


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

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
           del self.settings.compiler.libcxx
        except Exception:
           pass
        try:
           del self.settings.compiler.cppstd
        except Exception:
           pass

    def validate(self):
        if self.options.shared and is_msvc(self) and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("shared cjson is not supported with MT runtime")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_SANITIZERS"] = False
        tc.variables["ENABLE_SAFE_STACK"] = False
        tc.variables["ENABLE_PUBLIC_SYMBOLS"] = True
        tc.variables["ENABLE_HIDDEN_SYMBOLS"] = False
        tc.variables["ENABLE_TARGET_EXPORT"] = False
        tc.variables["BUILD_SHARED_AND_STATIC_LIBS"] = False
        tc.variables["CJSON_OVERRIDE_BUILD_SHARED_LIBS"] = False
        tc.variables["ENABLE_CJSON_UTILS"] = self.options.utils
        tc.variables["ENABLE_CJSON_TEST"] = False
        tc.variables["ENABLE_LOCALES"] = self.options.use_locales
        tc.variables["ENABLE_FUZZING"] = False
        tc.variables["ENABLE_CUSTOM_COMPILER_FLAGS"] = False
        # Relocatable shared libs on macOS
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        targets = {"cjson": "cJSON::cjson"}
        if self.options.utils:
            targets.update({"cjson_utils": "cJSON::cjson_utils"})
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            targets
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
