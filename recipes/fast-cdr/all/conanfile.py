from conan.tools.microsoft import msvc_runtime_flag
from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.43.0"


class FastCDRConan(ConanFile):
    name = "fast-cdr"
    license = "Apache-2.0"
    homepage = "https://github.com/eProsima/Fast-CDR"
    url = "https://github.com/conan-io/conan-center-index"
    description = "eProsima FastCDR library for serialization"
    topics = ("dds", "middleware", "serialization")

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
    exports_sources = ["CMakeLists.txt"]
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

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)
        if self._is_msvc and self.options.shared and "MT" in msvc_runtime_flag(self):
            # This combination leads to an fast-cdr error when linking
            # linking dynamic '*.dll' and static MT runtime
            # see https://github.com/eProsima/Fast-CDR/blob/v1.0.21/include/fastcdr/eProsima_auto_link.h#L37
            # (2021-05-31)
            raise ConanInvalidConfiguration("Mixing a dll eprosima library with a static runtime is a bad idea")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True,
                  destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_STATIC"] = not self.options.shared
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
        tools.files.rm(self, 
            directory=os.path.join(self.package_folder, "lib"),
            pattern="*.pdb"
        )
        tools.files.rm(self, 
            directory=os.path.join(self.package_folder, "bin"),
            pattern="*.pdb"
        )

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"fastcdr": "fastcdr::fastcdr"}
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
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "fastcdr")
        self.cpp_info.set_property("cmake_target_name", "fastcdr")
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines.append("FASTCDR_DYN_LINK")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "fastcdr"
        self.cpp_info.names["cmake_find_package_multi"] = "fastcdr"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
