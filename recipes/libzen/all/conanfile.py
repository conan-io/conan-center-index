from conan import ConanFile, tools
from conans import CMake
import os
import textwrap

required_conan_version = ">=1.43.0"


class LibzenConan(ConanFile):
    name = "libzen"
    license = "ZLIB"
    homepage = "https://github.com/MediaArea/ZenLib"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Small C++ derivate classes to have an easier life"
    topics = ("libzen", "c++", "helper", "util")

    settings = "os",  "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_unicode": [True, False],
        "enable_large_files": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_unicode": True,
        "enable_large_files": True,
    }

    generators = "cmake"
    _cmake = None

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

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_UNICODE"] = self.options.enable_unicode
        self._cmake.definitions["LARGE_FILES"] = self.options.enable_large_files
        # To install relocatable shared libs on Macos
        self._cmake.definitions["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("License.txt", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"zen": "ZenLib::ZenLib"}
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
        self.cpp_info.set_property("cmake_file_name", "ZenLib")
        self.cpp_info.set_property("cmake_target_name", "zen")
        self.cpp_info.set_property("pkg_config_name", "libzen")
        suffix = ""
        if self.settings.build_type == "Debug":
            if self.settings.os == "Windows":
                suffix = "d"
            elif tools.is_apple_os(self.settings.os):
                suffix = "_debug"
        self.cpp_info.libs = ["zen{}".format(suffix)]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])
        if self.options.enable_unicode:
            self.cpp_info.defines.extend(["UNICODE", "_UNICODE"])
        if self.options.shared:
            self.cpp_info.defines.append("LIBZEN_SHARED")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "ZenLib"
        self.cpp_info.names["cmake_find_package_multi"] = "ZenLib"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
