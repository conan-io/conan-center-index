from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"


class Assimp(ConanFile):
    name = "assimp"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/assimp/assimp"
    description = "A library to import and export various 3d-model-formats including scene-post-processing to generate missing render data."
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
        "with_xgl": ("ASSIMP_BUILD_XGL_IMPORTER", "5.0.0")
    }
    options.update(dict.fromkeys(_format_option_map, [True, False]))
    default_options.update(dict.fromkeys(_format_option_map, True))

    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "cmake_find_package"
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

        for option, (_, min_version) in self._format_option_map.items():
            if tools.Version(self.version) < tools.Version(min_version):
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
        if tools.Version(self.version) < "5.1.0":
            return False
        return self.options.with_gltf or self.options.with_gltf_exporter

    @property
    def _depends_on_zlib(self):
        return self.options.with_assbin or self.options.with_assbin_exporter or \
            self.options.with_assxml_exporter or self.options.with_blend or self.options.with_fbx or \
            self.options.with_q3bsp or self.options.with_x or self.options.with_xgl

    def requirements(self):
        # TODO: unvendor others libs:
        # - clipper (required by IFC importer): can't be unvendored because CCI
        #   has 6.4.2, not API compatible with 4.8.8 vendored in assimp
        # - Open3DGC
        # - openddlparser
        if tools.Version(self.version) < "5.1.0":
            self.requires("irrxml/1.2")
        else:
            self.requires("pugixml/1.11")

        self.requires("minizip/1.2.11")
        self.requires("utfcpp/3.1.2")
        if self._depends_on_kuba_zip:
            self.requires("kuba-zip/0.1.31")
        if self._depends_on_poly2tri:
            self.requires("poly2tri/cci.20130502")
        if self._depends_on_rapidjson:
            self.requires("rapidjson/cci.20200410")
        if self._depends_on_zlib:
            self.requires("zlib/1.2.11")
        if self._depends_on_draco:
            self.requires("draco/1.4.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

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
            tools.replace_in_file(os.path.join(
                self._source_subfolder, "CMakeLists.txt"), before, after, strict=False)
        # Take care to not use these vendored libs
        vendors = ["poly2tri", "rapidjson", "unzip", "utf8cpp", "zip"]
        if tools.Version(self.version) < "5.1.0":
            vendors.append("irrXML")
        else:
            vendors.extend(["pugixml", "draco"])
        for vendor in vendors:
            tools.rmdir(os.path.join(self._source_subfolder, "contrib", vendor))

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        if tools.Version(self.version) >= "5.1.0":
            self._cmake.definitions["ASSIMP_HUNTER_ENABLED"] = False
            self._cmake.definitions["ASSIMP_IGNORE_GIT_HASH"] = True
            self._cmake.definitions["ASSIMP_RAPIDJSON_NO_MEMBER_ITERATOR"] = False
        else:
            self._cmake.definitions["HUNTER_ENABLED"] = False
            self._cmake.definitions["IGNORE_GIT_HASH"] = True
            self._cmake.definitions["SYSTEM_IRRXML"] = True

        self._cmake.definitions["ASSIMP_ANDROID_JNIIOSYSTEM"] = False
        self._cmake.definitions["ASSIMP_BUILD_ALL_IMPORTERS_BY_DEFAULT"] = False
        self._cmake.definitions["ASSIMP_BUILD_ALL_EXPORTERS_BY_DEFAULT"] = False
        self._cmake.definitions["ASSIMP_BUILD_ASSIMP_TOOLS"] = False
        self._cmake.definitions["ASSIMP_BUILD_SAMPLES"] = False
        self._cmake.definitions["ASSIMP_BUILD_TESTS"] = False
        self._cmake.definitions["ASSIMP_DOUBLE_PRECISION"] = self.options.double_precision
        self._cmake.definitions["ASSIMP_INSTALL_PDB"] = False
        self._cmake.definitions["ASSIMP_NO_EXPORT"] = False

        for option, (definition, _) in self._format_option_map.items():
            value = self.options.get_safe(option)
            if value is not None:
                self._cmake.definitions[definition] = value

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses",
                  src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "assimp"
        self.cpp_info.names["cmake_find_package_multi"] = "assimp"
        self.cpp_info.names["pkg_config"] = "assimp"
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            self.cpp_info.defines.append("ASSIMP_DLL")
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["rt", "m", "pthread"]
        if not self.options.shared:
            stdcpp_library = tools.stdcpp_library(self)
            if stdcpp_library:
                self.cpp_info.system_libs.append(stdcpp_library)
