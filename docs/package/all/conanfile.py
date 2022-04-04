from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from conan.tools.microsoft import msvc_runtime_flag
import functools
import os

required_conan_version = ">=1.36.0"

class packageConan(ConanFile):
    name = "package"
    description = "shortd escription"
    license = "" # conform to SPDX License List: https://spdx.org/licenses/
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/project/package"
    topics = ("topic1", "topic2") # no "conan"  and project name in topics
    settings = "os", "arch", "compiler", "build_type" # even for header only
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "cmake", "cmake_find_package_multi"

    # no manual caching of build helper like  _cmake = None


    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    # don't use self.settings_build
    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    # don't use self.user_info_build
    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    # no exports_sources attribute, but export_sources(self) method instead
    # this allows finer grain exportation of patches per version
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
        del self.settings.compiler.libcxx # for plain C projects only
        del self.settings.compiler.cppstd # for plain C projects only

    def requirements(self):
        self.requires("dependency/0.8.1")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)
        if self._is_msvc and self.options.shared:
            raise ConanInvalidConfiguration("package can't be built as shared on visual studio")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        # remove bundled xxhash
        tools.remove_files_by_mask(os.path.join(self._source_subfolder, "lib"), "whateer.*")
        tools.replace_in_file(
            os.path.join(self._cmakelists_subfolder, "CMakeLists.txt"),
            "...",
            "",
        )

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        if self._is_msvc:
            # don't use self.settings.compiler.runtime
            cmake.definitions["USE_MSVC_RUNTIME_LIBRARY_DLL"] = "MD" in msvc_runtime_flag(self)
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.pdb")

    def package_info(self):
        self.cpp_info.libs = ["package_lib"]

        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_module_file_name", "PACKAGE")
        self.cpp_info.set_property("cmake_file_name", "package")
        self.cpp_info.set_property("cmake_target_name", "PACKAGE::PACKAGE")
        self.cpp_info.set_property("pkg_config_name", "package")

        # If they are needed on Linux, m, pthread and dl are usually needed on FreeBSD too
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
            self.cpp_info.system_libs.append("dl")



        #  TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "PACKAGE"
        self.cpp_info.filenames["cmake_find_package_multi"] = "PACKAGE"
        self.cpp_info.names["cmake_find_package"] = "PACKAGE"
        self.cpp_info.names["cmake_find_package_multi"] = "PACKAGE"
