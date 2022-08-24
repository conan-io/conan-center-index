from conan import ConanFile, tools
from conan.tools.cmake import CMake
import os
import textwrap

required_conan_version = ">=1.33.0"


class LiblslConan(ConanFile):
    name = "liblsl"
    description = "Lab Streaming Layer is a C++ library for multi-modal " \
                  "time-synched data transmission over the local network"
    license = "MIT"
    topics = ("labstreaminglayer", "lsl", "network", "stream", "signal", 
              "transmission")
    homepage = "https://github.com/sccn/liblsl"
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
    generators = "cmake", "cmake_find_package_multi"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):
        self.requires("boost/1.78.0")
        self.requires("pugixml/1.11")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        if not self.options.shared:
            # Do not force PIC
            tools.replace_in_file(
                os.path.join(self._source_subfolder, "CMakeLists.txt"),
                "set(CMAKE_POSITION_INDEPENDENT_CODE ON)",
                ""
            )

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["LSL_BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["LSL_BUNDLED_BOOST"] = False
        self._cmake.definitions["LSL_BUNDLED_PUGIXML"] = False
        self._cmake.definitions["lslgitrevision"] = "v" + self.version
        self._cmake.definitions["lslgitbranch"] = "master"
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "lslver*")
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"lsl": "LSL::lsl"}
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
        self.cpp_info.names["cmake_find_package"] = "lsl"
        self.cpp_info.names["cmake_find_package_multi"] = "lsl"
        self.cpp_info.builddirs.append(self._module_subfolder)
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.defines = ["LSLNOAUTOLINK"]
        if not self.options.shared:
            self.cpp_info.defines.append("LIBLSL_STATIC")
        self.cpp_info.libs = ["lsl"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["iphlpapi", "winmm", "mswsock", "ws2_32"]
