from conans import ConanFile, tools
import os
import textwrap

required_conan_version = ">=1.33.0"


class CppZmqConan(ConanFile):
    name = "cppzmq"
    description = "C++ binding for 0MQ"
    homepage = "https://github.com/zeromq/cppzmq"
    license = "MIT"
    topics = ("conan", "cppzmq", "zmq-cpp", "zmq", "cpp-bind")
    url = "https://github.com/conan-io/conan-center-index"

    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("zeromq/4.3.4")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("cppzmq-{}".format(self.version), self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("zmq*.hpp", dst="include", src=self._source_subfolder)
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {
                # cppzmq has 2 weird official CMake imported targets:
                # - cppzmq if cppzmq depends on shared zeromq
                # - cppzmq-static if cppzmq depends on static zeromq
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
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file_rel_path(self):
        return os.path.join(self._module_subfolder,
                            "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "cppzmq"
        self.cpp_info.names["cmake_find_package_multi"] = "cppzmq"
        self.cpp_info.builddirs.append(self._module_subfolder)
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
