from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, get, replace_in_file, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
from conans import tools as tools_legacy
import os

required_conan_version = ">=1.50.2 <1.51.0 || >=1.51.2"


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
    settings = "os", "compiler", "build_type", "arch"
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
        "with_3d": ("ASSIMP_BUILD_3D_IMPORTER", "5.0.0"),
        "with_3ds": ("ASSIMP_BUILD_3DS_IMPORTER", "5.0.0"),
        "with_3ds_exporter": ("ASSIMP_BUILD_3DS_EXPORTER", "5.0.0"),
        "with_3mf": ("ASSIMP_BUILD_3MF_IMPORTER", "5.0.0"),
        "with_3mf_exporter": ("ASSIMP_BUILD_3MF_EXPORTER", "5.0.0"),
        "with_ac": ("ASSIMP_BUILD_AC_IMPORTER", "5.0.0"),
        "with_amf": ("ASSIMP_BUILD_AMF_IMPORTER", "5.0.0"),
        "with_ase": ("ASSIMP_BUILD_ASE_IMPORTER", "5.0.0"),
        "with_assbin": ("ASSIMP_BUILD_ASSBIN_IMPORTER", "5.0.0"),
        "with_assbin_exporter": ("ASSIMP_BUILD_ASSBIN_EXPORTER", "5.0.0"),
        "with_assxml_exporter": ("ASSIMP_BUILD_ASSXML_EXPORTER", "5.0.0"),
        "with_assjson_exporter": ("ASSIMP_BUILD_ASSJSON_EXPORTER", "5.0.0"),
        "with_b3d": ("ASSIMP_BUILD_B3D_IMPORTER", "5.0.0"),
        "with_blend": ("ASSIMP_BUILD_BLEND_IMPORTER", "5.0.0"),
        "with_bvh": ("ASSIMP_BUILD_BVH_IMPORTER", "5.0.0"),
        "with_ms3d": ("ASSIMP_BUILD_MS3D_IMPORTER", "5.0.0"),
        "with_cob": ("ASSIMP_BUILD_COB_IMPORTER", "5.0.0"),
        "with_collada": ("ASSIMP_BUILD_COLLADA_IMPORTER", "5.0.0"),
        "with_collada_exporter": ("ASSIMP_BUILD_COLLADA_EXPORTER", "5.0.0"),
        "with_csm": ("ASSIMP_BUILD_CSM_IMPORTER", "5.0.0"),
        "with_dxf": ("ASSIMP_BUILD_DXF_IMPORTER", "5.0.0"),
        "with_fbx": ("ASSIMP_BUILD_FBX_IMPORTER", "5.0.0"),
        "with_fbx_exporter": ("ASSIMP_BUILD_FBX_EXPORTER", "5.0.0"),
        "with_gltf": ("ASSIMP_BUILD_GLTF_IMPORTER", "5.0.0"),
        "with_gltf_exporter": ("ASSIMP_BUILD_GLTF_EXPORTER", "5.0.0"),
        "with_hmp": ("ASSIMP_BUILD_HMP_IMPORTER", "5.0.0"),
        "with_ifc": ("ASSIMP_BUILD_IFC_IMPORTER", "5.0.0"),
        "with_irr": ("ASSIMP_BUILD_IRR_IMPORTER", "5.0.0"),
        "with_irrmesh": ("ASSIMP_BUILD_IRRMESH_IMPORTER", "5.0.0"),
        "with_lwo": ("ASSIMP_BUILD_LWO_IMPORTER", "5.0.0"),
        "with_lws": ("ASSIMP_BUILD_LWS_IMPORTER", "5.0.0"),
        "with_md2": ("ASSIMP_BUILD_MD2_IMPORTER", "5.0.0"),
        "with_md3": ("ASSIMP_BUILD_MD3_IMPORTER", "5.0.0"),
        "with_md5": ("ASSIMP_BUILD_MD5_IMPORTER", "5.0.0"),
        "with_mdc": ("ASSIMP_BUILD_MDC_IMPORTER", "5.0.0"),
        "with_mdl": ("ASSIMP_BUILD_MDL_IMPORTER", "5.0.0"),
        "with_mmd": ("ASSIMP_BUILD_MMD_IMPORTER", "5.0.0"),
        "with_ndo": ("ASSIMP_BUILD_NDO_IMPORTER", "5.0.0"),
        "with_nff": ("ASSIMP_BUILD_NFF_IMPORTER", "5.0.0"),
        "with_obj": ("ASSIMP_BUILD_OBJ_IMPORTER", "5.0.0"),
        "with_obj_exporter": ("ASSIMP_BUILD_OBJ_EXPORTER", "5.0.0"),
        "with_off": ("ASSIMP_BUILD_OFF_IMPORTER", "5.0.0"),
        "with_ogre": ("ASSIMP_BUILD_OGRE_IMPORTER", "5.0.0"),
        "with_opengex": ("ASSIMP_BUILD_OPENGEX_IMPORTER", "5.0.0"),
        "with_opengex_exporter": ("ASSIMP_BUILD_OPENGEX_EXPORTER", "5.0.0"),
        "with_pbrt_exporter": ("ASSIMP_BUILD_PBRT_EXPORTER", "5.1.0"),
        "with_ply": ("ASSIMP_BUILD_PLY_IMPORTER", "5.0.0"),
        "with_ply_exporter": ("ASSIMP_BUILD_PLY_EXPORTER", "5.0.0"),
        "with_q3bsp": ("ASSIMP_BUILD_Q3BSP_IMPORTER", "5.0.0"),
        "with_q3d": ("ASSIMP_BUILD_Q3D_IMPORTER", "5.0.0"),
        "with_raw": ("ASSIMP_BUILD_RAW_IMPORTER", "5.0.0"),
        "with_sib": ("ASSIMP_BUILD_SIB_IMPORTER", "5.0.0"),
        "with_smd": ("ASSIMP_BUILD_SMD_IMPORTER", "5.0.0"),
        "with_step": ("ASSIMP_BUILD_STEP_IMPORTER", "5.0.0"),
        "with_step_exporter": ("ASSIMP_BUILD_STEP_EXPORTER", "5.0.0"),
        "with_stl": ("ASSIMP_BUILD_STL_IMPORTER", "5.0.0"),
        "with_stl_exporter": ("ASSIMP_BUILD_STL_EXPORTER", "5.0.0"),
        "with_terragen": ("ASSIMP_BUILD_TERRAGEN_IMPORTER", "5.0.0"),
        "with_x": ("ASSIMP_BUILD_X_IMPORTER", "5.0.0"),
        "with_x_exporter": ("ASSIMP_BUILD_X_EXPORTER", "5.0.0"),
        "with_x3d": ("ASSIMP_BUILD_X3D_IMPORTER", "5.0.0"),
        "with_x3d_exporter": ("ASSIMP_BUILD_X3D_EXPORTER", "5.0.0"),
        "with_xgl": ("ASSIMP_BUILD_XGL_IMPORTER", "5.0.0"),
        "with_m3d": ("ASSIMP_BUILD_M3D_IMPORTER", "5.1.0"),
        "with_m3d_exporter": ("ASSIMP_BUILD_M3D_EXPORTER", "5.1.0"),
        "with_iqm": ("ASSIMP_BUILD_IQM_IMPORTER", "5.2.0"),
    }
    options.update(dict.fromkeys(_format_option_map, [True, False]))
    default_options.update(dict.fromkeys(_format_option_map, True))

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        for option, (_, min_version) in self._format_option_map.items():
            if Version(self.version) < Version(min_version):
                delattr(self.options, option)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

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
        if Version(self.version) < "5.1.0":
            return False
        return self.options.with_gltf or self.options.with_gltf_exporter

    @property
    def _depends_on_clipper(self):
        return self.options.with_ifc

    @property
    def _depends_on_stb(self):
        if Version(self.version) < "5.1.0":
            return False
        return self.options.with_m3d or self.options.with_m3d_exporter or \
            self.options.with_pbrt_exporter

    @property
    def _depends_on_zlib(self):
        return self.options.with_assbin or self.options.with_assbin_exporter or \
            self.options.with_assxml_exporter or self.options.with_blend or self.options.with_fbx or \
            self.options.with_q3bsp or self.options.with_x or self.options.with_xgl

    @property
    def _depends_on_openddlparser(self):
        if Version(self.version) < "5.1.0":
            return False
        return self.options.with_opengex

    def requirements(self):
        # TODO: unvendor others libs:
        # - Open3DGC
        self.requires("minizip/1.2.12")
        self.requires("utfcpp/3.2.1")
        if Version(self.version) < "5.1.0":
            self.requires("irrxml/1.2")
        else:
            self.requires("pugixml/1.12.1")
        if self._depends_on_kuba_zip:
            self.requires("kuba-zip/0.2.4")
        if self._depends_on_poly2tri:
            self.requires("poly2tri/cci.20130502")
        if self._depends_on_rapidjson:
            self.requires("rapidjson/cci.20211112")
        if self._depends_on_zlib:
            self.requires("zlib/1.2.12")
        if self._depends_on_draco:
            self.requires("draco/1.5.3")
        if self._depends_on_clipper:
            self.requires("clipper/4.10.0")  # Only 4.x supported
        if self._depends_on_stb:
            self.requires("stb/cci.20210910")
        if self._depends_on_openddlparser:
            self.requires("openddl-parser/0.5.0")

    def validate(self):
        if self._depends_on_clipper and Version(self.dependencies["clipper"].ref.version).major != "4":
            raise ConanInvalidConfiguration("Only 'clipper/4.x' is supported")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if Version(self.version) >= "5.1.0":
            tc.variables["ASSIMP_HUNTER_ENABLED"] = False
            tc.variables["ASSIMP_IGNORE_GIT_HASH"] = True
            tc.variables["ASSIMP_RAPIDJSON_NO_MEMBER_ITERATOR"] = False
        else:
            tc.variables["HUNTER_ENABLED"] = False
            tc.variables["IGNORE_GIT_HASH"] = True
            tc.variables["SYSTEM_IRRXML"] = True
        tc.variables["ASSIMP_ANDROID_JNIIOSYSTEM"] = False
        tc.variables["ASSIMP_BUILD_ALL_IMPORTERS_BY_DEFAULT"] = False
        tc.variables["ASSIMP_BUILD_ALL_EXPORTERS_BY_DEFAULT"] = False
        tc.variables["ASSIMP_BUILD_ASSIMP_TOOLS"] = False
        tc.variables["ASSIMP_BUILD_SAMPLES"] = False
        tc.variables["ASSIMP_BUILD_TESTS"] = False
        tc.variables["ASSIMP_DOUBLE_PRECISION"] = self.options.double_precision
        tc.variables["ASSIMP_INSTALL_PDB"] = False
        tc.variables["ASSIMP_NO_EXPORT"] = False
        tc.variables["ASSIMP_BUILD_MINIZIP"] = False
        for option, (definition, _) in self._format_option_map.items():
            value = self.options.get_safe(option)
            if value is not None:
                tc.variables[definition] = value
        if self.settings.os == "Windows":
            tc.preprocessor_definitions["NOMINMAX"] = 1
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW" # to avoid warnings
        tc.generate()

        cd = CMakeDeps(self)
        cd.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

        # Don't force several compiler and linker flags
        replace_mapping = [
            ("-fPIC", ""),
            ("-g ", ""),
            ("SET(CMAKE_POSITION_INDEPENDENT_CODE ON)", ""),
            ('SET(CMAKE_CXX_FLAGS_DEBUG "/D_DEBUG /MDd /Ob2 /DEBUG:FULL /Zi")', ""),
            ('SET(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /D_DEBUG /Zi /Od")', ""),
            ('SET(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /Zi")', ""),
            ('SET(CMAKE_SHARED_LINKER_FLAGS_RELEASE "${CMAKE_SHARED_LINKER_FLAGS_RELEASE} /DEBUG:FULL /PDBALTPATH:%_PDB% /OPT:REF /OPT:ICF")', ""),
            ("/WX", "")
        ]

        for before, after in replace_mapping:
            replace_in_file(self, os.path.join(
                self.source_folder, "CMakeLists.txt"), before, after, strict=False)
        # Take care to not use these vendored libs
        vendors = ["poly2tri", "rapidjson", "utf8cpp", "zip", "unzip", "stb", "zlib", "clipper"]
        if Version(self.version) < "5.1.0":
            vendors.append("irrXML")
        else:
            vendors.extend(["pugixml", "draco", "openddlparser"])
        for vendor in vendors:
            rmdir(self, os.path.join(self.source_folder, "contrib", vendor))

    def build(self):
        self._patch_sources()
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
            stdcpp_library = tools_legacy.stdcpp_library(self)
            if stdcpp_library:
                self.cpp_info.system_libs.append(stdcpp_library)

        # FIXME: shouldn't be necessary.
        # It's a workaround to support conan v1 generators
        self.cpp_info.requires.append("minizip::minizip")
        self.cpp_info.requires.append("utfcpp::utfcpp")
        if Version(self.version) < "5.1.0":
            self.cpp_info.requires.append("irrxml::irrxml")
        else:
            self.cpp_info.requires.append("pugixml::pugixml")
        if self._depends_on_kuba_zip:
            self.cpp_info.requires.append("kuba-zip::kuba-zip")
        if self._depends_on_poly2tri:
            self.cpp_info.requires.append("poly2tri::poly2tri")
        if self._depends_on_rapidjson:
            self.cpp_info.requires.append("rapidjson::rapidjson")
        if self._depends_on_zlib:
            self.cpp_info.requires.append("zlib::zlib")
        if self._depends_on_draco:
            self.cpp_info.requires.append("draco::draco")
        if self._depends_on_clipper:
            self.cpp_info.requires.append("clipper::clipper")
        if self._depends_on_stb:
            self.cpp_info.requires.append("stb::stb")
        if self._depends_on_openddlparser:
            self.cpp_info.requires.append("openddl-parser::openddl-parser")
