from conans import ConanFile, tools
import os
import textwrap

required_conan_version = ">=1.43.0"


class CppZmqConan(ConanFile):
    name = "cppzmq"
    description = "C++ binding for 0MQ"
    homepage = "https://github.com/zeromq/cppzmq"
    license = "MIT"
    topics = ("cppzmq", "zmq-cpp", "zmq", "cpp-bind")
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"

    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("zeromq/4.3.4")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("zmq*.hpp", dst="include", src=self._source_subfolder)

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {
                "cppzmq": "cppzmq::cppzmq",
                "cppzmq-static": "cppzmq::cppzmq",
            }
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
        self.cpp_info.set_property("cmake_file_name", "cppzmq")
        # cppzmq has 2 weird official CMake imported targets:
        # - cppzmq if cppzmq depends on shared zeromq
        # - cppzmq-static if cppzmq depends on static zeromq
        self.cpp_info.set_property("cmake_target_name", "cppzmq")
        self.cpp_info.set_property("cmake_target_aliases", ["cppzmq-static"])

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "cppzmq"
        self.cpp_info.names["cmake_find_package_multi"] = "cppzmq"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
