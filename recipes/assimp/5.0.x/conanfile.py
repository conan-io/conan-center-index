import os
from conans import ConanFile, CMake, tools


class Assimp(ConanFile):
    name = "assimp"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/assimp/assimp"
    description = "A library to import and export various 3d-model-formats including scene-post-processing to generate missing render data."
    topics = ("conan", "assimp", "3d")
    license = "BSD-3-Clause"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "double_precision": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "double_precision": False,
        "fPIC": True,
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
    }
    options.update(dict.fromkeys(_format_option_map, [True, False]))
    default_options.update(dict.fromkeys(_format_option_map, True))

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):
        self.requires("zlib/1.2.11")
        self.requires("irrxml/1.2")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("assimp-%s" % self.version, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["SYSTEM_IRRXML"] = True
        self._cmake.definitions["ASSIMP_DOUBLE_PRECISION"] = self.options.double_precision
        self._cmake.definitions["ASSIMP_NO_EXPORT"] = False
        self._cmake.definitions["ASSIMP_BUILD_ASSIMP_TOOLS"] = False
        self._cmake.definitions["ASSIMP_BUILD_TESTS"] = False
        self._cmake.definitions["ASSIMP_BUILD_SAMPLES"] = False
        self._cmake.definitions["ASSIMP_INSTALL_PDB"] = False

        self._cmake.definitions["ASSIMP_ANDROID_JNIIOSYSTEM"] = False

        self._cmake.definitions["ASSIMP_BUILD_ALL_IMPORTERS_BY_DEFAULT"] = False
        self._cmake.definitions["ASSIMP_BUILD_ALL_EXPORTERS_BY_DEFAULT"] = False
        for option, definition in self._format_option_map.items():
            self._cmake.definitions[definition] = bool(getattr(self.options, option))

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for before, after in [("-fPIC", ""), ("-g ", ""), ('SET(CMAKE_CXX_FLAGS_DEBUG "/D_DEBUG /MDd /Ob2 /DEBUG:FULL /Zi")', "")]:
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), before, after)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["rt", "m", "pthread"]
        if not self.options.shared and self._stdcpp_library:
            self.cpp_info.system_libs.append(self._stdcpp_library)

    @property
    def _stdcpp_library(self):
        libcxx = self.settings.get_safe("compiler.libcxx")
        if libcxx in ("libstdc++", "libstdc++11"):
            return "stdc++"
        elif libcxx in ("libc++",):
            return "c++"
        else:
            return False
