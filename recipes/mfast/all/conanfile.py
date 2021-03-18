from conans import ConanFile, CMake, tools
import glob
import os
import shutil
import textwrap

required_conan_version = ">=1.33.0"


class mFASTConan(ConanFile):
    name = "mfast"
    license = "LGPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://objectcomputing.com/"
    description = "mFAST is a high performance C++ encoding/decoding library for FAST (FIX Adapted for STreaming)"\
                  " protocol"
    topics = ("conan", "mFAST", "FAST", "FIX", "Fix Adapted for STreaming", "Financial Information Exchange",
              "libraries", "cpp")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
    }

    short_paths = True

    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
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

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("boost/1.75.0")
        self.requires("tinyxml2/8.0.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("mFAST-*/")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["BUILD_TESTS"] = False
            self._cmake.definitions["BUILD_EXAMPLES"] = False
            self._cmake.definitions["BUILD_PACKAGES"] = False
            if self.version != "1.2.1":
                if not self.settings.compiler.cppstd:
                    self._cmake.definitions["CMAKE_CXX_STANDARD"] = 14
                else:
                    tools.check_min_cppstd(self, 14)
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("licence.txt", dst="licenses", src=self._source_subfolder)

        tools.mkdir(os.path.join(self.package_folder, self._new_mfast_config_dir))
        self._extract_fasttypegentarget_macro()
        tools.rmdir(os.path.join(self.package_folder, self._old_mfast_config_dir))
        tools.rmdir(os.path.join(self.package_folder, "share"))

        # TODO: several CMake variables should also be emulated (casing issues):
        #       [ ] MFAST_INCLUDE_DIR         - include directories for mFAST
        #       [ ] MFAST_LIBRARY_DIRS        - library directories for mFAST
        #       [ ] MFAST_LIBRARIES           - libraries to link against
        #       [ ] MFAST_COMPONENTS          - installed components
        #       [ ] MFAST_<component>_LIBRARY - particular component library
        #       [x] MFAST_EXECUTABLE          - the fast_type_gen executable => done in _prepend_exec_target_in_fasttypegentarget()
        self._prepend_exec_target_in_fasttypegentarget()
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._lib_targets_module_file),
            {values["lib"]:"mFAST::{}".format(values["lib"]) for values in self._mfast_lib_components.values()}
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
        if self.version == "1.2.1":
            config_file_content = tools.load(os.path.join(self.package_folder, self._old_mfast_config_dir, "mFASTConfig.cmake"))
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
                get_filename_component(MFAST_EXECUTABLE "${{CMAKE_CURRENT_LIST_DIR}}/{fast_type_rel_path}" ABSOLUTE)
                add_executable(fast_type_gen IMPORTED)
                set_property(TARGET fast_type_gen PROPERTY IMPORTED_LOCATION ${{MFAST_EXECUTABLE}})
            endif()
        """.format(fast_type_rel_path=fast_type_rel_path))
        module_abs_path = os.path.join(self.package_folder, self._fast_type_gen_target_file)
        old_content = tools.load(module_abs_path)
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
        # TODO: improve accuracy of external requirements of each component
        suffix = "_static" if self.settings.os == "Windows" and not self.options.shared else ""
        return {
            "libmfast": {
                "comp": "mfast",
                "lib": "mfast" + suffix,
                "requires": ["boost::boost", "tinyxml2::tinyxml2"]
            },
            "mfast_coder": {
                "comp": "mfast_coder",
                "lib": "mfast_coder" + suffix,
                "requires": ["libmfast", "boost::boost", "tinyxml2::tinyxml2"]
            },
            "mfast_xml_parser": {
                "comp": "mfast_xml_parser",
                "lib": "mfast_xml_parser" + suffix,
                "requires": ["libmfast", "boost::boost", "tinyxml2::tinyxml2"]
            },
            "mfast_json": {
                "comp": "mfast_json",
                "lib": "mfast_json" + suffix,
                "requires": ["libmfast", "boost::boost", "tinyxml2::tinyxml2"]
            }
        }

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "mFAST"
        self.cpp_info.names["cmake_find_package_multi"] = "mFAST"

        for conan_comp, values in self._mfast_lib_components.items():
            target_lib = values["lib"]
            requires = values["requires"]
            self.cpp_info.components[conan_comp].names["cmake_find_package"] = target_lib
            self.cpp_info.components[conan_comp].names["cmake_find_package_multi"] = target_lib
            self.cpp_info.components[conan_comp].builddirs.append(self._new_mfast_config_dir)
            self.cpp_info.components[conan_comp].build_modules["cmake"] = [self._fast_type_gen_target_file]
            self.cpp_info.components[conan_comp].build_modules["cmake_find_package"] = [
                self._lib_targets_module_file,
                self._fast_type_gen_target_file
            ]
            self.cpp_info.components[conan_comp].build_modules["cmake_find_package_multi"] = [
                self._lib_targets_module_file,
                self._fast_type_gen_target_file
            ]
            self.cpp_info.components[conan_comp].libs = [target_lib]
            self.cpp_info.components[conan_comp].requires = requires

            # Also provide alias component for find_package(mFAST COMPONENTS ...) if static:
            comp = values["comp"]
            if comp != target_lib:
                conan_comp_alias = conan_comp + "_alias"
                self.cpp_info.components[conan_comp_alias].names["cmake_find_package"] = comp
                self.cpp_info.components[conan_comp_alias].names["cmake_find_package_multi"] = comp
                self.cpp_info.components[conan_comp_alias].requires = [conan_comp]
                self.cpp_info.components[conan_comp_alias].includedirs = []
                self.cpp_info.components[conan_comp_alias].libdirs = []
                self.cpp_info.components[conan_comp_alias].resdirs = []
                self.cpp_info.components[conan_comp_alias].bindirs = []
                self.cpp_info.components[conan_comp_alias].frameworkdirs = []
