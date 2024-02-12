from conan import ConanFile
from conan.tools.files import get, copy, save
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.53.0"

class MsgpackCXXConan(ConanFile):
    name = "msgpack-cxx"
    description = "The official C++ library for MessagePack"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/msgpack/msgpack-c"
    topics = ("msgpack", "message-pack", "serialization", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "use_boost": [True, False],
    }
    default_options = {
        "use_boost": True,
    }
    no_copy_source = True

    def configure_options(self):
        # No boost was added since 4.1.0
        if Version(self.version) < "4.1.0":
            del self.options.use_boost

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.get_safe("use_boost", True):
            self.requires("boost/1.83.0")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE_1_0.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.h",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include"),
        )
        copy(
            self,
            pattern="*.hpp",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include"),
        )
        if Version(self.version) >= "6.0.0":
            self._create_cmake_module_alias_targets(
                os.path.join(self.package_folder, self._module_file_rel_path),
                {"msgpack-cxx": "msgpack-cxx::msgpack-cxx"}
            )
        else:
            self._create_cmake_module_alias_targets(
                os.path.join(self.package_folder, self._module_file_rel_path),
                {"msgpackc-cxx": "msgpackc-cxx::msgpackc-cxx"}
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
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package_info(self):
        # https://github.com/msgpack/msgpack-c/tree/cpp_master#usage
        self.cpp_info.set_property("cmake_file_name", "msgpack")

        if Version(self.version) >= "6.0.0":
            self.cpp_info.set_property("cmake_target_name", "msgpack-cxx")
            self.cpp_info.names["cmake_find_package"] = "msgpack-cxx"
            self.cpp_info.names["cmake_find_package_multi"] = "msgpack-cxx"
        else:
            self.cpp_info.set_property("cmake_target_name", "msgpackc-cxx")
            self.cpp_info.names["cmake_find_package"] = "msgpackc-cxx"
            self.cpp_info.names["cmake_find_package_multi"] = "msgpackc-cxx"

        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = []

        if Version(self.version) >= "4.1.0" and not self.options.use_boost:
            self.cpp_info.defines.append("MSGPACK_NO_BOOST")
        else:
            self.cpp_info.requires.append("boost::headers")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "msgpack"
        self.cpp_info.filenames["cmake_find_package_multi"] = "msgpack"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
