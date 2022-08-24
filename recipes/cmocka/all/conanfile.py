from conan import ConanFile, tools
from conans import CMake
import os
import textwrap

required_conan_version = ">=1.43.0"


class CmockaConan(ConanFile):
    name = "cmocka"
    license = "Apache-2.0"
    homepage = "https://cmocka.org"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A unit testing framework for C"
    topics = ("unit_test", "unittest", "test", "testing", "mock", "mocking")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["WITH_STATIC_LIB"] = not self.options.shared
        self._cmake.definitions["WITH_EXAMPLES"] = False
        self._cmake.configure(build_folder=self._build_subfolder)

        return self._cmake

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_file_rel_path)
        )

    @staticmethod
    def _create_cmake_module_variables(module_file):
        content = textwrap.dedent("""\
            if(NOT DEFINED CMOCKA_INCLUDE_DIR)
                set(CMOCKA_INCLUDE_DIR ${cmocka_INCLUDE_DIRS}
                                       ${cmocka_INCLUDE_DIRS_RELEASE}
                                       ${cmocka_INCLUDE_DIRS_RELWITHDEBINFO}
                                       ${cmocka_INCLUDE_DIRS_MINSIZEREL}
                                       ${cmocka_INCLUDE_DIRS_DEBUG})
            endif()
            if(TARGET cmocka::cmocka)
                if(NOT DEFINED CMOCKA_LIBRARY)
                    set(CMOCKA_LIBRARY cmocka::cmocka)
                endif()
                if(NOT DEFINED CMOCKA_LIBRARIES)
                    set(CMOCKA_LIBRARIES cmocka::cmocka)
                endif()
            endif()
        """)
        tools.files.save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-variables.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "cmocka")
        self.cpp_info.set_property("pkg_config_name", "cmocka")
        self.cpp_info.set_property("cmake_build_modules", [self._module_file_rel_path])
        self.cpp_info.libs = ["cmocka{}".format("" if self.options.shared else "-static")]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
