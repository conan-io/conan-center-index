from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir
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
    }
    default_options = {
        "shared": False,
        "fPIC": False,
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.shared:
            self.requires("onetbb/2021.12.0", transitive_headers=True)
        self.requires("opensubdiv/3.6.0")
        self.requires("opengl/system")
        
    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )
        # Require same options as in https://github.com/PixarAnimationStudios/OpenUSD/blob/release/build_scripts/build_usd.py#L1450
        if not self.dependencies["opensubdiv"].options.with_tbb and self.options.shared:
            raise ConanInvalidConfiguration("openusd requires -o opensubdiv/*:with_tbb=True when building shared")
        if not self.dependencies["opensubdiv"].options.with_opengl:
            raise ConanInvalidConfiguration("openusd requires -o opensubdiv/*:with_opengl=True")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # Use variables in documented in https://github.com/PixarAnimationStudios/OpenUSD/blob/release/BUILDING.md
        tc.variables["PXR_BUILD_USDVIEW"] = False
        tc.variables["PXR_BUILD_TESTS"] = False
        tc.variables["PXR_BUILD_EXAMPLES"] = False
        tc.variables["PXR_BUILD_TUTORIALS"] = False
        tc.variables["PXR_BUILD_HTML_DOCUMENTATION"] = False
        tc.variables["PXR_ENABLE_PYTHON_SUPPORT"] = False
        
        tc.variables["OPENSUBDIV_LIBRARIES"] = "OpenSubdiv::osdcpu"
        tc.variables["OPENSUBDIV_INCLUDE_DIR"] = self.dependencies['opensubdiv'].cpp_info.includedirs[0].replace("\\", "/")
        target_suffix = "" if self.dependencies["opensubdiv"].options.shared else "_static"
        tc.variables["OPENSUBDIV_OSDCPU_LIBRARY"] = "OpenSubdiv::osdcpu"+target_suffix
        if self.options.shared:
            tc.variables["TBB_tbb_LIBRARY"] = "TBB::tbb"
        tc.generate()

        tc = CMakeDeps(self)
        tc.set_property("opensubdiv::osdcpu", "cmake_target_name", "OpenSubdiv::osdcpu")
        tc.set_property("opensubdiv::osdcpu", "cmake_target_aliases", ["OpenSubdiv::osdcpu_static"])
        tc.generate()

    def build(self):
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
  
        self.cpp_info.components["usd_arch"].libs = ["usd_arch"]

        self.cpp_info.components["usd_ar"].libs = ["usd_ar"]
        self.cpp_info.components["usd_ar"].requires = ["usd_arch", "usd_js", "usd_tf", "usd_plug", "usd_vt"]
        if self.options.shared:
            self.cpp_info.components["usd_ar"].requires.append("onetbb::libtbb")

        self.cpp_info.components["usd_cameraUtil"].libs = ["usd_cameraUtil"]
        self.cpp_info.components["usd_cameraUtil"].requires = ["usd_tf", "usd_gf"]

        self.cpp_info.components["usd_garch"].libs = ["usd_garch"]
        self.cpp_info.components["usd_garch"].requires = ["usd_arch", "usd_tf", "opengl::opengl"]
    
        self.cpp_info.components["usd_geomUtil"].libs = ["usd_geomUtil"]
        self.cpp_info.components["usd_geomUtil"].requires = ["usd_arch", "usd_gf", "usd_tf", "usd_vt", "usd_pxOsd"]

        self.cpp_info.components["usd_gf"].libs = ["usd_gf"]
        self.cpp_info.components["usd_gf"].requires = ["usd_arch", "usd_tf"]

        self.cpp_info.components["usd_glf"].libs = ["usd_glf"]
        self.cpp_info.components["usd_glf"].requires = ["usd_ar", "usd_arch", "usd_garch", "usd_gf", "usd_hf", "usd_hio", "usd_plug", "usd_tf", "usd_trace", "usd_sdf", "opengl::opengl"]

        self.cpp_info.components["usd_hd"].libs = ["usd_hd"]
        self.cpp_info.components["usd_hd"].requires = ["usd_plug", "usd_tf", "usd_trace", "usd_vt", "usd_work", "usd_sdf", "usd_cameraUtil", "usd_hf", "usd_pxOsd", "usd_sdr"]
        if self.options.shared:
            self.cpp_info.components["usd_hd"].requires.append("onetbb::libtbb")

        self.cpp_info.components["usd_hdar"].libs = ["usd_hdar"]
        self.cpp_info.components["usd_hdar"].requires = ["usd_hd", "usd_ar"]

        self.cpp_info.components["usd_hdGp"].libs = ["usd_hdGp"]
        self.cpp_info.components["usd_hdGp"].requires = ["usd_hd", "usd_hf"]
        if self.options.shared:
            self.cpp_info.components["usd_hdGp"].requires.append("onetbb::libtbb")

        self.cpp_info.components["usd_hdsi"].libs = ["usd_hdsi"]
        self.cpp_info.components["usd_hdsi"].requires = ["usd_plug", "usd_tf", "usd_trace", "usd_vt", "usd_work", "usd_sdf", "usd_cameraUtil", "usd_geomUtil", "usd_hf", "usd_hd", "usd_pxOsd"]

        self.cpp_info.components["usd_hdSt"].libs = ["usd_hdSt"]
        self.cpp_info.components["usd_hdSt"].requires = ["usd_hio", "usd_garch", "usd_glf", "usd_hd", "usd_hdsi", "usd_hgiGL", "usd_hgiInterop", "usd_sdr", "usd_tf", "usd_trace", "opensubdiv::opensubdiv"]

        self.cpp_info.components["usd_hdx"].libs = ["usd_hdx"]
        self.cpp_info.components["usd_hdx"].requires = ["usd_plug", "usd_tf", "usd_vt", "usd_gf", "usd_work", "usd_garch", "usd_glf", "usd_pxOsd", "usd_hd", "usd_hdSt", "usd_hgi", "usd_hgiInterop", "usd_cameraUtil", "usd_sdf"]

        self.cpp_info.components["usd_hf"].libs = ["usd_hf"]
        self.cpp_info.components["usd_hf"].requires = ["usd_plug", "usd_tf", "usd_trace"]

        self.cpp_info.components["usd_hgi"].libs = ["usd_hgi"]
        self.cpp_info.components["usd_hgi"].requires = ["usd_gf", "usd_plug", "usd_tf", "usd_hio"]

        self.cpp_info.components["usd_hgiGL"].libs = ["usd_hgiGL"]
        self.cpp_info.components["usd_hgiGL"].requires = ["usd_arch", "usd_garch", "usd_hgi", "usd_tf", "usd_trace"]

        if is_apple_os(self):
            self.cpp_info.components["usd_hgiMetal"].libs = ["usd_hgiMetal"]
            self.cpp_info.components["usd_hgiMetal"].requires = ["usd_arch", "usd_hgi", "usd_tf", "usd_trace"]

        self.cpp_info.components["usd_hgiInterop"].libs = ["usd_hgiInterop"]
        self.cpp_info.components["usd_hgiInterop"].requires = ["usd_garch", "usd_gf", "usd_tf", "usd_hgi", "usd_vt", "usd_trace"]
        if is_apple_os(self):
            self.cpp_info.components["usd_hgiInterop"].requires.append("usd_hgiMetal")

        self.cpp_info.components["usd_hio"].libs = ["usd_hio"]
        self.cpp_info.components["usd_hio"].requires = ["usd_arch", "usd_js", "usd_plug", "usd_tf", "usd_vt", "usd_trace", "usd_ar", "usd_hf"]

        self.cpp_info.components["usd_js"].libs = ["usd_js"]
        self.cpp_info.components["usd_js"].requires = ["usd_tf"]

        self.cpp_info.components["usd_kind"].libs = ["usd_kind"]
        self.cpp_info.components["usd_kind"].requires = ["usd_tf", "usd_plug"]

        self.cpp_info.components["usd_ndr"].libs = ["usd_ndr"]
        self.cpp_info.components["usd_ndr"].requires = ["usd_tf", "usd_plug", "usd_vt", "usd_work", "usd_ar", "usd_sdf"]

        self.cpp_info.components["usd_pcp"].libs = ["usd_pcp"]
        self.cpp_info.components["usd_pcp"].requires = ["usd_tf", "usd_trace", "usd_vt", "usd_sdf", "usd_work", "usd_ar"]
        if self.options.shared:
            self.cpp_info.components["usd_pcp"].requires.append("onetbb::libtbb")

        self.cpp_info.components["usd_pegtl"].libs = ["usd_pegtl"]
        self.cpp_info.components["usd_pegtl"].requires = ["usd_arch"]

        self.cpp_info.components["usd_plug"].libs = ["usd_plug"]
        self.cpp_info.components["usd_plug"].requires = ["usd_arch", "usd_tf", "usd_js", "usd_trace", "usd_work"]
        if self.options.shared:
            self.cpp_info.components["usd_plug"].requires.append("onetbb::libtbb")

        self.cpp_info.components["usd_pxOsd"].libs = ["usd_pxOsd"]
        self.cpp_info.components["usd_pxOsd"].requires = ["usd_tf", "usd_gf", "usd_vt", "opensubdiv::opensubdiv"]

        self.cpp_info.components["usd_sdf"].libs = ["usd_sdf"]
        self.cpp_info.components["usd_sdf"].requires = ["usd_arch", "usd_tf", "usd_ts", "usd_gf", "usd_trace", "usd_vt", "usd_work", "usd_ar"]

        self.cpp_info.components["usd_sdr"].libs = ["usd_sdr"]
        self.cpp_info.components["usd_sdr"].requires = ["usd_tf", "usd_vt", "usd_ar", "usd_ndr", "usd_sdf"]

        self.cpp_info.components["usd_tf"].libs = ["usd_tf"]
        self.cpp_info.components["usd_tf"].requires = ["usd_arch"]
        if self.options.shared:
            self.cpp_info.components["usd_tf"].requires.append("onetbb::libtbb")

        self.cpp_info.components["usd_trace"].libs = ["usd_trace"]
        self.cpp_info.components["usd_trace"].requires = ["usd_arch", "usd_tf", "usd_js"]
        if self.options.shared:
            self.cpp_info.components["usd_trace"].requires.append("onetbb::libtbb")

        self.cpp_info.components["usd_ts"].libs = ["usd_ts"]
        self.cpp_info.components["usd_ts"].requires = ["usd_arch", "usd_gf", "usd_plug", "usd_tf", "usd_trace", "usd_vt"]

        self.cpp_info.components["usd_usd"].libs = ["usd_usd"]
        self.cpp_info.components["usd_usd"].requires = ["usd_arch", "usd_kind", "usd_pcp", "usd_sdf", "usd_ar", "usd_plug", "usd_tf", "usd_trace", "usd_vt", "usd_work"]
        if self.options.shared:
            self.cpp_info.components["usd_usd"].requires.append("onetbb::libtbb")

        self.cpp_info.components["usd_usdAppUtils"].libs = ["usd_usdAppUtils"]
        self.cpp_info.components["usd_usdAppUtils"].requires = ["usd_garch", "usd_gf", "usd_hio", "usd_sdf", "usd_tf", "usd_usd", "usd_usdGeom", "usd_usdImagingGL"]

        self.cpp_info.components["usd_usdGeom"].libs = ["usd_usdGeom"]
        self.cpp_info.components["usd_usdGeom"].requires = ["usd_js", "usd_tf", "usd_plug", "usd_vt", "usd_sdf", "usd_trace", "usd_usd", "usd_work"]
        if self.options.shared:
            self.cpp_info.components["usd_usdGeom"].requires.append("onetbb::libtbb")
            
        self.cpp_info.components["usd_usdGeomValidators"].libs = ["usd_usdGeomValidators"]
        self.cpp_info.components["usd_usdGeomValidators"].requires = ["usd_tf", "usd_plug", "usd_sdf", "usd_usd", "usd_usdGeom", "usd_usdValidation"]
        
        self.cpp_info.components["usd_usdHydra"].libs = ["usd_usdHydra"]
        self.cpp_info.components["usd_usdHydra"].requires = ["usd_tf", "usd_usd", "usd_usdShade"]

        self.cpp_info.components["usd_usdImaging"].libs = ["usd_usdImaging"]
        self.cpp_info.components["usd_usdImaging"].requires = ["usd_gf", "usd_tf", "usd_plug", "usd_trace", "usd_vt", "usd_work", "usd_geomUtil", "usd_hd", "usd_hdar", "usd_hio", "usd_pxOsd", "usd_sdf", "usd_usd", "usd_usdGeom", "usd_usdLux", "usd_usdRender", "usd_usdShade", "usd_usdVol", "usd_ar"]
        if self.options.shared:
            self.cpp_info.components["usd_usdImaging"].requires.append("onetbb::libtbb")

        self.cpp_info.components["usd_usdImagingGL"].libs = ["usd_usdImagingGL"]
        self.cpp_info.components["usd_usdImagingGL"].requires = ["usd_gf", "usd_tf", "usd_plug", "usd_trace", "usd_vt", "usd_work", "usd_hio", "usd_garch", "usd_glf", "usd_hd", "usd_hdsi", "usd_hdx", "usd_pxOsd", "usd_sdf", "usd_sdr", "usd_usd", "usd_usdGeom", "usd_usdHydra", "usd_usdShade", "usd_usdImaging", "usd_ar"]
        if self.options.shared:
            self.cpp_info.components["usd_usdImagingGL"].requires.append("onetbb::libtbb")

        self.cpp_info.components["usd_usdLux"].libs = ["usd_usdLux"]
        self.cpp_info.components["usd_usdLux"].requires = ["usd_tf", "usd_vt", "usd_ndr", "usd_sdf", "usd_usd", "usd_usdGeom", "usd_usdShade"]

        self.cpp_info.components["usd_usdMedia"].libs = ["usd_usdMedia"]
        self.cpp_info.components["usd_usdMedia"].requires = ["usd_tf", "usd_vt", "usd_sdf", "usd_usd", "usd_usdGeom"]

        self.cpp_info.components["usd_usdPhysics"].libs = ["usd_usdPhysics"]
        self.cpp_info.components["usd_usdPhysics"].requires = ["usd_tf", "usd_plug", "usd_vt", "usd_sdf", "usd_trace", "usd_usd", "usd_usdGeom", "usd_usdShade", "usd_work"]
        if self.options.shared:
            self.cpp_info.components["usd_usdPhysics"].requires.append("onetbb::libtbb")
        
        self.cpp_info.components["usd_usdPhysicsValidators"].libs = ["usd_usdPhysicsValidators"]

        self.cpp_info.components["usd_usdProc"].libs = ["usd_usdProc"]
        self.cpp_info.components["usd_usdProc"].requires = ["usd_tf", "usd_usd", "usd_usdGeom"]

        self.cpp_info.components["usd_usdProcImaging"].libs = ["usd_usdProcImaging"]
        self.cpp_info.components["usd_usdProcImaging"].requires = ["usd_usdImaging", "usd_usdProc"]

        self.cpp_info.components["usd_usdRender"].libs = ["usd_usdRender"]
        self.cpp_info.components["usd_usdRender"].requires = ["usd_gf", "usd_tf", "usd_usd", "usd_usdGeom", "usd_usdShade"]

        self.cpp_info.components["usd_usdRi"].libs = ["usd_usdRi"]
        self.cpp_info.components["usd_usdRi"].requires = ["usd_tf", "usd_vt", "usd_sdf", "usd_usd", "usd_usdShade", "usd_usdGeom"]

        self.cpp_info.components["usd_usdRiPxrImaging"].libs = ["usd_usdRiPxrImaging"]
        self.cpp_info.components["usd_usdRiPxrImaging"].requires = ["usd_gf", "usd_tf", "usd_plug", "usd_trace", "usd_vt", "usd_work", "usd_hd", "usd_pxOsd", "usd_sdf", "usd_usd", "usd_usdGeom", "usd_usdLux", "usd_usdShade", "usd_usdImaging", "usd_usdVol", "usd_ar"]
        if self.options.shared:
            self.cpp_info.components["usd_usdRiPxrImaging"].requires.append("onetbb::libtbb")

        self.cpp_info.components["usd_usdSemantics"].libs = ["usd_usdSemantics"]
        
        self.cpp_info.components["usd_usdShade"].libs = ["usd_usdShade"]
        self.cpp_info.components["usd_usdShade"].requires = ["usd_tf", "usd_vt", "usd_js", "usd_sdf", "usd_ndr", "usd_sdr", "usd_usd", "usd_usdGeom"]
        
        self.cpp_info.components["usd_usdShadeValidators"].libs = ["usd_usdShadeValidators"]

        self.cpp_info.components["usd_usdSkel"].libs = ["usd_usdSkel"]
        self.cpp_info.components["usd_usdSkel"].requires = ["usd_arch", "usd_gf", "usd_tf", "usd_trace", "usd_vt", "usd_work", "usd_sdf", "usd_usd", "usd_usdGeom"]
        if self.options.shared:
            self.cpp_info.components["usd_usdSkel"].requires.append("onetbb::libtbb")

        self.cpp_info.components["usd_usdSkelImaging"].libs = ["usd_usdSkelImaging"]
        self.cpp_info.components["usd_usdSkelImaging"].requires = ["usd_hio", "usd_hd", "usd_usdImaging", "usd_usdSkel"]

        self.cpp_info.components["usd_usdSkelValidators"].libs = ["usd_usdSkelValidators"]

        self.cpp_info.components["usd_usdUI"].libs = ["usd_usdUI"]
        self.cpp_info.components["usd_usdUI"].requires = ["usd_tf", "usd_vt", "usd_sdf", "usd_usd"]

        self.cpp_info.components["usd_usdUtils"].libs = ["usd_usdUtils"]
        self.cpp_info.components["usd_usdUtils"].requires = ["usd_arch", "usd_tf", "usd_gf", "usd_sdf", "usd_usd", "usd_usdGeom", "usd_usdShade"]
        
        self.cpp_info.components["usd_usdUtilsValidators"].libs = ["usd_usdUtilsValidators"]
 
        self.cpp_info.components["usd_usdValidation"].libs = ["usd_usdValidation"]

        self.cpp_info.components["usd_usdVol"].libs = ["usd_usdVol"]
        self.cpp_info.components["usd_usdVol"].requires = ["usd_tf", "usd_usd", "usd_usdGeom"]

        self.cpp_info.components["usd_usdVolImaging"].libs = ["usd_usdVolImaging"]
        self.cpp_info.components["usd_usdVolImaging"].requires = ["usd_usdImaging"]
        
        self.cpp_info.components["usd_vt"].libs = ["usd_vt"]
        self.cpp_info.components["usd_vt"].requires = ["usd_arch", "usd_tf", "usd_gf", "usd_trace"]
        if self.options.shared:
            self.cpp_info.components["usd_vt"].requires.append("onetbb::libtbb")
            
        self.cpp_info.components["usd_work"].libs = ["usd_work"]
        self.cpp_info.components["usd_work"].requires = ["usd_tf", "usd_trace"]
        if self.options.shared:
            self.cpp_info.components["usd_work"].requires.append("onetbb::libtbb")