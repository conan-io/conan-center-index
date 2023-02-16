from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, valid_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import (
    apply_conandata_patches, copy, export_conandata_patches, get, load, mkdir,
    rename, rm, rmdir, save
)
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.54.0"


class mFASTConan(ConanFile):
    name = "mfast"
    license = "LGPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://objectcomputing.com/"
    description = (
        "mFAST is a high performance C++ encoding/decoding library for FAST "
        "(FIX Adapted for STreaming) protocol"
    )
    topics = ("fast", "fix", "fix-adapted-for-streaming",
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

    @property
    def _min_cppstd(self):
        return "14" if Version(self.version) >= "1.2.2" else "98"

    @property
    def _compilers_minimum_version(self):
        if Version(self.version) >= "1.2.2":
            return {
                "gcc": "6",
                "Visual Studio": "14",
                "msvc": "190",
                "clang": "3.4",
                "apple-clang": "5.1",
            }
        else:
            return {}

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.75.0")
        self.requires("tinyxml2/9.0.0")
        if self.options.with_sqlite3:
            self.requires("sqlite3/3.40.1")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        def loose_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and loose_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTS"] = False
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_PACKAGES"] = False
        tc.variables["BUILD_SQLITE3"] = self.options.with_sqlite3
        if not valid_min_cppstd(self, self._min_cppstd):
            tc.variables["CMAKE_CXX_STANDARD"] = self._min_cppstd
        # Relocatable shared libs on macOS
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "licence.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        mkdir(self, os.path.join(self.package_folder, self._new_mfast_config_dir))
        self._extract_fasttypegentarget_macro()
        rmdir(self, os.path.join(self.package_folder, self._old_mfast_config_dir))
        rmdir(self, os.path.join(self.package_folder, "share"))
        if self.options.shared:
            rm(self, "*_static*" if self.settings.os == "Windows" else "*.a", os.path.join(self.package_folder, "lib"))

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
        if Version(self.version) < "1.2.2":
            config_file_content = load(self, os.path.join(self.package_folder, self._old_mfast_config_dir, "mFASTConfig.cmake"))
            begin = config_file_content.find("macro(FASTTYPEGEN_TARGET Name)")
            end = config_file_content.find("endmacro()", begin) + len("endmacro()")
            macro_str = config_file_content[begin:end]
            save(self, os.path.join(self.package_folder, self._fast_type_gen_target_file), macro_str)
        else:
            rename(self, os.path.join(self.package_folder, self._old_mfast_config_dir, "FastTypeGenTarget.cmake"),
                         os.path.join(self.package_folder, self._fast_type_gen_target_file))

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
        old_content = load(self, module_abs_path)
        new_content = exec_target_content + old_content
        save(self, module_abs_path, new_content)

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        save(self, module_file, content)

    @property
    def _lib_targets_module_file(self):
        return os.path.join(self._new_mfast_config_dir, f"conan-official-{self.name}-targets.cmake")

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
            self.cpp_info.components[conan_comp].set_property("cmake_target_name", target)
            if comp != target:
                # Also provide alias component for find_package(mFAST COMPONENTS ...) if static
                self.cpp_info.components[conan_comp].set_property("cmake_target_aliases", [comp])
            if self.settings.os in ("FreeBSD", "Linux"):
                self.cpp_info.components[conan_comp].system_libs.append("m")
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
                self.cpp_info.components[conan_comp_alias].bindirs = []

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "mFAST"
        self.cpp_info.names["cmake_find_package_multi"] = "mFAST"
