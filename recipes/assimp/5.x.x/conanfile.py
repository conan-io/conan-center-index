import os

from conans import ConanFile, CMake, tools

class AssimpConan(ConanFile):
    name = "assimp"
    description = "Loads 40+ 3D file formats into one unified and clean data structure."
    homepage = "https://github.com/assimp/assimp"
    topics = ("conan", "assimp", "3D", "format")
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD 3-Clause"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "double_precision": [True, False],
        "no_export": [True, False],
        "internal_irrxml": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "double_precision": False,
        "no_export": False,
        "internal_irrxml": False,
        "fPIC": True,
    }
    _format_option_map = {
        "with_3d_importer": "ASSIMP_BUILD_3D_IMPORTER",
        "with_3ds_importer": "ASSIMP_BUILD_3DS_IMPORTER",
        "with_3ds_exporter": "ASSIMP_BUILD_3DS_EXPORTER",
        "with_3mf_importer": "ASSIMP_BUILD_3MF_IMPORTER",
        "with_3mf_exporter": "ASSIMP_BUILD_3MF_EXPORTER",
        "with_ac_importer": "ASSIMP_BUILD_AC_IMPORTER",
        "with_amf_importer": "ASSIMP_BUILD_AMF_IMPORTER",
        "with_ase_importer": "ASSIMP_BUILD_ASE_IMPORTER",
        "with_assbin_importer": "ASSIMP_BUILD_ASSBIN_IMPORTER",
        "with_assbin_exporter": "ASSIMP_BUILD_ASSBIN_EXPORTER",
        "with_assjson_exporter": "ASSIMP_BUILD_ASSJSON_EXPORTER",
        "with_assxml_exporter": "ASSIMP_BUILD_ASSXML_EXPORTER",
        "with_b3d_importer": "ASSIMP_BUILD_B3D_IMPORTER",
        "with_blend_importer": "ASSIMP_BUILD_BLEND_IMPORTER",
        "with_bvh_importer": "ASSIMP_BUILD_BVH_IMPORTER",
        "with_cob_importer": "ASSIMP_BUILD_COB_IMPORTER",
        "with_collada_importer": "ASSIMP_BUILD_COLLADA_IMPORTER",
        "with_collada_exporter": "ASSIMP_BUILD_COLLADA_EXPORTER",
        "with_csm_importer": "ASSIMP_BUILD_CSM_IMPORTER",
        "with_dxf_importer": "ASSIMP_BUILD_DXF_IMPORTER",
        "with_fbx_importer": "ASSIMP_BUILD_FBX_IMPORTER",
        "with_fbx_exporter": "ASSIMP_BUILD_FBX_EXPORTER",
        "with_gltf_importer": "ASSIMP_BUILD_GLTF_IMPORTER",
        "with_gltf_exporter": "ASSIMP_BUILD_GLTF_EXPORTER",
        "with_hmp_importer": "ASSIMP_BUILD_HMP_IMPORTER",
        "with_ifc_importer": "ASSIMP_BUILD_IFC_IMPORTER",
        "with_irr_importer": "ASSIMP_BUILD_IRR_IMPORTER",
        "with_irrmesh_importer": "ASSIMP_BUILD_IRRMESH_IMPORTER",
        "with_lwo_importer": "ASSIMP_BUILD_LWO_IMPORTER",
        "with_lws_importer": "ASSIMP_BUILD_LWS_IMPORTER",
        "with_md2_importer": "ASSIMP_BUILD_MD2_IMPORTER",
        "with_md3_importer": "ASSIMP_BUILD_MD3_IMPORTER",
        "with_md5_importer": "ASSIMP_BUILD_MD5_IMPORTER",
        "with_mdc_importer": "ASSIMP_BUILD_MDC_IMPORTER",
        "with_mdl_importer": "ASSIMP_BUILD_MDL_IMPORTER",
        "with_mmd_importer": "ASSIMP_BUILD_MMD_IMPORTER",
        "with_ms3d_importer": "ASSIMP_BUILD_MS3D_IMPORTER",
        "with_ndo_importer": "ASSIMP_BUILD_NDO_IMPORTER",
        "with_nff_importer": "ASSIMP_BUILD_NFF_IMPORTER",
        "with_obj_importer": "ASSIMP_BUILD_OBJ_IMPORTER",
        "with_obj_exporter": "ASSIMP_BUILD_OBJ_EXPORTER",
        "with_off_importer": "ASSIMP_BUILD_OFF_IMPORTER",
        "with_ogre_importer": "ASSIMP_BUILD_OGRE_IMPORTER",
        "with_opengex_importer": "ASSIMP_BUILD_OPENGEX_IMPORTER",
        "with_opengex_exporter": "ASSIMP_BUILD_OPENGEX_EXPORTER",
        "with_ply_importer": "ASSIMP_BUILD_PLY_IMPORTER",
        "with_ply_exporter": "ASSIMP_BUILD_PLY_EXPORTER",
        "with_q3bsp_importer": "ASSIMP_BUILD_Q3BSP_IMPORTER",
        "with_q3d_importer": "ASSIMP_BUILD_Q3D_IMPORTER",
        "with_raw_importer": "ASSIMP_BUILD_RAW_IMPORTER",
        "with_sib_importer": "ASSIMP_BUILD_SIB_IMPORTER",
        "with_smd_importer": "ASSIMP_BUILD_SMD_IMPORTER",
        "with_step_importer": "ASSIMP_BUILD_STEP_IMPORTER",
        "with_step_exporter": "ASSIMP_BUILD_STEP_EXPORTER",
        "with_stl_importer": "ASSIMP_BUILD_STL_IMPORTER",
        "with_stl_exporter": "ASSIMP_BUILD_STL_EXPORTER",
        "with_terragen_importer": "ASSIMP_BUILD_TERRAGEN_IMPORTER",
        "with_x_importer": "ASSIMP_BUILD_X_IMPORTER",
        "with_x_exporter": "ASSIMP_BUILD_X_EXPORTER",
        "with_x3d_importer": "ASSIMP_BUILD_X3D_IMPORTER",
        "with_x3d_exporter": "ASSIMP_BUILD_X3D_EXPORTER",
        "with_xgl_importer": "ASSIMP_BUILD_XGL_IMPORTER",
    }
    options.update(dict.fromkeys(_format_option_map, [True, False]))
    default_options.update(dict.fromkeys(_format_option_map, True))

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        self.requires.add("zlib/1.2.11")
        if not self.options.internal_irrxml:
            self.requires.add("irrxml/1.2")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["SYSTEM_IRRXML"] = not self.options.internal_irrxml
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        cmake.definitions["ASSIMP_DOUBLE_PRECISION"] = self.options.double_precision
        cmake.definitions["ASSIMP_NO_EXPORT"] = self.options.no_export
        cmake.definitions["HUNTER_ENABLED"] = False
        cmake.definitions["BUILD_FRAMEWORK"] = False
        cmake.definitions["ASSIMP_OPT_BUILD_PACKAGES"] = False
        cmake.definitions["ASSIMP_ANDROID_JNIIOSYSTEM"] = False
        cmake.definitions["ASSIMP_BUILD_ZLIB"] = False
        cmake.definitions["ASSIMP_BUILD_ASSIMP_TOOLS"] = False
        cmake.definitions["ASSIMP_BUILD_SAMPLES"] = False
        cmake.definitions["ASSIMP_BUILD_TESTS"] = False
        cmake.definitions["ASSIMP_COVERALLS"] = False
        cmake.definitions["ASSIMP_WERROR"] = False
        cmake.definitions["ASSIMP_ASAN"] = False
        cmake.definitions["ASSIMP_UBSAN"] = False
        cmake.definitions["BUILD_DOCS"] = False
        cmake.definitions["INJECT_DEBUG_POSTFIX"] = True
        cmake.definitions["ASSIMP_INSTALL_PDB"] = False

        cmake.definitions["ASSIMP_BUILD_ALL_IMPORTERS_BY_DEFAULT"] = False
        cmake.definitions["ASSIMP_BUILD_ALL_EXPORTERS_BY_DEFAULT"] = False
        for option, definition in self._format_option_map.items():
            cmake.definitions[definition] = bool(getattr(self.options, option))

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
