from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, load, get, rm, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"

class OpenUSDConan(ConanFile):
    name = "openusd"
    description = "Universal Scene Description"
    license = "DocumentRef-LICENSE.txt:LicenseRef-Modified-Apache-2.0-License"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://openusd.org/"
    topics = ("3d", "scene", "usd")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_usd_tools": [True, False],
        "build_imaging": [True, False],
        "build_usd_imaging": [True, False],
        "build_usdview": [True, False],
        "build_openimageio_plugin": [True, False],
        "build_opencolorio_plugin": [True, False],
        "build_embree_plugin": [True, False],
        "enable_materialx_support": [True, False],
        "enable_vulkan_support": [True, False],
        "enable_gl_support": [True, False],
        "build_gpu_support": [True, False],
        "enable_ptex_support": [True, False],
        "enable_openvdb_support": [True, False],
        "build_alembic_plugin": [True, False],
        "enable_hdf5_support": [True, False],
        "build_draco_plugin": [True, False],
        "enable_osl_support": [True, False],
        "build_animx_tests": [True, False],
        "enable_python_support": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": False,
        "build_usd_tools": True,
        "build_imaging": True,
        "build_usd_imaging": True,
        "build_usdview": True,
        "build_openimageio_plugin": False,
        "build_opencolorio_plugin": False,
        "build_embree_plugin": False,
        "enable_materialx_support": True,
        "enable_vulkan_support": False,
        "enable_gl_support": False,
        "enable_ptex_support": True,
        "enable_openvdb_support": False,
        "build_alembic_plugin": False,
        "enable_hdf5_support": True,
        "build_draco_plugin": False,
        "enable_osl_support": False,
        "build_animx_tests": False,
        "enable_python_support": False
    }

    short_paths = True

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        # as defined in https://github.com/PixarAnimationStudios/OpenUSD/blob/release/VERSIONS.md
        return {
            "apple-clang": "13",
            "clang": "7",
            "gcc": "9",
            "msvc": "191",
            "Visual Studio": "15",
        }

    @property
    def _enable_ptex(self):
        return self.options.enable_ptex_support and self.options.enable_gl_support and self.options.build_gpu_support

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.options.build_usd_imaging and not self.options.build_imaging:
            self.options.build_usd_imaging = False
        self.options.build_gpu_support = self.options.enable_gl_support or is_apple_os(self) or self.options.enable_vulkan_support
        if self.options.build_usdview:
            if self.options.build_imaging:
                self.options.build_usd_imaging = False
        if self.options.build_usdview:
            if not self.options.build_usd_imaging:
                self.options.build_usdview = False
            elif not self.options.enable_python_support:
                self.options.build_usdview = False
            elif not self.options.build_gpu_support:
                self.options.build_usdview = False
        if self.options.build_embree_plugin:
            if not self.options.build_imaging:
                self.options.build_embree_plugin = False
            elif not self.options.build_gpu_support:
                self.options.build_embree_plugin = False

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # Set same options as in https://github.com/PixarAnimationStudios/OpenUSD/blob/release/build_scripts/build_usd.py#L1397
        # self.options["opensubdiv/*"].with_tbb = True
        if self.options.enable_gl_support:
            self.options["opensubdiv/*"].with_opengl = self.options.enable_gl_support
            # FIXME: provokes a missing binary error on conan center
            self.options["opensubdiv/*"].with_metal = is_apple_os(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.enable_python_support:
            self.requires("boost/1.86.0")
        # openusd doesn't support yet recent release of onetbb, see https://github.com/PixarAnimationStudios/OpenUSD/issues/1471
        self.requires("onetbb/2021.10.0", transitive_headers=True)

        if self.options.build_imaging:
            if self.options.build_openimageio_plugin and self.options.build_gpu_support:
                self.requires("openimageio/2.5.14.0")
            if not self.options.build_openimageio_plugin and self.options.build_opencolorio_plugin and self.options.build_gpu_support and self.options.enable_gl_support:
                self.requires("opencolorio/2.3.2")
            if self.options.enable_gl_support:
                self.requires("opensubdiv/3.6.0")
            if self.options.enable_vulkan_support:
                self.requires("vulkan-headers/1.3.290.0")
            if self.options.enable_gl_support:
                self.requires("opengl/system")
            if self._enable_ptex:
                self.requires("ptex/2.4.2")
            if self.options.enable_openvdb_support and self.options.build_gpu_support:
                self.requires("openvdb/11.0.0")
            if self.options.build_embree_plugin and self.options.build_gpu_support:
                self.requires("embree3/3.13.5")
        if self.options.build_alembic_plugin:
            self.requires("alembic/1.8.6")
            if self.options.enable_hdf5_support:
                self.requires("hdf5/1.14.4.3")
        if self.options.build_draco_plugin:
            self.requires("draco/1.5.6")
        if self.options.enable_materialx_support:
            self.requires("materialx/1.39.1", transitive_headers=True)
        # if self.options.enable_osl_support:
           # TODO: add osl to conan center (https://github.com/AcademySoftwareFoundation/OpenShadingLanguage)
            # self.requires("openshadinglanguage/1.13.8.0")
        # if self.options.build_animx_tests:
           # TODO: add animx to conan center (https://github.com/Autodesk/animx/)
            # self.requires("animx/x.y.z")
        if self.options.build_imaging and (self.options.build_openimageio_plugin and self.options.build_gpu_support or self.options.enable_openvdb_support):
            # or self.options.build_alembic_plugin or self.options.enable_osl_support:
            self.requires("imath/3.1.9")

    def validate(self):
        if not self.options.shared:
            raise ConanInvalidConfiguration("static not yet supported")
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )
        # if is_apple_os(self) and not self.dependencies["opensubdiv"].options["with_metal"]:
        if self.options.enable_gl_support and is_apple_os(self):
            raise ConanInvalidConfiguration(f'{self.ref} needs -o="opensubdiv/*:with_metal=True"')
        if self.options.build_animx_tests:
            raise ConanInvalidConfiguration("animx recipe doesn't yet exists in conan center index")
        if self.options.enable_osl_support:
            raise ConanInvalidConfiguration("openshadinglanguage recipe doesn't yet exists in conan center index")
        if self.options.enable_python_support:
            raise ConanInvalidConfiguration("python doesn't yet supported")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # Use variables in documented in https://github.com/PixarAnimationStudios/OpenUSD/blob/release/BUILDING.md
        tc.variables["PXR_BUILD_TESTS"] = False
        tc.variables["PXR_BUILD_EXAMPLES"] = False
        tc.variables["PXR_BUILD_TUTORIALS"] = False
        tc.variables["PXR_BUILD_HTML_DOCUMENTATION"] = False
        tc.variables["PXR_ENABLE_PYTHON_SUPPORT"] = self.options.enable_python_support
        tc.variables["PXR_BUILD_USD_TOOLS"] = self.options.build_usd_tools

        if self.options.enable_gl_support:
            # tc.variables["OPENSUBDIV_ROOT_DIR"] = self.dependencies['opensubdiv'].cpp_info.
            tc.variables["OPENSUBDIV_LIBRARIES"] = self.dependencies['opensubdiv'].cpp_info.libdirs[0].replace("\\", "/")
            # Provokes cmake parsing error
            # See https://c3i.jfrog.io/c3i/misc/logs/pr/24506/75-windows-visual_studio/openusd/24.08//a47d3be1b4a4ee7c129fc15ba3f28e471624adfb-build.txt
            # See https://github.com/conan-io/conan/issues/10539 
            tc.variables["OPENSUBDIV_INCLUDE_DIR"] = self.dependencies['opensubdiv'].cpp_info.includedirs[0].replace("\\", "/")
            # tc.variables["OPENSUBDIV_OSDCPU_LIBRARY"] = "OpenSubdiv::osdcpu"

        tc.variables["TBB_tbb_LIBRARY"] = "TBB::tbb"

        tc.variables["PXR_ENABLE_MATERIALX_SUPPORT"] = self.options.enable_materialx_support

        tc.variables["PXR_BUILD_IMAGING"] = self.options.build_imaging
        if self.options.build_imaging:
            tc.variables["PXR_BUILD_IMAGING"] = True
            tc.variables["PXR_ENABLE_GL_SUPPORT"] = self.options.enable_gl_support
            tc.variables["PXR_ENABLE_VULKAN_SUPPORT"] = self.options.enable_vulkan_support

            if self._enable_ptex:
                tc.variables["PXR_ENABLE_PTEX_SUPPORT"] = True
                tc.variables["PTEX_LIBRARY"] = self.dependencies['ptex'].cpp_info.libdirs[0]
                tc.variables["PTEX_INCLUDE_DIR"] = self.dependencies['ptex'].cpp_info.includedirs[0].replace("\\", "/")

            tc.variables["PXR_ENABLE_OPENVDB_SUPPORT"] = self.options.enable_openvdb_support and self.options.enable_gl_support
            tc.variables["OPENVDB_LIBRARY"] = "OpenVDB::openvdb"

            tc.variables["PXR_BUILD_OPENIMAGEIO_PLUGIN"] = self.options.build_openimageio_plugin and self.options.build_gpu_support
            tc.variables["PXR_BUILD_COLORIO_PLUGIN"] = self.options.build_opencolorio_plugin and self.options.enable_gl_support and self.options.build_gpu_support

            if self.options.build_embree_plugin and self.options.build_gpu_support:
                tc.variables["PXR_BUILD_EMBREE_PLUGIN"] = self.options.build_embree_plugin
                tc.variables["EMBREE_LIBRARY"] = self.dependencies['embree3'].cpp_info.libdirs[0]
                tc.variables["EMBREE_INCLUDE_DIR"] = self.dependencies['embree3'].cpp_info.includedirs[0].replace("\\", "/")

            if self.options.build_usd_imaging:
                tc.variables["PXR_BUILD_USD_IMAGING"] = True
                if self.options.build_usdview:
                    tc.variables["PXR_BUILD_USDVIEW"] = True

        # Renderman is a proprietary software, see build_renderman_plugin 
        tc.variables["PXR_BUILD_PRMAN_PLUGIN"] = False

        if self.options.build_alembic_plugin:
            tc.variables["PXR_BUILD_ALEMBIC_PLUGIN"] = True
            tc.variables["ALEMBIC_FOUND"] = True
            tc.variables["ALEMBIC_LIBRARIES"] = "Alembic::Alembic"
            tc.variables["ALEMBIC_LIBRARY_DIR"] = self.dependencies['alembic'].cpp_info.libdirs[0].replace("\\", "/")
            tc.variables["ALEMBIC_INCLUDE_DIR"] = self.dependencies['alembic'].cpp_info.includedirs[0].replace("\\", "/")

        tc.variables["PXR_ENABLE_HDF5_SUPPORT"] = self.options.build_alembic_plugin and self.options.enable_hdf5_support

        if self.options.build_draco_plugin:
            tc.variables["PXR_BUILD_DRACO_PLUGIN"] = True
            tc.variables["DRACO_LIBRARY"] = "draco::draco"
            tc.variables["DRACO_INCLUDES"] = self.dependencies['draco'].cpp_info.includedirs[0].replace("\\", "/")

        tc.variables["PXR_ENABLE_OSL_SUPPORT"] = self.options.enable_osl_support
        tc.variables["PXR_BUILD_ANIMX_TESTS"] = self.options.build_animx_tests

        tc.variables["MaterialX_DIR"] = self.options.build_animx_tests

        tc.generate()

        self.output.info("Content of conan_toolchain.cmake")
        self.output.info(str(self.build_folder))
        conan_toolchain = load(self, os.path.join(self.build_folder, "generators", "conan_toolchain.cmake"))
        self.output.info(str(conan_toolchain))
        self.output.info("End of conan_toolchain.cmake")

        tc = CMakeDeps(self)
        if self.options.enable_materialx_support:
            tc.set_property("materialx::MaterialXCore", "cmake_target_name", "MaterialXCore")
            tc.set_property("materialx::MaterialXFormat", "cmake_target_name", "MaterialXFormat")
            tc.set_property("materialx::MaterialXGenShader", "cmake_target_name", "MaterialXGenShader")
            tc.set_property("materialx::MaterialXRender", "cmake_target_name", "MaterialXRender")
            tc.set_property("materialx::MaterialXGenGlsl", "cmake_target_name", "MaterialXGenGlsl")
        tc.generate()

        tc = VirtualBuildEnv(self)
        tc.generate()

    def _patch_sources(self):
        rmdir(self, os.path.join(self.source_folder, "cmake", "modules"))
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rm(self, "pxrConfig.cmake", self.package_folder)
        rmdir(self, os.path.join(self.package_folder, "cmake"))

    def package_info(self):
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
            self.cpp_info.system_libs.append("dl")

        # base
        self.cpp_info.components["usd_arch"].libs = ["usd_arch"]

        self.cpp_info.components["usd_gf"].libs = ["usd_gf"]
        self.cpp_info.components["usd_gf"].requires = ["usd_arch", "usd_tf"]

        self.cpp_info.components["usd_js"].libs = ["usd_js"]
        self.cpp_info.components["usd_js"].requires = ["usd_tf"]

        self.cpp_info.components["usd_plug"].libs = ["usd_plug"]
        self.cpp_info.components["usd_plug"].requires = ["usd_arch", "usd_tf", "usd_js", "usd_trace", "usd_work", "onetbb::libtbb"]

        self.cpp_info.components["usd_tf"].libs = ["usd_tf"]
        self.cpp_info.components["usd_tf"].requires = ["usd_arch", "onetbb::libtbb"]

        self.cpp_info.components["usd_trace"].libs = ["usd_trace"]
        self.cpp_info.components["usd_trace"].requires = ["usd_arch", "usd_tf", "usd_js", "onetbb::libtbb"]

        self.cpp_info.components["usd_ts"].libs = ["usd_ts"]
        self.cpp_info.components["usd_ts"].requires = ["usd_arch", "usd_gf", "usd_plug", "usd_tf", "usd_trace", "usd_vt"]

        self.cpp_info.components["usd_vt"].libs = ["usd_vt"]
        self.cpp_info.components["usd_vt"].requires = ["usd_arch", "usd_tf", "usd_gf", "usd_trace", "onetbb::libtbb"]

        self.cpp_info.components["usd_work"].libs = ["usd_work"]
        self.cpp_info.components["usd_work"].requires = ["usd_tf", "usd_trace", "onetbb::libtbb"]

        # imaging
        if self.options.build_imaging:
            self.cpp_info.components["usd_cameraUtil"].libs = ["usd_cameraUtil"]
            self.cpp_info.components["usd_cameraUtil"].requires = ["usd_tf", "usd_gf"]

            if self.options.enable_gl_support:
                self.cpp_info.components["usd_garch"].libs = ["usd_garch"]
                self.cpp_info.components["usd_garch"].requires = ["usd_arch", "usd_tf", "opengl::opengl"]

            self.cpp_info.components["usd_geomUtil"].libs = ["usd_geomUtil"]
            self.cpp_info.components["usd_geomUtil"].requires = ["usd_arch", "usd_gf", "usd_tf", "usd_vt", "usd_pxOsd"]

            if self.options.enable_gl_support:
                self.cpp_info.components["usd_glf"].libs = ["usd_glf"]
                self.cpp_info.components["usd_glf"].requires = ["usd_ar", "usd_arch", "usd_garch", "usd_gf", "usd_hf", "usd_hio", "usd_plug", "usd_tf", "usd_trace", "usd_sdf", "opengl::opengl"]

            self.cpp_info.components["usd_hd"].libs = ["usd_hd"]
            self.cpp_info.components["usd_hd"].requires = ["usd_plug", "usd_tf", "usd_trace", "usd_vt", "usd_work", "usd_sdf", "usd_cameraUtil", "usd_hf", "usd_pxOsd", "usd_sdr", "onetbb::libtbb"]

            self.cpp_info.components["usd_hdar"].libs = ["usd_hdar"]
            self.cpp_info.components["usd_hdar"].requires = ["usd_hd", "usd_ar"]

            self.cpp_info.components["usd_hdGp"].libs = ["usd_hdGp"]
            self.cpp_info.components["usd_hdGp"].requires = ["usd_hd", "usd_hf", "onetbb::libtbb"]

            self.cpp_info.components["usd_hdsi"].libs = ["usd_hdsi"]
            self.cpp_info.components["usd_hdsi"].requires = ["usd_plug", "usd_tf", "usd_trace", "usd_vt", "usd_work", "usd_sdf", "usd_cameraUtil", "usd_geomUtil", "usd_hf", "usd_hd", "usd_pxOsd"]

            if self.options.enable_materialx_support:
                self.cpp_info.components["usd_hdMtlx"].libs = ["usd_hdMtlx"]
                self.cpp_info.components["usd_hdMtlx"].requires = ["usd_gf", "usd_hd", "usd_sdf", "usd_sdr", "usd_tf", "usd_trace", "usd_usdMtlx", "usd_vt", "usd_vt", "materialx::MaterialXCore", "materialx::MaterialXFormat"]

            self.cpp_info.components["usd_pxOsd"].libs = ["usd_pxOsd"]
            self.cpp_info.components["usd_pxOsd"].requires = ["usd_tf", "usd_gf", "usd_vt", "opensubdiv::opensubdiv"]

            if self.options.enable_gl_support and self.options.build_gpu_support:
                self.cpp_info.components["usd_hdSt"].libs = ["usd_hdSt"]
                self.cpp_info.components["usd_hdSt"].requires = ["usd_hio", "usd_garch", "usd_glf", "usd_hd", "usd_hdsi", "usd_hgiGL", "usd_hgiInterop", "usd_sdr", "usd_tf", "usd_trace", "opensubdiv::opensubdiv"]
                if self.options.enable_materialx_support:
                    self.cpp_info.components["usd_hdSt"].requires.extend(["materialx::MaterialXGenShader", "materialx::MaterialXRender", "materialx::MaterialXCore", "materialx::MaterialXFormat", "materialx::MaterialXGenGlsl", "usd_hdMtlx"])
                if self._enable_ptex:
                    self.cpp_info.components["usd_hdSt"].requires.append("ptex::ptex")

            if self.options.enable_gl_support and self.options.build_gpu_support:
                self.cpp_info.components["usd_hdx"].libs = ["usd_hdx"]
                self.cpp_info.components["usd_hdx"].requires = ["usd_plug", "usd_tf", "usd_vt", "usd_gf", "usd_work", "usd_garch", "usd_glf", "usd_pxOsd", "usd_hd", "usd_hdSt", "usd_hgi", "usd_hgiInterop", "usd_cameraUtil", "usd_sdf"]
                if self.options.build_opencolorio_plugin:
                    self.cpp_info.components["usd_hdx"].requires.append("opencolorio::opencolorio")

            self.cpp_info.components["usd_hf"].libs = ["usd_hf"]
            self.cpp_info.components["usd_hf"].requires = ["usd_plug", "usd_tf", "usd_trace"]

            self.cpp_info.components["usd_hgi"].libs = ["usd_hgi"]
            self.cpp_info.components["usd_hgi"].requires = ["usd_gf", "usd_plug", "usd_tf", "usd_hio"]

            if self.options.enable_gl_support:
                self.cpp_info.components["usd_hgiGL"].libs = ["usd_hgiGL"]
                self.cpp_info.components["usd_hgiGL"].requires = ["usd_arch", "usd_garch", "usd_hgi", "usd_tf", "usd_trace"]

            if self.options.enable_gl_support and self.options.build_gpu_support:
                self.cpp_info.components["usd_hgiInterop"].libs = ["usd_hgiInterop"]
                self.cpp_info.components["usd_hgiInterop"].requires = ["usd_garch", "usd_gf", "usd_tf", "usd_hgi", "usd_vt", "usd_trace"]
                if self.options.enable_vulkan_support:
                    self.cpp_info.components["usd_hgiInterop"].requires.append("usd_hgiVulkan")
                if is_apple_os(self):
                    self.cpp_info.components["usd_hgiInterop"].requires.append("usd_hgiMetal")

            if self.options.build_gpu_support and is_apple_os(self):
                self.cpp_info.components["usd_hgiMetal"].libs = ["usd_hgiMetal"]
                self.cpp_info.components["usd_hgiMetal"].requires = ["usd_arch", "usd_hgi", "usd_tf", "usd_trace"]

            if self.options.build_gpu_support and self.options.enable_vulkan_support:
                self.cpp_info.components["usd_hgiVulkan"].libs = ["usd_hgiVulkan"]
                self.cpp_info.components["usd_hgiVulkan"].requires = ["usd_arch", "usd_hgi", "usd_tf", "usd_trace"]

            self.cpp_info.components["usd_hio"].libs = ["usd_hio"]
            self.cpp_info.components["usd_hio"].requires = ["usd_arch", "usd_js", "usd_plug", "usd_tf", "usd_vt", "usd_trace", "usd_ar", "usd_hf"]

            if self.options.enable_openvdb_support and self.options.build_gpu_support:
                self.cpp_info.components["usd_hioOpenVDB"].libs = ["usd_hioOpenVDB"]
                self.cpp_info.components["usd_hioOpenVDB"].requires = ["usd_ar", "usd_gf", "usd_hio", "usd_tf", "usd_usd", "openvdb::openvdb"]
                if self.options.build_imaging and (self.options.build_openimageio_plugin and self.options.build_gpu_support or self.options.enable_openvdb_support) or self.options.build_alembic_plugin or self.options.enable_osl_support:
                    self.cpp_info.components["usd_hioOpenVDB"].requires.append("imath::imath")

            # plugins

            self.cpp_info.components["hioAvif"].libdirs = ["plugin/usd/"]
            self.cpp_info.components["hioAvif"].libs = ["hioAvif"]
            self.cpp_info.components["hioAvif"].requires = ["usd_ar", "usd_arch", "usd_gf", "usd_hio", "usd_tf"]

            if self.options.build_openimageio_plugin and self.options.build_gpu_support:
                self.cpp_info.components["usd_hioOiio"].libs = ["usd_hioOiio"]
                self.cpp_info.components["usd_hioOiio"].requires = ["usd_ar", "usd_arch", "usd_gf", "usd_hio", "usd_tf", "openimageio::openimageio"]
                if self.options.build_imaging and (self.options.build_openimageio_plugin and self.options.build_gpu_support or self.options.enable_openvdb_support) or self.options.build_alembic_plugin or self.options.enable_osl_support:
                    self.cpp_info.components["usd_hioOiio"].requires.append("imath::imath")

            if self.options.build_embree_plugin and self.options.build_gpu_support:
                self.cpp_info.components["usd_hdEmbree"].libs = ["usd_hdEmbree"]
                self.cpp_info.components["usd_hdEmbree"].requires = ["usd_plug", "usd_tf", "usd_vt", "usd_gf", "usd_work", "usd_hf", "usd_hd", "usd_hdx", "onetbb::libtbb", "embree3::embree3"]

            if self.options.build_usd_imaging:
                self.cpp_info.components["usd_usdImaging"].libs = ["usd_usdImaging"]
                self.cpp_info.components["usd_usdImaging"].requires = ["usd_gf", "usd_tf", "usd_plug", "usd_trace", "usd_vt", "usd_work", "usd_geomUtil", "usd_hd", "usd_hdar", "usd_hio", "usd_pxOsd", "usd_sdf", "usd_usd", "usd_usdGeom", "usd_usdLux", "usd_usdRender", "usd_usdShade", "usd_usdVol", "usd_ar", "onetbb::libtbb"]

                if self.options.build_gpu_support:
                    self.cpp_info.components["usd_usdAppUtils"].libs = ["usd_usdAppUtils"]
                    self.cpp_info.components["usd_usdAppUtils"].requires = ["usd_garch", "usd_gf", "usd_hio", "usd_sdf", "usd_tf", "usd_usd", "usd_usdGeom", "usd_usdImagingGL"]

                    self.cpp_info.components["usd_usdImagingGL"].libs = ["usd_usdImagingGL"]
                    self.cpp_info.components["usd_usdImagingGL"].requires = ["usd_gf", "usd_tf", "usd_plug", "usd_trace", "usd_vt", "usd_work", "usd_hio", "usd_garch", "usd_glf", "usd_hd", "usd_hdsi", "usd_hdx", "usd_pxOsd", "usd_sdf", "usd_sdr", "usd_usd", "usd_usdGeom", "usd_usdHydra", "usd_usdShade", "usd_usdImaging", "usd_ar", "onetbb::libtbb"]

                self.cpp_info.components["usd_usdProcImaging"].libs = ["usd_usdProcImaging"]
                self.cpp_info.components["usd_usdProcImaging"].requires = ["usd_usdImaging", "usd_usdProc"]

                self.cpp_info.components["usd_usdRiPxrImaging"].libs = ["usd_usdRiPxrImaging"]
                self.cpp_info.components["usd_usdRiPxrImaging"].requires = ["usd_gf", "usd_tf", "usd_plug", "usd_trace", "usd_vt", "usd_work", "usd_hd", "usd_pxOsd", "usd_sdf", "usd_usd", "usd_usdGeom", "usd_usdLux", "usd_usdShade", "usd_usdImaging", "usd_usdVol", "usd_ar", "onetbb::libtbb"]

                self.cpp_info.components["usd_usdSkelImaging"].libs = ["usd_usdSkelImaging"]
                self.cpp_info.components["usd_usdSkelImaging"].requires = ["usd_hio", "usd_hd", "usd_usdImaging", "usd_usdSkel"]

                if self.options.build_usdview:
                    self.cpp_info.components["usd_usdviewq"].libs = ["usd_usdviewq"]
                    self.cpp_info.components["usd_usdviewq"].requires = ["usd_tf", "usd_usd", "usd_usdGeom", "usd_hd"]

                self.cpp_info.components["usd_usdVolImaging"].libs = ["usd_usdVolImaging"]
                self.cpp_info.components["usd_usdVolImaging"].requires = ["usd_usdImaging"]

        # usd
        self.cpp_info.components["usd_ar"].libs = ["usd_ar"]
        self.cpp_info.components["usd_ar"].requires = ["usd_arch", "usd_js", "usd_tf", "usd_plug", "usd_vt", "onetbb::onetbb"]

        self.cpp_info.components["usd_kind"].libs = ["usd_kind"]
        self.cpp_info.components["usd_kind"].requires = ["usd_tf", "usd_plug"]

        self.cpp_info.components["usd_ndr"].libs = ["usd_ndr"]
        self.cpp_info.components["usd_ndr"].requires = ["usd_tf", "usd_plug", "usd_vt", "usd_work", "usd_ar", "usd_sdf"]

        self.cpp_info.components["usd_pcp"].libs = ["usd_pcp"]
        self.cpp_info.components["usd_pcp"].requires = ["usd_tf", "usd_trace", "usd_vt", "usd_sdf", "usd_work", "usd_ar", "onetbb::libtbb"]

        self.cpp_info.components["usd_sdf"].libs = ["usd_sdf"]
        self.cpp_info.components["usd_sdf"].requires = ["usd_arch", "usd_tf", "usd_gf", "usd_trace", "usd_vt", "usd_work", "usd_ar"]

        self.cpp_info.components["usd_sdr"].libs = ["usd_sdr"]
        self.cpp_info.components["usd_sdr"].requires = ["usd_tf", "usd_vt", "usd_ar", "usd_ndr", "usd_sdf"]

        self.cpp_info.components["usd_usd"].libs = ["usd_usd"]
        self.cpp_info.components["usd_usd"].requires = ["usd_arch", "usd_kind", "usd_pcp", "usd_sdf", "usd_ar", "usd_plug", "usd_tf", "usd_trace", "usd_vt", "usd_work", "onetbb::libtbb"]

        self.cpp_info.components["usd_usdGeom"].libs = ["usd_usdGeom"]
        self.cpp_info.components["usd_usdGeom"].requires = ["usd_js", "usd_tf", "usd_plug", "usd_vt", "usd_sdf", "usd_trace", "usd_usd", "usd_work", "onetbb::libtbb"]

        self.cpp_info.components["usd_usdHydra"].libs = ["usd_usdHydra"]
        self.cpp_info.components["usd_usdHydra"].requires = ["usd_tf", "usd_usd", "usd_usdShade"]

        self.cpp_info.components["usd_usdLux"].libs = ["usd_usdLux"]
        self.cpp_info.components["usd_usdLux"].requires = ["usd_tf", "usd_vt", "usd_ndr", "usd_sdf", "usd_usd", "usd_usdGeom", "usd_usdShade"]

        self.cpp_info.components["usd_usdMedia"].libs = ["usd_usdMedia"]
        self.cpp_info.components["usd_usdMedia"].requires = ["usd_tf", "usd_vt", "usd_sdf", "usd_usd", "usd_usdGeom"]

        if self.options.enable_materialx_support:
            self.cpp_info.components["usd_usdMtlx"].libs = ["usd_usdMtlx"]
            self.cpp_info.components["usd_usdMtlx"].requires = ["usd_arch", "usd_gf", "usd_ndr", "usd_sdf", "usd_sdr", "usd_tf", "usd_vt", "usd_usd", "usd_usdGeom", "usd_usdShade", "usd_usdUI", "usd_usdUtils", "materialx::MaterialXCore", "materialx::MaterialXFormat"]

        self.cpp_info.components["usd_usdPhysics"].libs = ["usd_usdPhysics"]
        self.cpp_info.components["usd_usdPhysics"].requires = ["usd_tf", "usd_plug", "usd_vt", "usd_sdf", "usd_trace", "usd_usd", "usd_usdGeom", "usd_usdShade", "usd_work", "onetbb::libtbb"]

        self.cpp_info.components["usd_usdProc"].libs = ["usd_usdProc"]
        self.cpp_info.components["usd_usdProc"].requires = ["usd_tf", "usd_usd", "usd_usdGeom"]

        self.cpp_info.components["usd_usdRender"].libs = ["usd_usdRender"]
        self.cpp_info.components["usd_usdRender"].requires = ["usd_gf", "usd_tf", "usd_usd", "usd_usdGeom", "usd_usdShade"]

        self.cpp_info.components["usd_usdRi"].libs = ["usd_usdRi"]
        self.cpp_info.components["usd_usdRi"].requires = ["usd_tf", "usd_vt", "usd_sdf", "usd_usd", "usd_usdShade", "usd_usdGeom"]

        self.cpp_info.components["usd_usdShade"].libs = ["usd_usdShade"]
        self.cpp_info.components["usd_usdShade"].requires = ["usd_tf", "usd_vt", "usd_js", "usd_sdf", "usd_ndr", "usd_sdr", "usd_usd", "usd_usdGeom"]

        self.cpp_info.components["usd_usdSkel"].libs = ["usd_usdSkel"]
        self.cpp_info.components["usd_usdSkel"].requires = ["usd_arch", "usd_gf", "usd_tf", "usd_trace", "usd_vt", "usd_work", "usd_sdf", "usd_usd", "usd_usdGeom", "onetbb::libtbb"]

        self.cpp_info.components["usd_usdUI"].libs = ["usd_usdUI"]
        self.cpp_info.components["usd_usdUI"].requires = ["usd_tf", "usd_vt", "usd_sdf", "usd_usd"]

        self.cpp_info.components["usd_usdUtils"].libs = ["usd_usdUtils"]
        self.cpp_info.components["usd_usdUtils"].requires = ["usd_arch", "usd_tf", "usd_gf", "usd_sdf", "usd_usd", "usd_usdGeom", "usd_usdShade"]

        self.cpp_info.components["usd_usdVol"].libs = ["usd_usdVol"]
        self.cpp_info.components["usd_usdVol"].requires = ["usd_tf", "usd_usd", "usd_usdGeom"]

        if self.options.build_draco_plugin:
            self.cpp_info.components["usdDraco"].libdirs = ["plugin/usd/"]
            self.cpp_info.components["usdDraco"].libs = ["usdDraco"]
            self.cpp_info.components["usdDraco"].requires = ["usd_tf", "usd_gf", "usd_sdf", "usd_usd", "usd_usdGeom", "draco::draco"]

        if self.options.build_alembic_plugin:
            self.cpp_info.components["usdAbc"].libdirs = ["plugin/usd/"]
            self.cpp_info.components["usdAbc"].libs = ["usdAbc"]
            self.cpp_info.components["usdAbc"].requires = ["usd_tf", "usd_work", "usd_sdf", "usd_usd", "usd_usdGeom", "alembic::alembic", "imath::imath"]
            if self.options.enable_hdf5_support:
                self.cpp_info.components["usdAbc"].requires.append("hdf5::hdf5")

        if self.options.build_usd_imaging and not self.options.build_imaging:
            self.cpp_info.components["usd_usdShaders"].libdirs = ["plugin/usd/"]
            self.cpp_info.components["usd_usdShaders"].libs = ["usdShaders"]
            self.cpp_info.components["usd_usdShaders"].requires = ["usd_ar", "usd_ndr", "usd_sdr", "usd_usdShade"]

            self.cpp_info.components["usd_sdrGlslfx"].libdirs = ["plugin/usd/"]
            self.cpp_info.components["usd_sdrGlslfx"].libs = ["sdrGlslfx"]
            self.cpp_info.components["usd_sdrGlslfx"].requires = ["usd_ar", "usd_ndr", "usd_sdr", "usd_hio"]
