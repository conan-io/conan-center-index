from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir, replace_in_file, save
import os
import textwrap

required_conan_version = ">=1.54.0"


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

    def requirements(self):
        self.requires("boost/1.78.0")
        self.requires("pugixml/1.11")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LSL_BUILD_STATIC"] = not self.options.shared
        tc.variables["LSL_BUNDLED_BOOST"] = False
        tc.variables["LSL_BUNDLED_PUGIXML"] = False
        tc.variables["lslgitrevision"] = "v" + self.version
        tc.variables["lslgitbranch"] = "master"
        tc.generate()
        cd = CMakeDeps(self)
        cd.generate()

    def _patch_sources(self):
        if not self.options.shared:
            # Do not force PIC
            replace_in_file(
                self,
                os.path.join(self.source_folder, "CMakeLists.txt"),
                "set(CMAKE_POSITION_INDEPENDENT_CODE ON)",
                ""
            )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        rm(self, "lslver*", os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

        copy(self, "LICENSE", src=self.source_folder, dst="licenses")

        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"lsl": "LSL::lsl"}
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        save(self, module_file, content)

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
