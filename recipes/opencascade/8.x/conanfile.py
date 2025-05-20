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

required_conan_version = ">=2.1"


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
        "with_freeimage": [True, False],
        "with_openvr": [True, False],
        "with_rapidjson": [True, False],
        "with_draco": [True, False],
        "with_tk": [True, False],
        "with_tbb": [True, False],
        "with_opengl": [True, False],
        "extended_debug_messages": [True, False],
        "mmgr_type": ["NATIVE", "FLEXIBLE", "TBB", "JEMALLOC"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ffmpeg": False,
        "with_freeimage": True,
        "with_openvr": True,
        "with_rapidjson": True,
        "with_draco": False,
        "with_tk": True,
        "with_tbb": True,
        "with_opengl": True,
        "extended_debug_messages": True,
        "mmgr_type": "NATIVE",
    }

    short_paths = True

    @property
    def _is_linux(self):
        return self.settings.os in ["Linux", "FreeBSD"]

    @property
    def _link_tk(self):
        return self.options.with_tk

    @property
    def _link_opengl(self):
        return self.options.with_opengl

    @property
    def _min_cppstd(self):
        return "11"

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
        self.requires("tcl/8.6.10")
        self.requires("freetype/2.13.2")
        if self._link_tk:
            self.requires("tk/8.6.10")
        if self._link_opengl:
            self.requires("opengl/system")
        if self._is_linux:
            self.requires("fontconfig/2.13.93")
            self.requires("xorg/system")
        # TODO: add vtk support?
        if self.options.with_ffmpeg:
            self.requires("ffmpeg/7.1.1")
        if self.options.with_freeimage:
            self.requires("freeimage/3.18.0")
        if self.options.with_openvr:
            self.requires("openvr/1.16.8")
        if self.options.with_rapidjson:
            self.requires("rapidjson/1.1.0")
        if self.options.get_safe("with_draco"):
            self.requires("draco/1.5.6")
        if self.options.with_tbb or self.options.mmgr_type == "TBB":
            self.requires("onetbb/2022.0.0")
        if self.options.mmgr_type == "JEMALLOC":
            self.requires("jemalloc/5.3.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        if self.settings.compiler == "clang" and self.settings.compiler.version == "6.0" and \
           self.settings.build_type == "Release":
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support Clang 6.0 if Release build type")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)

        # Inject C++ standard from profile since we have removed hardcoded C++ standard from upstream build files
        if not valid_min_cppstd(self, self._min_cppstd):
            tc.variables["BUILD_CPP_STANDARD"] = self._min_cppstd

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
        tc.cache_variables["BUILD_SAMPLES_QT"] = False
        if is_apple_os(self):
            tc.cache_variables["USE_GLX"] = False
        if self.settings.os == "Windows":
            tc.cache_variables["USE_D3D"] = False
        tc.cache_variables["BUILD_ENABLE_FPE_SIGNAL_HANDLER"] = False
        tc.cache_variables["BUILD_DOC_Overview"] = False

        tc.cache_variables["USE_FREEIMAGE"] = self.options.with_freeimage
        tc.cache_variables["USE_OPENVR"] = self.options.with_openvr
        tc.cache_variables["USE_FFMPEG"] = self.options.with_ffmpeg
        tc.cache_variables["USE_TBB"] = self.options.with_tbb
        tc.cache_variables["USE_RAPIDJSON"] = self.options.with_rapidjson
        tc.cache_variables["USE_DRACO"] = self.options.with_draco
        tc.cache_variables["USE_TK"] = self.options.with_tk
        tc.cache_variables["USE_OPENGL"] = self.options.with_opengl

        # 3RDPARTY_DIR 
        tc.variables["3RDPARTY_DIR"] = self.source_folder+"/../"+self.folders.generators
        
        tcl = self.dependencies['tcl'].cpp_info
        tc.variables["3RDPARTY_TCL_LIBRARY_DIR"] = tcl.includedirs[0]+"/../"
        tc.variables["3RDPARTY_TCL_LIBRARY"] = tcl.libdirs[0]
        tc.variables["3RDPARTY_TCL_INCLUDE_DIR"] = tcl.includedirs[0]

        freetype = self.dependencies['freetype'].cpp_info
        tc.variables["3RDPARTY_FREETYPE_DIR"] = freetype.includedirs[0]+"/../"
        tc.variables["3RDPARTY_FREETYPE_LIBRARY"] = freetype.libdirs[0]
        tc.variables["3RDPARTY_FREETYPE_INCLUDE_DIR"] = freetype.includedirs[0]

        if self._is_linux:
            fontconfig = self.dependencies['fontconfig'].cpp_info
            tc.variables["3RDPARTY_FONTCONFIG_DIR"] = freetype.includedirs[0]+"/../"
            tc.variables["3RDPARTY_FONTCONFIG_LIBRARY"] = fontconfig.libdirs[0]
            tc.variables["3RDPARTY_FONTCONFIG_INCLUDE_DIR"] = fontconfig.includedirs[0]
            # self.requires("xorg/system")

        if self._link_tk:
            tk = self.dependencies['tk'].cpp_info
            tc.variables["3RDPARTY_TK_DIR"] = tk.includedirs[0]+"/../"
            tc.variables["3RDPARTY_TK_LIBRARY"] = tk.libdirs[0]
            tc.variables["3RDPARTY_TK_INCLUDE_DIR"] = tk.includedirs[0]

        if self.options.with_openvr:
            openvr = self.dependencies['openvr'].cpp_info
            tc.variables["3RDPARTY_OP_DIR"] = openvr.includedirs[0]+"/../"
            tc.variables["3RDPARTY_RAPIDJSON_LIBRARY"] = openvr.libdirs[0]
            tc.variables["3RDPARTY_RAPIDJSON_INCLUDE_DIR"] = openvr.includedirs[0]

        if self.options.with_rapidjson:
            rapidjson = self.dependencies['rapidjson'].cpp_info
            tc.variables["3RDPARTY_RAPIDJSON_DIR"] = rapidjson.includedirs[0]+"/../"
            tc.variables["3RDPARTY_RAPIDJSON_INCLUDE_DIR"] = rapidjson.includedirs[0]

        if self.options.get_safe("with_draco"):
            draco = self.dependencies['draco'].cpp_info
            tc.variables["3RDPARTY_DRACO_DIR"] = draco.includedirs[0]+"/../"
            tc.variables["3RDPARTY_DRACO_LIBRARY"] = draco.libdirs[0]
            tc.variables["3RDPARTY_DRACO_INCLUDE_DIR"] = draco.includedirs[0]

        if self.options.with_tbb:
            onetbb = self.dependencies['onetbb'].cpp_info
            tc.variables["3RDPARTY_TBB_DIR"] = onetbb.includedirs[0]+"/../"
            tc.variables["3RDPARTY_TBB_LIBRARY"] = onetbb.libdirs[0]
            tc.variables["3RDPARTY_TBB_INCLUDE_DIR"] = onetbb.includedirs[0]
            tc.variables["TBB_INCLUDE_DIR"] = onetbb.includedirs[0]

        if self.options.mmgr_type == "JEMALLOC":
            jemalloc = self.dependencies['jemalloc'].cpp_info
            tc.variables["3RDPARTY_JEMALLOC_DIR"] = jemalloc.includedirs[0]+"/../"
            tc.variables["3RDPARTY_JEMALLOC_LIBRARY"] = jemalloc.libdirs[0]
            tc.variables["3RDPARTY_JEMALLOC_INCLUDE_DIR"] = jemalloc.includedirs[0]
            
        # Relocatable shared libs on Macos
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        tc.generate()

        deps = CMakeDeps(self)
        # deps.set_property("onetbb::libtbb", "INTERFACE_INCLUDE_DIRECTORIES", onetbb.includedirs[0])
        deps.generate()
        
    def _patch_sources(self):
        apply_conandata_patches(self)

        tbb_cmake = os.path.join(self.source_folder, "adm", "cmake", "tbb.cmake")
        replace_in_file(self, tbb_cmake, """TBB 2021.5
      PATHS "${3RDPARTY_TBB_DIR}" NO_DEFAULT_PATH""", "TBB")
        replace_in_file(self, tbb_cmake, "get_target_property (TBB_INCLUDE_DIR TBB::tbb INTERFACE_INCLUDE_DIRECTORIES)", "")
        

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
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        # if self.settings.build_type == "Debug":
        #     self._replace_package_folder("libd", "lib")
        #     self._replace_package_folder("bind", "bin")
        # elif self.settings.build_type == "RelWithDebInfo":
        #     self._replace_package_folder("libi", "lib")
        #     self._replace_package_folder("bini", "bin")

        occt_modules = self._get_modules_from_source_code()
        self._create_modules_json_file(occt_modules)

    def _get_modules_from_source_code(self):
        csf_to_conan_dependencies = {
            # Mandatory dependencies
            "CSF_FREETYPE": {"externals": ["freetype::freetype"]},
            "CSF_TclLibs": {"externals": ["tcl::tcl"]},
            "CSF_fontconfig": {"externals": ["fontconfig::fontconfig"] if self._is_linux else []},
            "CSF_XwLibs": {"externals": ["xorg::xorg"] if self._is_linux else []},
            # Optional dependencies
            "CSF_OpenGlLibs": {"externals": ["opengl::opengl"] if self._link_opengl else []},
            "CSF_TclTkLibs": {"externals": ["tk::tk"] if self._link_tk else []},
            "CSF_FFmpeg": {"externals": ["ffmpeg::ffmpeg"] if self.options.with_ffmpeg else []},
            "CSF_FreeImagePlus": {"externals": ["freeimage::freeimage"] if self.options.with_freeimage else []},
            "CSF_OpenVR": {"externals": ["openvr::openvr"] if self.options.with_openvr else []},
            "CSF_RapidJSON": {"externals": ["rapidjson::rapidjson"] if self.options.with_rapidjson else []},
            "CSF_Draco": {"externals": ["draco::draco"] if self.options.get_safe("with_draco") else []},
            "CSF_TBB": {"externals": ["onetbb::onetbb"] if self.options.with_tbb else []},
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
                        deps_dict = csf_to_conan_dependencies[dependency]
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

        occt_modules_json_content = load(self, self._modules_helper_filepath)
        occt_modules = json.loads(occt_modules_json_content)
        _register_components(occt_modules)
