from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os
import shutil
import textwrap

required_conan_version = ">=1.43.0"


class mFASTConan(ConanFile):
    name = "mfast"
    license = "LGPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://objectcomputing.com/"
    description = (
        "mFAST is a high performance C++ encoding/decoding library for FAST "
        "(FIX Adapted for STreaming) protocol"
    )
    topics = ("mfast", "fast", "fix", "fix-adapted-for-streaming",
              "financial-information-exchange", "libraries", "cpp")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_sqlite3": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_sqlite3": False,
    }

    short_paths = True
    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "6",
            "Visual Studio": "14",
            "clang": "3.4",
            "apple-clang": "5.1",
        }

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
        self.requires("boost/1.75.0")
        self.requires("tinyxml2/9.0.0")
        if self.options.with_sqlite3:
            self.requires("sqlite3/3.37.2")

    def validate(self):
        if tools.Version(self.version) >= "1.2.2":
            if self.settings.compiler.get_safe("cppstd"):
                tools.check_min_cppstd(self, 14)

            def lazy_lt_semver(v1, v2):
                lv1 = [int(v) for v in v1.split(".")]
                lv2 = [int(v) for v in v2.split(".")]
                min_length = min(len(lv1), len(lv2))
                return lv1[:min_length] < lv2[:min_length]

            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version and lazy_lt_semver(str(self.settings.compiler.version), minimum_version):
                raise ConanInvalidConfiguration(
                    "mfast {} requires C++14, which your compiler does not support.".format(self.version)
                )

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["BUILD_TESTS"] = False
            self._cmake.definitions["BUILD_EXAMPLES"] = False
            self._cmake.definitions["BUILD_PACKAGES"] = False
            self._cmake.definitions["BUILD_SQLITE3"] = self.options.with_sqlite3
            if tools.Version(self.version) >= "1.2.2" and not tools.valid_min_cppstd(self, 14):
                self._cmake.definitions["CMAKE_CXX_STANDARD"] = 14
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("licence.txt", dst="licenses", src=self._source_subfolder)

        tools.mkdir(os.path.join(self.package_folder, self._new_mfast_config_dir))
        self._extract_fasttypegentarget_macro()

        tools.files.rmdir(self, os.path.join(self.package_folder, self._old_mfast_config_dir))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
        if self.options.shared:
            tools.files.rm(self, 
                os.path.join(self.package_folder, "lib"),
                "*_static*" if self.settings.os == "Windows" else "*.a"
            )

        # TODO: several CMake variables should also be emulated (casing issues):
        #       [ ] MFAST_INCLUDE_DIR         - include directories for mFAST
        #       [ ] MFAST_LIBRARY_DIRS        - library directories for mFAST
        #       [ ] MFAST_LIBRARIES           - libraries to link against
        #       [ ] MFAST_COMPONENTS          - installed components
        #       [ ] MFAST_<component>_LIBRARY - particular component library
        #       [x] MFAST_EXECUTABLE          - the fast_type_gen executable => done in _prepend_exec_target_in_fasttypegentarget()
        self._prepend_exec_target_in_fasttypegentarget()

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._lib_targets_module_file),
            {values["target"]:"mFAST::{}".format(values["target"]) for values in self._mfast_lib_components.values()}
        )

    @property
    def _new_mfast_config_dir(self):
        return os.path.join("lib", "cmake")

    @property
    def _old_mfast_config_dir(self):
        return "CMake" if self.settings.os == "Windows" else os.path.join("lib", "cmake", "mFAST")

    @property
    def _fast_type_gen_target_file(self):
        return os.path.join(self._new_mfast_config_dir, "FastTypeGenTarget.cmake")

    def _extract_fasttypegentarget_macro(self):
        if tools.Version(self.version) < "1.2.2":
            config_file_content = tools.files.load(self, os.path.join(self.package_folder, self._old_mfast_config_dir, "mFASTConfig.cmake"))
            begin = config_file_content.find("macro(FASTTYPEGEN_TARGET Name)")
            end = config_file_content.find("endmacro()", begin) + len("endmacro()")
            macro_str = config_file_content[begin:end]
            tools.save(os.path.join(self.package_folder, self._fast_type_gen_target_file), macro_str)
        else:
            shutil.move(
                os.path.join(self.package_folder, self._old_mfast_config_dir, "FastTypeGenTarget.cmake"),
                os.path.join(self.package_folder, self._fast_type_gen_target_file)
            )

    def _prepend_exec_target_in_fasttypegentarget(self):
        extension = ".exe" if self.settings.os == "Windows" else ""
        fast_type_filename = "fast_type_gen" + extension
        module_folder_depth = len(os.path.normpath(self._new_mfast_config_dir).split(os.path.sep))
        fast_type_rel_path = "{}bin/{}".format("".join(["../"] * module_folder_depth), fast_type_filename)
        exec_target_content = textwrap.dedent("""\
            if(NOT TARGET fast_type_gen)
                if(CMAKE_CROSSCOMPILING)
                    find_program(MFAST_EXECUTABLE fast_type_gen PATHS ENV PATH NO_DEFAULT_PATH)
                endif()
                if(NOT MFAST_EXECUTABLE)
                    get_filename_component(MFAST_EXECUTABLE "${{CMAKE_CURRENT_LIST_DIR}}/{fast_type_rel_path}" ABSOLUTE)
                endif()
                add_executable(fast_type_gen IMPORTED)
                set_property(TARGET fast_type_gen PROPERTY IMPORTED_LOCATION ${{MFAST_EXECUTABLE}})
            endif()
        """.format(fast_type_rel_path=fast_type_rel_path))
        module_abs_path = os.path.join(self.package_folder, self._fast_type_gen_target_file)
        old_content = tools.files.load(self, module_abs_path)
        new_content = exec_target_content + old_content
        tools.save(module_abs_path, new_content)

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
    def _lib_targets_module_file(self):
        return os.path.join(self._new_mfast_config_dir,
                            "conan-official-{}-targets.cmake".format(self.name))

    @property
    def _mfast_lib_components(self):
        target_suffix = "_static" if not self.options.shared else ""
        lib_suffix = "_static" if self.settings.os == "Windows" and not self.options.shared else ""
        components = {
            "libmfast": {
                "comp": "mfast",
                "target": "mfast" + target_suffix,
                "lib": "mfast" + lib_suffix,
                "requires": ["boost::headers"],
            },
            "mfast_coder": {
                "comp": "mfast_coder",
                "target": "mfast_coder" + target_suffix,
                "lib": "mfast_coder" + lib_suffix,
                "requires": ["libmfast", "boost::headers"],
            },
            "mfast_xml_parser": {
                "comp": "mfast_xml_parser",
                "target": "mfast_xml_parser" + target_suffix,
                "lib": "mfast_xml_parser" + lib_suffix,
                "requires": ["libmfast", "boost::headers", "tinyxml2::tinyxml2"],
            },
            "mfast_json": {
                "comp": "mfast_json",
                "target": "mfast_json" + target_suffix,
                "lib": "mfast_json" + lib_suffix,
                "requires": ["libmfast", "boost::headers"],
            },
        }
        if self.options.with_sqlite3:
            components.update({
                "mfast_sqlite3": {
                    "comp": "mfast_sqlite3",
                    "target": "mfast_sqlite3" + target_suffix,
                    "lib": "mfast_sqlite3" + lib_suffix,
                    "requires": ["libmfast", "boost::headers", "sqlite3::sqlite3"],
                },
            })
        return components

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "mFAST")
        self.cpp_info.set_property("cmake_build_modules", [self._fast_type_gen_target_file])

        for conan_comp, values in self._mfast_lib_components.items():
            target = values["target"]
            comp = values["comp"]
            lib = values["lib"]
            requires = values["requires"]
            self.cpp_info.components[conan_comp].set_property("cmake_file_name", target)
            if comp != target:
                # Also provide alias component for find_package(mFAST COMPONENTS ...) if static
                self.cpp_info.components[conan_comp].set_property("cmake_target_aliases", [comp])
            self.cpp_info.components[conan_comp].libs = [lib]
            self.cpp_info.components[conan_comp].requires = requires
            if self.options.shared:
                self.cpp_info.components[conan_comp].defines = ["MFAST_DYN_LINK"]

            # TODO: to remove in conan v2 once cmake_find_package* generators removed
            self.cpp_info.components[conan_comp].names["cmake_find_package"] = target
            self.cpp_info.components[conan_comp].names["cmake_find_package_multi"] = target
            self.cpp_info.components[conan_comp].build_modules["cmake"] = [self._fast_type_gen_target_file]
            build_modules = [self._lib_targets_module_file, self._fast_type_gen_target_file]
            self.cpp_info.components[conan_comp].build_modules["cmake_find_package"] = build_modules
            self.cpp_info.components[conan_comp].build_modules["cmake_find_package_multi"] = build_modules
            if comp != target:
                conan_comp_alias = conan_comp + "_alias"
                self.cpp_info.components[conan_comp_alias].names["cmake_find_package"] = comp
                self.cpp_info.components[conan_comp_alias].names["cmake_find_package_multi"] = comp
                self.cpp_info.components[conan_comp_alias].requires = [conan_comp]
                self.cpp_info.components[conan_comp_alias].includedirs = []
                self.cpp_info.components[conan_comp_alias].libdirs = []
                self.cpp_info.components[conan_comp_alias].resdirs = []
                self.cpp_info.components[conan_comp_alias].bindirs = []
                self.cpp_info.components[conan_comp_alias].frameworkdirs = []

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "mFAST"
        self.cpp_info.names["cmake_find_package_multi"] = "mFAST"
