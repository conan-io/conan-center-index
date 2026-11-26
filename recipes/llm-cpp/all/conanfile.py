from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os


required_conan_version = ">=2.0"


class LlmCppConan(ConanFile):
    name = "llm-cpp"
    description = ("Header-only C++17 libraries for working with large language models: "
                   "chat, streaming, embeddings, RAG, caching, retries, JSON, cost tracking and more")
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Mattbusel/llm-cpp"
    topics = ("llm", "openai", "ai", "rag", "embeddings", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_libcurl": [True, False],
    }
    default_options = {
        "with_libcurl": True,
    }
    no_copy_source = True

    # Libraries with no external dependency.
    _plain_components = ("cache", "compress", "cost", "format", "guard", "json", "log", "mock",
                         "parse", "pool", "retry", "router", "template", "trace")
    # Libraries whose implementation (and, for eval and stream, the header itself) uses libcurl.
    _curl_components = ("ab", "agent", "audio", "batch", "chat", "embed", "eval", "finetune",
                        "rag", "rank", "stream", "vision")
    # Libraries that use std::thread / std::mutex.
    _thread_components = ("batch", "cache", "finetune", "mock", "pool", "retry", "stream")

    @property
    def _min_cppstd(self):
        return 17

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_libcurl:
            # llm_eval.hpp and llm_stream.hpp include <curl/curl.h>
            self.requires("libcurl/[>=7.78.0 <9]", transitive_headers=True)

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp",
             os.path.join(self.source_folder, "include", "llm"),
             os.path.join(self.package_folder, "include", "llm"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "llm-cpp")
        self.cpp_info.set_property("cmake_target_name", "llm-cpp::llm-cpp")
        self.cpp_info.set_property("pkg_config_name", "llm-cpp")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # Upstream accepts both #include <llm/llm_x.hpp> and #include "llm_x.hpp"
        includedirs = ["include", os.path.join("include", "llm")]

        components = list(self._plain_components)
        if self.options.with_libcurl:
            components += list(self._curl_components)

        def _add_component(name):
            comp = self.cpp_info.components[name]
            comp.set_property("cmake_target_name", f"llm::{name}")
            comp.set_property("pkg_config_name", f"llm-cpp-{name}")
            comp.includedirs = includedirs
            comp.bindirs = []
            comp.libdirs = []
            return comp

        for name in components:
            comp = _add_component(name)
            if name in self._thread_components and self.settings.os in ["Linux", "FreeBSD"]:
                comp.system_libs.append("pthread")
            if name in self._curl_components:
                comp.requires.append("libcurl::libcurl")

        if self.options.with_libcurl:
            # llm::compress with LLM_COMPRESS_SUMMARIZE defined: summarize-based compression over libcurl
            summarize = _add_component("compress_summarize")
            summarize.defines = ["LLM_COMPRESS_SUMMARIZE"]
            summarize.requires = ["compress", "libcurl::libcurl"]

        # llm::llm: the umbrella header <llm/llm.hpp> plus every library
        umbrella = _add_component("llm")
        umbrella.requires = list(components)
