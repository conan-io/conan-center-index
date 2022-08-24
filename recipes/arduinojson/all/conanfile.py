from conan import ConanFile, tools
import os
import textwrap

required_conan_version = ">=1.43.0"


class ArduinojsonConan(ConanFile):
    name = "arduinojson"
    description = "C++ JSON library for IoT. Simple and efficient."
    homepage = "https://github.com/bblanchon/ArduinoJson"
    topics = ("json", "arduino", "iot", "embedded", "esp8266")
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

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
        tools.files.save(self, module_file, content)

    def package(self):
        self.copy("*LICENSE*", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "src"))
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "src"))
        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"ArduinoJson": "ArduinoJson::ArduinoJson"}
        )

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ArduinoJson")
        self.cpp_info.set_property("cmake_target_name", "ArduinoJson")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "ArduinoJson"
        self.cpp_info.names["cmake_find_package_multi"] = "ArduinoJson"
        self.cpp_info.builddirs.append(self._module_subfolder)
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
