# TODO: per-vtk-version requirements for each dependency version - currently all in-recipe... interleaved list?  yml?  or as it is?
# TODO consider changing fake-modules (introduced for dependency management) from QtOpenGL to eg conan_QtOpenGL

# RECIPE MAINTAINER NOTES:
#   There are readme-*.md in the recipe folder.
#
# General recipe design notes: readme-recipe-design.md
# How to add a new version: readme-new-version.md
# How to build a dependency through conan: readme-support-dependency.md

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration, ConanException
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir, save, rename, collect_libs, load, replace_in_file
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

from pathlib import Path
import itertools  # for autoinit header generation
import json  # for auto-component generation
import os
import functools

required_conan_version = ">=1.59.0 <2 || >=2.0.6"


# https://docs.vtk.org/en/latest/api/cmake/ModuleSystem.html#enabling-modules-for-build
# Modules and groups are enable and disable preferences are specified using a 5-way flag setting:
# YES: The module or group must be built.
# NO: The module must not be built. If a YES module has a NO module in its dependency tree, an error is raised.
# WANT: The module should be built. It will not be built, however, if it depends on a NO module.
# DONT_WANT: The module doesn't need to be built. It will be built if a YES or WANT module depends on it.
# DEFAULT: Look at other metadata to determine the status.


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
    no_copy_source = True

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        # Note: there are a LOT of "module_XXX" and "group_XXX" options loaded in init()
        ### Conan package choices ###
        "with_jpeg": ["libjpeg", "libjpeg-turbo"],
        # debug what modules are available and why a module isn't available
        "debug_module": [True, False],
        ### Compile options ###
        "use_64bit_ids": ["Auto", True, False],  # default: 32 bit on 32-bit platforms.  64 on 64-bit platforms.
        "enable_kits": [True, False],  # VTK_ENABLE_KITS - smaller set of libraries - ONLY for shared mode
        "enable_logging": [True, False],
        ### Advanced tech ###
        "use_cuda": [True, False],
        "use_memkind": [True, False],
        "use_mpi": [True, False],
        ### SMP ###
        "smp_implementation_type": ["Sequential", "STDThread", "OpenMP", "TBB"],
        "smp_enable_Sequential": [True, False],
        "smp_enable_STDThread": [True, False],
        "smp_enable_OpenMP": [True, False],
        "smp_enable_TBB": [True, False],
        ### Modules ###
        "build_all_modules": [True, False],  # The big one, build everything - good for pre-built CCI
        "enable_remote_modules": [True, False],  # Build modules that exist in Remote folder
        # Currently LookingGlass, DICOM and MomentInvariants filter
        # The default will be off, they should be built externally in the conan world (when available).
        # Qt-specific modules
        "qt_version": ["5", "6"],
        ### Debugging / future proofing ###
        "legacy_remove": [True, False],
        "legacy_silent": [True, False],
        "use_future_const": [True, False],
        "debug_leaks": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        ### Conan package choices ###
        "with_jpeg": "libjpeg",  # the current standard in other packages on CCI
        ### Compile options ###
        "use_64bit_ids": "Auto",
        "enable_kits": False,
        "enable_logging": False,
        ### Advanced tech ###
        "use_cuda": False,
        "use_memkind": False,
        "use_mpi": False,
        ### SMP ###
        "smp_implementation_type": "Sequential",
        "smp_enable_Sequential": False,
        "smp_enable_STDThread": False,
        "smp_enable_OpenMP": False,
        "smp_enable_TBB": False,
        ### Modules ###
        "build_all_modules": True,  # disable to pick+choose modules
        "enable_remote_modules": False,  # see notes above
        # Qt-specific modules
        "qt_version": "6",
        ### Debugging / future proofing ###
        "legacy_remove": False,
        "legacy_silent": False,
        "use_future_const": False,
        "debug_leaks": False,
        "debug_module": False,
    }

    @property
    def _option_overrides(self):
        # special overrides for conan, to configure what we want CCI to build by default
        # TODO many of these could be enabled if the dependencies could be provided by Conan (some already are)
        return {
            # The CommonDataModel must ALWAYS be built, otherwise the VTK build will fail
            "module_CommonDataModel": "YES",
            # Group-enable-web disabled since wrapping_python is disabled
            "group_Web": "NO",
            # these aren't supported yet, need to system-install packages or provide conan packages for each
            "module_IOPDAL": "NO",
            "module_IOPostgreSQL": "NO",
            "module_IOOpenVDB": "NO",
            "module_IOLAS": "NO",
            "module_IOADIOS2": "NO",
            "module_fides": "NO",
            "module_GeovisGDAL": "NO",
            "module_IOGDAL": "NO",
            "module_FiltersOpenTURNS": "NO",
            "module_DomainsMicroscopy": "NO",
            "module_CommonArchive": "NO",
            "module_IOFFMPEG": "NO",  # FFMPEG required
            "module_IOOCCT": "NO",  # OpenCASCADE required
            "module_IOMySQL": "NO",  # MySQL required
            "module_RenderingOpenXR": "NO",  # OpenXR required
            "module_RenderingZSpace": "NO",  # New zSpace device support, not ready for Linux, so just disable by default
            "module_IOODBC": "NO",  # Requires odbc, which probably can be done now, needs fake-module
            "module_IOGeometry": "NO",  # Has a C++20 problem with building
            "module_ioss": "NO",  # Doesn't compile with C++20
            # OpenVR's recipe isn't v2 compatible yet
            "module_openvr": "NO",
            # MPI doesn't build (for me) so disable by default
            "module_mpi": "NO",
            # TODO there is likely a better way to do this ...
            # disable Qt Quick support, by default, for now, because Qt recipe (by default) doesn't build declarative
            "module_GUISupportQtQuick": "NO",
            "module_Python": "NO",
        }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "9",
            "Visual Studio": "15",
            "msvc": "191",
            "clang": "7",
            "apple-clang": "11",
        }

    @property
    def _modules_json_file(self):
        return os.path.join(self.recipe_folder, f"modules-{self.version}.json")

    @property
    @functools.lru_cache()
    def _recipe_modules_info(self):
        return self._vtkmods(self._modules_json_file)

    # NOTE: Could load our generated modules-src.json from the recipe folder,
    #  or it could load the generated modules.json file that was built by VTK and stored in the package folder.
    def _vtkmods(self, filename):
        # parse the modules.json file and generate a list of components
        vtkmods = json.loads(load(self, filename))
        vtkmods = vtkmods["modules"]

        def add_missing(fake_module, modules_that_depend_on_it, condition):
            if fake_module in vtkmods:
                raise ConanException(
                    f"Did not expect to find {fake_module} in modules.json - please investigate and adjust recipe"
                )

            # module_that_depends_on_it requires fake_module as a dependency
            has_dependency = False
            for mod in modules_that_depend_on_it:
                if mod in vtkmods:
                    vtkmods[mod]["depends"].append(fake_module)
                    has_dependency = True

            if has_dependency:
                vtkmods[fake_module] = {
                    "library_name": "EXTERNAL_LIB",
                    "depends": [],
                    "private_depends": [],
                    "kit": None,
                    "condition": condition,
                    "groups": [],
                }

        # TODO consider changing these to eg conan_QtOpenGL
        # GUISupportQt requires Qt6::QtOpenGL as a dependency
        add_missing("VTK::QtOpenGL", ["VTK::GUISupportQt"], "")
        add_missing("VTK::stub-system-display", ["VTK::RenderingCore"], "")
        add_missing("VTK::openvr", ["VTK::RenderingOpenVR"], "")
        add_missing("VTK::qt", ["VTK::RenderingQt", "VTK::GUISupportQt"], "")

        # print("MODULES:" + json.dumps(vtkmods, indent=2))
        return vtkmods

    def _load_options(self, mod_filename):
        groups = set()
        modules = set()
        modules_info = self._vtkmods(mod_filename)
        for mod_with_prefix in modules_info:
            mod = _remove_vtk_prefix(mod_with_prefix)
            modules.add(mod)
            groups.update(modules_info[mod_with_prefix]["groups"])
        return groups, modules

    def _load_all_possible_options_from_modules_files(self):
        groups = set()
        modules = set()
        for mod_filename in Path(self.recipe_folder).glob("modules-*.json"):
            this_version_groups, this_version_modules = self._load_options(mod_filename)
            groups.update(this_version_groups)
            modules.update(this_version_modules)
        return groups, modules

    def _override_options_values(self, new_values):
        overridden = {opt: ["DEFAULT", "YES", "NO", "WANT", "DONT_WANT"] for opt in new_values}
        self.options.update(overridden, new_values)

    def init(self):
        extra_defaults = {}
        # Note: I require the version number to init this recipe's options
        #    Hopefully it is possible to modify conan and pass this version number
        #    through somehow.  It is not yet attached to 'self' at this point,
        #    and is required to be gathered from conan-create --version x.y.z
        #
        # So instead, we will populate with ALL possible options from ALL known versions,
        # and then delete the missing options in config_options()
        #
        all_groups, all_modules = self._load_all_possible_options_from_modules_files()
        extra_defaults.update({f"module_{mod}": "DEFAULT" for mod in all_modules})
        extra_defaults.update({f"group_{group}": "DEFAULT" for group in all_groups})
        extra_defaults.update(self._option_overrides)
        self._override_options_values(extra_defaults)

    def export(self):
        # copy ALL of the modules-x.y.z.json files, as we need them all in config_options()
        copy(self, "modules-*.json", src=self.recipe_folder, dst=self.export_folder)

    def export_sources(self):
        export_conandata_patches(self)

    def _process_modules_conditions(self, modules_info):
        default_overrides = {}

        # look for known CONDITIONS from the vtk.module files
        # If 'default_overrides==None', then do validations and raise errors
        def _check_condition(condition, error_message):
            for mod, info in modules_info.items():
                if condition in info["condition"]:
                    mod_no_prefix = _remove_vtk_prefix(mod)
                    # user insisted this module be built? Error.
                    if self.options.get_safe(f"module_{mod_no_prefix}") == "YES":
                        raise ConanInvalidConfiguration(f"{mod} {error_message}")
                    # else, we force this option to NO
                    default_overrides[f"module_{mod_no_prefix}"] = "NO"

        required_option_message = (
            "can only be enabled with {} (module may have been enabled with group_Web or build_all_modules)"
        )

        if not self.options.use_mpi:
            _check_condition("VTK_USE_MPI", required_option_message.format("use_mpi"))
        if not self.options.enable_logging:
            _check_condition("VTK_ENABLE_LOGGING", required_option_message.format("enable_logging"))
        if self.settings.os == "Windows":
            _check_condition("NOT WIN32", "cannot be enabled on the Windows platform")
        # Note: this is a very simple and dumb test ... the condition could say "NOT MSVC" and it would still match this rule!
        #  But there aren't many conditions and these are just hand-rolled tests to suit.
        if not is_msvc(self):
            _check_condition("NOT WIN32", "can only be enabled with the MSVC compiler")
        return default_overrides

    def _compute_modules_enabled(self, modules_info):
        # NOTE: the order of items in 'groups' is important for the ModuleSystem enable/disable
        #  Do not reorder 'groups' !
        # ie a module's enable/disable is first determined by its groups, which is listed in order of priority
        # (the first group has the highest priority, then descending from there)

        # compute the enabled... implemented based on VTK/Documentation/Doxygen/ModuleSystem.md
        module_states = {}

        # first, init with our recipe options for individual modules and groups
        # print(self.options)

        self.output.info("*** Setting module-enabled based on Groups and build_all_modules ***")

        for mod_with_prefix, module_info in modules_info.items():
            mod_name = _remove_vtk_prefix(mod_with_prefix)
            state = self.options.get_safe(f"module_{mod_name}", default="NO")
            if state == "DEFAULT":
                for group in module_info["groups"]:
                    group_enabled = self.options.get_safe(f"group_{group}", default="NO")
                    if group_enabled != "DEFAULT":
                        state = group_enabled
                        break
                else:
                    state = "WANT" if self.options.build_all_modules else "DONT_WANT"
            # we have our answer for this module, it will be YES/NO/WANT/DONT_WANT
            module_states[mod_with_prefix] = state

        # We now have a lot of YES/NO/WANT/DONT_WANT
        # We now want to resolve the WANT/DONT_WANT into YES/NO

        # From VTK documentation:
        # - `WANT`: The module should be built. It will not be built, however, if it
        #   depends on a `NO` module.
        # - `DONT_WANT`: The module doesn't need to be built. It will be built if a
        #   `YES` or `WANT` module depends on it.

        # use "visited" to know which ones have already had their dependencies checked in depth
        def recurse_depends_has_NO(module_name, visited, last_yes_parent, chain):
            mod_enabled = module_states[module_name]
            if mod_enabled == "NO":
                if last_yes_parent:
                    raise RuntimeError(f"Module collision: {[' --> '.join(chain)]} has {last_yes_parent}=YES and {module_name}=NO")
                return True

            if module_name in visited:
                return mod_enabled == "NO"

            if mod_enabled == "YES":
                last_yes_parent = module_name

            # check: depends, private_depends.
            # optional_depends do not influence this computation
            any_no = False
            mod_info = modules_info[module_name]
            for dep in set(mod_info["depends"] + mod_info["private_depends"]):
                if recurse_depends_has_NO(dep, visited, last_yes_parent, chain + [dep]):
                    # note: not breaking to always check dependencies to catch NO-YES problems
                    any_no = True
            if any_no:
                module_states[module_name] = "NO"
            visited.add(module_name)
            return any_no

        self.output.info("*** Setting modules to NO if dependencies are NO ***")
        for mod_name in module_states:
            recurse_depends_has_NO(mod_name, set(), None, [mod_name])

        self.output.info("*** For all YES and WANT modules, setting all dependencies to YES ***")
        # find all modules that are tagged as YES, and tag all dependencies as YES
        # iterate multiple times rather than building a tree,
        # tagging those whose dependencies have been visited with YES-DONE
        mod_todo = list(module_states.keys())
        while mod_todo:
            mod_name = mod_todo.pop()
            if module_states[mod_name] == "WANT":
                module_states[mod_name] = "YES"
            if module_states[mod_name] == "YES":
                mod_info = modules_info[mod_name]
                for dep in set(mod_info["depends"] + mod_info["private_depends"]):
                    dep_enabled = module_states[dep]
                    if dep_enabled == "NO":
                        raise RuntimeError(f"Module collision, {mod_name} is YES, but dependency {dep} is NO")
                    elif dep_enabled != "YES":
                        module_states[dep] = "YES"
                        # process dependencies in a future pass
                        mod_todo.append(dep)

        self.output.info("*** Setting all WANT / DONT_WANT modules to YES / NO ***")
        # find all modules that are not tagged YES or NO (ie WANT_*) and tag appropriately
        final_module_states = {}
        for mod_with_prefix, state in module_states.items():
            mod_name = _remove_vtk_prefix(mod_with_prefix)
            if state == "WANT":  # if we WANT, then the answer is YES (dependencies don't care)
                final_module_states[f"module_{mod_name}"] = "YES"
            elif state == "DONT_WANT":  # if we don't want, then answer is no (dependencies don't care)
                final_module_states[f"module_{mod_name}"] = "NO"
            elif state == "YES" or state == "NO":
                final_module_states[f"module_{mod_name}"] = state
            else:
                raise RuntimeError(f"Unexpected module-enable flag: {state}")
        return final_module_states

    # delete all options due to system OS reasons,
    # and delete all options that are not part of this version's set of modules/groups
    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        all_groups, all_modules = self._load_all_possible_options_from_modules_files()
        this_version_groups, this_version_modules = self._load_options(self._modules_json_file)
        for group in all_groups:
            if group not in this_version_groups:
                self.options.rm_safe(f"group_{group}")
        for module in all_modules:
            if module not in this_version_modules:
                self.options.rm_safe(f"module_{module}")

    # The user has now set their options,
    # it is time resolve the remaining options based on dependencies and conditions.
    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

        # kissfft - we want the double format (also known as kiss_fft_scalar)
        self.options["kissfft"].datatype = "double"

        self.options["qt"].widgets = True
        self.options["qt"].qtdeclarative = True

        # load our modules info for our particular version
        modules_info = self._recipe_modules_info

        # use the CONDITIONS to disable any options not yet set to YES
        new_option_values = self._process_modules_conditions(modules_info)
        self._override_options_values(new_option_values)

        # now process the dependencies and compute the final module/group enable/disable
        final_modules_enabled = self._compute_modules_enabled(modules_info)
        self._override_options_values(final_modules_enabled)

        # at this point, all module/group options should be set to either YES or NO
        # the options are NOT deleted as it is not always the case that a NO module could not have been YES

    def layout(self):
        cmake_layout(self, src_folder="src")

    @property
    @functools.lru_cache()
    def _third_party(self):
        if self.version == "9.3.1":
            parties = {
                # LEFT field:  target name for linking, will be used as TARGET::TARGET in package_info()
                # RIGHT field: Force the version (for development mode), package/version to require, component requirement
                "cgns":              (False, "cgns/[>=4.3.0]",              ["cgns::cgns"]        ),
                "cli11":             (False, "cli11/[>=2.3.2]",             ["cli11::cli11"]      ),
                "doubleconversion":  (False, "double-conversion/[>=3.2.1]", ["double-conversion::double-conversion"]),
                "eigen":             (False, "eigen/[>=3.4.0]",             ["eigen::eigen"]      ),
                "expat":             (False, "expat/[>=2.6.2 <3]",          ["expat::expat"]      ),
                "exprtk":            (True,  "exprtk/[=0.0.1]",             ["exprtk::exprtk"]    ),  # TODO upgrade to 0.0.2 (there was a problem with first attempt)
                "fast_float":        (False, "fast_float/3.9.0",            ["fast_float::fast_float"]),
                "fmt":               (True,  "fmt/11.0.0",                  ["fmt::fmt"]          ),
                "freetype":          (False, "freetype/[>=2.13.2]",         ["freetype::freetype"]),
                "glew":              (False, "glew/[>=2.2.0]",              ["glew::glew"]        ),
                "hdf5":              (True,  "hdf5/[=1.14.3]",              ["hdf5::hdf5"]        ),  # TODO conflict: netcdf (.1) and cgns (.0)
                "jsoncpp":           (False, "jsoncpp/[>=1.9.4]",           ["jsoncpp::jsoncpp"]  ),
                "kissfft":           (False, "kissfft/[>=131.1.0]",         ["kissfft::kissfft"]  ),
                "libharu":           (False, "libharu/[>=2.4.3]",           ["libharu::libharu"]  ),
                "libproj":           (False, "proj/[>=9.1.1]",              ["proj::proj"]        ),
                "libxml2":           (False, "libxml2/[>=2.12.5 <3]",       ["libxml2::libxml2"]  ),
                "lz4":               (False, "lz4/[>=1.9.4]",               ["lz4::lz4"]          ),
                "lzma":              (False, "xz_utils/5.4.5",              ["xz_utils::xz_utils"]),
                "netcdf":            (False, "netcdf/[>=4.8.1]",            ["netcdf::netcdf"]    ),
                "nlohmannjson":      (False, "nlohmann_json/[>=3]",         ["nlohmann_json::nlohmann_json"]),
                "ogg":               (False, "ogg/[>=1.3.5]",               ["ogg::ogg"]          ),
                "opengl":            (False, "opengl/system",               ["opengl::opengl"]    ),
                "openvr":            (False, "openvr/[>=1.16.8]",           ["openvr::openvr"]    ),
                "png":               (True,  "libpng/[>=1.6 <2]",           ["libpng::libpng"]    ),  # TODO conflict: libharu (.40) and freetype (.42)
                "pugixml":           (False, "pugixml/[>=1.13]",            ["pugixml::pugixml"]  ),
                "sqlite":            (True,  "sqlite3/[=3.45.3]",           ["sqlite3::sqlite3"]  ),  # TODO conflict: qt (3.44.2) and proj (3.44.2)
                "theora":            (False, "theora/[>=1.1.1]",            ["theora::theora"]    ),
                "tiff":              (False, "libtiff/[>=4.4.0]",           ["libtiff::libtiff"]  ),
                "utf8":              (False, "utfcpp/[>=3.2.3]",            ["utfcpp::utfcpp"]    ),
                "zlib":              (False, "zlib/[>=1.2.13]",             ["zlib::zlib"]        ),

                # TODO what module depends on boost?
                # "boost":             (False, "boost/[>=1.82.0]"),

                # TODO what module depends on odbc?
                # "odbc":              (False, "odbc/[>=2.3.11]"),

                # MODULES: zfp, boost and odbc
                # parties["zfp"]     = "zfp/[>=0.5.5]"
            }

            # NOTE: You may NOT be able to just adjust the version numbers in here, without
            #   also adjusting the patch, as the versions are also mentioned in ThirdParty/*/CMakeLists.txt

            if self.options.with_jpeg == "libjpeg":
                parties["jpeg"] = (False, "libjpeg/9e", ["libjpeg::libjpeg"])
            elif self.options.with_jpeg == "libjpeg-turbo":
                parties["jpeg"] = (False, "libjpeg-turbo/[>=2.1.5]", ["libjpeg-turbo::jpeg"])

            qt_components = [
                "qt::qtCore",
                "qt::qtWidgets",
                "qt::qtOpenGL",
                "qt::qtQml",
            ]
            if self.options.qt_version == "5":
                parties["QtOpenGL"] = (False, "qt/[>=5.15.9 <6]", qt_components)
            else:
                parties["QtOpenGL"] = (False, "qt/[>=6.5.0 <7]", qt_components)

            if self.settings.os in ["Linux", "FreeBSD"]:
                parties["stub-system-display"] = (False, "xorg/system", ["xorg::x11", "xorg::xcursor"])
            else:
                pass  # nothing required for other platforms

            return parties

        raise ConanInvalidConfiguration(f"{self.version} not supported by recipe (update _third_party(self))")

    def requirements(self):
        for target, (force, requirement, _) in self._third_party.items():
            if self.options.get_safe(f"module_{target}") == "YES":
                # NOTE: optionally force to break dependency version clashes until CCI deps have been bumped
                # TODO: Change to use [replace_requires] for this to work correctly, locally
                self.output.info(f"Requires: {requirement}")
                self.requires(requirement, force=force, transitive_headers=True, transitive_libs=True)

    def package_id(self):
        # Overridden options have no effect on package_id
        for opt in self._option_overrides.values():
            self.info.options.rm_safe(opt)
        # Group options have been propagated to module options
        for opt, _ in self.info.options.items():
            if opt.startswith("group_"):
                self.info.options.rm_safe(opt)

    def validate(self):
        # Sanity check for option values
        for opt, value in self.options.items():
            if opt.startswith("module_") and str(value) not in ["YES", "NO"]:
                raise ConanException(f"Recipe bug: {self.ref} has invalid option value {opt}={value}. "
                                     "All option values should have been resolved to YES OR NO by now.")

        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.info.settings.compiler), False)
        if minimum_version and Version(self.info.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if not self.options.shared and self.options.enable_kits:
            raise ConanInvalidConfiguration("Kits can only be enabled with shared")

        if "pugixml" in self.dependencies and self.dependencies["pugixml"].options.wchar_mode:
            raise ConanInvalidConfiguration(f"{self.ref} requires pugixml/*:wchar_mode=False")

        if "kissfft" in self.dependencies and self.dependencies["kissfft"].options.datatype != "double":
            raise ConanInvalidConfiguration(f"{self.ref} requires kissfft/*:datatype=double")

        qt = self.dependencies["qt"].options
        if not qt.widgets:
            raise ConanInvalidConfiguration(f"{self.ref} requires qt/*:widgets=True")
        if not qt.qtdeclarative:
            raise ConanInvalidConfiguration(f"{self.ref} requires qt/*:qtdeclarative=True")
        if str(qt.opengl) == "no":
            raise ConanInvalidConfiguration(f"{self.ref} requires qt/*:opengl to not be 'no'")

        if (
            self.options.get_safe("module_GUISupportQtQuick") == "YES"
            and not self.dependencies["qt"].options.qtdeclaritive
        ):
            raise ConanInvalidConfiguration(
                f"{self.ref} has module_GUISupportQtQuick enabled, which requires qt:qtdeclarative=True"
            )

        if self.options.smp_enable_TBB:
            raise ConanInvalidConfiguration(
                f"{self.ref} has smp_enable_TBB enabled. TODO check modules.json for TBB/OpenTBB dependencies and adjust recipe to suit."
            )

    def build_requirements(self):
        if self.options.get_safe("module_libproj"):
            self.tool_requires("sqlite3/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
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
        tc.variables["VTK_BUILD_TESTING"] = False
        tc.variables["VTK_BUILD_EXAMPLES"] = False
        tc.variables["VTK_BUILD_DOCUMENTATION"] = False
        tc.variables["VTK_BUILD_SPHINX_DOCUMENTATION"] = False
        tc.variables["VTK_FORBID_DOWNLOADS"] = True

        # Nothing gets installed without this ON at the moment.
        tc.variables["VTK_INSTALL_SDK"] = True

        #
        # future-proofing for your code
        # disable legacy APIs
        tc.variables["VTK_LEGACY_REMOVE"] = self.options.legacy_remove
        # requires legacy_remove to be off. deprecated APIs will not cause warnings
        tc.variables["VTK_LEGACY_SILENT"] = self.options.legacy_silent
        # use the newer const-correct APIs
        tc.variables["VTK_USE_FUTURE_CONST"] = self.options.use_future_const
        tc.variables["VTK_ENABLE_LOGGING"] = self.options.enable_logging

        # development debugging
        tc.variables["VTK_DEBUG_LEAKS"] = self.options.debug_leaks

        # Enable KITs - Quote: "Compiles VTK into a smaller set of libraries."
        # Quote: "Can be useful on platforms where VTK takes a long time to launch due to expensive disk access."
        tc.variables["VTK_ENABLE_KITS"] = self.options.enable_kits

        tc.variables["VTK_ENABLE_WRAPPING"] = False
        tc.variables["VTK_WRAP_JAVA"] = False
        tc.variables["VTK_WRAP_PYTHON"] = False
        tc.variables["VTK_BUILD_PYI_FILES"] = False  # Warning: this fails on 9.2.2 if rendering is not enabled.
        tc.variables["VTK_USE_TK"] = False  # requires wrap_python

        #### CUDA / MPI / MEMKIND ####
        tc.variables["VTK_USE_CUDA"] = self.options.use_cuda
        tc.variables["VTK_USE_MEMKIND"] = self.options.use_memkind
        tc.variables["VTK_USE_MPI"] = self.options.use_mpi

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
        if self.options.get_safe("module_netcdf") == "YES":
            tc.variables["NetCDF_HAS_PARALLEL"] = self.dependencies["hdf5"].options.parallel

        # https://gitlab.kitware.com/vtk/vtk/-/blob/master/Documentation/dev/build.md
        # TODO try VTK_USE_VIDEO_FOR_WINDOWS   for video capture
        # TODO try VTK_USE_VIDEO_FOR_WINDOWS_CAPTURE   for video capture
        # TODO try VTK_USE_MICROSOFT_MEDIA_FOUNDATION   for video capture (MP4)

        ##### QT ######
        # QT has a few modules, we'll be specific
        tc.variables["VTK_QT_VERSION"] = self.options.qt_version

        # Setup ALL our discovered modules
        groups, modules = self._load_options(self._modules_json_file)
        for mod in modules:
            tc.variables[f"VTK_MODULE_ENABLE_VTK_{mod}"] = self.options.get_safe(f"module_{mod}", default="NO")
        # we set all groups to "NO" - every module is specified
        # we want ALL modules to be tightly controlled - no surprises
        for group in groups:
            tc.variables[f"VTK_GROUP_ENABLE_VTK_{group}"] = self.options.get_safe(f"group_{group}", default="NO")

        ##### SMP parallelism ####  Sequential  STDThread  OpenMP  TBB
        # Note that STDThread seems to be available by default
        tc.variables["VTK_SMP_IMPLEMENTATION_TYPE"] = self.options.smp_implementation_type
        # Change the mode during runtime, if you enable the backends like so:
        tc.variables["VTK_SMP_ENABLE_Sequential"] = self.options.smp_enable_Sequential
        tc.variables["VTK_SMP_ENABLE_STDThread"] = self.options.smp_enable_STDThread
        tc.variables["VTK_SMP_ENABLE_OpenMP"] = self.options.smp_enable_OpenMP
        tc.variables["VTK_SMP_ENABLE_TBB"] = self.options.smp_enable_TBB

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
            tc.variables[f"VTK_MODULE_USE_EXTERNAL_VTK_{lib}"] = False

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
            "qt",  # qt can be 5 or 6, so we need to avoid matching on SameMajorVersion
        ]
        for req in allow_newer_major_versions_for_these_requirements:
            deps.set_property(req, "cmake_config_version_compat", "AnyNewerVersion")

        # VTK expects different find_package() filenames and targets (check ThirdParty/LIB/CMakeLists.txt)
        cmake_file_names = {
            "netcdf": "NetCDF",
            "lz4": "LZ4",
            "xz_utils": "LZMA",
            "freetype": "Freetype",
            "expat": "EXPAT",
            "libharu": "LibHaru",
            "exprtk": "ExprTk",
            "openvr": "OpenVR",
            "theora": "THEORA",
            "proj": "LibPROJ",
        }
        cmake_target_names = {
            "eigen": "Eigen3::Eigen3",
            "expat": "EXPAT::EXPAT",
            "exprtk": "ExprTk::ExprTk",
            "freetype": "Freetype::Freetype",
            "libharu": "LibHaru::LibHaru",
            "lz4": "LZ4::LZ4",
            "netcdf": "NetCDF::NetCDF",
            "openvr": "OpenVR::OpenVR",
            "proj": "LibPROJ::LibPROJ",
            "theora": "THEORA::THEORA",
            "theora::theoradec": "THEORA::DEC",
            "theora::theoraenc": "THEORA::ENC",
            "utfcpp": "utf8cpp::utf8cpp",
            "xz_utils": "LZMA::LZMA",
        }
        for dep, file_name in cmake_file_names.items():
            deps.set_property(dep, "cmake_file_name", file_name)
        for dep, target_name in cmake_target_names.items():
            deps.set_property(dep, "cmake_target_name", target_name)

        # VTK also wants a variable LibPROJ_MAJOR_VERSION, which conan has as proj_VERSION_MAJOR
        if "proj" in self.dependencies:
            tc.variables["LibPROJ_MAJOR_VERSION"] = Version(self.dependencies["proj"].ref.version).major

        # double-version has their headers in <double-conversion/header>
        # but VTK expects just <header>
        if "double-conversion" in self.dependencies:
            double_conversion = self.dependencies["double-conversion"].cpp_info
            double_conversion.includedirs[0] = os.path.join(double_conversion.includedirs[0], "double-conversion")
        ###

        tc.generate()
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

        ###########
        # Hacks required for CMakeDeps, apparently not be required with CMakeDeps2 in the future sometime
        # https://github.com/conan-io/conan-center-index/pull/10776#issuecomment-1496800353
        # https://github.com/conan-io/conan-center-index/pull/10776#issuecomment-1499403634
        # Thanks to Eric for the fix: https://github.com/EricAtORS/conan-center-index/commit/a1cdc0803dca4fbff03393ee7324ee354b857789
        # fix detecting glew shared status
        third_party_dir = os.path.join(self.source_folder, "ThirdParty")
        on_if_shared = lambda dep: "ON" if self.dependencies[dep].options.shared else "OFF"
        if "glew" in self.dependencies:
            replace_in_file(self, os.path.join(third_party_dir, "glew", "CMakeLists.txt"),
                            'set(VTK_GLEW_SHARED "${vtkglew_is_shared}")',
                            f'set(VTK_GLEW_SHARED "{on_if_shared("glew")}")')
        # fix detecting freetype shared status
        if "freetype" in self.dependencies:
            replace_in_file(self, os.path.join(third_party_dir, "freetype", "CMakeLists.txt"),
                            'set(VTK_FREETYPE_SHARED "${vtkfreetype_is_shared}")',
                            f'set(VTK_FREETYPE_SHARED "{on_if_shared("freetype")}")')
        # fix detecting jsoncpp shared status
        if "jsoncpp" in self.dependencies:
            replace_in_file(self, os.path.join(third_party_dir, "jsoncpp", "CMakeLists.txt"),
                            'set(VTK_JSONCPP_SHARED "${vtkjsoncpp_is_shared}")',
                            f'set(VTK_JSONCPP_SHARED "{on_if_shared("jsoncpp")}")')
        # fix detecting lzma shared status (note: conan calls this xz_utils)
        if "xz_utils" in self.dependencies:
            replace_in_file(self, os.path.join(third_party_dir, "lzma", "CMakeLists.txt"),
                            'set(LZMA_BUILT_AS_DYNAMIC_LIB "${vtklzma_is_shared}")',
                            f'set(LZMA_BUILT_AS_DYNAMIC_LIB "{on_if_shared("xz_utils")}")')
        ###########

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    @property
    def _installed_modules_json_path(self):
        return os.path.join(self.package_folder, "lib", "conan", "modules.json")

    @property
    @functools.lru_cache()
    def _installed_modules_info(self):
        return self._vtkmods(self._installed_modules_json_path)

    @property
    @functools.lru_cache()
    def _installed_kits_info(self):
        kits = json.loads(load(self, self._installed_modules_json_path))["kits"]
        return {kit: kits[kit]["enabled"] for kit in kits}

    @property
    @functools.lru_cache()
    def _enabled_kits(self):
        return [kit for kit, enabled in self._installed_kits_info.items() if enabled]

    @property
    def _lib_suffix(self):
        return "d" if self.settings.os == "Windows" and self.settings.build_type == "Debug" else ""

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "vtk", f"conan-official-{self.name}-variables.cmake")

    @property
    @functools.lru_cache()
    def _existing_libs(self):
        return collect_libs(self, folder="lib")

    def package(self):
        cmake = CMake(self)
        cmake.install()

        # VTK installs the licenses under the share/licenses/VTK directory, move it
        rename(self, os.path.join(self.package_folder, "share", "licenses", "VTK"),
                     os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "share"))

        # delete VTK-installed cmake files
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

        # make a copy of the modules.json, we use that in package_info
        # NOTE: This is the file generated by VTK's build, NOT our pre-generated json file.
        copy(self, "modules.json",
             self.build_folder,
             os.path.join(self.package_folder, "lib", "conan"),
             keep_path=False)

        # create a cmake file with our special variables
        save(self, os.path.join(self.package_folder, self._module_file_rel_path),
             f"set(VTK_ENABLE_KITS {self.options.enable_kits})\n")

        self._generate_autoinits()

    def _generate_autoinits(self):
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
        # But the trick is the library consumer will only declare they want to use an implementing module
        # (eg vtkRenderingOpenGL2) but will not use that module directly.
        # Instead, they will only use vtkRenderingCore and expect the OpenGL2 module to be magically built
        # by the core factory.  OpenGL2 module has to register with the Core module, without the library
        # consumer specifically calling the registration.
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

        # WARNING: this code is a partial duplication from package_info(),
        #    it has to be out here to generate the autoinit file for packaging,
        #    AND we have to redo most of the loop code in package_info
        #    to compute the components etc.
        #  This could have probably been done in a more modular way.
        #

        # Note: loads the json file generated during the build, not the captured modules file
        # from the source.  If the resulting modules file is missing some of our requirements (somehow),
        # then conan may complain that a requirement wasn't used by a component and give an error.
        # In which case, if we can't figure out the real future information, we can instead
        # use the original captured json file from the recipe here.

        #
        autoinits = {}

        def autoinit_add_implements_package(comp, implements):
            for vtk_implemented in implements:
                implemented = "vtk" + _remove_vtk_prefix(vtk_implemented)
                vtkcomp = "vtk" + comp
                if implemented not in autoinits:
                    autoinits[implemented] = []
                if vtkcomp not in autoinits[implemented]:
                    autoinits[implemented].append("vtk" + comp)

        for module_name, module_info in self._installed_modules_info.items():
            comp = _remove_vtk_prefix(module_name)
            comp_libname = module_info["library_name"] + self._lib_suffix
            comp_kit = module_info["kit"]
            if comp_kit is not None:
                comp_kit = _remove_vtk_prefix(comp_kit)
            has_lib = comp_libname in self._existing_libs
            use_kit = comp_kit and comp_kit in self._enabled_kits
            # sanity check should be one or the other... not true for both
            if has_lib == use_kit and has_lib:
                raise ConanException(f"Logic Error: Component '{module_name}' has both a library and an enabled kit")
            if has_lib or use_kit:
                kit_info = f" (in kit {comp_kit})" if use_kit else ""
                self.output.info(f"Processing module {module_name}{kit_info}")
                # Add any required autoinit definitions for this component
                autoinit_add_implements_package(comp, module_info["implements"])

        # write those special autoinit header files
        for implemented, all_impls in autoinits.items():
            content = "#if 0\n\n"
            for L in reversed(range(1, len(all_impls) + 1)):
                for subset in itertools.combinations(all_impls, L):
                    num = len(subset)
                    impl = ",".join(subset)
                    expression = ' && '.join(f"defined(VTK_CONAN_WANT_AUTOINIT_{comp})" for comp in subset)
                    content += f"#elif {expression}\n"
                    content += f"#  define {implemented}_AUTOINIT {num}({impl})\n\n"
            content += "#endif\n"
            autoinit_file = os.path.join(self.package_folder, "include", "vtk", "vtk-conan", f"vtk_autoinit_{implemented}.h")
            save(self, autoinit_file, content)


    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "VTK")
        self.cpp_info.set_property("cmake_target_name", "VTK::VTK")

        # auto-include these .cmake files (generated by conan)
        vtk_cmake_build_modules = [self._module_file_rel_path]
        self.cpp_info.builddirs = [os.path.join("lib", "cmake", "vtk")]
        self.cpp_info.set_property("cmake_build_modules", vtk_cmake_build_modules)

        self.output.info(f"All module keys: {sorted(self._installed_modules_info)}")
        self.output.info(f"All kits keys: {sorted(self._installed_kits_info)}")
        self.output.info(f"Found libs: {self._existing_libs}")

        # Kits are always exported.
        #  If enabled, they will have a libname, and components will depend on them.
        #  If disabled, they will NOT have a libname, and will depend on their components.

        for kit_name, kit_enabled in self._installed_kits_info.items():
            self.output.info(f"Processing kit {kit_name} ({'enabled' if kit_enabled else 'disabled'})")
            if kit_enabled:
                kit = _remove_vtk_prefix(kit_name)
                self.cpp_info.components[kit].set_property("cmake_target_name", kit_name)
                # guess this, as json has empty library_name for kits
                self.cpp_info.components[kit].libs = [f"vtk{kit}"]
                # requires are added in the next loop, if disabled

        self.output.info("Processing modules")

        def autoinit_add_implements_packinfo(comp, implements):
            for vtk_implemented in implements:
                implemented = "vtk" + _remove_vtk_prefix(vtk_implemented)
                headerdef = f'{implemented}_AUTOINIT_INCLUDE="vtk-conan/vtk_autoinit_{implemented}.h"'
                cmddef = f"VTK_CONAN_WANT_AUTOINIT_vtk{comp}"
                if headerdef not in self.cpp_info.components[comp].defines:
                    self.cpp_info.components[comp].defines.append(headerdef)
                if cmddef not in self.cpp_info.components[comp].defines:
                    self.cpp_info.components[comp].defines.append(cmddef)

        for module_name, module_info in self._installed_modules_info.items():
            comp = _remove_vtk_prefix(module_name)
            comp_libname = module_info["library_name"] + self._lib_suffix
            comp_kit = module_info["kit"]
            if comp_kit is not None:
                comp_kit = _remove_vtk_prefix(comp_kit)
            has_lib = comp_libname in self._existing_libs
            use_kit = comp_kit and comp_kit in self._enabled_kits
            # sanity check should be one or the other... not true for both
            if has_lib == use_kit and has_lib:
                raise ConanException(f"Logic Error: Component '{module_name}' has both a library and an enabled kit")
            if has_lib or use_kit:
                kit_info = f" (in kit {comp_kit})" if use_kit else ""
                self.output.info(f"Processing module {module_name}{kit_info}")
                # Add any required autoinit definitions for this component
                autoinit_add_implements_packinfo(comp, module_info["implements"])
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
                # not sure how to be more specific here, the modules.json doesn't specify which other modules are required
            elif comp in self._third_party:
                _, _, extern = self._third_party[comp]
                self.cpp_info.components[comp].set_property("cmake_target_name", module_name)
                self.output.info(f"Component {comp} requires EXTERNAL {extern}")
                self.cpp_info.components[comp].requires.extend(extern)
            else:
                self.output.warning(f"Skipping module (lib file does not exist, or no kit) {module_name}")

        self.output.info("Components:")
        for dep in self.cpp_info.components:
            self.output.info(f"   {dep}")
        self.output.info("-----------")

        # second loop for internal dependencies
        for module_name, module_info in self._installed_modules_info.items():
            comp = _remove_vtk_prefix(module_name)
            if comp not in self.cpp_info.components:
                self.output.warning(f"Skipping module, did not become a component: {module_name}")
                continue

            # always depend on the headers mini-module
            # which also includes the cmake extra file definitions (declared afterwards)
            self.cpp_info.components[comp].requires.append("headers")

            # these are the public depends ONLY
            # For consumers of this VTK recipe, they need to also link the public depends of a module.
            # Optional and Private depends (in VTK's world) are only used when building VTK.
            # We still need to include the private_depends for the linker to correctly gather the libs.
            # But, this will also expose private header includes for the consumer.
            for dep in module_info["depends"] + module_info["private_depends"]:
                depname = _remove_vtk_prefix(dep)
                if depname in self.cpp_info.components:
                    self.output.info(f"{comp}   depends on {depname}")
                    self.cpp_info.components[comp].requires.append(depname)
                elif depname in self._third_party:
                    _, _, extern = self._third_party[depname]
                    self.output.info(f"{comp}   depends on external {dep} --> {extern}")
                    self.cpp_info.components[comp].requires.extend(extern)
                else:
                    self.output.info(f"{comp}   skipping depends (component does not exist): {dep}")

            self.cpp_info.components[comp].set_property("cmake_build_modules", vtk_cmake_build_modules)
            if self.settings.os in ("FreeBSD", "Linux"):
                self.cpp_info.components[comp].system_libs.extend(["dl", "pthread", "m"])

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


def _remove_vtk_prefix(mod):
    if not mod.startswith("VTK::"):
        raise RuntimeError(f"RECIPE BUG: Expected VTK module ({mod}) to start with VTK::")
    return mod[5:]
