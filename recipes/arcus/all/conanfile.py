from conan import ConanFile, tools
from conans import CMake
import os
import textwrap

required_conan_version = ">=1.43.0"


class ArcusConan(ConanFile):
    name = "arcus"
    description = "This library contains C++ code and Python3 bindings for " \
                  "creating a socket in a thread and using this socket to send " \
                  "and receive messages based on the Protocol Buffers library."
    license = "LGPL-3.0-or-later"
    topics = ("arcus", "protobuf", "socket", "cura")
    homepage = "https://github.com/Ultimaker/libArcus"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],

    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("protobuf/3.17.1")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        # Do not force PIC
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "set(CMAKE_POSITION_INDEPENDENT_CODE ON)",
                              "")
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "set_target_properties(Arcus PROPERTIES COMPILE_FLAGS -fPIC)",
                              "")
        # TODO: this patch could be removed when CMake variables fixed in protobuf recipe
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "target_link_libraries(Arcus PUBLIC ${PROTOBUF_LIBRARIES})",
                              "target_link_libraries(Arcus PUBLIC protobuf::libprotobuf)")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_PYTHON"] = False
        self._cmake.definitions["BUILD_EXAMPLES"] = False
        self._cmake.definitions["BUILD_STATIC"] = not self.options.shared
        if self._is_msvc:
            if self.settings.compiler == "Visual Studio":
                is_static_runtime = str(self.settings.compiler.runtime).startswith("MT")
            else:
                is_static_runtime = self.settings.compiler.runtime == "static"
            self._cmake.definitions["MSVC_STATIC_RUNTIME"] = is_static_runtime
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"Arcus": "Arcus::Arcus"}
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
        self.cpp_info.set_property("cmake_file_name", "Arcus")
        self.cpp_info.set_property("cmake_target_name", "Arcus")
        self.cpp_info.libs = ["Arcus"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "Arcus"
        self.cpp_info.names["cmake_find_package_multi"] = "Arcus"
        self.cpp_info.builddirs.append(self._module_subfolder)
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
