# RECIPE MAINTAINER NOTES:
# - Read vtk's Documentation/release/9.1.md for important notes about versions and forks
# - Also read vtk's Documentation/build.md for information about build settings and flags
# - Modify build_requirements() to match the version of CMake that VTK tested with that release.

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration, ConanException
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.build import check_min_cppstd
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir, save, rename, collect_libs, load, replace_in_file
from conan.tools.scm import Version

from shutil import which

import os
import textwrap

import json # for auto-component generation

# Enable to keep VTK-generated cmake files, to check contents
_debug_packaging = False

required_conan_version = ">=1.53.0"


# for self.options.group_* and self.options.

# https://vtk.org/doc/nightly/html/group__module.html
# QUOTE #
# QUOTE # Modules and groups are enable and disable preferences are specified using a 5-way flag setting:
# QUOTE #
# QUOTE # YES: The module or group must be built.
# QUOTE # NO: The module or group must not be built.
# QUOTE # WANT: The module or group should be built if possible.
# QUOTE # DONT_WANT: The module or group should only be built if required (e.g., via a dependency).
# QUOTE # DEFAULT: Acts as either WANT or DONT_WANT based on the group settings for the module or WANT_BY_DEFAULT option to vtk_module_scan if no other preference is specified. This is usually handled via another setting in the main project.
# QUOTE # If a YES module preference requires a module with a NO preference, an error is raised.
# QUOTE #
# QUOTE # A module with a setting of DEFAULT will look for its first non-DEFAULT group setting and only if all of those are set to DEFAULT is the WANT_BY_DEFAULT setting used.

# This means we don't truly know what is required until after configuration,
# and we can't configure without the correct requires!
# So we will just do our best and the consumer can adjust as required.

# See notes below in _is_module_enabled()

def _is_module_YES_or_WANT(flag):
    return flag in ["YES", "WANT"]

def _is_module_NO(flag):
    return flag in ["NO"]




class VtkConan(ConanFile):
    name = "vtk"
    description = "The Visualization Toolkit (VTK) by Kitware is an open-source, \
        freely available software system for 3D computer graphics, \
        image processing, and visualization."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.vtk.org/"
    topics = ("scientific", "image", "processing", "visualization")
    settings = "os", "compiler", "build_type", "arch"

    short_paths = True

    # Alternative method: can use git directly - helpful when hacking VTK
    # TODO allow user to set the git_url from the command line, during conan install
    # git_url = "https://gitlab.kitware.com/vtk/vtk.git"
    git_url = "/build/git-mirrors/vtk.git"


    ############
    # list of all possible 3rd parties (as of 9.1.0)
    # with each one marked as where they should come from.
    #
    # Procedure for this list:
    #  - for each item, check if there is a recipe in CCI (clone it for easy search)
    #  - check VTK/ThirdParty/PACKAGE/CMakeLists.txt for minimum version
    #  - check VTK/ThirdParty/PACKAGE/vtkPACK/README.kitware.md
    #       for any notes on special changes to the library,
    #       apart from integration with the build system.
    #  - try adding to the "parties" list
    #  - ensure VTK_MODULE_USE_EXTERNAL_VTK_pack is NOT set to False
    #  - 'conan create' with the group/module enabled that requires this pack
    #  - build with CMAKE_FIND_DEBUG_MODE=True (option below to uncomment)
    #       and carefully ensure it isn't picking up any system libs
    #       (search the output for "The item was")
    #
    # cgns:             conan (cgns)
    # cli11:            conan (cli11)
    # diy2:             internal (not available in CCI - TODO)
    # doubleconversion: conan (double-conversion)
    # eigen:            conan (eigen)
    # exodusII:         internal (not available in CCI - TODO)
    # expat:            conan (expat)
    # exprtk:           conan (exprtk)
    # fides:            internal (not available in CCI - TODO)
    # fmt:              conan (fmt)
    # freetype:         conan (freetype)
    # gl2ps:            internal (not available in CCI - TODO)
    # glew:             conan (glew)
    # h5part:           internal (not available in CCI - TODO)
    # hdf5:             conan (hdf5)
    # ioss:             internal (not available in CCI - TODO)
    # jpeg:             conan (libjpeg or libjpeg-turbo)
    # jsoncpp:          conan (jsoncpp)
    # kissfft:          conan (kissfft)
    # libharu:          conan (libharu)
    # libproj:          conan (proj)
    # libxml2:          conan (libxml2)
    # loguru:           internal (not available in CCI - TODO)
    # lz4:              conan (lz4)
    # lzma:             conan (xz_utils)
    # mpi4py:           internal (not available in CCI - TODO)
    # netcdf:           conan (netcdf)
    # ogg:              conan (ogg)
    # pegtl:            internal (not available in CCI - TODO)
    # png:              conan (libpng)
    # pugixml:          conan (pugixml)
    # sqlite:           conan (sqlite3)
    # theora:           conan (theora)
    # tiff:             conan (libtiff)
    # utf8:             conan (utfcpp)
    # verdict:          internal (not available in CCI TODO)
    # vpic:             internal (not available in CCI TODO)
    # vtkm:             internal (not available in CCI TODO)
    # xdmf2:            internal (not available in CCI TODO)
    # xdmf3:            internal (not available in CCI TODO)
    # zfp:              conan (zfp) - but not actually used in VTK?
    # zlib:             conan (zlib)
    #
    ############

    options = {
            "shared": [True, False],
            "fPIC": [True, False],

            ### Helpful option when hacking on VTK - faster to extract on linux too ###
            "use_source_from_git": [True, False],

            ### Conan package choices ###
            "with_jpeg":        ["libjpeg", "libjpeg-turbo"],

            ### Debugging / future proofing ###
            "legacy_remove":    [True, False],
            "legacy_silent":    [True, False],
            "use_future_const": [True, False],
            "debug_leaks":      [True, False],

            ### Compile options ###
            "use_64bit_ids": ["Auto", True, False], # default: 32 bit on 32 bit platforms.  64 on 64 bit platforms.
            "enable_kits":   [True, False],         # VTK_ENABLE_KITS - smaller set of libraries - ONLY for shared mode
            "enable_logging": [True, False],

            ### Wrapping support ###
            "enable_wrapping": [True, False],
            "wrap_java":       [True, False],
            "wrap_python":     [True, False],
            "build_pyi_files": [True, False],   # requires wrap_python
            "use_tk":          [True, False],   # requires wrap_python

            ### Advanced tech ###
            "use_cuda":    [True, False],
            "use_memkind": [True, False],
            "use_mpi":     [True, False],

            ### SMP ###
            "smp_implementation_type": ["Sequential", "STDThread", "OpenMP", "TBB"],
            "smp_enable_Sequential":   [True, False],
            "smp_enable_STDThread":    [True, False],
            "smp_enable_OpenMP":       [True, False],
            "smp_enable_TBB":          [True, False],

            ### Modules ###
            "build_all_modules":       [True, False],     # The big one, build everything - good for pre-built CCI

            "enable_remote_modules":   [True, False],   # Build modules that exist in Remote folder
                                                        # Currently LookingGlass, DICOM and MomentInvariants filter
                                                        # The default will be off, they should be built externally in the conan world (when available).

            # Groups of modules
            "group_enable_Qt":         ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],   # can set to False, and use modules for enabling parts of Qt support
            "group_enable_Imaging":    ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "group_enable_MPI":        ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "group_enable_Rendering":  ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "group_enable_Views":      ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "group_enable_Web":        ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],

            # With StandAlone enabled, it will use the conan libraries rather than the copies
            # bundled with VTK (eg: HDF5, cgns, theora, ogg, netcdf, libxml2)
            "group_enable_StandAlone": ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],

            # Modules (many not listed)
            "module_enable_IOExport":          ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "module_enable_IOLegacy":          ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "module_enable_RenderingCore":     ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "module_enable_RenderingExternal": ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],

            # Qt-specific modules
            "qt_version": ["Auto", "5", "6"],
            "module_enable_GUISupportQt":      ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "module_enable_GUISupportQtQuick": ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "module_enable_GUISupportQtSQL":   ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "module_enable_RenderingQt":       ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "module_enable_ViewsQt":           ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],

            # TODO modules that require extra stuff to be installed
            "module_enable_IOPDAL":            ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "module_enable_IOPostgreSQL":      ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "module_enable_IOOpenVDB":         ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "module_enable_IOLAS":             ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "module_enable_IOADIOS2":          ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "module_enable_fides":             ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "module_enable_GeovisGDAL":        ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "module_enable_IOGDAL":            ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "module_enable_FiltersOpenTURNS":  ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "module_enable_DomainsMicroscopy": ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "module_enable_CommonArchive":     ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            }

    default_options = {
            "shared": False,
            "fPIC":   True,

            ### Helpful option when hacking on VTK - faster to extract on linux too ###
            "use_source_from_git": False, # False = use the tarball

            ### Conan package choices ###
            "with_jpeg":        "libjpeg",  # the current standard in other packages on CCI

            ### Debugging / future proofing ###
            "legacy_remove":    False,
            "legacy_silent":    False,
            "use_future_const": False,
            "debug_leaks":      False,

            ### Compile options ###
            "use_64bit_ids":   "Auto",
            "enable_kits":     False,
            "enable_logging":  False,

            ### Wrapping support ###
            "enable_wrapping": False,
            "wrap_java":       False,
            "wrap_python":     False,
            "use_tk":          False,

            ### Python specifics ###
            "build_pyi_files": False,

            ### Advanced tech ###
            "use_cuda":    False,
            "use_memkind": False,
            "use_mpi":     False,

            ### SMP ###
            "smp_implementation_type": "Sequential",
            "smp_enable_Sequential":   False,
            "smp_enable_STDThread":    False,
            "smp_enable_OpenMP":       False,
            "smp_enable_TBB":          False,

            ### Modules ###
            "build_all_modules":       True,    # disable to pick+choose modules

            "enable_remote_modules":   False,   # see notes above

            # Groups of modules
            "group_enable_Imaging":    "DEFAULT",
            "group_enable_MPI":        "DEFAULT",
            "group_enable_Rendering":  "DEFAULT",
            "group_enable_StandAlone": "DEFAULT",
            "group_enable_Views":      "DEFAULT",
            "group_enable_Web":        "DEFAULT",

            # Qt-specific modules
            "qt_version":                      "Auto",
            "group_enable_Qt":                 "DEFAULT",   # can keep this false/default, enable specific QT modules
            "module_enable_GUISupportQt":      "DEFAULT",
            "module_enable_GUISupportQtQuick": "DEFAULT",
            "module_enable_GUISupportQtSQL":   "DEFAULT",
            "module_enable_RenderingQt":       "DEFAULT",
            "module_enable_ViewsQt":           "DEFAULT",

            # More specific modules
            "module_enable_IOExport":          "DEFAULT",
            "module_enable_IOLegacy":          "DEFAULT",
            "module_enable_RenderingCore":     "DEFAULT",
            "module_enable_RenderingExternal": "DEFAULT",

            # these aren't supported yet, need to system-install packages
            "module_enable_IOPDAL":            "NO",
            "module_enable_IOPostgreSQL":      "NO",
            "module_enable_IOOpenVDB":         "NO",
            "module_enable_IOLAS":             "NO",
            "module_enable_IOADIOS2":          "NO",
            "module_enable_fides":             "NO",
            "module_enable_GeovisGDAL":        "NO",
            "module_enable_IOGDAL":            "NO",
            "module_enable_FiltersOpenTURNS":  "NO",
            "module_enable_DomainsMicroscopy": "NO",
            "module_enable_CommonArchive":     "NO",
            }


    # If build_all_modules=True, then we will ask the consumer will set modules=NO if they really don't want that requirement.
    # Else, if build_all_modules=False, then we will ask the consumer to set modules=YES/WANT to get the requirement.
    #
    # options_to_check is a list/array
    def _is_module_enabled(self, options_to_check):
        # assume module is enabled if any of the options_to_check are WANT or YES,
        # but assume module is DISABLED if build_all_modules=True and ALL of the options_to_check are "NO"
        #
        # See notes above, VTK may do even deeper checks but this hopefully will be good enough.
        #
        if self.options.build_all_modules:
            for option in options_to_check:
                if not _is_module_NO(option):
                    return True # something was not 'NO', then this module is at least partially enabled
            # ALL are NO, then assume this module is disabled
            return False
        else:
            for option in options_to_check:
                if _is_module_YES_or_WANT(option):
                    return True
            return False


    # special case for QT as it is more involved
    @property
    def _is_any_Qt_enabled(self):
        return self._is_module_enabled([
            self.options.group_enable_Qt,
            self.options.module_enable_GUISupportQt,
            self.options.module_enable_GUISupportQtQuick,
            self.options.module_enable_GUISupportQtSQL,
            self.options.module_enable_RenderingQt,
            self.options.module_enable_ViewsQt
            ])


    # Required as VTK adds 'd' to the end of library files on windows
    @property
    def _lib_suffix(self):
        return "d" if self.settings.os == "Windows" and self.settings.build_type == "Debug" else ""

    def build_requirements(self):
        self.tool_requires("sqlite3/3.40.1")

    def source(self):
        if self.options.use_source_from_git:
            self.run("git clone -b release --single-branch " + self.git_url + " " + self.source_folder)
            # note: we give the branch a name so we don't have detached heads
            # TODO change to standard git and python chdir
            # Version: support targeting a commit hash instead of a version tag, assume version number < 8 chars long
            # 1.34.67 ... only 7 chars long
            # anything more, assume a branch name or a hash (or short hash)
            git_hash = self.version if len(self.version) > 7 else "v" + self.version
            self.run("cd " + self.source_folder + " && git checkout -b branch-" + git_hash + " " + git_hash)
        else:
            get(self, **self.conan_data["sources"][self.version],
                    strip_root=True,
                    destination=self.source_folder)

    def _third_party(self):
        parties = {
                # LEFT field:  target name for linking, will be used as TARGET::TARGET in package_info()
                # RIGHT field: package/version to require
                "cli11":             "cli11/2.3.1",
                "double-conversion": "double-conversion/3.2.1",
                "eigen":             "eigen/3.4.0",
                "expat":             "expat/2.5.0",
                "exprtk":            "exprtk/0.0.1",
                "fmt":               "fmt/8.1.1",      # 9.1.0 release docs mention a PR - confirmed merged 8.1.0
                "freetype":          "freetype/2.12.1",
                "glew":              "glew/2.2.0",
                "jsoncpp":           "jsoncpp/1.9.5",
                "libharu":           "libharu/2.4.3",
                "kissfft":           "kissfft/131.1.0",
                "lz4":               "lz4/1.9.4",
                "libpng":            "libpng/1.6.39",
                "proj":              "proj/9.0.1", # if MAJOR version changes, update ThirdParty/libproj/CMakeLists.txt
                "pugixml":           "pugixml/1.13",
                "sqlite3":           "sqlite3/3.40.1",
                "utfcpp":            "utfcpp/3.2.2",
                "xz_utils":          "xz_utils/5.2.5", # note: VTK calls this lzma
                "zlib":              "zlib/1.2.13",
                "TIFF":              "libtiff/4.4.0",
                }

        # NOTE: You may NOT be able to just adjust the version numbers in here, without
        #   also adjusting the patch, as the versions are also mentioned in ThirdParty/*/CMakeLists.txt

        if self.options.with_jpeg == "libjpeg":
            parties["jpeg"] = "libjpeg/9e"
        elif self.options.with_jpeg == "libjpeg-turbo":
            parties["jpeg"] = "libjpeg-turbo/2.1.4"

        if self._is_module_enabled([self.options.group_enable_StandAlone]):
            parties["hdf5"]    = "hdf5/1.13.1"
            parties["theora"]  = "theora/1.1.1"
            parties["ogg"]     = "ogg/1.3.5"
            parties["netcdf"]  = "netcdf/4.8.1"
            parties["libxml2"] = "libxml2/2.10.3"
            parties["cgns"]    = "cgns/4.3.0"

        # unused dependency, mentioned in vtk but not actually used
        # parties["zfp"]     = "zfp/0.5.5"

        if self.options.build_all_modules:
            parties["boost"]  = "boost/1.80.0"
            parties["openvr"] = "openvr/1.16.8"
            parties["odbc"]   = "odbc/2.3.11"

        if self._is_any_Qt_enabled:
            parties["qt"] = "qt/6.4.1"

        return parties


    def requirements(self):
        if self._is_module_enabled([self.options.group_enable_Rendering]):
            self.requires("opengl/system")
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.requires("xorg/system")
        for pack in self._third_party().values():
            self.requires(pack)

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 191)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.info.settings.compiler), False)
            if minimum_version and Version(self.info.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.")
        if not self.options.shared and self.options.enable_kits:
            raise ConanInvalidConfiguration("KITS can only be enabled with shared")

        if self._is_module_enabled([self.options.group_enable_Web]) and not self.options.wrap_python:
            raise ConanInvalidConfiguration("group_enable_Web can only be enabled with wrap_python")

        if self.options.wrap_python and not self.options.enable_wrapping:
            raise ConanInvalidConfiguration("wrap_python can only be enabled with enable_wrapping")

        if self.options.wrap_python and not self._is_module_enabled([self.options.module_enable_IOExport]):
            raise ConanInvalidConfiguration("wrap_python can only be enabled with module_enable_IOExport enabled, otherwise it has problems compiling")

        if self.options.wrap_java and not self.options.enable_wrapping:
            raise ConanInvalidConfiguration("wrap_java can only be enabled with enable_wrapping")

        if self.options.use_tk and not self.options.wrap_python:
            raise ConanInvalidConfiguration("use_tk can only be enabled with wrap_python")

        if self.options.build_pyi_files and not self.options.wrap_python:
            raise ConanInvalidConfiguration("build_pyi_files can only be enabled with wrap_python")

        if self.dependencies["libtiff"].options.jpeg != self.info.options.with_jpeg:
            raise ConanInvalidConfiguration(f"{self.ref} requires option value {self.name}:with_jpeg equal to libtiff:jpeg.")

        if self.dependencies["pugixml"].options.wchar_mode:
            raise ConanInvalidConfiguration(f"{self.ref} requires pugixml:wchar_mode=False")

        if self.dependencies["kissfft"].options.datatype != "double":
            # kissfft - we want the double format (also known as kiss_fft_scalar)
            raise ConanInvalidConfiguration(f"{self.ref} requires kissfft:datatype=double")


    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "9",
            "Visual Studio": "15.7",
            "msvc": "191",
            "clang": "7",
            "apple-clang": "11",
        }

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.options["libtiff"].jpeg = self.options.with_jpeg
        # kissfft - we want the double format (also known as kiss_fft_scalar)
        self.options["kissfft"].datatype = "double"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)

        # for debugging the conan recipe
        # tc.variables["CMAKE_FIND_DEBUG_MODE"] = True

        # 64 / 32 bit IDs
        if self.options.use_64bit_ids != "Auto":
            tc.variables["VTK_USE_64BIT_IDS"] = self.options.use_64bit_ids

        # Be sure to set this, otherwise vtkCompilerChecks.cmake will downgrade our CXX standard to 11
        tc.variables["VTK_IGNORE_CMAKE_CXX11_CHECKS"] = True


        # No need for versions on installed names
        tc.variables["VTK_VERSIONED_INSTALL"] = False

        # Turn these off for CCI
        tc.variables["BUILD_TESTING"] = False
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_DOCUMENTATION"] = False


        # Needed or not? Nothing gets installed without this ON at the moment.
        # tc.variables["VTK_INSTALL_SDK"] = False


        # future-proofing for your code
        tc.variables["VTK_LEGACY_REMOVE"] = self.options.legacy_remove # disable legacy APIs
        tc.variables["VTK_LEGACY_SILENT"] = self.options.legacy_silent # requires legacy_remove to be off. deprecated APIs will not cause warnings
        tc.variables["VTK_USE_FUTURE_CONST"] = self.options.use_future_const # use the newer const-correct APIs
        tc.variables["VTK_ENABLE_LOGGING"] = self.options.enable_logging


        # development debugging
        tc.variables["VTK_DEBUG_LEAKS"] = self.options.debug_leaks



        # Enable KITs - Quote: "Compiles VTK into a smaller set of libraries."
        # Quote: "Can be useful on platforms where VTK takes a long time to launch due to expensive disk access."
        tc.variables["VTK_ENABLE_KITS"] = self.options.enable_kits


        tc.variables["VTK_ENABLE_WRAPPING"] = self.options.enable_wrapping
        tc.variables["VTK_WRAP_JAVA"] = self.options.wrap_java
        tc.variables["VTK_WRAP_PYTHON"] = self.options.wrap_python
        tc.variables["VTK_BUILD_PYI_FILES"] = self.options.build_pyi_files # Warning: this fails on 9.2.2 if rendering is not enabled.
        tc.variables["VTK_USE_TK"] = self.options.use_tk    # requires wrap_python


        #### CUDA / MPI / MEMKIND ####
        tc.variables["VTK_USE_CUDA"]    = self.options.use_cuda
        tc.variables["VTK_USE_MEMKIND"] = self.options.use_memkind
        tc.variables["VTK_USE_MPI"]     = self.options.use_mpi


        ### Modules ###
        tc.variables["VTK_BUILD_ALL_MODULES"] = self.options.build_all_modules

        tc.variables["VTK_ENABLE_REMOTE_MODULES"] = self.options.enable_remote_modules

        # TODO when conan OpenMPI package works: check if this is a valid test.
        # This is normally computed by VTK's bundled FindNetCDF.cmake, which checks
        # netcdf's include/netcdf_meta.h for the value of NC_HAS_PARALLEL,
        # which apparently is set when parallel IO is supported by HDF5 / PnetCDF.
        # This could be exported from NetCDF's recipe in a cmake module or similar,
        # but the recipe would have to parse netcdf's generated cmake files, and,
        # it would be exported with the wrong case (netCDF_HAS_PARALLEL), so it is easier
        # to just guess here.
        tc.variables["NetCDF_HAS_PARALLEL"] = self.dependencies["hdf5"].options.parallel


        # There are LOTS of these modules now ...
        # for vtkModule in self.required_modules:
            # tc.variables["VTK_MODULE_ENABLE_VTK_" + vtkModule] = _yesno(True)

        # TODO support more modules - see notes above re hdf5
        # tc.variables["VTK_MODULE_ENABLE_VTK_hdf5"] = _yesno(True)

        # https://gitlab.kitware.com/vtk/vtk/-/blob/master/Documentation/dev/build.md
        # TODO try VTK_USE_VIDEO_FOR_WINDOWS   for video capture
        # TODO try VTK_USE_VIDEO_FOR_WINDOWS_CAPTURE   for video capture
        # TODO try VTK_USE_MICROSOFT_MEDIA_FOUNDATION   for video capture (MP4)


        # this little function only to help mark out the special
        # default/yes/no/want/dont_want options
        def _yesno(flag):
            return flag


        # groups can be:  DEFAULT   DONT_WANT   WANT   YES   NO
        # Note that YES is like WANT, but will show errors if can't make everything
        # NO is also more forceful than DONT_WANT
        # Default is DONT_WANT, let it auto-enable when required
        tc.variables["VTK_GROUP_ENABLE_Imaging"]    = _yesno(self.options.group_enable_Imaging)    # TODO test
        tc.variables["VTK_GROUP_ENABLE_MPI"]        = _yesno(self.options.group_enable_MPI)        # TODO test
        tc.variables["VTK_GROUP_ENABLE_Rendering"]  = _yesno(self.options.group_enable_Rendering)
        tc.variables["VTK_GROUP_ENABLE_StandAlone"] = _yesno(self.options.group_enable_StandAlone)  # TODO test
        tc.variables["VTK_GROUP_ENABLE_Views"]      = _yesno(self.options.group_enable_Views)       # TODO test
        tc.variables["VTK_GROUP_ENABLE_Web"]        = _yesno(self.options.group_enable_Web)         # TODO test

        # for Qt, can also use the more specific MODULE options below
        tc.variables["VTK_GROUP_ENABLE_Qt"] = _yesno(self.options.group_enable_Qt)

        ##### QT ######
        # QT has a few modules, we'll be specific
        tc.variables["VTK_QT_VERSION"]                          = self.options.qt_version
        tc.variables["VTK_MODULE_ENABLE_VTK_GUISupportQt"]      = _yesno(self.options.module_enable_GUISupportQt)
        tc.variables["VTK_MODULE_ENABLE_VTK_GUISupportQtQuick"] = _yesno(self.options.module_enable_GUISupportQtQuick)
        tc.variables["VTK_MODULE_ENABLE_VTK_GUISupportQtSQL"]   = _yesno(self.options.module_enable_GUISupportQtSQL)
        tc.variables["VTK_MODULE_ENABLE_VTK_RenderingQt"]       = _yesno(self.options.module_enable_RenderingQt)
        tc.variables["VTK_MODULE_ENABLE_VTK_ViewsQt"]           = _yesno(self.options.module_enable_ViewsQt)

        ### Other stuff ###

        # Modules
        tc.variables["VTK_MODULE_ENABLE_VTK_IOExport"]          = _yesno(self.options.module_enable_IOExport)
        tc.variables["VTK_MODULE_ENABLE_VTK_IOLegacy"]          = _yesno(self.options.module_enable_IOLegacy)
        tc.variables["VTK_MODULE_ENABLE_VTK_RenderingCore"]     = _yesno(self.options.module_enable_RenderingCore)
        tc.variables["VTK_MODULE_ENABLE_VTK_RenderingExternal"] = _yesno(self.options.module_enable_RenderingExternal)

        # Modules that aren't supported yet
        tc.variables["VTK_MODULE_ENABLE_VTK_IOPDAL"]            = _yesno(self.options.module_enable_IOPDAL)
        tc.variables["VTK_MODULE_ENABLE_VTK_IOPostgreSQL"]      = _yesno(self.options.module_enable_IOPostgreSQL)
        tc.variables["VTK_MODULE_ENABLE_VTK_IOOpenVDB"]         = _yesno(self.options.module_enable_IOOpenVDB)
        tc.variables["VTK_MODULE_ENABLE_VTK_IOLAS"]             = _yesno(self.options.module_enable_IOLAS)
        tc.variables["VTK_MODULE_ENABLE_VTK_IOADIOS2"]          = _yesno(self.options.module_enable_IOADIOS2)
        tc.variables["VTK_MODULE_ENABLE_VTK_fides"]             = _yesno(self.options.module_enable_fides)
        tc.variables["VTK_MODULE_ENABLE_VTK_GeovisGDAL"]        = _yesno(self.options.module_enable_GeovisGDAL)
        tc.variables["VTK_MODULE_ENABLE_VTK_IOGDAL"]            = _yesno(self.options.module_enable_IOGDAL)
        tc.variables["VTK_MODULE_ENABLE_VTK_FiltersOpenTURNS"]  = _yesno(self.options.module_enable_FiltersOpenTURNS)
        tc.variables["VTK_MODULE_ENABLE_VTK_DomainsMicroscopy"] = _yesno(self.options.module_enable_DomainsMicroscopy)
        tc.variables["VTK_MODULE_ENABLE_VTK_CommonArchive"]     = _yesno(self.options.module_enable_CommonArchive)

        # TODO if true (or all) then system has to install postgres dev package

        ##### SMP parallelism ####  Sequential  STDThread  OpenMP  TBB
        # Note that STDThread seems to be available by default
        tc.variables["VTK_SMP_IMPLEMENTATION_TYPE"] = self.options.smp_implementation_type
        # Change change the mode during runtime, if you enable the backends like so:
        tc.variables["VTK_SMP_ENABLE_Sequential"]   = self.options.smp_enable_Sequential
        tc.variables["VTK_SMP_ENABLE_STDThread"]    = self.options.smp_enable_STDThread
        tc.variables["VTK_SMP_ENABLE_OpenMP"]       = self.options.smp_enable_OpenMP
        tc.variables["VTK_SMP_ENABLE_TBB"]          = self.options.smp_enable_TBB

        #### Use the Internal VTK bundled libraries for these Third Party dependencies ...
        # Ask VTK to use their bundled versions for these:
        # These are missing in CCI, could probably use if they become available.
        # Note that we may need to use bundled versions if they are heavily patched.
        missing_from_cci = [
                "diy2",
                "exodusII",
                "fides",
                "gl2ps",
                "h5part",
                "ioss",
                "mpi4py",
                "pegtl",
                "verdict",
                "vpic",
                "vtkm",
                "xdmf2",
                "xdmf3",
                ]

        for lib in missing_from_cci:
            tc.variables["VTK_MODULE_USE_EXTERNAL_VTK_" + lib] = False

        # Everything else should come from conan.
        # TODO check if anything is coming from the system CMake,
        # and change it to conan or add as a build_requirement for the system to install.
        # SOME of VTK's bundled Third Party libs are heavily forked and patched, so system versions may
        # not be appropriate to use externally.
        tc.variables["VTK_USE_EXTERNAL"] = True

        # TODO these dependencies modules aren't available in CCI or internally
        # this one was used for RenderingRayTracing
        tc.variables["VTK_ENABLE_OSPRAY"] = False

        deps = CMakeDeps(self)
        #
        # VTK expected different finder filenames and targets (check ThirdParty/LIB/CMakeLists.txt)
        # We adjust here so VTK will find our Finders.
        #
        # netcdf is netCDF, but VTK expected NetCDF
        deps.set_property("netcdf", "cmake_file_name", "NetCDF")
        deps.set_property("netcdf", "cmake_target_name", "NetCDF::NetCDF")
        #
        # eigen's target is Eigen3::Eigen, but VTK expected Eigen3::Eigen3
        deps.set_property("eigen", "cmake_target_name", "Eigen3::Eigen3")
        #
        # lz4 is lz4, but VTK expected LZ4
        deps.set_property("lz4", "cmake_file_name", "LZ4")
        deps.set_property("lz4", "cmake_target_name", "LZ4::LZ4")
        #
        # lzma is LibLZMA, but VTK expected LZMA
        deps.set_property("xz_utils", "cmake_file_name", "LZMA")
        deps.set_property("xz_utils", "cmake_target_name", "LZMA::LZMA")
        #
        # utfcpp's target is utf8cpp, but VTK expected utf8cpp::utf8cpp
        deps.set_property("utfcpp", "cmake_target_name", "utf8cpp::utf8cpp")
        #
        # freetype is freetype, but VTK expected Freetype and Freetype::Freetype
        deps.set_property("freetype", "cmake_file_name", "Freetype")
        deps.set_property("freetype", "cmake_target_name", "Freetype::Freetype")
        #
        # expat is expat, but VTK expected EXPAT and EXPAT::EXPAT
        deps.set_property("expat", "cmake_file_name", "EXPAT")
        deps.set_property("expat", "cmake_target_name", "EXPAT::EXPAT")
        #
        # libharu is libharu, but VTK expected LibHaru and LibHaru::LibHaru
        deps.set_property("libharu", "cmake_file_name", "LibHaru")
        deps.set_property("libharu", "cmake_target_name", "LibHaru::LibHaru")
        #
        # openvr is openvr, but VTK expected OpenVR and OpenVR::OpenVR
        deps.set_property("openvr", "cmake_file_name", "OpenVR")
        deps.set_property("openvr", "cmake_target_name", "OpenVR::OpenVR")
        #
        # exprtk is exprtk, but VTK expected ExprTk and ExprTk::ExprTk
        deps.set_property("exprtk", "cmake_file_name", "ExprTk")
        deps.set_property("exprtk", "cmake_target_name", "ExprTk::ExprTk")
        #
        # theora is theora ::theora ::theoradec ::theoraenc,
        # but VTK wants THEORA ::THEORA ::DEC ::ENC
        deps.set_property("theora", "cmake_file_name", "THEORA")
        deps.set_property("theora", "cmake_target_name", "THEORA::THEORA")
        deps.set_property("theora::theoradec", "cmake_target_name", "THEORA::DEC")
        deps.set_property("theora::theoraenc", "cmake_target_name", "THEORA::ENC")
        #
        # proj is proj and PROJ::proj, but VTK wants LibPROJ and LibPROJ::LibPROJ
        deps.set_property("proj", "cmake_file_name", "LibPROJ")
        deps.set_property("proj", "cmake_target_name", "LibPROJ::LibPROJ")
        # VTK also wants a variable LibPROJ_MAJOR_VERSION, which conan has as proj_VERSION_MAJOR
        tc.variables["LibPROJ_MAJOR_VERSION"] = Version(self.dependencies["proj"].ref.version).major
        #
        # double-version has their headers in <double-conversion/header>
        # but VTK expects just <header>
        self.dependencies["double-conversion"].cpp_info.includedirs[0] = os.path.join(self.dependencies["double-conversion"].cpp_info.includedirs[0], "double-conversion")
        ###

        tc.generate()
        deps.generate()


    def build(self):
        apply_conandata_patches(self)

        if self.options.wrap_python and self.settings.build_type == "Debug" and self.settings.os == "Windows":
            # This is specifically for Python < 3.8
            # Building VTK in Debug, on Windows, with Python < 3.8,
            #  ... while linking to the standard release python libraries.
            # Then you need this hack so the API/ABI that VTK expects will match the Release ABI.
            # ie: comment out Py_DEBUG from pyconfig.h - described here - https://stackoverflow.com/a/40594968
            # And then put a copy of pythonVER_d.lib in a spot where it can be found by the linker...
            # but it doesn't get found for some reason (experienced by EricAtORS)
            python_lib_folder = os.path.realpath(os.path.join(which("python"), "..", "libs")).replace("\\", "/")
            replace_in_file(self, os.path.join(self.build_folder,"..", "..", "src", "CMakeLists.txt"),
                                  "project(VTK)",
                                  'project(VTK)\nlink_directories("{}")\n'.format(python_lib_folder)
                                  )

        cmake = CMake(self)
        cmake.configure()
        cmake.build()


    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "vtk", f"conan-official-{self.name}-variables.cmake")


    def package(self):
        cmake = CMake(self)
        cmake.install()

        # VTK installs the licenses under the share/licenses/VTK directory, move it
        rename( self, os.path.join(self.package_folder,"share","licenses","VTK"),
                os.path.join(self.package_folder,"licenses"))

        rmdir(self, os.path.join(self.package_folder,"share","licenses"))
        rmdir(self, os.path.join(self.package_folder,"share"))

        # keep copy of generated VTK cmake files, for inspection
        if _debug_packaging:
            rename( self, os.path.join(self.package_folder,"lib","cmake"),
                    os.path.join(self.package_folder,"vtk-cmake-backup"))
        else:
            # delete VTK-installed cmake files
            rmdir(self, os.path.join(self.package_folder,"lib","cmake"))

        # make a copy of the modules.json, we use that in package_info
        # TODO where should this file live?  perhaps just in the base package folder?
        copy(self, pattern="modules.json",
                dst=os.path.join(self.package_folder,"lib","conan"),
                src=self.build_folder,
                keep_path=False
                )

        # create a cmake file with our special variables
        content = textwrap.dedent(f"""\
                set (VTK_ENABLE_KITS {self.options.enable_kits})
                """
                )
        if self.settings.os == "Windows" and self.options.wrap_python:
            rename(self,
                   os.path.join(self.package_folder, "bin", "Lib", "site-packages"),
                   os.path.join(self.package_folder, "lib", "site-packages")
            )
        save(self, os.path.join(self.package_folder, self._module_file_rel_path), content)


    def package_info(self):
        # auto-include these .cmake files (generated by conan)
        vtk_cmake_build_modules = [self._module_file_rel_path]
        self.cpp_info.names["cmake_find_package"] = "VTK"
        self.cpp_info.names["cmake_find_package_multi"] = "VTK"
        self.cpp_info.set_property("cmake_file_name", "VTK")
        self.cpp_info.set_property("cmake_target_name", "VTK::VTK")

        self.cpp_info.builddirs = [os.path.join("lib", "cmake", "vtk")]
        self.cpp_info.set_property("cmake_build_modules", vtk_cmake_build_modules)

        # FIXME Should not be added to the VTK::VTK target... right?
        # self.cpp_info.libdirs   = ["lib"]

        existing_libs = collect_libs(self, folder="lib")

        # Specify what VTK 3rd party targets we are supplying with conan packages
        # Note that we aren't using cmake_package::cmake_component here, this is for conan so we use conan package names.
        thirds = {
                # Format for this map:
                # "VTK::module": "conan_package::conan_package",      # if the whole package required
                # "VTK::module": "conan_package::package_component",  # if subcomponent required
                "VTK::eigen":    "eigen::eigen",
                "VTK::exprtk":   "exprtk::exprtk",
                "VTK::expat":    "expat::expat",
                "VTK::glew":     "glew::glew",
                "VTK::fmt":      "fmt::fmt",
                "VTK::freetype": "freetype::freetype",
                "VTK::jsoncpp":  "jsoncpp::jsoncpp",
                "VTK::libharu":  "libharu::libharu",
                "VTK::libproj":  "proj::proj",
                "VTK::lz4":      "lz4::lz4",
                "VTK::lzma":     "xz_utils::xz_utils",
                "VTK::png":      "libpng::libpng",
                "VTK::pugixml":  "pugixml::pugixml",
                "VTK::tiff":     "libtiff::libtiff",
                "VTK::utf8":     "utfcpp::utfcpp",
                "VTK::zlib":     "zlib::zlib",
                "VTK::doubleconversion": "double-conversion::double-conversion",

                # VTK::QtOpenGL doesn't currently exist in VTK, I have added this.
                # Note that the component name is qt::qtOpenGL, different to CMake's target name
                "VTK::QtOpenGL": "qt::qtOpenGL",
                }

        if self.options.with_jpeg == "libjpeg":
            thirds["VTK::jpeg"] = "libjpeg::libjpeg"
        elif self.options.with_jpeg == "libjpeg-turbo":
            thirds["VTK::jpeg"] = "libjpeg-turbo::jpeg"

        if self._is_module_enabled([self.options.group_enable_Rendering]):
            thirds["VTK::opengl"] = "opengl::opengl"    # TODO can we always leave this in the thirds list?

        # parse the modules.json file and generate a list of components
        modfile = load(self, os.path.join(self.package_folder,"lib","conan","modules.json"))
        vtkmods = json.loads(modfile)

        if self._is_any_Qt_enabled:
            # VTK::QtOpenGL doesn't currently exist in VTK, I have added this.
            # Check it doesn't appear in the future, if so then we should check it out.
            if "VTK::QtOpenGL" in vtkmods["modules"]:
                raise ConanException("Did not expect to find VTK::QtOpenGL in modules.json - please investigate and adjust recipe")
            vtkmods["modules"]["VTK::QtOpenGL"] = {
                    "library_name": "EXTERNAL_LIB",
                    "depends": [],
                    "private_depends": [],
                    }
            # GUISupportQt requires Qt6::QtOpenGL as a dependency
            vtkmods["modules"]["VTK::GUISupportQt"]["depends"].append("VTK::QtOpenGL")

        self.output.info("All module keys: {}".format(vtkmods["modules"].keys()))

        self.output.info(f"Found libs: {existing_libs}")
        self.output.info("Processing modules")
        for module_name in vtkmods["modules"]:
            comp = module_name.split(':')[2]
            comp_libname = vtkmods["modules"][module_name]["library_name"] + self._lib_suffix

            if comp_libname in existing_libs:
                self.output.info(f"Processing module {module_name}")
                self.cpp_info.components[comp].set_property("cmake_target_name", module_name)
                self.cpp_info.components[comp].libs         = [comp_libname]
                self.cpp_info.components[comp].include_dirs = ["include/vtk"]
                self.cpp_info.components[comp].names["cmake_find_package"] = comp
                self.cpp_info.components[comp].names["cmake_find_package_multi"] = comp
                # not sure how to be more specific here, the modules.json doesn't specify which other modules are required
            elif module_name in thirds:
                self.output.info("Processing external module {} --> {}".format(module_name, thirds[module_name]))
                self.cpp_info.components[comp].set_property("cmake_target_name", module_name)
                self.cpp_info.components[comp].requires.append(thirds[module_name])
            else:
                self.output.warning(f"Skipping module (lib file does not exist) {module_name}")

        # second loop for internal dependencies
        for module_name in vtkmods["modules"]:
            comp = module_name.split(':')[2]
            if comp in self.cpp_info.components:

                # always depend on the headers mini-module
                # which also includes the cmake extra file definitions (declared afterwards)
                self.cpp_info.components[comp].requires.append("headers")

                # these are the public depends + private depends
                # FIXME should private be added as a different kind of private-requires?
                for section in ["depends", "private_depends"]:
                    for dep in vtkmods["modules"][module_name][section]:
                        dep_libname = vtkmods["modules"][dep]["library_name"] + self._lib_suffix
                        if dep_libname in existing_libs:
                            depname = dep.split(':')[2]
                            self.output.info(f"{comp}   depends on {depname}")
                            self.cpp_info.components[comp].requires.append(depname)
                        elif dep in thirds:
                            extern = thirds[dep]
                            self.output.info(f"{comp}   depends on external {dep} --> {extern}")
                            self.cpp_info.components[comp].requires.append(extern)
                        else:
                            self.output.info(f"{comp}   skipping depends (lib file does not exist): {dep}")

                # DEBUG # self.output.info("  Final deps: {}".format(self.cpp_info.components[comp].requires))

                self.cpp_info.components[comp].set_property("cmake_build_modules", vtk_cmake_build_modules)
                if self.settings.os in ("FreeBSD", "Linux"):
                    self.cpp_info.components[comp].system_libs.extend(["dl","pthread","m"])
            else:
                self.output.warning(f"Skipping module, did not become a component: {module_name}")


        # add some more system libs
        if self.settings.os == "Windows" and "vtksys" in self.cpp_info.components:
            self.cpp_info.components["vtksys"].system_libs = ["ws2_32", "dbghelp", "psapi"]

        # All modules use the same include dir.
        #
        # Cannot just be vtk_include_dirs = "include",
        # as vtk files include themselves with #include <vtkCommand.h>
        # and the files can't find each other in the same dir when included with <>
        #
        # Plus, it is standard to include vtk files with #include <vtkWhatever.h>
        #
        # Note also we aren't using "-9" in include/vtk-9: VTK_VERSIONED_INSTALL=False
        # With versioned_install, we would do: "include/vtk-%s" % self.short_version,
        #

        # mini component just for the headers and the cmake build modules
        self.cpp_info.components["headers"].set_property("cmake_target_name", "headers")
        self.cpp_info.components["headers"].includedirs = [os.path.join("include", "vtk")]
        self.cpp_info.components["headers"].set_property("cmake_build_modules", vtk_cmake_build_modules)
