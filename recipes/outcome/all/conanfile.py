from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rename, replace_in_file
from conan.tools.layout import basic_layout
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.scm import Version
import glob
import os
import yaml

required_conan_version = ">=1.52.0"


class OutcomeConan(ConanFile):
    name = "outcome"
    homepage = "https://github.com/ned14/outcome"
    description = "Provides very lightweight outcome<T> and result<T>"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("outcome", "result")
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "single_header": [True, False],
        "experimental": [True, False],
    }
    default_options = {
        "single_header": True,
        "experimental": False,
    }

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "6",
            "clang": "3.9",
            "apple-clang": "5.1",
        }

    @property
    def _is_experimental(self):
        return self.options.experimental

    @property
    def _use_custom_byte_impl(self):
        cppstd = self.settings.compiler.get_safe("cppstd")
        return cppstd is not None and cppstd < "17"

    @property
    def _use_custom_span_impl(self):
        cppstd = self.settings.compiler.get_safe("cppstd")
        return cppstd is not None and cppstd < "20"

    @property
    def _use_new_span(self):
        return Version(self.version) > "2.2.4"

    def export(self):
        copy(self, "submoduledata.yml",
             src=self.recipe_folder, dst=self.export_folder)

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self._use_custom_byte_impl:
            self.requires("byte-lite/0.3.0")
        if self._use_custom_span_impl:
            self.requires("span-lite/0.10.3" if self._use_new_span else "gsl-lite/0.38.1")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        if is_msvc(self):
            check_min_vs(self, 191)
        else:
            minimum_version = self._compilers_minimum_version.get(
                str(self.settings.compiler), False)
            if not minimum_version:
                self.output.warn(
                    f"Unknown compiler {self.settings.compiler} {self.settings.compiler.version}. Assuming compiler supports C++14.")
            elif Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )
        if self.options.single_header and self._is_experimental:
            raise ConanInvalidConfiguration(
                "The experimental single header option is not supported.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        submodule_data_file = os.path.join(
            self.recipe_folder, "submoduledata.yml")
        with open(submodule_data_file, 'r', encoding="utf-8") as submodule_stream:
            submodules_data = yaml.safe_load(submodule_stream)
            for _, submodule in submodules_data["submodules"][self.version].items():
                submodule_data = {
                    "url": submodule["url"],
                    "sha256": submodule["sha256"]
                }
                dst = self.source_folder
                for seg in submodule["destination"]:
                    dst = os.path.join(dst, seg)

                get(self, **submodule_data, destination=dst, strip_root=True)

    def _patch_sources(self):
        apply_conandata_patches(self)

        # https://github.com/microsoft/vcpkg/blob/cf48528dfffa14f762e6ad169c5cd6209fe5f22f/ports/ned14-internal-quickcpplib/portfile.cmake#L80-L92
        include_internal = os.path.join(
            self.source_folder, "quickcpplib",  "include", "quickcpplib")

        if self._use_custom_span_impl:
            replace_in_file(
                self, os.path.join(include_internal, "span.hpp"),
                '#include "span-lite/include/nonstd/span.hpp"' if self._use_new_span else '#include "gsl-lite/include/gsl/gsl-lite.hpp"',
                "#include <nonstd/span.hpp>" if self._use_new_span else "#include <gsl/gsl-lite.hpp>",
            )

        if self._use_custom_byte_impl:
            replace_in_file(
                self, os.path.join(include_internal, "byte.hpp"),
                "#include \"byte/include/nonstd/byte.hpp\"",
                "#include <nonstd/byte.hpp>",
            )
        if self._is_experimental:
            include_internal = os.path.join(
                self.source_folder, "include", "outcome", "experimental")
            replace_in_file(self, os.path.join(include_internal, "coroutine_support.hpp"),
                '#include "status-code/include/system_code_from_exception.hpp"',
                '#include "status-code/include/status-code/system_code_from_exception.hpp"')
            replace_in_file(self, os.path.join(include_internal, "status_result.hpp"),
                '#include "status-code/include/system_error2.hpp"',
                '#include "status-code/include/status-code/system_error2.hpp"')


    def build(self):
        apply_conandata_patches(self)
        self._patch_sources()

    def _package_multi_header(self):
        # Copy quickcpplibs
        with open(os.path.join(self.source_folder, "quickcpplib", "cmake", "headers.cmake"), 'r', encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line.startswith('"include'):
                    continue
                parts = line.replace('"', '').split('/')
                dir_parts = parts[:-1]
                copy(self, pattern=parts[-1], dst=os.path.join(self.package_folder, *dir_parts),
                        src=os.path.join(self.source_folder, "quickcpplib", *dir_parts))

        valid_extensions = [".h", ".[hi]pp", ".ixx"]
        files = []
        root = os.path.join(self.source_folder, "include")
        sep = os.path.sep
        for ext in valid_extensions:
            files += [x for x in glob.glob(os.path.join(root, "**", f"*{ext}"), recursive=True)
                        if f"{sep}experimental{sep}" not in x]
            if self._is_experimental:
                files += glob.glob(os.path.join(root, "**", "experimental", f"*{ext}"))
                files += glob.glob(os.path.join(root, "**", "experimental", "status-code", "include", "**", f"*{ext}"), recursive=True)

        dst = os.path.join(self.package_folder, "include")
        for f in files:
            copy(self, os.path.relpath(f, root), src=root, dst=dst)

        if self._is_experimental:
            base = os.path.join(dst, "outcome", "experimental", "status-code", )
            src = os.path.join(base, "include")
            if os.path.exists(os.path.join(src, "status_code.hpp")) and os.path.exists(os.path.join(src, "detail")):
                tmp =  os.path.join(base, "include_tmp")
                dst = os.path.join(src, "status-code")
                # allow including as <status-code/xx.hpp>
                # first move to sibling to avoid errors with moving dir into itself
                rename(self, src=src, dst=tmp)
                rename(self, src=tmp, dst=dst)

    def package(self):
        copy(self, pattern="Licence.txt", dst=os.path.join(
            self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="LICENSE", dst=os.path.join(
            self.package_folder, "licenses", "Optional"), src=os.path.join(self.source_folder, "quickcpplib", "include", "quickcpplib", "optional"))

        if self.options.single_header:
            copy(self, pattern="outcome.hpp", dst=os.path.join(self.package_folder,
                 "include"), src=os.path.join(self.source_folder, "single-header"))
        else:
            self._package_multi_header()


    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # Link using outcome::outcome & outcome::hl
        name = "outcome"
        component = "hl"
        self.cpp_info.set_property("cmake_module_file_name", name)
        self.cpp_info.set_property(
            "cmake_module_target_name", f"{name}::{name}")
        self.cpp_info.set_property("cmake_file_name", name)
        self.cpp_info.set_property("cmake_target_name", f"{name}::{name}")

        self.cpp_info.components[component].defines = [
            "QUICKCPPLIB_DISABLE_ABI_PERMUTATION=1"]

        self.cpp_info.components[component].bindirs = []
        self.cpp_info.components[component].libdirs = []

        self.cpp_info.components[component].set_property(
            "cmake_target_name", f"{name}::{component}")
        if self._use_custom_byte_impl:
            self.cpp_info.components[component].requires.append(
                "byte-lite::byte-lite")
        if self._use_custom_span_impl:
            self.cpp_info.components[component].requires.append(
                "span-lite::span-lite" if self._use_new_span else "gsl-lite::gsl-lite")
        if self._is_experimental:
            # allow including as <status-code/xx.hpp>
            self.cpp_info.components[component].includedirs.append("include/outcome/experimental/status-code/include")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = name
        self.cpp_info.filenames["cmake_find_package_multi"] = name
        self.cpp_info.names["cmake_find_package"] = name
        self.cpp_info.names["cmake_find_package_multi"] = name
        self.cpp_info.components[component].names["cmake_find_package"] = component
        self.cpp_info.components[component].names["cmake_find_package_multi"] = component

    def package_id(self):
        self.info.settings.clear()
