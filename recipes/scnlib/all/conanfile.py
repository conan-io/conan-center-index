from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class ScnlibConan(ConanFile):
    name = "scnlib"
    description = "scanf for modern C++"
    license = "Apache-2.0"
    topics = ("scnlib", "parsing", "io", "scanf")
    homepage = "https://github.com/eliaskosunen/scnlib"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "header_only": [True, False],
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "header_only": False,
        "shared": False,
        "fPIC": True,
    }

    # required cmake_find_package_multi since scnlib>=1.1 uses `find_package(fast_float)`
    generators = "cmake", "cmake_find_package_multi"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.header_only or self.options.shared:
            del self.options.fPIC
        if self.options.header_only:
            del self.options.shared

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
            "clang": "6.0",
            "Visual Studio": "16" if tools.Version(self.version) >= "1.0" else "15",
        }

    def requirements(self):
        if tools.Version(self.version) >= "1.0":
            self.requires("fast_float/3.4.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and tools.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                "{} {} requires several C++11 features, which your compiler does not support.".format(
                    self.name, self.version,
                )
            )

    def package_id(self):
        if self.options.header_only:
            self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["SCN_INSTALL"] = True
        if tools.Version(self.version) >= "1.0":
            self._cmake.definitions["SCN_USE_BUNDLED_FAST_FLOAT"] = False
        self._cmake.definitions["SCN_INSTALL"] = True
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        if not self.options.header_only:
            cmake = self._configure_cmake()
            cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        if self.options.header_only:
            self.copy("*", dst="include", src=os.path.join(self._source_subfolder, "include"))
            if tools.Version(self.version) >= "1.0":
                self.copy("reader_*.cpp", dst=os.path.join("include", "scn", "reader"), src=os.path.join(self._source_subfolder, "src"))
                self.copy("vscan.cpp", dst=os.path.join("include", "scn", "scan"), src=os.path.join(self._source_subfolder, "src"))
                self.copy("locale.cpp", dst=os.path.join("include", "scn", "detail"), src=os.path.join(self._source_subfolder, "src"))
                self.copy("file.cpp", dst=os.path.join("include", "scn", "detail"), src=os.path.join(self._source_subfolder, "src"))
            else:
                self.copy("*.cpp", dst=os.path.join("include", "scn", "detail"), src=os.path.join(self._source_subfolder, "src"))
        else:
            cmake = self._configure_cmake()
            cmake.install()
            tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
            tools.rmdir(os.path.join(self.package_folder, "share"))
        if tools.Version(self.version) >= "1.0":
            tools.remove_files_by_mask(os.path.join(self.package_folder, "include", "scn", "detail"), "*.cmake")
            tools.rmdir(os.path.join(self.package_folder, "include", "scn", "detail", "CMakeFiles"))
            tools.rmdir(os.path.join(self.package_folder, "include", "scn", "detail", "deps", "CMakeFiles"))

    def package_info(self):
        target = "scn-header-only" if self.options.header_only else "scn"
        self.cpp_info.set_property("cmake_file_name", "scn")
        self.cpp_info.set_property("cmake_target_name", "scn::{}".format(target))
        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        if self.options.header_only:
            self.cpp_info.components["_scnlib"].defines = ["SCN_HEADER_ONLY=1"]
        else:
            self.cpp_info.components["_scnlib"].defines = ["SCN_HEADER_ONLY=0"]
            self.cpp_info.components["_scnlib"].libs = ["scn"]
        if tools.Version(self.version) >= "1.0":
            self.cpp_info.components["_scnlib"].requires = ["fast_float::fast_float"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "scn"
        self.cpp_info.names["cmake_find_package_multi"] = "scn"
        self.cpp_info.components["_scnlib"].names["cmake_find_package"] = target
        self.cpp_info.components["_scnlib"].names["cmake_find_package_multi"] = target
        self.cpp_info.components["_scnlib"].set_property("cmake_target_name", "scn::{}".format(target))
