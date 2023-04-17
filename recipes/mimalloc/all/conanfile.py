from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rm, rmdir, replace_in_file, save, collect_libs
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime, VCVars
from conan.tools.scm import Version
import os
import shutil
import textwrap

required_conan_version = ">=1.53.0"


class MimallocConan(ConanFile):
    name = "mimalloc"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/microsoft/mimalloc"
    description = "mimalloc is a compact general purpose allocator with excellent performance."
    topics = ("mimalloc", "allocator", "performance", "microsoft")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "secure": [True, False],
        "override": [True, False],
        "inject": [True, False],
        "single_object": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "secure": False,
        "override": False,
        "inject": False,
        "single_object": False,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "Visual Studio": "15",
            "msvc": "191",
            "clang": "5",
            "apple-clang": "10",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        # single_object and inject are options
        # only when overriding on Unix-like platforms:
        if is_msvc(self):
            del self.options.single_object
            del self.options.inject

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

            # single_object is valid only for static
            # override:
            self.options.rm_safe("single_object")

        # inject is valid only for Unix-like dynamic override:
        if not self.options.shared:
            self.options.rm_safe("inject")

        # single_object and inject are valid only when
        # overriding on Unix-like platforms:
        if not self.options.override:
            self.options.rm_safe("single_object")
            self.options.rm_safe("inject")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        # Currently, mimalloc some version do not work properly with shared MD builds.
        # https://github.com/conan-io/conan-center-index/pull/10333#issuecomment-1114110046
        if  self.version in ["1.7.6", "1.7.7", "2.0.6", "2.0.7"] and \
            self.options.shared and \
            is_msvc(self) and \
            not is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration(
                f"Currently, {self.ref} doesn't work properly with shared MD builds in CCI. Contributions welcomed")

        # Shared overriding requires dynamic runtime for MSVC:
        if self.options.override and \
           self.options.shared and \
           is_msvc(self) and \
           is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration(
                "Dynamic runtime (MD/MDd) is required when using mimalloc as a shared library for override")

        if self.options.override and \
           self.options.get_safe("single_object") and \
           self.options.get_safe("inject"):
            raise ConanInvalidConfiguration("Single object is incompatible with library injection")

        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["MI_BUILD_TESTS"] = "OFF"
        tc.variables["MI_BUILD_SHARED"] = self.options.shared
        tc.variables["MI_BUILD_STATIC"] = not self.options.shared
        tc.variables["MI_BUILD_OBJECT"] = self.options.get_safe("single_object", False)
        tc.variables["MI_OVERRIDE"] = "ON" if self.options.override else "OFF"
        tc.variables["MI_SECURE"] = "ON" if self.options.secure else "OFF"
        if Version(self.version) >= "1.7.0":
            tc.variables["MI_INSTALL_TOPLEVEL"] = "ON"
        tc.generate()

        if is_msvc(self):
            vcvars = VCVars(self)
            vcvars.generate()

    def build(self):
        apply_conandata_patches(self)
        if is_msvc(self) and self.settings.arch == "x86" and self.options.shared:
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                            "mimalloc-redirect.lib",
                            "mimalloc-redirect32.lib")
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        if self.options.get_safe("single_object"):
            rm(self, "*.a", os.path.join(self.package_folder, "lib"))
            shutil.move(os.path.join(self.package_folder, self._obj_name + ".o"),
                        os.path.join(self.package_folder, "lib"))
            shutil.copy(os.path.join(self.package_folder, "lib", self._obj_name + ".o"),
                        os.path.join(self.package_folder, "lib", self._obj_name))

        if self.settings.os == "Windows" and self.options.shared:
            if self.settings.arch == "x86_64":
                copy(self, "mimalloc-redirect.dll",
                    src=os.path.join(self.source_folder, "bin"),
                    dst=os.path.join(self.package_folder, "bin"))
            elif self.settings.arch == "x86":
                copy(self, "mimalloc-redirect32.dll",
                    src=os.path.join(self.source_folder, "bin"),
                    dst=os.path.join(self.package_folder, "bin"))

        rmdir(self, os.path.join(self.package_folder, "share"))

        cmake_target = "mimalloc" if self.options.shared else "mimalloc-static"
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {cmake_target: "mimalloc::mimalloc"}
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    @property
    def _obj_name(self):
        name = "mimalloc"
        if self.options.secure:
            name += "-secure"
        if self.settings.build_type not in ("Release", "RelWithDebInfo", "MinSizeRel"):
            name += "-{}".format(str(self.settings.build_type).lower())
        return name

    @property
    def _lib_name(self):
        name = "mimalloc" if self.settings.os == "Windows" else "libmimalloc"

        if self.settings.os == "Windows" and not self.options.shared:
            name += "-static"
        if self.options.secure:
            name += "-secure"
        if self.settings.build_type not in ("Release", "RelWithDebInfo", "MinSizeRel"):
            name += "-{}".format(str(self.settings.build_type).lower())
        return name

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "mimalloc")
        self.cpp_info.set_property("cmake_target_name", "mimalloc" if self.options.shared else "mimalloc-static")

        self.cpp_info.names["cmake_find_package"] = "mimalloc"
        self.cpp_info.names["cmake_find_package_multi"] = "mimalloc"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

        if self.options.get_safe("inject"):
            self.cpp_info.includedirs = []
            self.cpp_info.libdirs = []
            self.cpp_info.resdirs = []
            return

        if self.options.get_safe("single_object"):
            obj_ext = "o"
            obj_file = "{}.{}".format(self._obj_name, obj_ext)
            obj_path = os.path.join(self.package_folder, "lib", obj_file)
            self.cpp_info.exelinkflags = [obj_path]
            self.cpp_info.sharedlinkflags = [obj_path]
            self.cpp_info.libdirs = []
            self.cpp_info.bindirs = []
        else:
            self.cpp_info.libs = collect_libs(self)

        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
        if not self.options.shared:
            if self.settings.os == "Windows":
                self.cpp_info.system_libs.extend(["psapi", "shell32", "user32", "bcrypt"])
            elif self.settings.os == "Linux":
                self.cpp_info.system_libs.append("rt")
