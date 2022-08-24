from conan import ConanFile, tools$
from conan.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.43.0"


class MsgpackCXXConan(ConanFile):
    name = "msgpack-cxx"
    description = "The official C++ library for MessagePack"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/msgpack/msgpack-c"
    topics = ("msgpack", "message-pack", "serialization")
    license = "BSL-1.0"
    no_copy_source = True

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "use_boost": [True, False],
    }
    default_options = {
        "use_boost": True
    }


    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def configure_options(self):
        # No boost was added in 4.1.0
        if tools.scm.Version(self.version) < "4.1.0":
            del self.options.use_boost

    def requirements(self):
        if self.options.get_safe("use_boost", True):
            self.requires("boost/1.78.0")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE_1_0.txt", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"msgpackc-cxx": "msgpackc-cxx::msgpackc-cxx"}
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
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file_rel_path(self):
        return os.path.join(self._module_subfolder,
                            "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "msgpack")
        self.cpp_info.set_property("cmake_target_name", "msgpackc-cxx")

        self.cpp_info.filenames["cmake_find_package"] = "msgpack"
        self.cpp_info.filenames["cmake_find_package_multi"] = "msgpack"
        self.cpp_info.names["cmake_find_package"] = "msgpackc-cxx"
        self.cpp_info.names["cmake_find_package_multi"] = "msgpackc-cxx"
        self.cpp_info.builddirs.append(self._module_subfolder)
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

        if tools.scm.Version(self.version) >= "4.1.0" and not self.options.use_boost:
            self.cpp_info.defines.append("MSGPACK_NO_BOOST")
