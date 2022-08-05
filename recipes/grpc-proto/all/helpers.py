import os
import re
import textwrap


def grpc_target_name(internal_name):
    return f"grpc_{internal_name}"


class _ProtoLibrary:
    name: str = None
    srcs: list = None
    deps: list = None
    is_used: bool = False

    def __init__(self) -> None:
        self.srcs = []
        self.deps = set(["protobuf::libprotobuf"])  # Add to all libraries even if not explicitly set
        self.is_used = True

    def validate(self, source_folder, all_deps):
        # Check all files exists
        for it in self.srcs:
            assert os.path.exists(os.path.join(source_folder, it)), f"{self.name} - file '{it}' doesn't exist"
        # Check all deps exists
        for it in self.deps:
            assert it in all_deps, f"{self.name} - dep '{it}' not found"

    def dumps(self):
        import json
        return json.dumps({
            "name": self.name,
            "srcs": self.srcs,
            "deps": list(self.deps),
        }, indent=4)

    @property
    def cmake_target(self):
        return grpc_target_name(self.name)

    @property
    def cmake_deps(self):
        def to_cmake_target(item):
            if item.startswith("//"):
                return item[2:].replace("/", "_").replace(":", "_")
            return item
        return [to_cmake_target(it) for it in self.deps]

    @property
    def cmake_content(self):
        content = f"\n\n# {self.cmake_target}\n"
        content += "\n".join([f"#{it}" for it in self.dumps().split('\n')])
        content += "\n"        
        if not self.srcs:
            content += textwrap.dedent(f"""\
                add_library({self.cmake_target} INTERFACE)
            """)
        else:
            content += textwrap.dedent(f"""\
                set({self.cmake_target}_PROTOS {" ".join(["${CMAKE_SOURCE_DIR}/"+it for it in self.srcs])})
                add_library({self.cmake_target} ${{{self.cmake_target}_PROTOS}})
                target_include_directories({self.cmake_target} PUBLIC ${{CMAKE_BINARY_DIR}})
                target_compile_features({self.cmake_target} PUBLIC cxx_std_11)
                protobuf_generate(LANGUAGE cpp 
                                TARGET {self.cmake_target} 
                                PROTOS ${{{self.cmake_target}_PROTOS}}
                                IMPORT_DIRS ${{IMPORT_DIRS}}
                                )
            """)

        if self.deps:
            content += textwrap.dedent(f"""\
                target_link_libraries({self.cmake_target} {"PUBLIC" if self.srcs else "INTERFACE"} {" ".join(self.cmake_deps)})
            """)

        return content


def parse_proto_libraries(filename, source_folder, error):
    # Generate the libraries to build dynamically
    re_name = re.compile(r'name = "(.*)"')
    re_srcs_oneline = re.compile(r'srcs = \["(.*)"\],')
    re_deps_oneline = re.compile(r'deps = \["(.*)"\],')
    re_add_varname = re.compile(r'] \+ (.*),')

    proto_libraries = []

    basedir = os.path.dirname(filename)
    proto_library = None

    def parsing_sources(line):
        proto_path = os.path.relpath(os.path.join(basedir, line.strip(",").strip("\"")), source_folder).replace('\\', '/')
        proto_library.srcs.append(proto_path)

    def parsing_deps(line):
        line = line.strip(",").strip("\"")
        if line.startswith("@com_google_protobuf//:"):
            proto_library.deps.add("protobuf::libprotobuf")
        elif line.startswith("@com_google_googleapis//"):
            proto_library.deps.add("googleapis::googleapis")
        elif line.startswith(":"):
            proto_library.deps.add(grpc_target_name(line[1:]))
        else:
            error(f"Unrecognized dep: {line} -- {os.path.relpath(filename, source_folder)}")

    with open(filename, 'r') as f:
        action = None
        parsing_variable = None
        variables = {}
        for line in f.readlines():
            line = line.strip()

            if line == "proto_library(":
                assert proto_library == None
                proto_library = _ProtoLibrary()
            elif parsing_variable != None:
                if line == "]":
                    parsing_variable = None
                else:
                    parsing_variable(line)
            elif proto_library != None:
                if line.startswith("name ="):
                    proto_library.name = re_name.search(line).group(1)
                elif line.startswith("srcs = "):
                    m = re_srcs_oneline.search(line)
                    if m:
                        parsing_sources(m.group(1))
                    else:
                        action = parsing_sources
                elif line.startswith("deps = "):
                    m = re_deps_oneline.search(line)
                    if m:
                        parsing_deps(m.group(1))
                    else:
                        action = parsing_deps
                elif line.startswith("visibility = "):
                    pass
                elif line == ")":
                    proto_libraries.append(proto_library)
                    proto_library = None
                    action = None
                elif line == "],":
                    action = None 
                elif line.startswith("] + "):
                    varname = re_add_varname.search(line).group(1)
                    for it in variables[varname]:
                        action(it) 
                elif action:
                    action(line)

    return proto_libraries
