import os
import textwrap

from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.43.0"


class CharlsConan(ConanFile):
    name = "charls"
    description = "C++ implementation of the JPEG-LS standard for lossless " \
                  "and near-lossless image compression and decompression."
    license = "BSD-3-Clause"
    topics = ("charls", "jpeg", "JPEG-LS", "compression", "decompression", )
    homepage = "https://github.com/team-charls/charls"
    url = "https://github.com/conan-io/conan-center-index"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file_rel_path(self):
        return os.path.join(self._module_subfolder,
                            "conan-official-{}-targets.cmake".format(self.name))

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

    def validate(self):
        minimal_cpp_standard = "14"
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, minimal_cpp_standard)

        # brace initialization issue for gcc < 5
        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration("CharLS can't be compiled by {0} {1}".format(self.settings.compiler,
                                                                                         self.settings.compiler.version))

        # name lookup issue for gcc == 5 in charls/2.2.0
        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) == "5" and tools.Version(self.version) >= "2.2.0":
            raise ConanInvalidConfiguration("CharLS can't be compiled by {0} {1}".format(self.settings.compiler,
                                                                                         self.settings.compiler.version))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["CHARLS_INSTALL"] = True
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

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

    def package(self):
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"charls": "charls::charls"}
        )

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "charls")
        self.cpp_info.set_property("cmake_target_name", "charls")

        self.cpp_info.builddirs.append(self._module_subfolder)
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

        self.cpp_info.filenames["cmake_find_package"] = "charls"
        self.cpp_info.filenames["cmake_find_package_multi"] = "charls"
        self.cpp_info.names["cmake_find_package"] = "charls"
        self.cpp_info.names["cmake_find_package_multi"] = "charls"

        self.cpp_info.libs = tools.collect_libs(self)
        if not self.options.shared:
            self.cpp_info.defines.append("CHARLS_STATIC")
