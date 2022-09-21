from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, replace_in_file, save
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.50.0"


class JsoncppConan(ConanFile):
    name = "jsoncpp"
    license = "MIT"
    homepage = "https://github.com/open-source-parsers/jsoncpp"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("json", "parser", "config")
    description = "A C++ library for interacting with JSON."

    settings = "os", "compiler", "arch", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
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

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["JSONCPP_WITH_TESTS"] = False
        tc.variables["JSONCPP_WITH_WARNING_AS_ERROR"] = False
        tc.variables["JSONCPP_WITH_CMAKE_PACKAGE"] = False
        tc.variables["JSONCPP_WITH_STRICT_ISO"] = False
        tc.variables["JSONCPP_WITH_PKGCONFIG_SUPPORT"] = False
        jsoncpp_version = Version(self.version)
        if jsoncpp_version < "1.9.0" or jsoncpp_version >= "1.9.4":
            tc.variables["BUILD_STATIC_LIBS"] = not self.options.shared
        if jsoncpp_version >= "1.9.3":
            tc.variables["JSONCPP_WITH_EXAMPLE"] = False
        if jsoncpp_version >= "1.9.4":
            tc.variables["BUILD_OBJECT_LIBS"] = False
        if jsoncpp_version < "1.9.0":
            # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
            tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                              "${jsoncpp_SOURCE_DIR}",
                              "${JSONCPP_SOURCE_DIR}")
        if self.settings.compiler == "Visual Studio" and self.settings.compiler.version == "11":
            replace_in_file(self, os.path.join(self.source_folder, "include", "json", "value.h"),
                                  "explicit operator bool()",
                                  "operator bool()")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        # TODO: to remove in conan v2 once legacy generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {
                "JsonCpp::JsonCpp": "jsoncpp::jsoncpp",   # alias target since 1.9.5
                "jsoncpp_lib": "jsoncpp::jsoncpp",        # imported target for shared lib, but also static between 1.9.0 & 1.9.3
                "jsoncpp_static": "jsoncpp::jsoncpp",     # imported target for static lib if >= 1.9.4
                "jsoncpp_lib_static": "jsoncpp::jsoncpp", # imported target for static lib if < 1.9.0
            }
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "jsoncpp")
        self.cpp_info.set_property("cmake_target_name", "JsonCpp::JsonCpp")
        self.cpp_info.set_property(
            "cmake_target_aliases",
            ["jsoncpp_lib"] if self.options.shared else ["jsoncpp_lib", "jsoncpp_static", "jsoncpp_lib_static"],
        )
        self.cpp_info.set_property("pkg_config_name", "jsoncpp")
        self.cpp_info.libs = ["jsoncpp"]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines.append("JSON_DLL")

        # TODO: to remove in conan v2 once legacy generators removed
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
