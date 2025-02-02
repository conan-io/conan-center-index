import json
import os
import textwrap

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd, valid_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import (
    apply_conandata_patches, collect_libs, copy, export_conandata_patches, get,
    load, rename, replace_in_file, rmdir, save
)
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"

class OpenCascadeConan(ConanFile):
    name = "opencascade"
    description = "A software development platform providing services for 3D " \
                  "surface and solid modeling, CAD data exchange, and visualization."
    homepage = "https://dev.opencascade.org"
    url = "https://github.com/conan-io/conan-center-index"
    license = "LGPL-2.1-or-later"
    topics = ("occt", "3d", "modeling", "cad")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ffmpeg": [True, False],
        "extended_debug_messages": [True, False],
        "with_samples": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ffmpeg": False,
        "extended_debug_messages": False,
        "with_samples": False
    }

    short_paths = True

    @property
    def _is_linux(self):
        return self.settings.os in ["Linux", "FreeBSD"]

    @property
    def _min_cppstd(self):
        return "14"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "7",
            "apple-clang": "10",
            "Visual Studio": "15",
            "msvc": "191",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.build_type != "Debug":
            del self.options.extended_debug_messages

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("freetype/2.13.2")
        self.requires("freeimage/3.18.0")
        # openvr enabled provokes compilation error:
        # src/Aspect/Aspect_OpenVRSession.cxx:171:35: error: expected member name or ';' after declaration specifiers
        # https://c3i.jfrog.io/artifactory/cci-build-logs/cci/prod/PR-24958/9/package_build_logs/build_log_opencascade_7_8_1_48754798153f23d7b142ece9713827d2_59d1e7b531c07c6c68eb8fdee173dcd9b5f6ddcd.txt
        # self.requires("openvr/1.16.8")
        self.requires("opengl/system")
        # Failed with rapidjson
#         [  3%] Linking CXX shared library ../../lin64/gcc/lib/libTKernel.so
# /opt/conan/binutils/bin/ld: cannot find -lrapidjson
# /opt/conan/binutils/bin/ld: /usr/lib/x86_64-linux-gnu/libGL.so: .dynsym local symbol at index 3 (>= sh_info of 3)
        # self.requires("rapidjson/cci.20230929")
        self.requires("draco/1.5.6")
        # self.requires("tk/8.6.10")
        self.requires("onetbb/2021.12.0")

        if self._is_linux:
            self.requires("fontconfig/2.13.93")
            self.requires("xorg/system")
        # TODO: add vtk support?
        if self.options.with_ffmpeg:
            self.requires("ffmpeg/6.1")
            
        if self.options.with_samples:
            self.requires("qt/6.7.1")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        if self.settings.compiler == "clang" and self.settings.compiler.version == "6.0" and \
           self.settings.build_type == "Release":
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support Clang 6.0 if Release build type")
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if not valid_min_cppstd(self, self._min_cppstd):
            tc.cache_variables["BUILD_CPP_STANDARD"] = "C++"+self._min_cppstd
        else:
            tc.cache_variables["BUILD_CPP_STANDARD"] = "C++"+str(self.settings.compiler.cppstd)

        tc.cache_variables["BUILD_LIBRARY_TYPE"] = "Shared" if self.options.shared else "Static"
        tc.cache_variables["INSTALL_TEST_CASES"] = False
        tc.cache_variables["BUILD_RESOURCES"] = False
        tc.cache_variables["BUILD_RELEASE_DISABLE_EXCEPTIONS"] = True
        if self.settings.build_type == "Debug":
            tc.cache_variables["BUILD_WITH_DEBUG"] = self.options.extended_debug_messages
        tc.cache_variables["BUILD_USE_PCH"] = False
        tc.cache_variables["INSTALL_SAMPLES"] = False

        tc.cache_variables["INSTALL_DIR_LAYOUT"] = "Unix"
        tc.cache_variables["INSTALL_DIR_BIN"] = "bin"
        tc.cache_variables["INSTALL_DIR_LIB"] = "lib"
        tc.cache_variables["INSTALL_DIR_INCLUDE"] = "include"
        tc.cache_variables["INSTALL_DIR_RESOURCE"] = "res/resource"
        tc.cache_variables["INSTALL_DIR_DATA"] = "res/data"
        tc.cache_variables["INSTALL_DIR_SAMPLES"] = "res/samples"
        tc.cache_variables["INSTALL_DIR_DOC"] = "res/doc"

        if is_msvc(self):
            tc.cache_variables["BUILD_SAMPLES_MFC"] = False
        tc.cache_variables["BUILD_SAMPLES_QT"] = self.options.with_samples
        tc.cache_variables["BUILD_Inspector"] = False
        if is_apple_os(self):
            tc.cache_variables["USE_GLX"] = False
        if self.settings.os == "Windows":
            tc.cache_variables["USE_D3D"] = False
        tc.cache_variables["BUILD_ENABLE_FPE_SIGNAL_HANDLER"] = False
        tc.cache_variables["BUILD_DOC_Overview"] = False

        tc.cache_variables["USE_FFMPEG"] = self.options.with_ffmpeg
        
        tc.cache_variables["USE_FREEIMAGE"] = "freeimage" in self.dependencies
        tc.cache_variables["USE_OPENVR"] = "openvr" in self.dependencies
        tc.cache_variables["USE_OPENGL"] = "opengl" in self.dependencies
        # tc.cache_variables["USE_RAPIDJSON"] = True
        # tc.cache_variables["USE_DRACO"] = True
        # # tc.cache_variables["USE_TK"] = True
        tc.cache_variables["USE_TBB"] = "onetbb" in self.dependencies

        # Relocatable shared libs on Macos
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"

        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        cmakelists_tools = os.path.join(self.source_folder, "tools", "CMakeLists.txt")
        occt_toolkit_cmake = os.path.join(self.source_folder, "adm", "cmake", "occt_toolkit.cmake")
        occt_csf_cmake = os.path.join(self.source_folder, "adm", "cmake", "occt_csf.cmake")
        occt_defs_flags_cmake = os.path.join(self.source_folder, "adm", "cmake", "occt_defs_flags.cmake")

        # Inject interface definitions of dependencies because opencascade
        # does not always link to CMake imported targets
        sorted_deps = [dep for dep in reversed(self.dependencies.host.topological_sort.values())]
        deps_defines = " ".join([f"-D{d}" for dep in sorted_deps for d in dep.cpp_info.aggregated_components().defines])
        replace_in_file(
            self,
            cmakelists,
            "project (OCCT)",
            textwrap.dedent(f"""\
                project (OCCT)
                add_definitions({deps_defines})
            """),
        )

        # Avoid to add system include/libs directories and inject directories
        # from conan dependencies instead
        for cmake_file in [cmakelists, cmakelists_tools]:
            deps_includedirs = ";".join([p.replace("\\", "/") for dep in sorted_deps for p in dep.cpp_info.aggregated_components().includedirs])
            replace_in_file(
                self,
                cmake_file,
                "if (3RDPARTY_INCLUDE_DIRS)",
                f"set(3RDPARTY_INCLUDE_DIRS \"{deps_includedirs}\")\nif (3RDPARTY_INCLUDE_DIRS)",
            )
            deps_libdirs = ";".join([p.replace("\\", "/") for dep in sorted_deps for p in dep.cpp_info.aggregated_components().libdirs])
            replace_in_file(
                self,
                cmake_file,
                "if (3RDPARTY_LIBRARY_DIRS)",
                f"set(3RDPARTY_LIBRARY_DIRS \"{deps_libdirs}\")\nif (3RDPARTY_LIBRARY_DIRS)",
            )

        # Do not fail due to "fragile" upstream logic to find dependencies
        replace_in_file(self, cmakelists, "if (3RDPARTY_NOT_INCLUDED)", "if(0)")
        replace_in_file(self, cmakelists, "if (3RDPARTY_NO_LIBS)", "if(0)")
        replace_in_file(self, cmakelists, "if (3RDPARTY_NO_DLLS)", "if(0)")

        # Inject dependencies from conan, and avoid to rely on upstream custom CMake files
        deps_targets = []

        ## freetype
        if "freetype" in self.dependencies:
            deps_targets.append("Freetype::Freetype")
            replace_in_file(
                self,
                cmakelists,
                "OCCT_INCLUDE_CMAKE_FILE (\"adm/cmake/freetype\")",
                "find_package(Freetype REQUIRED MODULE)",
            )
            freetype_libs = " ".join(self.dependencies["freetype"].cpp_info.aggregated_components().libs)
            replace_in_file(
                self,
                occt_csf_cmake,
                "set (CSF_FREETYPE \"freetype\")",
                f"set (CSF_FREETYPE \"{freetype_libs}\")",
            )
        # tk
        if "tk" in self.dependencies:
            deps_targets.append("tk::tk")
            replace_in_file(self, cmakelists, "OCCT_INCLUDE_CMAKE_FILE (\"adm/cmake/tk\")", "find_package(tk REQUIRED)")
            tk_libs = " ".join(self.dependencies["tk"].cpp_info.aggregated_components().libs)
            csf_tk_libs = f"set (CSF_TclTkLibs \"{tk_libs}\")"
            replace_in_file(self, occt_csf_cmake, "set (CSF_TclTkLibs   \"tk86\")", csf_tk_libs)
            replace_in_file(self, occt_csf_cmake, "set (CSF_TclTkLibs Tk)", csf_tk_libs)
            replace_in_file(self, occt_csf_cmake, "set (CSF_TclTkLibs \"tk8.6\")", csf_tk_libs)
        ## fontconfig
        if "fontconfig" in self.dependencies and self._is_linux:
            deps_targets.append("Fontconfig::Fontconfig")
            fontconfig_libs = " ".join(self.dependencies["fontconfig"].cpp_info.aggregated_components().libs)
            replace_in_file(
                self,
                occt_csf_cmake,
                "set (CSF_fontconfig \"fontconfig\")",
                f"find_package(Fontconfig REQUIRED)\nset (CSF_fontconfig \"{fontconfig_libs}\")",
            )
        ## onetbb
        if "onetbb" in self.dependencies:
            deps_targets.append("TBB::tbb")
            replace_in_file(
                self,
                cmakelists,
                "OCCT_INCLUDE_CMAKE_FILE (\"adm/cmake/tbb\")",
                "find_package(TBB REQUIRED)",
            )
            tbb_libs = " ".join(self.dependencies["onetbb"].cpp_info.aggregated_components().libs)
            replace_in_file(
                self,
                occt_csf_cmake,
                "set (CSF_TBB \"tbb tbbmalloc\")",
                f"set (CSF_TBB \"{tbb_libs}\")",
            )
        ## ffmpeg
        if "ffmpeg" in self.dependencies:
            deps_targets.append("ffmpeg::ffmpeg")
            replace_in_file(
                self,
                cmakelists,
                "OCCT_INCLUDE_CMAKE_FILE (\"adm/cmake/ffmpeg\")",
                "find_package(ffmpeg REQUIRED)",
            )
            ffmpeg_libs = " ".join(self.dependencies["ffmpeg"].cpp_info.aggregated_components().libs)
            replace_in_file(
                self,
                occt_csf_cmake,
                "set (CSF_FFmpeg \"avcodec avformat swscale avutil\")",
                f"set (CSF_FFmpeg \"{ffmpeg_libs}\")",
            )
        ## freeimage
        if "freeimage" in self.dependencies:
            deps_targets.append("freeimage::freeimage")
            replace_in_file(
                self, cmakelists,
                "OCCT_INCLUDE_CMAKE_FILE (\"adm/cmake/freeimage\")",
                "find_package(freeimage REQUIRED)",
            )
            freeimage_libs = " ".join(self.dependencies["freeimage"].cpp_info.aggregated_components().libs)
            replace_in_file(
                self,
                occt_csf_cmake,
                "set (CSF_FreeImagePlus \"freeimage\")",
                f"set (CSF_FreeImagePlus \"{freeimage_libs}\")",
            )
        ## openvr
        if "openvr" in self.dependencies:
            deps_targets.append("openvr::openvr")
            replace_in_file(
                self,
                cmakelists,
                "OCCT_INCLUDE_CMAKE_FILE (\"adm/cmake/openvr\")",
                "find_package(openvr REQUIRED)",
            )
            openvr_libs = " ".join(self.dependencies["openvr"].cpp_info.aggregated_components().libs)
            replace_in_file(
                self,
                occt_csf_cmake,
                "set (CSF_OpenVR \"openvr_api\")",
                f"set (CSF_OpenVR \"{openvr_libs}\")",
            )
        ## rapidjson
        if "rapidjson" in self.dependencies:
            deps_targets.append("rapidjson")
            replace_in_file(
                self,
                cmakelists,
                "OCCT_INCLUDE_CMAKE_FILE (\"adm/cmake/rapidjson\")",
                "find_package(RapidJSON REQUIRED)",
            )
        ## draco
        if "draco" in self.dependencies:
            deps_targets.append("draco::draco")
            replace_in_file(
                self,
                cmakelists,
                "if (CAN_USE_DRACO)",
                "if (true)",
            )
            replace_in_file(
                self,
                cmakelists,
                "if (USE_DRACO)",
                "if (true)",
            )
            replace_in_file(
                self,
                cmakelists,
                "OCCT_INCLUDE_CMAKE_FILE (\"adm/cmake/draco\")",
                "find_package(draco REQUIRED)",
            )
        ## opengl
        if "opengl" in self.dependencies:
            replace_in_file(
                self,
                occt_csf_cmake,
                "set (CSF_OpenGlLibs ",
                "find_package(OpenGL)\n# set (CSF_OpenGlLibs ",
            )
            deps_targets.append("OpenGL::GL")

        ## Inject dependencies targets
        replace_in_file(
            self,
            occt_toolkit_cmake,
            "${USED_EXTERNAL_LIBS_BY_CURRENT_PROJECT}",
            "${{USED_EXTERNAL_LIBS_BY_CURRENT_PROJECT}} {}".format(" ".join(deps_targets)),
        )

        # Do not install pdb files
        # replace_in_file(
        #     self,
        #     occt_toolkit_cmake,
        #     """    install (FILES  ${CMAKE_BINARY_DIR}/${OS_WITH_BIT}/${COMPILER}/bin\\${OCCT_INSTALL_BIN_LETTER}/${PROJECT_NAME}.pdb
        #     CONFIGURATIONS Debug ${aReleasePdbConf} RelWithDebInfo
        #     DESTINATION "${INSTALL_DIR_BIN}\\${OCCT_INSTALL_BIN_LETTER}")""",
        #     "",
        # )

        # Honor fPIC option, compiler.cppstd and compiler.libcxx
        replace_in_file(self, occt_defs_flags_cmake, "-fPIC", "")
        replace_in_file(self, occt_defs_flags_cmake, "-stdlib=libc++", "")
        replace_in_file(self, occt_csf_cmake,
                              'set (CSF_ThreadLibs  "pthread rt stdc++")',
                              'set (CSF_ThreadLibs  "pthread rt")')

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def _replace_package_folder(self, source, target):
        if os.path.isdir(os.path.join(self.package_folder, source)):
            rmdir(self, os.path.join(self.package_folder, target))
            rename(self, os.path.join(self.package_folder, source),
                         os.path.join(self.package_folder, target))

    def package(self):
        cmake = CMake(self)
        cmake.install()
        for license_file in ["LICENSE_LGPL_21.txt", "OCCT_LGPL_EXCEPTION.txt"]:
            copy(self, license_file, src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        if self.settings.build_type == "Debug":
            self._replace_package_folder("libd", "lib")
            self._replace_package_folder("bind", "bin")
        elif self.settings.build_type == "RelWithDebInfo":
            self._replace_package_folder("libi", "lib")
            self._replace_package_folder("bini", "bin")

        occt_modules = self._get_modules_from_source_code()
        self._create_modules_json_file(occt_modules)

    @property
    def _cmake_module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def _get_modules_from_source_code(self):
        csf_to_conan_dependencies = {
            # Mandatory dependencies
            "CSF_FREETYPE": {"externals": ["freetype::freetype"]},
            "CSF_TclLibs": {"externals": ["tcl::tcl"]},
            "CSF_fontconfig": {"externals": ["fontconfig::fontconfig"] if self._is_linux else []},
            "CSF_XwLibs": {"externals": ["xorg::xorg"] if self._is_linux else []},
            # Optional dependencies
            "CSF_OpenGlLibs": {"externals": ["opengl::opengl"] if "opengl" in self.dependencies else []},
            "CSF_TclTkLibs": {"externals": ["tk::tk"] if "tk" in self.dependencies else []},
            "CSF_FFmpeg": {"externals": ["ffmpeg::ffmpeg"] if "ffmpeg" in self.dependencies else []},
            "CSF_FreeImagePlus": {"externals": ["freeimage::freeimage"] if "freeimage" in self.dependencies else []},
            "CSF_OpenVR": {"externals": ["openvr::openvr"] if "openvr" in self.dependencies else []},
            "CSF_RapidJSON": {"externals": ["rapidjson::rapidjson"] if "rapidjson" in self.dependencies else []},
            "CSF_Draco": {"externals": ["draco::draco"] if "draco" in self.dependencies else []},
            "CSF_TBB": {"externals": ["onetbb::onetbb"] if "onetbb" in self.dependencies else []},

            "CSF_VTK": {},
            # Android system libs
            "CSF_androidlog": {"system_libs": ["log"] if self.settings.os == "Android" else []},
            # Linux system libs
            "CSF_ThreadLibs": {"system_libs": ["pthread", "rt"] if self._is_linux else []},
            "CSF_dl": {"system_libs": ["dl"] if self._is_linux else []},
            "CSF_dpsLibs": {},
            "CSF_XmuLibs": {},
            # Windows system libs
            "CSF_advapi32": {"system_libs": ["advapi32"] if self.settings.os == "Windows" else []},
            "CSF_gdi32": {"system_libs": ["gdi32"] if self.settings.os == "Windows" else []},
            "CSF_psapi": {"system_libs": ["psapi"] if self.settings.os == "Windows" else []},
            "CSF_shell32": {"system_libs": ["shell32"] if self.settings.os == "Windows" else []},
            "CSF_user32": {"system_libs": ["user32"] if self.settings.os == "Windows" else []},
            "CSF_winmm": {"system_libs": ["winmm"] if self.settings.os == "Windows" else []},
            "CSF_wsock32": {"system_libs": ["wsock32"] if self.settings.os == "Windows" else []},
            "CSF_d3d9": {},
            # Apple OS frameworks
            "CSF_Appkit": {"frameworks": ["UIKit"] if self.settings.os == "iOS" else ["Appkit"] if is_apple_os(self) else []},
            "CSF_IOKit": {"frameworks": ["IOKit"] if is_apple_os(self) else []},
            "CSF_objc": {},
        }

        modules = {}

        # MODULES: lists all modules and all possible components per module
        modules_content = load(self, os.path.join(self.source_folder, "adm", "MODULES"))
        packaged_libs_list = collect_libs(self, "lib")
        for module_line in modules_content.splitlines():
            components = {}
            module_components = module_line.split()
            components_list = [component for component in module_components[1:] if component in packaged_libs_list]
            for component_name in components_list:
                component_deps = {}
                # EXTERNLIB: stores dependencies of each component. External dependencies are prefixed with CSF_
                externlib_content = load(self, os.path.join(self.source_folder, "src", component_name, "EXTERNLIB"))
                for dependency in externlib_content.splitlines():
                    if dependency.startswith("TK") and dependency in packaged_libs_list:
                        component_deps.setdefault("internals", []).append(dependency)
                    elif dependency.startswith("CSF_"):
                        deps_dict = csf_to_conan_dependencies.get(dependency)
                        if deps_dict:
                            for dep_type, deps in deps_dict.items():
                                if deps:
                                    component_deps.setdefault(dep_type, []).extend(deps)
                components.update({component_name: component_deps})
            modules.update({module_components[0]:components})

        return modules

    def _create_modules_json_file(self, modules):
        save(self, self._modules_helper_filepath, json.dumps(modules, indent=4))

    @property
    def _modules_helper_filepath(self):
        return os.path.join(self.package_folder, "lib", "occt_modules.json")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OpenCASCADE")

        def _to_qualified_name(target):
            return f"occt_{target.lower()}"

        def _register_components(modules_dict):
            for module, targets in modules_dict.items():
                conan_component_module_name = _to_qualified_name(module)
                # FIXME: in this "module" target we would like to model COMPONENTS for find_package() but
                #       for the moment it generates in CMakeDeps some weird component name like
                #       opencascade::FoundationClasses instead of FoundationClasses.
                #       see https://github.com/conan-io/conan/issues/10258
                self.cpp_info.components[conan_component_module_name].set_property("cmake_target_name", module)

                for target_lib, target_deps in targets.items():
                    conan_component_target_name = _to_qualified_name(target_lib)
                    requires = [_to_qualified_name(internal) for internal in target_deps.get("internals", [])] + \
                               target_deps.get("externals", [])
                    system_libs = target_deps.get("system_libs", [])
                    frameworks = target_deps.get("frameworks", [])

                    self.cpp_info.components[conan_component_target_name].set_property("cmake_target_name", target_lib)
                    self.cpp_info.components[conan_component_target_name].libs = [target_lib]
                    self.cpp_info.components[conan_component_target_name].requires = requires
                    self.cpp_info.components[conan_component_target_name].system_libs = system_libs
                    self.cpp_info.components[conan_component_target_name].frameworks = frameworks
                    if self.settings.os == "Windows" and not self.options.shared:
                        self.cpp_info.components[conan_component_target_name].defines.append("OCCT_STATIC_BUILD")

                    self.cpp_info.components[conan_component_module_name].requires.append(conan_component_target_name)

                    # TODO: to remove in conan v2 once cmake_find_package* generators removed
                    self.cpp_info.components[conan_component_target_name].names["cmake_find_package"] = target_lib
                    self.cpp_info.components[conan_component_target_name].names["cmake_find_package_multi"] = target_lib
                    self.cpp_info.components[conan_component_target_name].build_modules["cmake_find_package"] = [self._cmake_module_file_rel_path]
                    self.cpp_info.components[conan_component_target_name].build_modules["cmake_find_package_multi"] = [self._cmake_module_file_rel_path]

                # TODO: to remove in conan v2 once cmake_find_package* generators removed
                self.cpp_info.components[conan_component_module_name].names["cmake_find_package"] = module
                self.cpp_info.components[conan_component_module_name].names["cmake_find_package_multi"] = module

        occt_modules_json_content = load(self, self._modules_helper_filepath)
        occt_modules = json.loads(occt_modules_json_content)
        _register_components(occt_modules)

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "OpenCASCADE"
        self.cpp_info.filenames["cmake_find_package_multi"] = "OpenCASCADE"
        if self.options.shared:
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
