# TODO: check validate() still works!
# TODO: per-vtk-version requirements for each dependency version - currently all in-recipe... interleaved list?  yml?  or as it is?
# TODO: add ALL possible options in init() from ALL json files, and then delete as approprate in config_options()
# TODO consider changing fake-modules (introduced for dependency management) from QtOpenGL to eg conan_QtOpenGL

# RECIPE MAINTAINER NOTES:
#   There are readme-*.md in the recipe folder.
#
# General recipe design notes: readme-recipe-design.md
# How to add a new version: readme-new-version.md
# How to build a dependency through conan: readme-support-dependency.md

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
import itertools # for autoinit header generation

# Enable to keep VTK-generated cmake files, to check contents
_debug_packaging = False

required_conan_version = ">=1.59.0"


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



def _module_remove_prefix(mod):
    if not mod.startswith("VTK::"):
        raise RuntimeError("RECIPE BUG: Expected VTK module to start with VTK::")
    return mod[5:]







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

            # debug what modules are available and why a module isn't available
            "debug_module":     [True, False],

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

            # Qt-specific modules
            "qt_version": ["Auto", "5", "6"],

            # Note: there are a LOT of "module_enable_XXX" and "group_enable_XXX" options loaded in init()
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

            "debug_module":     False,

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

            # Qt-specific modules
            "qt_version":              "Auto",  # Use 6 if provided, else use 5
        }


    def _vtk_module_json_filename(self, version):
        return f"modules-{version}.json";

    def _load_modules_info(self, version):
        return self._vtkmods(os.path.join(self.recipe_folder, self._vtk_module_json_filename(version)))


    # look for known CONDITIONS from the vtk.module files
    # If 'default_overrides==None', then do validations and raise errors
    def _process_module_conditions(self, modules_info, modules_enabled, default_overrides, condition, error_message):
        for mod in modules_info["modules"]:
            if condition in modules_info["modules"][mod]["condition"]:
                if default_overrides is not None:
                    mod_no_prefix = _module_remove_prefix(mod)
                    default_overrides[f"module_enable_{mod_no_prefix}"] = "NO"
                else:
                    if modules_enabled[mod]:
                        raise ConanInvalidConfiguration(f"{mod} {error_message}")

    def _process_modules_conditions(self, modules_info, modules_enabled, default_overrides):
        required_option_message = "can only be enabled with {} (module may have been enabled with group_enable_Web or build_all_modules)"

        # for our purposes, if wrap_python=False, then VTK::Python is disabled
        # VTK's cmake does this internally, but it isn't specified in their modules files.
        if len(modules_info["modules"]["VTK::Python"]["condition"]) > 0:
            raise ConanInvalidConfiguration(f"Did not expect a condition in VTK::Python! (saw: {modules_info['modules']['VTK::Python']['condition']}. Edit recipe to suit.")

        modules_info["modules"]["VTK::Python"]["condition"] = "VTK_WRAP_PYTHON"

        if not self.options.wrap_python:
            self._process_module_conditions(modules_info, modules_enabled, default_overrides, "VTK_WRAP_PYTHON", required_option_message.format("wrap_python"))
        if not self.options.use_mpi:
            self._process_module_conditions(modules_info, modules_enabled, default_overrides, "VTK_USE_MPI", required_option_message.format("use_mpi"))
        if not self.options.use_tk:
            self._process_module_conditions(modules_info, modules_enabled, default_overrides, "VTK_USE_TK", required_option_message.format("use_tk"))
        if not self.options.enable_logging:
            self._process_module_conditions(modules_info, modules_enabled, default_overrides, "VTK_ENABLE_LOGGING", required_option_message.format("enable_logging"))
        if self.settings.os == "Windows":
            self._process_module_conditions(modules_info, modules_enabled, default_overrides, "NOT WIN32", "cannot be enabled on the Windows platform")
        # Note: this is a very simple and dumb test ... the condition could say "NOT MSVC" and it would still match this rule!
        #  But there aren't many conditions and these are just hand-rolled tests to suit.
        if not is_msvc(self):
            self._process_module_conditions(modules_info, modules_enabled, default_overrides, "NOT WIN32", "can only be enabled with the MSVC compiler")
        # note: this test is something we added as a condition on some of our 'fake' modules to add conan-package dependencies
        if self.settings.os not in ["Linux", "FreeBSD"]:
            self._process_module_conditions(modules_info, modules_enabled, default_overrides, "conan_Linux_FreeBSD", "{mod} can only be enabled on the Linux or FreeBSD platform")




    # finish populating options and default_options
    def _init_with_version(self, version):
        modules_info = self._load_modules_info(version)

        extra_options = {}
        extra_defaults = {}

        groups = set()
        # Add in other modules that have not been added manually
        for mod_with_prefix in modules_info["modules"]:
            # print(f"Module {mod_with_prefix}")
            mod = _module_remove_prefix(mod_with_prefix)
            option_name = f"module_enable_{mod}"
            extra_options[option_name] = ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"]
            extra_defaults[option_name] = "DEFAULT"
            for group in modules_info["modules"][mod_with_prefix]["groups"]:
                # print(f"  has group {group}")
                if not group in groups:
                    # print(f"     added")
                    groups.add(group)
                    option_name = f"group_enable_{group}"
                    extra_options[option_name] = ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"]
                    extra_defaults[option_name] = "DEFAULT"

        # special overrides for conan, to configure what we want CCI to build by default
        default_overrides = {
            # The CommonDataModel must ALWAYS be built, otherwise the VTK build will fail
            "module_enable_CommonDataModel":   "YES",

            # TODO Group-enable-web disabled until wrapping_python also enabled by default
            "group_enable_Web":        "NO",

            # these aren't supported yet, need to system-install packages or provide conan packages for each
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
            "module_enable_IOFFMPEG":          "NO", # FFMPEG required
            "module_enable_IOOCCT":            "NO", # OpenCASCADE required
            "module_enable_IOMySQL":           "NO", # MySQL required
            "module_enable_RenderingOpenXR":   "NO", # OpenXR required

            "module_enable_RenderingZSpace":   "NO", # New zSpace device support, not ready for Linux, so just disable by default

            "module_enable_IOODBC":            "NO", # Requires odbc, which probably can be done now, needs fake-module

            "module_enable_IOGeometry":        "NO", # Has a C++20 problem with building
            "module_enable_ioss":              "NO", # Doesn't compile with C++20

            # OpenVR's recipe isn't v2 compatible yet
            "module_enable_openvr":            "NO",

            # MPI doesn't build (for me) so disable by default
            "module_enable_mpi":               "NO",

            # disable Qt Quick support, by default, for now, because Qt recipe (by default) doesn't build declarative
            "module_enable_GUISupportQtQuick": "NO",
        }

        # merge the default lists
        extra_defaults = {**extra_defaults, **default_overrides}
        self.options.update(extra_options, extra_defaults)


    # finish populating options and default_options
    # Note: I require the version number to init this recipe's options
    #    Hopefully it is possible to modify conan and pass this version number
    #    through somehow.  It is not yet attached to 'self' at this point,
    #    and is required to be gathered from conan-create --version x.y.z
    def init(self):
        # TODO load all possible versions, and then remove in config_options()
        HACK_VERSION = "9.3.0"
        # HACK_VERSION = "9.2.6"
        self._init_with_version(HACK_VERSION)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        modules_info = self._load_modules_info(self.version)
        default_overrides = {}
        self._process_modules_conditions(modules_info, None, default_overrides)
        updated_options = {}
        for pack in default_overrides.keys():
            updated_options[pack] = ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"]
        self.options.update(updated_options, default_overrides)


    def _compute_modules_enabled(self, modules_info):
        # NOTE: the order of items in 'groups' is important for the ModuleSystem enable/disable
        #  Do not reorder 'groups' !

        # compute the enabled... implemented based on VTK/Documentation/Doxygen/ModuleSystem.md
        base_modules_enabled = {}

        # TODO implement CONDITION handling

        # first, init with our recipe options for individual modules and groups
        # print(self.options)

        # print("*** Setting module-enabled based on Groups and build_all_modules ***")

        for mod_with_prefix in modules_info["modules"]:
            mod = _module_remove_prefix(mod_with_prefix)
            mod_enabled = self.options.get_safe(f"module_enable_{mod}",None)
            message = None
            if mod_enabled == "DEFAULT":
                message = f"{mod_with_prefix} is DEFAULT"
                # if module is still default, check its groups
                for group in modules_info["modules"][mod_with_prefix]["groups"]:
                    group_enabled = self.options.get_safe(f"group_enable_{group}",None)
                    message += f", has group {group} ({group_enabled})"
                    if group_enabled != "DEFAULT":
                        message += f", setting mod to {group_enabled}"
                        mod_enabled = group_enabled
                        break   # take the first non-DEFAULT group setting
            # STILL 'default'...
            if mod_enabled == "DEFAULT":
                # take the result from build_all_modules
                if self.options.build_all_modules: 
                    message += ", ALL is WANT, setting to WANT"
                    mod_enabled = "WANT"
                else:
                    message += ", ALL is DONT_WANT, setting to DONT_WANT"
                    mod_enabled = "DONT_WANT"
            # we have our answer for this module, it will be YES/NO/WANT/DONT_WANT
            base_modules_enabled[mod_with_prefix] = mod_enabled
            # if message: print(message)

        # We now have a lot of YES/NO/WANT/DONT_WANT
        # We now want to resolve the WANT/DONT_WANT into YES/NO

        # From VTK documentation:
        # - `WANT`: The module should be built. It will not be built, however, if it
        #   depends on a `NO` module.
        # - `DONT_WANT`: The module doesn't need to be built. It will be built if a
        #   `YES` or `WANT` module depends on it.


        # use "visited" to know which ones have already had their dependencies checked in depth
        def recurse_depends_has_NO(visited, mod, last_yes_parent, chain_txt):
            mod_enabled = base_modules_enabled[mod]
            if mod_enabled == "NO":
                if len(last_yes_parent) > 0:
                    raise RuntimeError(f"Module collision: {chain_txt} has {last_yes_parent}=YES and {mod}=NO")
                return True

            if mod in visited:
                return mod_enabled == "NO"

            if mod_enabled == "YES":
                last_yes_parent = mod

            # check: depends, private_depends.
            # optional_depends do not influence this computation
            mod_info = modules_info["modules"][mod]
            depends = set(mod_info["depends"] + mod_info["private_depends"])    # there can be repeated dependencies
            any_no = False
            for dep in depends:
                # note: always check dependencies to catch NO-YES problems
                if recurse_depends_has_NO(visited, dep, last_yes_parent, f"{chain_txt} --> {dep}"):
                    if not any_no:
                        # print(f"Setting {mod} to NO, due to dependency {dep} (NO)")
                        any_no = True
            if any_no:
                base_modules_enabled[mod] = "NO"
            visited.add(mod)
            return any_no

        # print("*** Setting modules to NO if dependencies are NO ***")
        for mod in base_modules_enabled:
            recurse_depends_has_NO(set(), mod, "", mod)

        # print("*** For all YES and WANT modules, setting all dependencies to YES ***")
        # find all modules that are tagged as YES, and tag all dependencies as YES
        # iterate multiple times rather than building a tree,
        # tagging those whose dependencies have been visited with YES-DONE
        mod_todo = set(base_modules_enabled.keys())
        while len(mod_todo) > 0:
            mod = mod_todo.pop()
            if base_modules_enabled[mod] == "WANT":
                base_modules_enabled[mod] = "YES"
            if base_modules_enabled[mod] == "YES":
                mod_info = modules_info["modules"][mod]
                depends = set(mod_info["depends"] + mod_info["private_depends"])    # there can be repeated dependencies
                for dep in depends:
                    dep_enabled = base_modules_enabled[dep]
                    if dep_enabled == "YES":
                        pass # already done
                    elif dep_enabled == "NO":
                        raise RuntimeError(f"Module collision, {mod} is YES, but dependency {dep} is NO")
                    else:
                        self.output.info(f"{mod} is YES, setting {dep} from {dep_enabled} to YES")
                        base_modules_enabled[dep] = "YES" # will process dependencies in future pass
                        mod_todo.add(dep)   # re-add to todo list, if not already in there (may have already been checked while it was still a "WANT" or other)

        # print("*** Setting all WANT / DONT_WANT modules to YES / NO ***")
        # find all modules that are not tagged YES or NO (ie WANT_*) and tag appropriately
        final_modules_enabled = {}
        for mod in base_modules_enabled:
            mod_enabled = base_modules_enabled[mod]
            if mod_enabled == "WANT":         # if we WANT, then the answer is YES (dependencies dont care)
                mod_enabled = "YES"
                self.output.info(f"{mod} set WANT to YES")
            elif mod_enabled == "DONT_WANT":    # if we dont want, then answer is no (dependencies dont care)
                mod_enabled = "NO"
                self.output.info(f"{mod} set DONT_WANT to NO")
            elif mod_enabled == "YES" or mod_enabled == "NO":
                self.output.info(f"{mod} Leaving as {mod_enabled}")
                pass
            else:
                raise RuntimeError(f"Unexpected module-enable flag: {mod_enabled}")
            final_modules_enabled[mod] = (mod_enabled == "YES")
            if final_modules_enabled[mod]:
                self.output.info(f"Module enabled: {mod}");

        return final_modules_enabled



    # Required as VTK adds 'd' to the end of library files on windows
    @property
    def _lib_suffix(self):
        return "d" if self.settings.os == "Windows" and self.settings.build_type == "Debug" else ""

    def build_requirements(self):
        self.tool_requires("sqlite3/[>=3.41.1]")

    def source(self):
        # NOTE: if using git, have to also use the git submodule thing to get VTKm... the tarball has it.
        if False: # TODO TODO self.options.use_source_from_git:
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
        if self.version == "9.2.6":
            parties = {
                    # LEFT field:  target name for linking, will be used as TARGET::TARGET in package_info()
                    # RIGHT field: Force the version (for development mode)... package/version to require ... component requirement
                    # "VTK::module": "conan_package::conan_package",      # if the whole package required
                    # "VTK::module": "conan_package::package_component",  # if subcomponent required
                    "cgns":              [False, "cgns/[>=4.3.0]",              "cgns::cgns"    ],
                    "cli11":             [False, "cli11/[>=2.3.2]",             "cli11::cli11"  ],
                    "doubleconversion":  [False, "double-conversion/[>=3.2.1]", "double-conversion::double-conversion" ],
                    "eigen":             [False, "eigen/[>=3.4.0]",             "eigen::eigen"  ],
                    "expat":             [True,  "expat/[=2.6.0]",              "expat::expat"  ],  # TODO conflict: wayland (2.5.0)
                    "exprtk":            [True,  "exprtk/[=0.0.1]",             "exprtk::exprtr"],  # TODO upgrade to 0.0.2 (there was a problem with first attempt)
                    "fmt":               [True,  "fmt/[=8.1.1]",                "fmt::fmt"      ],  # TODO must be 8.1.1 for some reason ... VTK 9.1.0 release docs mention a PR - confirmed merged 8.1.0, will be bumped in future VTK release
                    "freetype":          [False, "freetype/[>=2.13.0]",         "freetype::freetype" ],
                    "glew":              [False, "glew/[>=2.2.0]",              "glew::glew"    ],
                    "hdf5":              [True,  "hdf5/[=1.14.3]",              "hdf5::hdf5"    ],  # TODO conflict: netcdf (.1) and cgns (.0)
                    "jsoncpp":           [False, "jsoncpp/[>=1.9.4]"            "jsoncpp::jsoncpp"  ],
                    "libharu":           [False, "libharu/[>=2.4.3]"            "libharu::libharu"  ],
                    "kissfft":           [False, "kissfft/[>=131.1.0]",         "kissfft::kissfft"  ],
                    "lz4":               [False, "lz4/[>=1.9.4]",               "lz4::lz4"          ],

                    "png":               [True,  "libpng/[=1.6.42]",            "libpng::libpng"    ],  # TODO conflict: libharu (.40) and freetype (.42)
                    "libxml2":           [True,  "libxml2/[=2.12.4]",           "libxml2::libxml2"  ],  # TODO conflict: xkbcommon (2.12.3)

                    "netcdf":            [False, "netcdf/[>=4.8.1]",            "netcdf::netcdf"    ],
                    "nlohmannjson":      [False, "nlohmann_json/[>=3]",         "nlohmann_json::nlohman_json" ],

                    "ogg":               [False, "ogg/[>=1.3.5]",               "ogg::ogg"          ],
                    "opengl":            [False, "opengl/system",               "opengl::opengl"    ],
                    "openvr":            [False, "openvr/[>=1.16.8]",           "openvr::openvr"    ],

                    "libproj":           [False, "proj/[>=9.1.1]",              "proj::proj"        ],
                    "pugixml":           [False, "pugixml/[>=1.13]",            "pugixml::pugixml"  ],

                    "sqlite":            [True,  "sqlite3/[=3.45.1]",           "sqlite3::sqlite3"  ],  # TODO conflict: qt (3.44.2) and proj (3.44.2)

                    "theora":            [False, "theora/[>=1.1.1]",            "theora::theora"    ],

                    "utf8":              [False, "utfcpp/[>=3.2.3]",            "utfcpp::utfcpp"    ],
                    "lzma":              [False, "xz_utils/[>=5.4.2]",          "xz_utils::xz_utils"], # note: VTK calls this lzma
                    "zlib":              [False, "zlib/[>=1.2.13]",             "zlib::zlib"        ],
                    "tiff":              [False, "libtiff/[>=4.4.0]",           "libtiff::libtiff"  ],

                    "xorg-system":       [False, "xorg/system",                 "xorg::xorg"        ],

                    # TODO what module depends on boost?
                    # "boost":             [False, "boost/[>=1.82.0]"],

                    # TODO what module depends on odbc?
                    # "odbc":              [False, "odbc/[>=2.3.11]"],

                    # MODULES: zfp, boost and odbc
                    # parties["zfp"]     = "zfp/[>=0.5.5]"
                    }

            # NOTE: You may NOT be able to just adjust the version numbers in here, without
            #   also adjusting the patch, as the versions are also mentioned in ThirdParty/*/CMakeLists.txt

            if self.options.with_jpeg == "libjpeg":
                parties["jpeg"] = [False, "libjpeg/9e", "libjpeg::libjpeg"]
            elif self.options.with_jpeg == "libjpeg-turbo":
                parties["jpeg"] = [False, "libjpeg-turbo/[>=2.1.5]", "libjpeg-turbo::jpeg"]

            if self.options.qt_version == "5":
                parties["QtOpenGL"] = [False, "qt/[>=5.15.9]", "qt::qtOpenGL"]
            else:
                parties["QtOpenGL"] = [False, "qt/[>=6.5.0]", "qt::qtOpenGL"]
            return parties


        if self.version == "9.3.0":
            parties = {
                    # LEFT field:  target name for linking, will be used as TARGET::TARGET in package_info()
                    # RIGHT field: Force the version (for development mode)... package/version to require ... component requirement
                    # "VTK::module": "conan_package::conan_package",      # if the whole package required
                    # "VTK::module": "conan_package::package_component",  # if subcomponent required
                    "cgns":              [False, "cgns/[>=4.3.0]",              "cgns::cgns"    ],
                    "cli11":             [False, "cli11/[>=2.3.2]",             "cli11::cli11"  ],
                    "doubleconversion":  [False, "double-conversion/[>=3.2.1]", "double-conversion::double-conversion" ],
                    "eigen":             [False, "eigen/[>=3.4.0]",             "eigen::eigen"  ],
                    "expat":             [True,  "expat/[=2.6.0]",              "expat::expat"  ],  # TODO conflict: wayland (2.5.0)
                    "exprtk":            [True,  "exprtk/[=0.0.1]",             "exprtk::exprtr"],  # TODO upgrade to 0.0.2 (there was a problem with first attempt)
                    "fast_float":        [False, "fast_float/3.9.0",            "fast_float::fast_float"],
                    "fmt":               [True,  "fmt/10.2.1",                  "fmt::fmt"      ],
                    "freetype":          [False, "freetype/[>=2.13.0]",         "freetype::freetype" ],
                    "glew":              [False, "glew/[>=2.2.0]",              "glew::glew"    ],
                    "hdf5":              [True,  "hdf5/[=1.14.3]",              "hdf5::hdf5"    ],  # TODO conflict: netcdf (.1) and cgns (.0)
                    "jsoncpp":           [False, "jsoncpp/[>=1.9.4]",           "jsoncpp::jsoncpp"  ],
                    "libharu":           [False, "libharu/[>=2.4.3]",           "libharu::libharu"  ],
                    "kissfft":           [False, "kissfft/[>=131.1.0]",         "kissfft::kissfft"  ],
                    "lz4":               [False, "lz4/[>=1.9.4]",               "lz4::lz4"          ],

                    "png":               [True,  "libpng/[=1.6.42]",            "libpng::libpng"    ],  # TODO conflict: libharu (.40) and freetype (.42)
                    "libxml2":           [True,  "libxml2/[=2.12.4]",           "libxml2::libxml2"  ],  # TODO conflict: xkbcommon (2.12.3)

                    "netcdf":            [False, "netcdf/[>=4.8.1]",            "netcdf::netcdf"    ],
                    "nlohmannjson":      [False, "nlohmann_json/[>=3]",         "nlohmann_json::nlohman_json" ],

                    "ogg":               [False, "ogg/[>=1.3.5]",               "ogg::ogg"          ],
                    "opengl":            [False, "opengl/system",               "opengl::opengl"    ],
                    "openvr":            [False, "openvr/[>=1.16.8]",           "openvr::openvr"    ],

                    "libproj":           [False, "proj/[>=9.1.1]",              "proj::proj"        ],
                    "pugixml":           [False, "pugixml/[>=1.13]",            "pugixml::pugixml"  ],

                    "sqlite":            [True,  "sqlite3/[=3.45.1]",           "sqlite3::sqlite3"  ],  # TODO conflict: qt (3.44.2) and proj (3.44.2)

                    "theora":            [False, "theora/[>=1.1.1]",            "theora::theora"    ],

                    "utf8":              [False, "utfcpp/[>=3.2.3]",            "utfcpp::utfcpp"    ],
                    "lzma":              [False, "xz_utils/[>=5.4.2]",          "xz_utils::xz_utils"], # note: VTK calls this lzma
                    "zlib":              [False, "zlib/[>=1.2.13]",             "zlib::zlib"        ],
                    "tiff":              [False, "libtiff/[>=4.4.0]",           "libtiff::libtiff"  ],

                    "xorg-system":       [False, "xorg/system",                 "xorg::xorg"        ],

                    # TODO what module depends on boost?
                    # "boost":             [False, "boost/[>=1.82.0]"],

                    # TODO what module depends on odbc?
                    # "odbc":              [False, "odbc/[>=2.3.11]"],

                    # MODULES: zfp, boost and odbc
                    # parties["zfp"]     = "zfp/[>=0.5.5]"
                    }

            # NOTE: You may NOT be able to just adjust the version numbers in here, without
            #   also adjusting the patch, as the versions are also mentioned in ThirdParty/*/CMakeLists.txt

            if self.options.with_jpeg == "libjpeg":
                parties["jpeg"] = [False, "libjpeg/9e", "libjpeg::libjpeg"]
            elif self.options.with_jpeg == "libjpeg-turbo":
                parties["jpeg"] = [False, "libjpeg-turbo/[>=2.1.5]", "libjpeg-turbo::jpeg"]

            if self.options.qt_version == "5":
                parties["QtOpenGL"] = [False, "qt/[>=5.15.9]", "qt::qtOpenGL"]
            else:
                parties["QtOpenGL"] = [False, "qt/[>=6.5.0]", "qt::qtOpenGL"]
            return parties

        raise ConanInvalidConfiguration(f"{self.version} not supported by recipe (update _third_party(self))")



    def requirements(self):
        modules_info    = self._load_modules_info(self.version)
        modules_enabled = self._compute_modules_enabled(modules_info)

        for target, requirement in self._third_party().items():
            mod = f"VTK::{target}"
            if modules_enabled[mod]:
                # NOTE: optionally force to break dependency version clashes until CCI deps have been bumped
                # TODO: Change to use [replace_requires] for this to work correctly, locally
                self.requires(requirement[1], force=requirement[0])


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

        modules_info    = self._load_modules_info(self.version)
        modules_enabled = self._compute_modules_enabled(modules_info)

        if self.options.wrap_python and not self.options.enable_wrapping:
            raise ConanInvalidConfiguration("wrap_python can only be enabled with enable_wrapping")
        if self.options.wrap_java and not self.options.enable_wrapping:
            raise ConanInvalidConfiguration("wrap_java can only be enabled with enable_wrapping")

        if self.options.use_tk and not self.options.wrap_python:
            raise ConanInvalidConfiguration("use_tk can only be enabled with wrap_python")

        if self.options.build_pyi_files and not self.options.wrap_python:
            raise ConanInvalidConfiguration("build_pyi_files can only be enabled with wrap_python")

        self._process_modules_conditions(modules_info, modules_enabled, None)

        # this problem was observed with 9.2.6
        # Perhaps not a problem in 9.3.0, or with the new recipe?
        # if self.options.wrap_python and not modules_enabled["VTK::IOExport"]:
            # raise ConanInvalidConfiguration("wrap_python can only be enabled with module_enable_IOExport enabled, otherwise it has problems compiling")

        if "libtiff" in self.dependencies and self.dependencies["libtiff"].options.jpeg != self.info.options.with_jpeg:
            raise ConanInvalidConfiguration(f"{self.ref} requires option value {self.name}:with_jpeg equal to libtiff:jpeg.")

        if "pugixml" in self.dependencies and self.dependencies["pugixml"].options.wchar_mode:
            raise ConanInvalidConfiguration(f"{self.ref} requires pugixml:wchar_mode=False")

        if "kissfft" in self.dependencies and self.dependencies["kissfft"].options.datatype != "double":
            # kissfft - we want the double format (also known as kiss_fft_scalar)
            raise ConanInvalidConfiguration(f"{self.ref} requires kissfft:datatype=double")

        if modules_enabled["VTK::GUISupportQtQuick"] and not self.dependencies["qt"].options.qtdeclaritive:
            raise ConanInvalidConfiguration(f"{self.ref} has module_enable_GUISupportQtQuick enabled, which requires qt:qtdeclarative=True")

        if self.options.smp_enable_TBB:
            raise ConanInvalidConfiguration(f"{self.ref} has smp_enable_TBB enabled. TODO check modules.json for TBB/OpenTBB dependencies and adjust recipe to suit.")

    def export(self):
        copy(self, self._vtk_module_json_filename(self.version), src=self.recipe_folder, dst=self.export_folder)

    def export_sources(self):
        export_conandata_patches(self)

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
        modules_info    = self._load_modules_info(self.version)
        modules_enabled = self._compute_modules_enabled(modules_info)

        tc = CMakeToolchain(self)

        # for debugging the conan recipe
        # tc.variables["CMAKE_FIND_DEBUG_MODE"] = True

        # 64 / 32 bit IDs
        if self.options.use_64bit_ids != "Auto":
            tc.variables["VTK_USE_64BIT_IDS"] = self.options.use_64bit_ids

        # Be sure to set this, otherwise vtkCompilerChecks.cmake will downgrade our CXX standard to 11
        tc.variables["VTK_IGNORE_CMAKE_CXX11_CHECKS"] = True

        # print out info about why modules are not available
        if self.options.debug_module:
            tc.variables["VTK_DEBUG_MODULE"] = True
            tc.variables["VTK_DEBUG_MODULE_ALL"] = True
            tc.variables["VTK_DEBUG_MODULE_building"] = True
            tc.variables["VTK_DEBUG_MODULE_enable"] = True
            tc.variables["VTK_DEBUG_MODULE_kit"] = True
            tc.variables["VTK_DEBUG_MODULE_module"] = True
            tc.variables["VTK_DEBUG_MODULE_provide"] = True
            tc.variables["VTK_DEBUG_MODULE_testing"] = True

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
        if modules_enabled["VTK::netcdf"]:
            tc.variables["NetCDF_HAS_PARALLEL"] = self.dependencies["hdf5"].options.parallel


        # https://gitlab.kitware.com/vtk/vtk/-/blob/master/Documentation/dev/build.md
        # TODO try VTK_USE_VIDEO_FOR_WINDOWS   for video capture
        # TODO try VTK_USE_VIDEO_FOR_WINDOWS_CAPTURE   for video capture
        # TODO try VTK_USE_MICROSOFT_MEDIA_FOUNDATION   for video capture (MP4)


# No longer required, we compute pre-module what is desired
#        # this little function only to help mark out the special
#        # default/yes/no/want/dont_want options
#        def _yesno(flag):
#            return flag
#
#
#        # groups can be:  DEFAULT   DONT_WANT   WANT   YES   NO
#        # Note that YES is like WANT, but will show errors if can't make everything
#        # NO is also more forceful than DONT_WANT
#        # Default is DONT_WANT, let it auto-enable when required
#        tc.variables["VTK_GROUP_ENABLE_Imaging"]    = _yesno(self.options.group_enable_Imaging)    # TODO test
#        tc.variables["VTK_GROUP_ENABLE_MPI"]        = _yesno(self.options.group_enable_MPI)        # TODO test
#        tc.variables["VTK_GROUP_ENABLE_Rendering"]  = _yesno(self.options.group_enable_Rendering)
#        tc.variables["VTK_GROUP_ENABLE_StandAlone"] = _yesno(self.options.group_enable_StandAlone)  # TODO test
#        tc.variables["VTK_GROUP_ENABLE_Views"]      = _yesno(self.options.group_enable_Views)       # TODO test
#        tc.variables["VTK_GROUP_ENABLE_Web"]        = _yesno(self.options.group_enable_Web)         # TODO test
#
#        # for Qt, can also use the more specific MODULE options below
#        tc.variables["VTK_GROUP_ENABLE_Qt"] = _yesno(self.options.group_enable_Qt)

        ##### QT ######
        # QT has a few modules, we'll be specific
        tc.variables["VTK_QT_VERSION"]                          = self.options.qt_version

        # Setup ALL our discovered modules
        # this will generate lots of variables, such as:
        # tc.variables["VTK_MODULE_ENABLE_VTK_RenderingCore"]     = _yesno(self.options.module_enable_RenderingCore)
        for mod_with_prefix in modules_enabled:
            mod = _module_remove_prefix(mod_with_prefix)
            option_name   = f"module_enable_{mod}"
            variable_name = f"VTK_MODULE_ENABLE_VTK_{mod}"
            if modules_enabled[mod_with_prefix]:
                yesno = "YES"
            else:
                yesno = "NO"
            tc.variables[variable_name] = yesno

        # TODO if true (or all) then system has to install postgres dev package

        ##### SMP parallelism ####  Sequential  STDThread  OpenMP  TBB
        # Note that STDThread seems to be available by default
        tc.variables["VTK_SMP_IMPLEMENTATION_TYPE"] = self.options.smp_implementation_type
        # Change the mode during runtime, if you enable the backends like so:
        tc.variables["VTK_SMP_ENABLE_Sequential"]   = self.options.smp_enable_Sequential
        tc.variables["VTK_SMP_ENABLE_STDThread"]    = self.options.smp_enable_STDThread
        tc.variables["VTK_SMP_ENABLE_OpenMP"]       = self.options.smp_enable_OpenMP
        tc.variables["VTK_SMP_ENABLE_TBB"]          = self.options.smp_enable_TBB

        #### Use the Internal VTK bundled libraries for these Third Party dependencies ...
        # Ask VTK to use their bundled versions for these:
        # These are missing in CCI, could probably use if they become available.
        # Note that we may need to use bundled versions if they are heavily patched.
        # See notes in readme-support-dependency.md
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
        # Allow VTK to use packages with larger major versions for these dependencies.
        #  The conan dependency cmake files will (by default) only allow compatible matching where the major version matches
        #  what the package's native cmake file specifies in find_package(), ie find_package(qt 5.9) will NOT allow qt 6 to be used.
        #  This is not what VTK expect, which assumes the version number is the absolute MINIMUM version, anything higher is ok.
        #
        #                                  (default)
        # Options: ["AnyNewerVersion", "SameMajorVersion", "SameMinorVersion", "ExactVersion"])
        #
        # We could set this flag for ALL dependencies, as per VTK standard,
        #  but I think better we are alerted when pushing to a higher major version that may not be compatible.
        #
        allow_newer_major_versions_for_these_requirements = [
                "fmt",  # fmt has been bumped for 9.3.0 (internally) to 10.x but VTK's external package version was still 9.x
                "qt",   # qt can be 5 or 6, so we need to avoid matching on SameMajorVersion
                ]
        for req in allow_newer_major_versions_for_these_requirements:
            deps.set_property(req, "cmake_config_version_compat", "AnyNewerVersion")


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
        if "proj" in self.dependencies:
            tc.variables["LibPROJ_MAJOR_VERSION"] = Version(self.dependencies["proj"].ref.version).major
        #
        # double-version has their headers in <double-conversion/header>
        # but VTK expects just <header>
        if "double-conversion" in self.dependencies:
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

        ###########
        # Hacks required for CMakeDeps, apparently not be required with CMakeDeps2 in the future sometime
        # https://github.com/conan-io/conan-center-index/pull/10776#issuecomment-1496800353
        # https://github.com/conan-io/conan-center-index/pull/10776#issuecomment-1499403634
        # Thanks to Eric for the fix: https://github.com/EricAtORS/conan-center-index/commit/a1cdc0803dca4fbff03393ee7324ee354b857789

        # fix detecting glew shared status
        if "glew" in self.dependencies:
            replace_in_file(self, os.path.join(self.source_folder, "ThirdParty", "glew", "CMakeLists.txt"),
                'set(VTK_GLEW_SHARED "${vtkglew_is_shared}")',
                f'set(VTK_GLEW_SHARED "{ "ON" if self.dependencies["glew"].options.shared else "OFF"}")'
            )

        # fix detecting freetype shared status
        if "freetype" in self.dependencies:
            replace_in_file(self, os.path.join(self.source_folder, "ThirdParty", "freetype", "CMakeLists.txt"),
                'set(VTK_FREETYPE_SHARED "${vtkfreetype_is_shared}")',
                f'set(VTK_FREETYPE_SHARED "{ "ON" if self.dependencies["freetype"].options.shared else "OFF"}")'
            )

        # fix detecting jsoncpp shared status
        if "jsoncpp" in self.dependencies:
            replace_in_file(self, os.path.join(self.source_folder, "ThirdParty", "jsoncpp", "CMakeLists.txt"),
             'set(VTK_JSONCPP_SHARED "${vtkjsoncpp_is_shared}")',
             f'set(VTK_JSONCPP_SHARED "{ "ON" if self.dependencies["jsoncpp"].options.shared else "OFF"}")'
            )

        # fix detecting lzma shared status (note: conan calls this xz_utils)
        if "xz_utils" in self.dependencies:
            replace_in_file(self, os.path.join(self.source_folder, "ThirdParty", "lzma", "CMakeLists.txt"),
             'set(LZMA_BUILT_AS_DYNAMIC_LIB "${vtklzma_is_shared}")',
             f'set(LZMA_BUILT_AS_DYNAMIC_LIB "{ "ON" if self.dependencies["xz_utils"].options.shared else "OFF"}")'
            )
        ###########


        cmake = CMake(self)
        cmake.configure()
        cmake.build()


    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "vtk", f"conan-official-{self.name}-variables.cmake")


    # NOTE: Could load our generated modules-src.json from the recipe folder,
    #  or it could load the generated modules.json file that was built by VTK and stored in the package folder.
    def _vtkmods(self, filename):
        # parse the modules.json file and generate a list of components
        modfile = load(self, filename)
        vtkmods = json.loads(modfile)

        def add_missing(fake_module, modules_that_depend_on_it, condition):
            if fake_module in vtkmods["modules"]:
                raise ConanException(f"Did not expect to find {fake_module} in modules.json - please investigate and adjust recipe")

            # module_that_depends_on_it requires fake_module as a dependency
            has_dependency = False
            for mod in modules_that_depend_on_it:
                if mod in vtkmods["modules"]:
                    vtkmods["modules"][mod]["depends"].append(fake_module)
                    has_dependency = True

            if has_dependency:
                vtkmods["modules"][fake_module] = {
                        "library_name": "EXTERNAL_LIB",
                        "depends": [],
                        "private_depends": [],
                        "kit": None,
                        "condition": condition,
                        "groups": []
                        }

        # TODO consider changing these to eg conan_QtOpenGL
        # GUISupportQt requires Qt6::QtOpenGL as a dependency
        add_missing("VTK::QtOpenGL",    ["VTK::GUISupportQt"],                     "")
        add_missing("VTK::xorg-system", ["VTK::RenderingCore"],                    "conan_Linux_FreeBSD")  # my own special condition
        add_missing("VTK::openvr",      ["VTK::RenderingOpenVR"],                  "")
        add_missing("VTK::qt",          ["VTK::RenderingQt", "VTK::GUISupportQt"], "")

        # print("MODULES:" + json.dumps(vtkmods,indent=2))
        return vtkmods


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
        # NOTE: This is the file generated by VTK's build, NOT our pre-generated json file.
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

        ### VTK AUTOINIT ###
        # records each implements --> [many modules]
        # This function is called for each module, with a list of the things that this implements.
        # VTK has a special factory registration system, and modules that implement others have to be registered.
        # This mechanism was encoded into VTK's cmake autoinit system, which we (probably) can't use in a conan context.
        # So, we will implement the required autoinit registration things here.
        #
        # This recipe will ultimately generate special header files that contain lines like:
        #       #define vtkRenderingCore_AUTOINIT 2(vtkRenderingFreeType, vtkInteractionStyle)
        #           (this module is implemented)              (by these modules)
        #                IMPLEMENTED         by                 IMPLEMENTING
        #
        # There is one header per implementable module, and each user of an implementing-module must
        # have a special #define that tells the VTK system where this header is.  The header will be
        # included into the compilation and the autoinit system will register the implementing-module.
        #
        # But the trick is the library comsumer will only declare they want to use an implementing module
        # (eg vtkRenderingOpenGL2) but will not use that module directly.
        # Instead, they will only use vtkRenderingCore and expect the OpenGL2 module to be magically built
        # by the core factory.  OpenGL2 module has to register with the Core module, without the library
        # comsumer specifically calling the registration.
        #
        # VTK's cmake seems to generate headers for different combinations of components,
        #   so they need to create a unique autoinit file when a downstream consumer calls cmake function
        #   vtk_module_autoinit(TARGETS <target>... MODULES <module>...), so each target must know ALL
        #   of the vtk modules they will use (at cmake-time), and a unique header will be made for that combination.
        #  That header will be #included via a clever define for that target.
        #
        # This won't work in our case, and that would only work for cmake consumers.
        #
        # So I'm going to try a different approach:
        #  * define a header for all possible combinations of implementing-modules for a implemented-module.
        #  * use a define for each of the implementing-modules.  If a target is using that implementing-module,
        #     it will activate the autoinit for that module thanks to the #define flag
        #
        # Note that we can't just register every possible module, as not every possible module will be linked to the exe.
        #
        # Also note we have to be clever with the ordering of the combinations, as we only want to pick ONE of the combos.
        #
        # Example of a 2-module combination autoinit file:
        ################
        ##  #if 0
        ##
        ##  #elif defined(VTK_CONAN_WANT_AUTOINIT_vtkRenderingOpenGL2) && defined(VTK_CONAN_WANT_AUTOINIT_vtkInteractionStyle)
        ##  #  define vtkRenderingCore_AUTOINIT 2(vtkRenderingOpenGL2,vtkInteractionStyle)
        ##
        ##  #elif defined(VTK_CONAN_WANT_AUTOINIT_vtkRenderingOpenGL2)
        ##  #  define vtkRenderingCore_AUTOINIT 1(vtkRenderingOpenGL2)
        ##
        ##  #elif defined(VTK_CONAN_WANT_AUTOINIT_vtkInteractionStyle)
        ##  #  define vtkRenderingCore_AUTOINIT 1(vtkInteractionStyle)
        ##
        ##  #endif
        ################
        # 
        # WARNING: this code is a partial duplication from package_info(),
        #    it has to be out here to generate the autoinit file for packaging,
        #    AND we have to redo most of the loop code in package_info
        #    to compute the components etc.
        #  This could have probably been done in a more modular way.
        #
        existing_libs = collect_libs(self, folder="lib")

        # Note: loads the json file generated during the build, not the captured modules file
        # from the source.  If the resulting modules file is missing some of our requirements (somehow),
        # then conan may complain that a requirement wasn't used by a component and give an error.
        # In which case, if we can't figure out the real future information, we can instead
        # use the original captured json file from the recipe here.
        vtkmods = self._vtkmods(os.path.join(self.package_folder,"lib","conan","modules.json"))

        enabled_kits = []
        for kit_name in vtkmods["kits"]:
            kit = kit_name.split(':')[2]
            kit_enabled = vtkmods["kits"][kit_name]["enabled"]
            if kit_enabled:
                enabled_kits.append(kit)

        #
        autoinits = {}
        def autoinit_add_implements_package( comp, implements ):
            for vtk_implemented in implements:
                implemented = "vtk" + vtk_implemented.split(':')[2]
                vtkcomp = "vtk" + comp

                # print(f"ADDING AUTOINIT {implemented} --> {vtkcomp}")

                if implemented not in autoinits:
                    autoinits[implemented] = []
                if vtkcomp not in autoinits[implemented]:
                    autoinits[implemented].append( "vtk" + comp )


        for module_name in vtkmods["modules"]:
            comp = module_name.split(':')[2]
            comp_libname = vtkmods["modules"][module_name]["library_name"] + self._lib_suffix
            comp_kit = vtkmods["modules"][module_name]["kit"]
            if comp_kit is not None:
                comp_kit = comp_kit.split(':')[2]

            has_lib = comp_libname in existing_libs
            use_kit = comp_kit and comp_kit in enabled_kits

            # sanity check should be one or the other... not true for both
            if has_lib == use_kit and has_lib:
                raise ConanException(f"Logic Error: Component '{module_name}' has both a library and an enabled kit")

            if has_lib or use_kit:
                self.output.info("Processing module {}{}".format(module_name, f" (in kit {comp_kit})" if use_kit else ""))
                # Add any required autoinit definitions for this component
                autoinit_add_implements_package( comp, vtkmods["modules"][module_name]["implements"] )



        # write those special autoinit header files
        for implemented in autoinits:
            content = "#if 0\n\n"
            all_impls = autoinits[implemented]
            for L in reversed(range(1, len(all_impls)+1)):
                for subset in itertools.combinations(all_impls, L):
                    # print(subset)
                    num = len(subset)
                    impls = ','.join(subset)
                    gateways = [f"defined(VTK_CONAN_WANT_AUTOINIT_{comp})" for comp in subset]
                    content += "#elif " + " && ".join(gateways) + "\n"
                    content += f"#  define {implemented}_AUTOINIT {num}({impls})\n\n"
            content += "#endif\n"
            save(self, os.path.join(self.package_folder, "include", "vtk", "vtk-conan", f"vtk_autoinit_{implemented}.h"), content)



    def package_info(self):
        # auto-include these .cmake files (generated by conan)
        vtk_cmake_build_modules = [self._module_file_rel_path]
        self.cpp_info.names["cmake_find_package"] = "VTK"
        self.cpp_info.names["cmake_find_package_multi"] = "VTK"
        self.cpp_info.set_property("cmake_file_name", "VTK")
        self.cpp_info.set_property("cmake_target_name", "VTK::VTK")

        self.cpp_info.builddirs = [os.path.join("lib", "cmake", "vtk")]
        self.cpp_info.set_property("cmake_build_modules", vtk_cmake_build_modules)

        existing_libs = collect_libs(self, folder="lib")

        # Specify what VTK 3rd party targets we are supplying with conan packages
        # Note that we aren't using cmake_package::cmake_component here, this is for conan so we use conan package names.
        thirds = self._third_party()

        vtkmods = self._vtkmods(os.path.join(self.package_folder,"lib","conan","modules.json"))

        self.output.info("All module keys: {}".format(vtkmods["modules"].keys()))
        self.output.info("All kits keys: {}".format(vtkmods["kits"].keys()))
        self.output.info(f"Found libs: {existing_libs}")

        enabled_kits = []

        # Kits are always exported.
        #  If enabled, they will have a libname, and components will depend on them.
        #  If disabled, they will NOT have a libname, and will depend on their components.

        for kit_name in vtkmods["kits"]:
            kit = kit_name.split(':')[2]
            kit_enabled = vtkmods["kits"][kit_name]["enabled"]
            kit_libname = "vtk" + kit  # guess this, as json has empty library_name for kits
            self.output.info(f"Processing kit {kit_name} ({'enabled' if kit_enabled else 'disabled'})")
            if kit_enabled:
                # print(f"1 Adding component {kit}")
                self.cpp_info.components[kit].set_property("cmake_target_name", kit_name)
                self.cpp_info.components[kit].names["cmake_find_package"] = kit
                self.cpp_info.components[kit].names["cmake_find_package_multi"] = kit
                self.cpp_info.components[kit].libs = [kit_libname]
                enabled_kits.append(kit)
                # requires are added in the next loop, if disabled

        self.output.info("Processing modules")


        def autoinit_add_implements_packinfo( comp, implements ):
            for vtk_implemented in implements:
                implemented = "vtk" + vtk_implemented.split(':')[2]
                vtkcomp = "vtk" + comp
                headerdef = f'{implemented}_AUTOINIT_INCLUDE="vtk-conan/vtk_autoinit_{implemented}.h"'
                cmddef = f"VTK_CONAN_WANT_AUTOINIT_vtk{comp}"

                # print(f"ADDING AUTOINIT {implemented} --> {vtkcomp}")

                # print(f"2 Adding component {comp}")
                if headerdef not in self.cpp_info.components[comp].defines:
                    self.cpp_info.components[comp].defines.append(headerdef)
                if cmddef    not in self.cpp_info.components[comp].defines:
                    self.cpp_info.components[comp].defines.append(cmddef)


        for module_name in vtkmods["modules"]:
            comp = module_name.split(':')[2]
            comp_libname = vtkmods["modules"][module_name]["library_name"] + self._lib_suffix
            comp_kit = vtkmods["modules"][module_name]["kit"]
            if comp_kit is not None:
                comp_kit = comp_kit.split(':')[2]

            has_lib = comp_libname in existing_libs
            use_kit = comp_kit and comp_kit in enabled_kits

            # sanity check should be one or the other... not true for both
            if has_lib == use_kit and has_lib:
                raise ConanException(f"Logic Error: Component '{module_name}' has both a library and an enabled kit")

            if has_lib or use_kit:
                self.output.info("Processing module {}{}".format(module_name, f" (in kit {comp_kit})" if use_kit else ""))
                # Add any required autoinit definitions for this component
                autoinit_add_implements_packinfo( comp, vtkmods["modules"][module_name]["implements"] )
                # print(f"3 Adding component {comp}")
                self.cpp_info.components[comp].set_property("cmake_target_name", module_name)
                if has_lib:
                    self.cpp_info.components[comp].libs = [comp_libname]
                if comp_kit is not None:
                    if has_lib:
                        self.output.info(f"Component {comp_kit} requires {comp}")
                        self.cpp_info.components[comp_kit].requires.append(comp)
                    else:
                        self.output.info(f"Component {comp} requires {comp_kit}")
                        self.cpp_info.components[comp].requires.append(comp_kit)
                self.cpp_info.components[comp].names["cmake_find_package"] = comp
                self.cpp_info.components[comp].names["cmake_find_package_multi"] = comp
                # not sure how to be more specific here, the modules.json doesn't specify which other modules are required
            elif comp in thirds:
                # print(f"4 Adding component {comp}")
                extern = thirds[comp]
                self.cpp_info.components[comp].set_property("cmake_target_name", module_name)
                self.output.info(f"Component {comp} requires EXTERNAL {extern[2]}")
                self.cpp_info.components[comp].requires.append(extern[2])
            else:
                self.output.warning(f"Skipping module (lib file does not exist, or no kit) {module_name}")


        self.output.info("Components:")
        for dep in self.cpp_info.components:
            self.output.info(f"   {dep}")
        self.output.info("-----------")

        # second loop for internal dependencies
        for module_name in vtkmods["modules"]:
            comp = module_name.split(':')[2]
            if comp in self.cpp_info.components:

                # always depend on the headers mini-module
                # which also includes the cmake extra file definitions (declared afterwards)
                # print(f"5 Adding component {comp}")
                self.cpp_info.components[comp].requires.append("headers")

                # these are the public depends + private depends
                # FIXME should private be added as a different kind of private-requires?
                for section in ["depends", "private_depends"]:
                    for dep in vtkmods["modules"][module_name][section]:
                        depname = dep.split(':')[2]
                        if depname in self.cpp_info.components:
                            self.output.info(f"{comp}   depends on {depname}")
                            self.cpp_info.components[comp].requires.append(depname)
                        elif depname in thirds:
                            extern = thirds[depname]
                            self.output.info(f"{comp}   depends on external {dep} --> {extern[2]}")
                            self.cpp_info.components[comp].requires.append(extern[2])
                        else:
                            self.output.info(f"{comp}   skipping depends (component does not exist): {dep}")

                # DEBUG # self.output.info("  Final deps: {}".format(self.cpp_info.components[comp].requires))

                # print(f"6 Adding component {comp}")
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
