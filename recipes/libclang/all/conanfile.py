import os
from conans import ConanFile, CMake, tools
from conan.tools.cmake import CMakeFileAPI
from conan.tools.files import CppPackage
import functools
import textwrap
import re
from collections import defaultdict
import json

required_conan_version = ">=1.36.0"


class LibClangConan(ConanFile):
    name = 'libclang'
    description = 'A compiler front-end for the C family of languages.'
    license = 'Apache-2.0 WITH LLVM-exception'
    topics = ('clang', 'llvm', 'compiler')
    homepage = 'https://clang.llvm.org/'
    url = 'https://github.com/conan-io/conan-center-index'

    settings = 'os', 'arch', 'compiler', 'build_type'
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_plugin_support": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_plugin_support": True,
        "llvm-core:use_llvm_cmake_files": True,
    }

    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"
    short_paths = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires('llvm-core/13.0.0')

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True,
                  destination=self._source_subfolder)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)

        cmake.definitions['BUILD_SHARED_LIBS'] = False
        cmake.definitions['CMAKE_SKIP_RPATH'] = True
        cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = \
            self.options.get_safe('fPIC', default=False) or self.options.shared

        cmake.definitions["CLANG_PLUGIN_SUPPORT"] = self.options.with_plugin_support

        cmake.definitions["CLANG_BUILT_STANDALONE"] = True
        cmake.definitions["LLVM_ENABLE_LIBXML2"] = False
        cmake.definitions["CLANG_BUILD_TOOLS"] = False
        cmake.definitions["CLANG_INSTALL_SCANBUILD"] = False
        cmake.definitions["CLANG_INSTALL_SCANVIEW"] = False
        cmake.definitions["CLANG_BUILD_TOOLS"] = False
        cmake.definitions["CLANG_INCLUDE_TESTS"] = False
        cmake.definitions["LLVM_INCLUDE_TESTS"] = False
        cmake.definitions["CLANG_INCLUDE_DOCS"] = False
        cmake.definitions["LIBCLANG_BUILD_STATIC"] = not self.options.shared
        cmake.configure()

        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        file_api = CMakeFileAPI(self)
        file_api.query(CMakeFileAPI.CODEMODELV2)
        cmake = self._configure_cmake()
        reply = file_api.reply(CMakeFileAPI.CODEMODELV2)
        package = reply.to_conan_package()
        package.save()
        cmake.build()

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake", "clang")

    @property
    def _alias_module_file_rel_path(self):
        return os.path.join(self._module_subfolder, "conan-official-{}-targets.cmake".format(self.name))

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        tools.save(module_file, content)

    def package(self):
        self.copy('LICENSE.TXT', dst='licenses', src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, 'libexec'))
        tools.rmdir(os.path.join(self.package_folder, 'share'))
        if self.settings.os == "Windows" and self.options.shared:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*[!.dll]")
        else:
            tools.rmdir(os.path.join(self.package_folder, "bin"))

        for mask in ["Find*.cmake", "*Config.cmake", "*-config.cmake", "*Targets*.cmake"]:
            tools.remove_files_by_mask(self.package_folder, mask)

        alias_targets = {}

        if not self.options.shared:
            CMake(self).configure(args=['--graphviz=graph/clang.dot'], source_dir='.', build_dir='.')
            with tools.chdir('graph'):
                dot_text = tools.load('clang.dot').replace('\r\n', '\n')

            dep_regex = re.compile(r'//\s(.+)\s->\s(.+)$', re.MULTILINE)
            deps = re.findall(dep_regex, dot_text)

            cpp_package = CppPackage.load()
            llvm_components = list(self.deps_cpp_info["llvm-core"].components.keys())

            for name, component in cpp_package.components.items():
                new_requires = []
                for require in component.requires:
                    if require in cpp_package.components:
                        new_requires.append(require)
                    elif require in llvm_components:
                        new_requires.append("llvm-core::" + require)

                for lib, dep in deps:
                    if name != lib:
                        continue
                    elif dep.startswith('obj.'):
                        continue
                    elif dep.startswith('-delayload:'):
                        continue
                    elif dep in llvm_components:
                        dep = "llvm-core::" + dep
                    else:
                        continue

                    if dep not in new_requires:
                        new_requires.append(dep)

                component.requires = new_requires

                alias_targets[name] = "Clang::{}".format(name)

            cpp_package.save(os.path.join(self.package_folder, 'lib', CppPackage.DEFAULT_FILENAME))

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._alias_module_file_rel_path),
            alias_targets
        )

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Clang")

        cpp_package = CppPackage.load(os.path.join(self.package_folder, 'lib', CppPackage.DEFAULT_FILENAME))

        extra_info = {}

        if self.settings.os == "Windows":
            extra_info["clangDriver"] = {
                "system_libs": ["Version"]
            }

        for name, component in cpp_package.components.items():
            if name == "libclang":
                name = "libclanglib"

            self.cpp_info.components[name].set_property("cmake_target_name", name)
            self.cpp_info.components[name].libs = component.libs
            self.cpp_info.components[name].requires = [require if require != "libclang" else "libclanglib" for require in component.requires]
            self.cpp_info.components[name].builddirs.append(self._module_subfolder)
            self.cpp_info.components[name].set_property("cmake_build_modules", [
                self._alias_module_file_rel_path
            ])

            if name in extra_info:
                extra = extra_info[name]
                if "system_libs" in extra:
                    self.cpp_info.components[name].system_libs.extend(extra["system_libs"])

            # TODO: to remove in conan v2 once cmake_find_package* generators removed
            self.cpp_info.components[name].names["cmake_find_package"] = name
            self.cpp_info.components[name].names["cmake_find_package_multi"] = name
            self.cpp_info.components[name].build_modules["cmake_find_package"].append(
                self._alias_module_file_rel_path
            )
            self.cpp_info.components[name].build_modules["cmake_find_package_multi"].append(
                self._alias_module_file_rel_path
            )

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "Clang"
        self.cpp_info.names["cmake_find_package_multi"] = "Clang"
