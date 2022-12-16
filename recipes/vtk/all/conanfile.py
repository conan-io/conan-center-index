# TODO LIST
# - Make cmake a build requirement for conan-CI to work
# - Why are cmake_wrapper cmake files being deployed?
# - How can I utilise VTK's built-in cmake module dependency system, rather than recreate it here?
# - 3rd party deps are required for different enabled module configurations, how to take that info out of VTK's module system?
# - patching with src in local folder seems to fail - export_sources_folder = None?
# - use build/modules.json to compute the components and dependencies
#
# - how do i make one component depend on another (in cpp_info), ie i'm attaching the custom-cmake-module to all of the components, but technically it should only be connected to the "common" one.
#   BUT, logically it is a bit weird, because WHICH "common" module (VTK::Common or VTK::CommonCore) depends on VTK_ENABLE_KITS,
#   which is what i'm trying to attach and export.
# So I need some kind of general component that the user could import, to determine which modules they further need to import?
#
# freetype_MAJOR_VERSION or whatever it was... proj?
# SpaceIm: CMakeDeps creates a config version file for each dependency, so if find_package(<package>) is resolved, it will define <package>_VERSION

# RECIPE MAINTAINER NOTES:
# - Read vtk's Documentation/release/9.1.md for important notes about versions and forks
# - Also read vtk's Documentation/build.md for information about build settings and flags
# - Modify build_requirements() to match the version of CMake that VTK tested with that release.

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.build import check_min_cppstd
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir, save, rename, collect_libs, load
from conan.tools.scm import Version

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
    no_copy_source = False

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
            "group_enable_StandAlone": ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "group_enable_Views":      ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "group_enable_Web":        ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],

            # Qt-specific modules
            "qt_version": ["Auto", "5", "6"],
            "module_enable_GUISupportQt":      ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "module_enable_GUISupportQtQuick": ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "module_enable_GUISupportQtSQL":   ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "module_enable_RenderingQt":       ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "module_enable_ViewsQt":           ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],

            # TODO modules that require extra stuff to be installed
            "module_IOPDAL":            ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "module_IOPostgreSQL":      ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "module_IOOpenVDB":         ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "module_IOLAS":             ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "module_IOADIOS2":          ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "module_fides":             ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "module_GeovisGDAL":        ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "module_IOGDAL":            ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "module_FiltersOpenTURNS":  ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "module_DomainsMicroscopy": ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
            "module_CommonArchive":     ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"],
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

            # Note: parallel MPI support should be also applied to hdf5 and cgns

            # HDF5 is expected to have "parallel" enabled
            # "hdf5:parallel":   True,
            # "hdf5:enable_cxx": False,  # can't be enabled with parallel

            # these aren't supported yet, need to system-install packages
            "module_IOPDAL":            "NO",
            "module_IOPostgreSQL":      "NO",
            "module_IOOpenVDB":         "NO",
            "module_IOLAS":             "NO",
            "module_IOADIOS2":          "NO",
            "module_fides":             "NO",
            "module_GeovisGDAL":        "NO",
            "module_IOGDAL":            "NO",
            "module_FiltersOpenTURNS":  "NO",
            "module_DomainsMicroscopy": "NO",
            "module_CommonArchive":     "NO",

            # kissfft - we want the double format (also known as kiss_fft_scalar)
            # FIXME should this be in configure/validate? I recall it was required for some reason...
            "kissfft:datatype": "double",
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


    def _patch_source(self):
        # Note that VTK's cmake will insert its own CMAKE_MODULE_PATH at the
        # front of the list.  This is ok as long as there is nothing in that
        # path that will be found before our conan cmake files...
        # That is why we delete the third party finders.
        # Else, we have to patch VTK's CMakeLists.txt, like so:
        #####
        # diff --git a/CMakeLists.txt b/CMakeLists.txt
        # index c15890cfdc..022f704d75 100644
        # --- a/CMakeLists.txt
        # +++ b/CMakeLists.txt
        # @@ -7,7 +7,7 @@ if (POLICY CMP0127)
        #  endif ()
        #
        #  set(vtk_cmake_dir "${VTK_SOURCE_DIR}/CMake")
        # -list(INSERT CMAKE_MODULE_PATH 0 "${vtk_cmake_dir}")
        # +list(APPEND CMAKE_MODULE_PATH "${vtk_cmake_dir}")
        #####

        # DELETE any of the third party finders, before we build - see note above
# ALLOW FINDERS #        rm(self, "Find*.cmake", os.path.join(self.source_folder,"CMake"))

        # Delete VTK's cmake patches (these support older cmake programs).
        # We do not have to support old cmake: we require an updated cmake instead.
# ALLOW FINDERS #        if _support_old_ci_20220514:
# ALLOW FINDERS #            rmdir(self, os.path.join(self.source_folder,"CMake","patches"))
# ALLOW FINDERS #        else:
# ALLOW FINDERS #            rmdir(self, os.path.join(self.source_folder,"CMake","patches"))

        # And apply our patches.  I do it here rather than in build, so I can repeatedly call build without applying patches.
        apply_conandata_patches(self)


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

        if self.no_copy_source:
            self._patch_source()


    def _third_party(self):
        parties = {
                # LEFT field:  target name for linking, will be used as TARGET::TARGET in package_info()
                # RIGHT field: package/version to require
                "cli11":             "cli11/2.2.0",
                "double-conversion": "double-conversion/3.2.0",
                "eigen":             "eigen/3.4.0",
                "expat":             "expat/2.4.8",
                "exprtk":            "exprtk/0.0.1",
                "fmt":               "fmt/8.1.1",      # 9.1.0 release docs mention a PR - confirmed merged 8.1.0
                "freetype":          "freetype/2.12.1",
                "glew":              "glew/2.2.0",
                "jsoncpp":           "jsoncpp/1.9.5",
                "libharu":           "libharu/2.4.3",
                "kissfft":           "kissfft/131.1.0",
                "lz4":               "lz4/1.9.3",
                "libpng":            "libpng/1.6.37",
                "proj":              "proj/9.0.1", # if MAJOR version changes, update ThirdParty/libproj/CMakeLists.txt
                "pugixml":           "pugixml/1.12.1",
                "sqlite3":           "sqlite3/3.38.5",
                "utfcpp":            "utfcpp/3.2.1",
                "xz_utils":          "xz_utils/5.2.5", # note: VTK calls this lzma
                "zlib":              "zlib/1.2.12",
                "TIFF":              "libtiff/4.3.0",
                }

        if self.options.with_jpeg == "libjpeg":
            parties["jpeg"] = "libjpeg/9e"
        elif self.options.with_jpeg == "libjpeg-turbo":
            parties["jpeg"] = "libjpeg-turbo/2.1.2"


        if self._is_module_enabled([self.options.group_enable_StandAlone]):
            parties["hdf5"]    = "hdf5/1.13.1"
            parties["theora"]  = "theora/1.1.1"
            parties["ogg"]     = "ogg/1.3.5"
            parties["netcdf"]  = "netcdf/4.8.1"
            parties["libxml2"] = "libxml2/2.9.14"
            parties["cgns"]    = "cgns/4.3.0"

        # unused
        if False:
            parties["zfp"]     = "zfp/0.5.5"

        if self.options.build_all_modules:
            parties["boost"]  = "boost/1.79.0"
            parties["openvr"] = "openvr/1.16.8"
            parties["odbc"]   = "odbc/2.3.9"

        if self._is_any_Qt_enabled:
            parties["qt"] = "qt/6.3.1"

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
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )

        if not self.options.shared and self.options.enable_kits:
            raise ConanInvalidConfiguration("KITS can only be enabled with shared")

        if self._is_module_enabled([self.options.group_enable_Web]) and not self.options.wrap_python:
            raise ConanInvalidConfiguration("group_enable_Web can only be enabled with wrap_python")

        if self.options.wrap_python and not self.options.enable_wrapping:
            raise ConanInvalidConfiguration("wrap_python can only be enabled with enable_wrapping")

        if self.options.wrap_java and not self.options.enable_wrapping:
            raise ConanInvalidConfiguration("wrap_java can only be enabled with enable_wrapping")

        if self.options.use_tk and not self.options.wrap_python:
            raise ConanInvalidConfiguration("use_tk can only be enabled with wrap_python")

        if self.dependencies["libtiff"].options.jpeg != self.info.options.with_jpeg:
            raise ConanInvalidConfiguration(f"{self.ref} requires option value {self.name}:with_jpeg equal to libtiff:jpeg.")

        if self.dependencies["pugixml"].options.wchar_mode:
            raise ConanInvalidConfiguration(f"{self.ref} requires pugixml:wchar_mode=False")


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
            "clang": "7",
            "apple-clang": "11",
        }

        # TODO for debugging weird behaviour on mac on CCI
        #if str(self.settings.compiler) != "apple-clang":
            #raise ConanInvalidConfiguration("Not building, just want to focus on apple-clang for now")


    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.options["libtiff"].jpeg = self.options.with_jpeg


    def layout(self):
        cmake_layout(self, src_folder="src")
        # WTF resdirs # self.cpp.package.resdirs = ["res"]


    def generate(self):
        tc = CMakeToolchain(self)

        # for debugging the conan recipe
        # tc.variables["CMAKE_FIND_DEBUG_MODE"] = True

        # 64 / 32 bit IDs
        if self.options.use_64bit_ids != "Auto":
            tc.variables["VTK_USE_64BIT_IDS"] = self.options.use_64bit_ids

        # Be sure to set this, otherwise vtkCompilerChecks.cmake will downgrade our CXX standard to 11
        tc.variables["VTK_IGNORE_CMAKE_CXX11_CHECKS"] = True


        # no need for versions on installed names?
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
        tc.variables["VTK_USE_TK"] = self.options.use_tk    # requires wrap_python


        #### CUDA / MPI / MEMKIND ####
        tc.variables["VTK_USE_CUDA"]    = self.options.use_cuda
        tc.variables["VTK_USE_MEMKIND"] = self.options.use_memkind
        tc.variables["VTK_USE_MPI"]     = self.options.use_mpi


        ### Modules ###
        tc.variables["VTK_BUILD_ALL_MODULES"] = self.options.build_all_modules

        tc.variables["VTK_ENABLE_REMOTE_MODULES"] = self.options.enable_remote_modules


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
        tc.variables["VTK_MODULE_ENABLE_VTK_IOPDAL"]            = _yesno(self.options.module_IOPDAL)
        tc.variables["VTK_MODULE_ENABLE_VTK_IOPostgreSQL"]      = _yesno(self.options.module_IOPostgreSQL)
        tc.variables["VTK_MODULE_ENABLE_VTK_IOOpenVDB"]         = _yesno(self.options.module_IOOpenVDB)
        tc.variables["VTK_MODULE_ENABLE_VTK_IOLAS"]             = _yesno(self.options.module_IOLAS)
        tc.variables["VTK_MODULE_ENABLE_VTK_IOADIOS2"]          = _yesno(self.options.module_IOADIOS2)
        tc.variables["VTK_MODULE_ENABLE_VTK_fides"]             = _yesno(self.options.module_fides)
        tc.variables["VTK_MODULE_ENABLE_VTK_GeovisGDAL"]        = _yesno(self.options.module_GeovisGDAL)
        tc.variables["VTK_MODULE_ENABLE_VTK_IOGDAL"]            = _yesno(self.options.module_IOGDAL)
        tc.variables["VTK_MODULE_ENABLE_VTK_FiltersOpenTURNS"]  = _yesno(self.options.module_FiltersOpenTURNS)
        tc.variables["VTK_MODULE_ENABLE_VTK_DomainsMicroscopy"] = _yesno(self.options.module_DomainsMicroscopy)
        tc.variables["VTK_MODULE_ENABLE_VTK_CommonArchive"]     = _yesno(self.options.module_CommonArchive)
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

        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()


    def build(self):
        if not self.no_copy_source:
            self._patch_source()

        # RunEnvironment needed to build shared version with ALL modules
        # Still needed with 1.53.0 ? # env_build = RunEnvironment(self)
        # Still needed with 1.53.0 ? # with environment_append(env_build.vars):
        cmake = CMake(self)
            # Still needed with 1.53.0 ? # cmake.configure(build_script_folder=self.source_folder)
        cmake.configure()
        cmake.build()


    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "vtk", "conan-official-{}-variables.cmake".format(self.name))


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
        save(self, os.path.join(self.package_folder, self._module_file_rel_path), content)


    def package_info(self):
        # Note: I don't currently import the explicit dependency list for each component from VTK,
        # so every module will depend on "everything" external, and there are no internal dependencies.
        # Consumers just have to figure out what they have to link.

        # get keys as a list and make a list of target::target
        all_requires = [k + "::" + k for k in self._third_party().keys()]

        if self._is_module_enabled([self.options.group_enable_Rendering]):
            all_requires += [ "opengl::opengl" ]
            if self.settings.os in ["Linux", "FreeBSD"]:
                all_requires += [ "xorg::xorg" ]
        all_requires.sort()


        # auto-include these .cmake files (generated by conan)
        vtk_cmake_build_modules = [self._module_file_rel_path]


        # Just generate 'config' version, FindVTK.cmake hasn't existed since CMake 3.1, according to:
        # https://cmake.org/cmake/help/latest/module/FindVTK.html

        self.cpp_info.set_property("cmake_file_name", "VTK")
        self.cpp_info.set_property("cmake_target_name", "VTK::VTK")

        self.cpp_info.builddirs = [os.path.join("lib", "cmake", "vtk")]
        self.cpp_info.set_property("cmake_build_modules", vtk_cmake_build_modules)

        # Should not be added to the VTK::VTK target... right?
        # self.cpp_info.libdirs   = ["lib"]

        existing_libs = collect_libs(self, folder="lib")

        if False:
            # old way - work from the list of library files and build a component list
            # does not handle internal module dependencies.
            for libname in existing_libs:
                comp = libname[3:]
                self.cpp_info.components[comp].set_property("cmake_target_name", "VTK::" + comp)
                self.cpp_info.components[comp].libs          = ["vtk" + comp]
                # NEEDED with 1.53? # self.cpp_info.components[comp].libdirs       = ["lib"]
                # NEEDED with 1.53? # # WTF resdirs # self.cpp_info.components[comp].resdirs       = ["res"]
                self.cpp_info.components[comp].requires      = all_requires
                self.cpp_info.components[comp].set_property("cmake_build_modules", vtk_cmake_build_modules)
                if self.settings.os in ("FreeBSD", "Linux"):
                    self.cpp_info.system_libs.extend(["dl","pthread","m"])

        else:
            # Specify what VTK 3rd party targets we are supplying with conan packages
            # Note that we aren't using cmake_package::cmake_component here, this is for conan so we use conan package names.
            thirds = {
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

            # TODO check out abseil recipe, it parses the generated cmake-targets file for extra info.

            # new way - parse the modules.json file and generate a list of components
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
                comp_libname = vtkmods["modules"][module_name]["library_name"]

                if comp_libname in existing_libs:
                    self.output.info(f"Processing module {module_name}")
                    self.cpp_info.components[comp].set_property("cmake_target_name", module_name)
                    self.cpp_info.components[comp].libs          = [comp_libname]
                    # NEEDED with 1.53? # self.cpp_info.components[comp].libdirs       = ["lib"]
                    # NEEDED with 1.53? # # WTF resdirs # self.cpp_info.components[comp].resdirs       = ["res"]

                    # not sure how to be more specific here, the modules.json doesn't specify which other modules are required
                elif module_name in thirds:
                    self.output.info("Processing external module {} --> {}".format(module_name, thirds[module_name]))
                    self.cpp_info.components[comp].set_property("cmake_target_name", module_name)
                    self.cpp_info.components[comp].requires.append(thirds[module_name])

                else:
                    self.output.warning(f"Skipping module (lib file does not exist) {module_name}")

                # this is how we used to add ALL the requires at once
                # self.cpp_info.components[comp].requires      = all_requires.copy() # else, []

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
                            dep_libname = vtkmods["modules"][dep]["library_name"]
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
                    self.output.warning("Skipping module, did not become a component: {}".format(module_name))


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
