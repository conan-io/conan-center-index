from conans import CMake, ConanFile, tools
import os

required_conan_version = ">=1.43.0"


class AngelScriptConan(ConanFile):
    name = "angelscript"
    license = "Zlib"
    homepage = "http://www.angelcode.com/angelscript"
    url = "https://github.com/conan-io/conan-center-index"
    description = (
        "An extremely flexible cross-platform scripting library designed to "
        "allow applications to extend their functionality through external scripts."
    )
    topics = ("angelcode", "embedded", "scripting", "language", "compiler", "interpreter")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [False, True],
        "fPIC": [False, True],
        "no_exceptions": [False, True],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "no_exceptions": False,
    }

    short_paths = True
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        # Website blocks default user agent string.
        tools.get(
            **self.conan_data["sources"][self.version],
            destination=self._source_subfolder,
            headers={"User-Agent": "ConanCenter"},
            strip_root=True,
        )

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["AS_NO_EXCEPTIONS"] = self.options.no_exceptions
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _extract_license(self):
        header = tools.load(os.path.join(self._source_subfolder, "angelscript", "include", "angelscript.h"))
        tools.save("LICENSE", header[header.find("/*", 1) + 3 : header.find("*/", 1)])

    def package(self):
        self._extract_license()
        self.copy("LICENSE", dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Angelscript")
        self.cpp_info.set_property("cmake_target_name", "Angelscript::angelscript")
        postfix = "d" if self._is_msvc and self.settings.build_type == "Debug" else ""
        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["_angelscript"].libs = ["angelscript" + postfix]
        if self.settings.os in ("Linux", "FreeBSD", "SunOS"):
            self.cpp_info.components["_angelscript"].system_libs.append("pthread")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "Angelscript"
        self.cpp_info.names["cmake_find_package_multi"] = "Angelscript"
        self.cpp_info.components["_angelscript"].names["cmake_find_package"] = "angelscript"
        self.cpp_info.components["_angelscript"].names["cmake_find_package_multi"] = "angelscript"
        self.cpp_info.components["_angelscript"].set_property("cmake_target_name", "Angelscript::angelscript")
