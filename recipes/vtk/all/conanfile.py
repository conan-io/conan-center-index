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

import os
import textwrap
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import apply_conandata_patches
from conan.tools.system.package_manager import Apt

# TODO upgrade to new conan.* imports
from conans import RunEnvironment
from conans.errors import ConanInvalidConfiguration
from conans.tools import get, remove_files_by_mask, save, rmdir, rename, collect_libs, check_min_cppstd, Version, environment_append, load

# for auto-component generation
import json

# Enable to keep VTK-generated cmake files, to check contents
_debug_packaging = False


class VtkConan(ConanFile):
    name = "vtk"
    settings = "os", "compiler", "build_type", "arch"
    description = "The Visualization Toolkit (VTK) by Kitware is an open-source, \
        freely available software system for 3D computer graphics, \
        image processing, and visualization."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.vtk.org/"
    license = "BSD-3-Clause"
    topics = ("vtk", "scientific", "image", "processing", "visualization")

    short_paths = True
    no_copy_source = False

    generators = "CMakeDeps"

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
    # jpeg:             conan (I'm trying libjpeg-turbo)
    # jsoncpp:          conan (jsoncpp)
    # kissfft:          conan (kissfft)
    # libharu:          VTK (heavily patched)
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

            "use_source_from_git": [True, False],

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

            "use_source_from_git": False, # False = use the tarball

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
            "kissfft:datatype": "double",
            }


    @property
    def _source_subfolder(self):
        return "source_subfolder"



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
# ALLOW FINDERS #        remove_files_by_mask(os.path.join(self._source_subfolder,"CMake"), "Find*.cmake")

        # Delete VTK's cmake patches (these support older cmake programs).
        # We do not have to support old cmake: we require an updated cmake instead.
# ALLOW FINDERS #        if _support_old_ci_20220514:
# ALLOW FINDERS #            rmdir(os.path.join(self._source_subfolder,"CMake","patches"))
# ALLOW FINDERS #        else:
# ALLOW FINDERS #            rmdir(self, os.path.join(self._source_subfolder,"CMake","patches"))

        # And apply our patches.  I do it here rather than in build, so I can repeatedly call build without applying patches.
        apply_conandata_patches(self)



    def source(self):
        if self.options.use_source_from_git:
            self.run("git clone -b release --single-branch " + self.git_url + " " + self._source_subfolder)
            # note: we give the branch a name so we don't have detached heads
            # TODO change to standard git and python chdir
            git_hash = "v" + self.version
            self.run("cd " + self._source_subfolder + " && git checkout -b branch-" + git_hash + " " + git_hash)
        else:
            get(**self.conan_data["sources"][self.version],
                    strip_root=True,
                    destination=self._source_subfolder)

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
                # "libharu": "libharu/2.3.0", -- use VTK's bundled version - heavily patched
                "kissfft":           "kissfft/131.1.0",
                "lz4":               "lz4/1.9.3",
                "libpng":            "libpng/1.6.37",
                "proj":              "proj/9.0.1", # if MAJOR version changes, update ThirdParty/libproj/CMakeLists.txt
                "pugixml":           "pugixml/1.12.1",
                "sqlite3":           "sqlite3/3.38.5",
                "utfcpp":            "utfcpp/3.2.1",
                "xz_utils":          "xz_utils/5.2.5", # note: VTK calls this lzma
                "zlib":              "zlib/1.2.12",
                "jpeg":              "libjpeg-turbo/2.1.2",
                "TIFF":              "libtiff/4.3.0",
                }

        if (self.options.build_all_modules
                or self.options.group_enable_StandAlone):
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

        if (self.options.build_all_modules
                or self.options.group_enable_Qt
                or self.options.module_enable_GUISupportQt
                or self.options.module_enable_GUISupportQtQuick
                or self.options.module_enable_GUISupportQtSQL
                or self.options.module_enable_RenderingQt
                or self.options.module_enable_ViewsQt):
            parties["qt"] = "qt/6.2.4"

            # NOTE: could also try QT's offical QT
            # self.requires("qtbase/6.2.4@qt/everywhere")

        return parties


    def requirements(self):
        if self.options.group_enable_Rendering:
            self.requires("opengl/system")
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.requires("xorg/system")

        for pack in self._third_party().values():
            self.requires(pack)

        # Cmake requires an older openssl than libcurl, so override here
        # We don't need openssl on windows. Shouldn't need this line at all.
        if self.settings.os != "Windows":
            self.requires("openssl/1.1.1o", override=True)

        # HACK TODO working around a dependency bug in conan
        self.requires("cmake/3.23.2")


    def build_requirements(self):
        # Recipe Maintainers:
        # Check the CMake/patches folder, and use the most recent cmake
        # that matches the largest major version in the list.
        # That should be the last cmake that was tested by VTK.
        # Also adjust our CMakeLists.txt to match this number.
        # TODO automate this?  Put this version number in conandata.yml?

        # Note that 3.22.4 may have been the last version that Kitware tested, so we'll use that.
        # Should be ok to use the latest CMake always though...
        # TODO SHOULD BE HERE, but doesn't work
        # self.tool_requires("cmake/3.22.4")
        pass

    def validate(self):
        if not self.options.shared and self.options.enable_kits:
            raise ConanInvalidConfiguration("KITS can only be enabled with shared")

        if ((self.options.group_enable_Web == "WANT"
            or self.options.group_enable_Web == "YES")
            and not self.options.wrap_python):
            raise ConanInvalidConfiguration("group_enable_Web can only be enabled with wrap_python")

        if self.options.wrap_python and not self.options.enable_wrapping:
            raise ConanInvalidConfiguration("wrap_python can only be enabled with enable_wrapping")

        if self.options.wrap_java and not self.options.enable_wrapping:
            raise ConanInvalidConfiguration("wrap_java can only be enabled with enable_wrapping")

        if self.options.use_tk and not self.options.wrap_python:
            raise ConanInvalidConfiguration("use_tk can only be enabled with wrap_python")


    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC


    def _ensure_cpp17(self):
        compilers_minimum_version = {
                "gcc": "9",
                "Visual Studio": "15.7",
                "clang": "7",
                "apple-clang": "11",
            }

        # TODO for debugging weird behaviour on mac on CCI
        #if str(self.settings.compiler) != "apple-clang":
            #raise ConanInvalidConfiguration("Not building, just want to focus on apple-clang for now")

        # VTK needs C++17 to compile
        # This code was copied from p-ranav-glob
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 17)
        minimum_version = compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("{} requires C++17, which your compiler does not support.".format(self.name))
        else:
            self.output.warn("{} requires C++17. Your compiler is unknown. Assuming it supports C++17.".format(self.name))




    def configure(self):
        self._ensure_cpp17()
        if self.options.shared:
            del self.options.fPIC


    def layout(self):
        cmake_layout(self)


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
        #
        # VTK uses a heavily-forked version they call 2.4.0.  Upstream libharu is currently unmaintained.
        tc.variables["VTK_MODULE_USE_EXTERNAL_VTK_libharu"] = False


        # these are missing in CCI, could probably use if they become available
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
        # not be appropriate to use externally (like libharu).
        tc.variables["VTK_USE_EXTERNAL"] = True


        # TODO these dependencies modules aren't available in CCI or internally
        # this one was used for RenderingRayTracing
        tc.variables["VTK_ENABLE_OSPRAY"] = False


        tc.generate()


    def build(self):
        if not self.no_copy_source:
            self._patch_source()

        # RunEnvironment needed to build shared version with ALL modules
        env_build = RunEnvironment(self)
        with environment_append(env_build.vars):
            cmake = CMake(self)
            cmake.configure(build_script_folder=self._source_subfolder)
            cmake.build()


    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "vtk", "conan-official-{}-variables.cmake".format(self.name))


    def package(self):
        cmake = CMake(self)
        cmake.install()

        # VTK installs the licenses under the res/licenses/VTK directory, move it
        rename( os.path.join(self.package_folder,"res","licenses","VTK"),
                os.path.join(self.package_folder,"licenses"))

        # keep copy of generated VTK cmake files, for inspection
        if _debug_packaging:
            rename( os.path.join(self.package_folder,"lib","cmake"),
                    os.path.join(self.package_folder,"vtk-cmake-backup"))
        else:
            # delete VTK-installed cmake files
            rmdir(os.path.join(self.package_folder,"lib","cmake"))

        # make a copy of the modules.json, we use that in package_info
        # TODO where should this file live?  perhaps just in the base package folder?
        self.copy("modules.json",
                dst=os.path.join(self.package_folder), # ,"lib","conan"))
                src=os.path.join(self.build_folder,"modules.json"),
                keep_path=False
                )

        # create a cmake file with our special variables
        content = textwrap.dedent("""\
                set (VTK_ENABLE_KITS {})
                """
                .format(self.options.enable_kits)
                )
        save(os.path.join(self.package_folder, self._module_file_rel_path),
                content
                )


    def package_info(self):
        # Note: I don't currently import the explicit dependency list for each component from VTK,
        # so every module will depend on "everything" external, and there are no internal dependencies.
        # Consumers just have to figure out what they have to link.

        # get keys as a list and make a list of target::target
        all_requires = [k + "::" + k for k in self._third_party().keys()]

        if self.options.group_enable_Rendering:
            all_requires += [ "opengl::opengl" ]
            if self.settings.os in ["Linux", "FreeBSD"]:
                all_requires += [ "xorg::xorg" ]
        all_requires.sort()


        # auto-include these .cmake files (generated by conan)
        vtk_cmake_build_modules = [self._module_file_rel_path]


        # Needed?
        # if self.settings.os == "Linux":
        #     self.cpp_info.system_libs += ["dl","pthread"]

        # Just generate 'config' version, FindVTK.cmake hasn't existed since CMake 3.1, according to:
        # https://cmake.org/cmake/help/latest/module/FindVTK.html

        self.cpp_info.set_property("cmake_file_name", "VTK")
        self.cpp_info.set_property("cmake_target_name", "VTK::VTK")

        # Dont set this, the hook is wrong... already set the build_modules...
        # self.cpp_info.builddirs = [os.path.join("lib", "cmake", "vtk")]

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
                self.cpp_info.components[comp].libdirs       = ["lib"]
                self.cpp_info.components[comp].requires      = all_requires
                self.cpp_info.components[comp].set_property("cmake_build_modules", vtk_cmake_build_modules)
                if self.settings.os == "Linux":
                    self.cpp_info.components[comp].system_libs = ["m"]

        else:
            # hard code the replacement 3rd party targets we are supplying,
            # it doesn't seem to be listed in VTK anywhere
            thirds = {
                    "VTK::eigen":    "eigen::eigen",
                    "VTK::exprtk":   "exprtk::exprtk",
                    "VTK::expat":    "expat::expat",
                    "VTK::glew":     "glew::glew",
                    "VTK::fmt":      "fmt::fmt",
                    "VTK::freetype": "freetype::freetype",
                    "VTK::jpeg":     "libjpeg-turbo::jpeg",
                    "VTK::jsoncpp":  "jsoncpp::jsoncpp",
                    "VTK::libproj":  "proj::proj",
                    "VTK::lz4":      "lz4::lz4",
                    "VTK::lzma":     "xz_utils::xz_utils",
                    "VTK::png":      "libpng::libpng",
                    "VTK::pugixml":  "pugixml::pugixml",
                    "VTK::tiff":     "libtiff::libtiff",
                    "VTK::utf8":     "utfcpp::utfcpp",
                    "VTK::zlib":     "zlib::zlib",
                    "VTK::doubleconversion": "double-conversion::double-conversion",
                    }

            if self.options.group_enable_Rendering:
                thirds["VTK::opengl"] = "opengl::opengl"

            # TODO check out abseil recipe, it parses the generated cmake-targets file for extra info.

            # new way - parse the modules.json file and generate a list of components
            modfile = load(os.path.join(self.package_folder,"modules.json"))
            vtkmods = json.loads(modfile)

            self.output.info("All module keys: {}".format(vtkmods["modules"].keys()))

            self.output.info("Found libs: {}".format(existing_libs))
            self.output.info("Processing modules")
            for module_name in vtkmods["modules"]:
                comp = module_name.split(':')[2]
                comp_libname = vtkmods["modules"][module_name]["library_name"]

                if comp_libname in existing_libs:
                    self.output.info("Processing module {}".format(module_name))
                    self.cpp_info.components[comp].set_property("cmake_target_name", module_name)
                    self.cpp_info.components[comp].libs          = [comp_libname]
                    self.cpp_info.components[comp].libdirs       = ["lib"]

                    # not sure how to be more specific here, the modules.json doesn't specify which other modules are required
                elif module_name in thirds:
                    self.output.info("Processing external module {} --> {}".format(module_name, thirds[module_name]))
                    self.cpp_info.components[comp].set_property("cmake_target_name", module_name)
                    self.cpp_info.components[comp].requires.append(thirds[module_name])

                else:
                    self.output.warning("Skipping module (lib file does not exist) {}".format(module_name))

                # this is how we used to add ALL the requires at once
                # self.cpp_info.components[comp].requires      = all_requires.copy() # else, []

            # second loop for internal dependencies
            for module_name in vtkmods["modules"]:
                comp = module_name.split(':')[2]
                if comp in self.cpp_info.components:

                    # always depend on the headers mini-module
                    # which also includes the cmake extra file definitions (declared afterwards)
                    self.cpp_info.components[comp].requires.append("headers")

                    # these are the public depends
                    for dep in vtkmods["modules"][module_name]["depends"]:
                        dep_libname = vtkmods["modules"][dep]["library_name"]
                        if dep_libname in existing_libs:
                            depname = dep.split(':')[2]
                            self.output.info("   depends on {}".format(depname))
                            self.cpp_info.components[comp].requires.append(depname)
                        elif dep in thirds:
                            extern = thirds[dep]
                            self.output.info("   depends on external {} --> {}".format(dep, extern))
                            self.cpp_info.components[comp].requires.append(extern)
                        else:
                            self.output.info("   skipping depends (lib file does not exist): {}".format(dep))

                    # DEBUG # self.output.info("  Final deps: {}".format(self.cpp_info.components[comp].requires))

                    # these are the private depends, not sure if we need these
                    # for dep in vtkmods["modules"][module_name]["private_depends"]:
                        # self.cpp_info.components[comp].requires.append(dep)

                    if self.settings.os == "Linux":
                        self.cpp_info.components[comp].system_libs = ["m"]
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
