from conan.tools.microsoft import msvc_runtime_flag
from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.43.0"


class GDCMConan(ConanFile):
    name = "gdcm"
    topics = ("dicom", "images")
    homepage = "http://gdcm.sourceforge.net/"
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-3-Clause"
    description = "C++ library for DICOM medical files"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "src"

    @property
    def _build_subfolder(self):
        return "build"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

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

    def requirements(self):
        self.requires("expat/2.4.8")
        self.requires("openjpeg/2.4.0")
        self.requires("zlib/1.2.12")

    def validate(self):
        if self.options.shared and self._is_msvc and "MT" in msvc_runtime_flag(self):
            raise ConanInvalidConfiguration("shared gdcm can't be built with MT or MTd")
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, "11")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["GDCM_BUILD_DOCBOOK_MANPAGES"] = False
        self._cmake.definitions["GDCM_BUILD_SHARED_LIBS"] = self.options.shared
        # FIXME: unvendor deps https://github.com/conan-io/conan-center-index/pull/5705#discussion_r647224146
        self._cmake.definitions["GDCM_USE_SYSTEM_EXPAT"] = True
        self._cmake.definitions["GDCM_USE_SYSTEM_OPENJPEG"] = True
        self._cmake.definitions["GDCM_USE_SYSTEM_ZLIB"] = True
        if not tools.valid_min_cppstd(self, 11):
            self._cmake.definitions["CMAKE_CXX_STANDARD"] = 11

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("Copyright.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        if self.settings.os == "Windows":
            bin_dir = os.path.join(self.package_folder, "bin")
            tools.files.rm(self, "[!gs]*.dll", bin_dir)
            tools.files.rm(self, "*.pdb", bin_dir)
        lib_dir = os.path.join(self.package_folder, "lib")
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
        tools.files.rm(self, "[!U]*.cmake", os.path.join(lib_dir, self._gdcm_subdir)) #leave UseGDCM.cmake untouched
        self._create_cmake_variables(os.path.join(self.package_folder, self._gdcm_cmake_variables_path))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._gdcm_cmake_module_aliases_path),
            {library: "GDCM::{}".format(library) for library in self._gdcm_libraries},
        )

    def _create_cmake_variables(self, variables_file):
        v = tools.scm.Version(self.version)
        content = textwrap.dedent("""\
            # The GDCM version number.
            set(GDCM_MAJOR_VERSION "{v_major}")
            set(GDCM_MINOR_VERSION "{v_minor}")
            set(GDCM_BUILD_VERSION "{v_patch}")

            get_filename_component(SELF_DIR "${{CMAKE_CURRENT_LIST_FILE}}" PATH)

            # The libraries.
            set(GDCM_LIBRARIES "")

            # The CMake macros dir.
            set(GDCM_CMAKE_DIR "")

            # The configuration options.
            set(GDCM_BUILD_SHARED_LIBS "{build_shared_libs}")

            set(GDCM_USE_VTK "OFF")

            # The "use" file.
            set(GDCM_USE_FILE ${{SELF_DIR}}/UseGDCM.cmake)

            # The VTK options.
            set(GDCM_VTK_DIR "")

            get_filename_component(GDCM_INCLUDE_ROOT "${{SELF_DIR}}/../../include/{gdcm_subdir}" ABSOLUTE)
            set(GDCM_INCLUDE_DIRS ${{GDCM_INCLUDE_ROOT}})
            get_filename_component(GDCM_LIB_ROOT "${{SELF_DIR}}/../../lib" ABSOLUTE)
            set(GDCM_LIBRARY_DIRS ${{GDCM_LIB_ROOT}})
        """.format(v_major=v.major,
                   v_minor=v.minor,
                   v_patch=v.patch,
                   build_shared_libs="ON" if self.options.shared else "OFF",
                   gdcm_subdir=self._gdcm_subdir))
        tools.files.save(self, variables_file, content)

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
    def _gdcm_subdir(self):
        v = tools.scm.Version(self.version)
        return "gdcm-{}.{}".format(v.major, v.minor)

    @property
    def _gdcm_builddir(self):
        return os.path.join("lib", self._gdcm_subdir)

    @property
    def _gdcm_cmake_module_aliases_path(self):
        return os.path.join("lib", self._gdcm_subdir, "conan-official-gdcm-targets.cmake")

    @property
    def _gdcm_cmake_variables_path(self):
        return os.path.join("lib", self._gdcm_subdir, "conan-official-gdcm-variables.cmake")

    @property
    def _gdcm_build_modules(self):
        return [self._gdcm_cmake_module_aliases_path, self._gdcm_cmake_variables_path]

    @property
    def _gdcm_libraries(self):
        gdcm_libs = ["gdcmcharls",
                     "gdcmCommon",
                     "gdcmDICT",
                     "gdcmDSED",
                     "gdcmIOD",
                     "gdcmjpeg12",
                     "gdcmjpeg16",
                     "gdcmjpeg8",
                     "gdcmMEXD",
                     "gdcmMSFF",
                     "socketxx"]
        if self.settings.os == "Windows":
            gdcm_libs.append("gdcmgetopt")
        else:
            gdcm_libs.append("gdcmuuid")
        return gdcm_libs

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "GDCM")
        self.cpp_info.set_property("cmake_build_modules", [self._gdcm_cmake_variables_path])

        for lib in self._gdcm_libraries:
            self.cpp_info.components[lib].set_property("cmake_target_name", lib)
            self.cpp_info.components[lib].libs = [lib]
            self.cpp_info.components[lib].includedirs = [os.path.join("include", self._gdcm_subdir)]
            self.cpp_info.components[lib].builddirs.append(self._gdcm_builddir)

            # TODO: to remove in conan v2 once cmake_find_package* generators removed
            self.cpp_info.components[lib].build_modules["cmake"] = [self._gdcm_cmake_module_aliases_path]
            self.cpp_info.components[lib].build_modules["cmake_find_package"] = self._gdcm_build_modules
            self.cpp_info.components[lib].build_modules["cmake_find_package_multi"] = self._gdcm_build_modules

        self.cpp_info.components["gdcmDSED"].requires.extend(["gdcmCommon", "zlib::zlib"])
        self.cpp_info.components["gdcmIOD"].requires.extend(["gdcmDSED", "gdcmCommon", "expat::expat"])
        self.cpp_info.components["gdcmMSFF"].requires.extend(["gdcmIOD", "gdcmDSED", "gdcmDICT", "openjpeg::openjpeg"])
        if not self.options.shared:
            self.cpp_info.components["gdcmDICT"].requires.extend(["gdcmDSED", "gdcmIOD"])
            self.cpp_info.components["gdcmMEXD"].requires.extend(["gdcmMSFF", "gdcmDICT", "gdcmDSED", "gdcmIOD", "socketxx"])
            self.cpp_info.components["gdcmMSFF"].requires.extend(["gdcmjpeg8", "gdcmjpeg12", "gdcmjpeg16", "gdcmcharls"])

            if self.settings.os == "Windows":
                self.cpp_info.components["gdcmCommon"].system_libs = ["ws2_32", "crypt32"]
                self.cpp_info.components["gdcmMSFF"].system_libs = ["rpcrt4"]
                self.cpp_info.components["socketxx"].system_libs = ["ws2_32"]
            else:
                self.cpp_info.components["gdcmMSFF"].requires.append("gdcmuuid")

                self.cpp_info.components["gdcmCommon"].system_libs = ["dl"]
                if tools.apple.is_apple_os(self):
                    self.cpp_info.components["gdcmCommon"].frameworks = ["CoreFoundation"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "GDCM"
        self.cpp_info.names["cmake_find_package_multi"] = "GDCM"
