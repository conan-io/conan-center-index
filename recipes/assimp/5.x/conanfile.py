from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import stdcpp_library, check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, collect_libs, copy, export_conandata_patches, get, replace_in_file, rmdir, save
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

    @property
    def _min_cppstd(self):
        if Version(self.version) < "5.2.0":
            return 11
        return 17

    @property
    def _compilers_minimum_version(self):
        if Version(self.version) < "5.2.0":
            return {}
        return {
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10",
            "msvc": "191",
            "Visual Studio": "15",
        }

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "conan_deps.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        for option, (_, min_version) in self._format_option_map.items():
            if Version(self.version) < Version(min_version):
                delattr(self.options, option)

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
        self.requires("minizip/1.2.13")
        self.requires("pugixml/1.14")
        self.requires("utfcpp/4.0.1")
        self.requires("zlib/[>=1.2.11 <2]")
        if self._depends_on_kuba_zip:
            self.requires("kuba-zip/0.3.0")
        if self._depends_on_poly2tri:
            self.requires("poly2tri/cci.20130502")
        if self._depends_on_rapidjson:
            self.requires("rapidjson/cci.20230929")
        if self._depends_on_draco:
            self.requires("draco/1.5.6")
        if self._depends_on_clipper:
            if Version(self.version) >= "5.3.0":
                self.requires("clipper/6.4.2")
            else:
                self.requires("clipper/4.10.0")
        if self._depends_on_stb:
            self.requires("stb/cci.20230920")
        if self._depends_on_openddlparser:
            self.requires("openddl-parser/0.5.1")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.")

        if Version(self.version) < "5.3.0" and self._depends_on_clipper and Version(self.dependencies["clipper"].ref.version).major != "4":
            raise ConanInvalidConfiguration("Only 'clipper/4.x' is supported")

    def build_requirements(self):
        if Version(self.version) >= "5.4.0":
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

        for option, (definition, _) in self._format_option_map.items():
            value = self.options.get_safe(option)
            if value is not None:
                tc.variables[definition] = value
        if self.settings.os == "Windows":
            tc.preprocessor_definitions["NOMINMAX"] = 1
        if Version(self.version) < "5.4.0":
            tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"

        tc.cache_variables["CMAKE_PROJECT_Assimp_INCLUDE"] = "conan_deps.cmake"
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

    def _patch_sources(self):
        apply_conandata_patches(self)

        # Don't force several compiler and linker flags
        for pattern in [
            "-fPIC",
            "-g ",
            "SET(CMAKE_POSITION_INDEPENDENT_CODE ON)",
            'SET(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /D_DEBUG /Zi /Od")',
            'SET(CMAKE_SHARED_LINKER_FLAGS_RELEASE "${CMAKE_SHARED_LINKER_FLAGS_RELEASE} /DEBUG:FULL /PDBALTPATH:%_PDB% /OPT:REF /OPT:ICF")',
        ]:
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), pattern, "")

        for pattern in ["-Werror", "/WX"]:
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), pattern, "")
            replace_in_file(self, os.path.join(self.source_folder, "code", "CMakeLists.txt"), pattern, "")

        # Make sure vendored libs are not used by accident by removing their subdirs
        allow_vendored = ["Open3DGC"]
        for contrib_dir in self.source_path.joinpath("contrib").iterdir():
            if contrib_dir.is_dir() and contrib_dir.name not in allow_vendored:
                rmdir(self, contrib_dir)

        # Do not include add vendored library sources to the build
        # https://github.com/assimp/assimp/blob/v5.3.1/code/CMakeLists.txt#L1151-L1159
        code_cmakelists = self.source_path.joinpath("code", "CMakeLists.txt")
        content = code_cmakelists.read_text(encoding="utf-8")
        for vendored_lib in [
            "unzip_compile",
            "Poly2Tri",
            "Clipper",
            "openddl_parser",
            # "open3dgc",
            "ziplib",
            "Pugixml",
            "stb",
        ]:
            content = content.replace("${%s_SRCS}" % vendored_lib, "")
        code_cmakelists.write_text(content, encoding="utf-8")

        # Make vendored headers redirect to external ones.
        for contrib_header, include in [
            (os.path.join("clipper", "clipper.hpp"), "polyclipping/clipper.hpp"),
            (os.path.join("poly2tri", "poly2tri", "poly2tri.h"), "poly2tri/poly2tri.h"),
            (os.path.join("stb", "stb_image.h"), "stb_image.h"),
            (os.path.join("utf8cpp", "source", "utf8.h"), "utf8.h"),
            (os.path.join("zip", "src", "zip.h"), "zip/zip.h"),
        ]:
            save(self, os.path.join(self.source_folder, "contrib", contrib_header),
                 f"#include <{include}>\n")
        if Version(self.version) >= "5.4.0":
            rmdir(self, self.source_path.joinpath("contrib", "utf8cpp"))

        # minizip is provided via conan_deps.cmake, no need to use pkgconfig
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "use_pkgconfig(UNZIP minizip)", "set(UNZIP_FOUND TRUE)")

        # ZLIB is unvendored, no need to install it
        # https://github.com/assimp/assimp/blob/v5.3.1/CMakeLists.txt#L483-L487
        # https://github.com/assimp/assimp/blob/v5.1.6/CMakeLists.txt#L463-L466
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "INSTALL( TARGETS zlib", "set(_ #")

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
            libcxx = stdcpp_library(self)
            if libcxx:
                self.cpp_info.system_libs.append(libcxx)
