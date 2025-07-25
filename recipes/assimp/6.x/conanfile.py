from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import stdcpp_library, check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import collect_libs, copy, export_conandata_patches, get, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"

class AssimpConan(ConanFile):
    name = "assimp"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/assimp/assimp"
    description = (
        "A library to import and export various 3d-model-formats including "
        "scene-post-processing to generate missing render data."
    )
    topics = ("assimp", "3d", "game development", "3mf", "collada")
    license = "BSD-3-Clause"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "double_precision": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "double_precision": False,
    }

    _format_option_map = {
        "with_3d": "ASSIMP_BUILD_3D_IMPORTER",
        "with_3ds": "ASSIMP_BUILD_3DS_IMPORTER",
        "with_3ds_exporter": "ASSIMP_BUILD_3DS_EXPORTER",
        "with_3mf": "ASSIMP_BUILD_3MF_IMPORTER",
        "with_3mf_exporter": "ASSIMP_BUILD_3MF_EXPORTER",
        "with_ac": "ASSIMP_BUILD_AC_IMPORTER",
        "with_amf": "ASSIMP_BUILD_AMF_IMPORTER",
        "with_ase": "ASSIMP_BUILD_ASE_IMPORTER",
        "with_assbin": "ASSIMP_BUILD_ASSBIN_IMPORTER",
        "with_assbin_exporter": "ASSIMP_BUILD_ASSBIN_EXPORTER",
        "with_assxml_exporter": "ASSIMP_BUILD_ASSXML_EXPORTER",
        "with_assjson_exporter": "ASSIMP_BUILD_ASSJSON_EXPORTER",
        "with_b3d": "ASSIMP_BUILD_B3D_IMPORTER",
        "with_blend": "ASSIMP_BUILD_BLEND_IMPORTER",
        "with_bvh": "ASSIMP_BUILD_BVH_IMPORTER",
        "with_ms3d": "ASSIMP_BUILD_MS3D_IMPORTER",
        "with_cob": "ASSIMP_BUILD_COB_IMPORTER",
        "with_collada": "ASSIMP_BUILD_COLLADA_IMPORTER",
        "with_collada_exporter": "ASSIMP_BUILD_COLLADA_EXPORTER",
        "with_csm": "ASSIMP_BUILD_CSM_IMPORTER",
        "with_dxf": "ASSIMP_BUILD_DXF_IMPORTER",
        "with_fbx": "ASSIMP_BUILD_FBX_IMPORTER",
        "with_fbx_exporter": "ASSIMP_BUILD_FBX_EXPORTER",
        "with_gltf": "ASSIMP_BUILD_GLTF_IMPORTER",
        "with_gltf_exporter": "ASSIMP_BUILD_GLTF_EXPORTER",
        "with_hmp": "ASSIMP_BUILD_HMP_IMPORTER",
        "with_ifc": "ASSIMP_BUILD_IFC_IMPORTER",
        "with_irr": "ASSIMP_BUILD_IRR_IMPORTER",
        "with_irrmesh": "ASSIMP_BUILD_IRRMESH_IMPORTER",
        "with_lwo": "ASSIMP_BUILD_LWO_IMPORTER",
        "with_lws": "ASSIMP_BUILD_LWS_IMPORTER",
        "with_md2": "ASSIMP_BUILD_MD2_IMPORTER",
        "with_md3": "ASSIMP_BUILD_MD3_IMPORTER",
        "with_md5": "ASSIMP_BUILD_MD5_IMPORTER",
        "with_mdc": "ASSIMP_BUILD_MDC_IMPORTER",
        "with_mdl": "ASSIMP_BUILD_MDL_IMPORTER",
        "with_mmd": "ASSIMP_BUILD_MMD_IMPORTER",
        "with_ndo": "ASSIMP_BUILD_NDO_IMPORTER",
        "with_nff": "ASSIMP_BUILD_NFF_IMPORTER",
        "with_obj": "ASSIMP_BUILD_OBJ_IMPORTER",
        "with_obj_exporter": "ASSIMP_BUILD_OBJ_EXPORTER",
        "with_off": "ASSIMP_BUILD_OFF_IMPORTER",
        "with_ogre": "ASSIMP_BUILD_OGRE_IMPORTER",
        "with_opengex": "ASSIMP_BUILD_OPENGEX_IMPORTER",
        "with_opengex_exporter": "ASSIMP_BUILD_OPENGEX_EXPORTER",
        "with_pbrt_exporter": "ASSIMP_BUILD_PBRT_EXPORTER",
        "with_ply": "ASSIMP_BUILD_PLY_IMPORTER",
        "with_ply_exporter": "ASSIMP_BUILD_PLY_EXPORTER",
        "with_q3bsp": "ASSIMP_BUILD_Q3BSP_IMPORTER",
        "with_q3d": "ASSIMP_BUILD_Q3D_IMPORTER",
        "with_raw": "ASSIMP_BUILD_RAW_IMPORTER",
        "with_sib": "ASSIMP_BUILD_SIB_IMPORTER",
        "with_smd": "ASSIMP_BUILD_SMD_IMPORTER",
        "with_step": "ASSIMP_BUILD_STEP_IMPORTER",
        "with_step_exporter": "ASSIMP_BUILD_STEP_EXPORTER",
        "with_stl": "ASSIMP_BUILD_STL_IMPORTER",
        "with_stl_exporter": "ASSIMP_BUILD_STL_EXPORTER",
        "with_terragen": "ASSIMP_BUILD_TERRAGEN_IMPORTER",
        "with_x": "ASSIMP_BUILD_X_IMPORTER",
        "with_x_exporter": "ASSIMP_BUILD_X_EXPORTER",
        "with_x3d": "ASSIMP_BUILD_X3D_IMPORTER",
        "with_x3d_exporter": "ASSIMP_BUILD_X3D_EXPORTER",
        "with_xgl": "ASSIMP_BUILD_XGL_IMPORTER",
        "with_m3d": "ASSIMP_BUILD_M3D_IMPORTER",
        "with_m3d_exporter": "ASSIMP_BUILD_M3D_EXPORTER",
        "with_iqm": "ASSIMP_BUILD_IQM_IMPORTER"
    }
    options.update(dict.fromkeys(_format_option_map, [True, False]))
    default_options.update(dict.fromkeys(_format_option_map, True))

    short_paths = True

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10",
            "msvc": "191",
            "Visual Studio": "15",
        }

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

    @property
    def _depends_on_kuba_zip(self):
        return self.options.with_3mf_exporter

    @property
    def _depends_on_poly2tri(self):
        return self.options.with_blend or self.options.with_ifc

    @property
    def _depends_on_rapidjson(self):
        return self.options.with_gltf or self.options.with_gltf_exporter

    @property
    def _depends_on_draco(self):
        return self.options.with_gltf or self.options.with_gltf_exporter

    @property
    def _depends_on_clipper(self):
        return self.options.with_ifc

    @property
    def _depends_on_stb(self):
        return self.options.with_m3d or self.options.with_m3d_exporter or \
            self.options.with_pbrt_exporter

    @property
    def _depends_on_openddlparser(self):
        return self.options.with_opengex

    def requirements(self):
        # TODO: unvendor others libs:
        # - Open3DGC
        self.requires("minizip/1.3.1")
        self.requires("pugixml/1.15")
        self.requires("utfcpp/4.0.5")
        self.requires("zlib/[>=1.2.11 <2]")
        if self._depends_on_kuba_zip:
            self.requires("kuba-zip/0.3.2")
        if self._depends_on_poly2tri:
            self.requires("poly2tri/cci.20130502")
        if self._depends_on_rapidjson:
            self.requires("rapidjson/1.1.0")
        if self._depends_on_draco:
            self.requires("draco/1.5.6")
        if self._depends_on_clipper:
            self.requires("clipper/6.4.2")
        if self._depends_on_stb:
            self.requires("stb/cci.20240531")
        if self._depends_on_openddlparser:
            self.requires("openddl-parser/0.5.1")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.22 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ASSIMP_ANDROID_JNIIOSYSTEM"] = False
        tc.variables["ASSIMP_BUILD_ALL_IMPORTERS_BY_DEFAULT"] = False
        tc.variables["ASSIMP_BUILD_ALL_EXPORTERS_BY_DEFAULT"] = False
        tc.variables["ASSIMP_BUILD_ASSIMP_TOOLS"] = False
        tc.variables["ASSIMP_BUILD_DOCS"] = False
        tc.variables["ASSIMP_BUILD_DRACO"] = False
        tc.variables["ASSIMP_BUILD_FRAMEWORK"] = False
        tc.variables["ASSIMP_BUILD_MINIZIP"] = False
        tc.variables["ASSIMP_BUILD_SAMPLES"] = False
        tc.variables["ASSIMP_BUILD_TESTS"] = False
        tc.variables["ASSIMP_BUILD_ZLIB"] = False
        tc.variables["ASSIMP_DOUBLE_PRECISION"] = self.options.double_precision
        tc.variables["ASSIMP_HUNTER_ENABLED"] = False
        tc.variables["ASSIMP_IGNORE_GIT_HASH"] = True
        tc.variables["ASSIMP_INJECT_DEBUG_POSTFIX"] = False
        tc.variables["ASSIMP_INSTALL"] = True
        tc.variables["ASSIMP_INSTALL_PDB"] = False
        tc.variables["ASSIMP_NO_EXPORT"] = False
        tc.variables["ASSIMP_OPT_BUILD_PACKAGES"] = False
        tc.variables["ASSIMP_RAPIDJSON_NO_MEMBER_ITERATOR"] = False
        tc.variables["ASSIMP_UBSAN"] = False
        tc.variables["ASSIMP_WARNINGS_AS_ERRORS"] = False
        tc.variables["USE_STATIC_CRT"] = is_msvc_static_runtime(self)
        tc.variables["ASSIMP_BUILD_USE_CCACHE"] = False

        for option, definition in self._format_option_map.items():
            value = self.options.get_safe(option)
            if value is not None:
                tc.variables[definition] = value
        if self.settings.os == "Windows":
            tc.preprocessor_definitions["NOMINMAX"] = 1

        # tc.cache_variables["CMAKE_PROJECT_Assimp_INCLUDE"] = "conan_deps.cmake"
        tc.cache_variables["WITH_CLIPPER"] = self._depends_on_clipper
        tc.cache_variables["WITH_DRACO"] = self._depends_on_draco
        tc.cache_variables["WITH_KUBAZIP"] = self._depends_on_kuba_zip
        tc.cache_variables["WITH_OPENDDL"] = self._depends_on_openddlparser
        tc.cache_variables["WITH_POLY2TRI"] = self._depends_on_poly2tri
        tc.cache_variables["WITH_RAPIDJSON"] = self._depends_on_rapidjson
        tc.cache_variables["WITH_STB"] = self._depends_on_stb
        tc.generate()

        cd = CMakeDeps(self)
        cd.set_property("rapidjson", "cmake_target_name", "rapidjson::rapidjson")
        cd.set_property("utfcpp", "cmake_target_name", "utf8cpp::utf8cpp")
        cd.generate()

        venv = VirtualBuildEnv(self)
        venv.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "assimp")
        self.cpp_info.set_property("cmake_target_name", "assimp::assimp")
        self.cpp_info.set_property("pkg_config_name", "assimp")
        self.cpp_info.libs = collect_libs(self)
        if is_msvc(self) and self.options.shared:
            self.cpp_info.defines.append("ASSIMP_DLL")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["rt", "m", "pthread"]
        if not self.options.shared:
            libcxx = stdcpp_library(self)
            if libcxx:
                self.cpp_info.system_libs.append(libcxx)
