import os.path
import textwrap

from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.files import collect_libs, get, save


class WebsocketParserConan(ConanFile):
    name = "websocket-parser"
    license = "BSD-3"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/php-ion/websocket-parser"
    description = "Streaming websocket frame parser and frame builder for c"
    topics = "websockets", "parser"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": False}
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def layout(self):
        cmake_layout(self)

    def build(self):
        save(self, os.path.join(self.source_folder, "CMakeLists.txt"), textwrap.dedent("""\
            cmake_minimum_required(VERSION 3.15 FATAL_ERROR)
            project(websocket-parser C)

            add_library(websocket-parser websocket_parser.h websocket_parser.c)

            target_include_directories(websocket-parser PUBLIC
                $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
                $<INSTALL_INTERFACE:include/>)

            set_target_properties(websocket-parser PROPERTIES
                SOVERSION 0
                PUBLIC_HEADER "websocket_parser.h")

            install(TARGETS websocket-parser
                LIBRARY DESTINATION ${CMAKE_INSTALL_DIR}
                PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/websocket_parser)
            """))
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", keep_path=False)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        self.cpp_info.set_property("cmake_file_name", "websocket-parser")
        self.cpp_info.set_property("cmake_target_name", "websocket-parser::websocket-parser")
        self.cpp_info.set_property("pkg_config_name", "websocket-parser")
