from conans import ConanFile, CMake, tools
import os
import re
import sys
import shutil

required_conan_version = ">=1.33.0"


def _patch_cmake_file(cmake_file):
    """
        Removes all the different artifacts and configures the cmake file to
        generate only one library.
    """
    cmake_patch = '''

add_library(${PROJECT_NAME} ${PROTO_SRCS} ${PROTO_HEADERS})

target_include_directories(${PROJECT_NAME}
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}>
        $<INSTALL_INTERFACE:${INSTALL_INCLUDE_DIR}>
)

target_link_libraries(${PROJECT_NAME} PUBLIC protobuf::libprotobuf)

set_property(TARGET ${PROJECT_NAME} PROPERTY POSITION_INDEPENDENT_CODE ON)

set_property(
    TARGET ${PROJECT_NAME}
    PROPERTY SOVERSION ${${PROJECT_NAME}_SOVERSION}
)
set_property(
    TARGET ${PROJECT_NAME}
    PROPERTY VERSION ${${PROJECT_NAME}_LIBVERSION}
)

    '''

    result = None
    with open(cmake_file) as f:
        lines = f.read()
        result = re.sub("(add_library\(\$\{PROJECT_NAME\}_static.+?)\n(set_property\(\n.+?\)\n)", rf"{cmake_patch}", lines,
                flags=re.S)

    with open(cmake_file, 'w') as fh:
        fh.write(result)



class OpenSimulationInterfaceConan(ConanFile):
    name = "open_simulation_interface"
    homepage = "https://github.com/OpenSimulationInterface/open-simulation-interface"
    description = 'Generic interface environmental perception of automated driving functions in virtual scenarios'
    topics = ("ASAM", "OSI", "ADAS", "simulation")
    url = "https://github.com/conan-io/conan-center-index"
    license = "MPL 2.0"
    settings = "cppstd", "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "cmake", "cmake_paths", "cmake_find_package"
    exports_sources = "CMakeLists.txt"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def configure(self):
        del self.settings.compiler.cstd
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("protobuf/3.17.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)
        _patch_cmake_file(f"{self._source_subfolder}/CMakeLists.txt")
        tools.replace_in_file(f"{self._source_subfolder}/CMakeLists.txt",
                "set(INSTALL_LIB_DIR ${INSTALL_LIB_DIR}/osi${VERSION_MAJOR})",
                "")

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        try:
            shutil.rmtree(os.path.join(self.package_folder, "CMake"))
        except:
            pass

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "open_simulation_interface"
        self.cpp_info.names["cmake_find_package_multi"] = "open_simulation_interface"
        self.cpp_info.components["libopen_simulation_interface"].names["cmake_find_package"] = "open_simulation_interface"
        self.cpp_info.components["libopen_simulation_interface"].names["cmake_find_package_multi"] = "open_simulation_interface"
        self.cpp_info.components["libopen_simulation_interface"].libs = ["open_simulation_interface"]
        self.cpp_info.components["libopen_simulation_interface"].requires = ["protobuf::libprotobuf"]
        #self.cpp_info.components["libopen_simulation_interface"].requires = ["protobuf::protobuf"]

