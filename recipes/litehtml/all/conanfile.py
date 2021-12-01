import os
import textwrap
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.43.0"


class LitehtmlConan(ConanFile):
    name = "litehtml"
    description = "litehtml is the lightweight HTML rendering engine with CSS2/CSS3 support."
    license = "BSD-3-Clause"
    topics = ("render engine", "html", "parser")
    homepage = "https://github.com/litehtml/litehtml"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "utf8": [True, False],
        "with_icu": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "utf8": False,
        "with_icu": False,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _min_cppstd(self):
        return "11"

    @property
    def _with_xxd(self):
        # FIXME: create conan recipe for xxd, and use it unconditionally (returning False means cross build doesn't work)
        if self.settings.os == "Windows":
            return False
        else:
            return True

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._min_cppstd)
        if self.options.shared and self.settings.os == "Windows":
            raise ConanInvalidConfiguration("litehtml must be built as a static library on windows")

    def requirements(self):
        # FIXME: add gumbo requirement (it is vendored right now)
        if self.options.with_icu:
            self.requires("icu/69.1")

    def build_requirements(self):
        # FIXME: add unconditional xxd build requirement
        pass

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["LITEHTML_UTF8"] = self.options.utf8
        self._cmake.definitions["USE_ICU"] = self.options.with_icu
        self._cmake.definitions["EXTERNAL_GUMBO"] = False # FIXME: add cci recipe, and use it unconditionally (option value should be True)
        self._cmake.definitions["EXTERNAL_XXD"] = self._with_xxd  # FIXME: should be True unconditionally
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"litehtml": "litehtml::litehtml",
             "gumbo":"litehtml::gumbo"}
        )

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

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file_rel_path(self):
        return os.path.join(self._module_subfolder,
                            "conan-official-{}-targets.cmake".format(self.name))
    def package_info(self):
        self.cpp_info.components["litehtml_litehtml"].set_property("cmake_target_name", "litehtml")

        self.cpp_info.components["litehtml_litehtml"].names["cmake_find_package"] = "litehtml"
        self.cpp_info.components["litehtml_litehtml"].names["cmake_find_package_multi"] = "litehtml"

        self.cpp_info.components["litehtml_litehtml"].builddirs.append(self._module_subfolder)

        self.cpp_info.components["litehtml_litehtml"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["litehtml_litehtml"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

        self.cpp_info.components["litehtml_litehtml"].libs = ["litehtml"]
        self.cpp_info.components["litehtml_litehtml"].requires = ["gumbo"]
        if self.options.with_icu:
            self.cpp_info.components["litehtml_litehtml"].requires.append("icu::icu")

        if True: # FIXME: remove once we use a vendored gumbo library
            self.cpp_info.components["gumbo"].set_property("cmake_target_name", "gumbo")
            self.cpp_info.components["gumbo"].libs = ["gumbo"]

            self.cpp_info.components["gumbo"].names["cmake_find_package"] = "gumbo"
            self.cpp_info.components["gumbo"].names["cmake_find_package_multi"] = "gumbo"
