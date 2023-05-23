cmake_minimum_required(VERSION 3.0)
project(ragel)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

file(GLOB HEADERS
	source_subfolder/ragel/buffer.h
	source_subfolder/ragel/cdgoto.h
	source_subfolder/ragel/cscodegen.h
	source_subfolder/ragel/csipgoto.h
	source_subfolder/ragel/inputdata.h
	source_subfolder/ragel/rbxgoto.h
	source_subfolder/ragel/rubyflat.h
	source_subfolder/ragel/cdcodegen.h
	source_subfolder/ragel/cdipgoto.h
	source_subfolder/ragel/csfflat.h
	source_subfolder/ragel/cssplit.h
	source_subfolder/ragel/javacodegen.h
	source_subfolder/ragel/redfsm.h
	source_subfolder/ragel/rubyftable.h
	source_subfolder/ragel/cdfflat.h
	source_subfolder/ragel/cdsplit.h
	source_subfolder/ragel/csfgoto.h
	source_subfolder/ragel/cstable.h
	source_subfolder/ragel/parsedata.h
	source_subfolder/ragel/rlparse.h
	source_subfolder/ragel/rubytable.h
	source_subfolder/ragel/cdfgoto.h
	source_subfolder/ragel/cdtable.h
	source_subfolder/ragel/csflat.h
	source_subfolder/ragel/dotcodegen.h
	source_subfolder/ragel/parsetree.h
	source_subfolder/ragel/rlscan.h
	source_subfolder/ragel/version.h
	source_subfolder/ragel/cdflat.h
	source_subfolder/ragel/common.h
	source_subfolder/ragel/csftable.h
	source_subfolder/ragel/fsmgraph.h
	source_subfolder/ragel/pcheck.h
	source_subfolder/ragel/rubycodegen.h
	source_subfolder/ragel/xmlcodegen.h
	source_subfolder/ragel/cdftable.h
	source_subfolder/ragel/csgoto.h
	source_subfolder/ragel/gendata.h
	source_subfolder/ragel/ragel.h
	source_subfolder/ragel/rubyfflat.h
	source_subfolder/ragel/gocodegen.h
	source_subfolder/ragel/gotable.h
	source_subfolder/ragel/goftable.h
	source_subfolder/ragel/goflat.h
	source_subfolder/ragel/gofflat.h
	source_subfolder/ragel/gogoto.h
	source_subfolder/ragel/gofgoto.h
	source_subfolder/ragel/goipgoto.h
	source_subfolder/ragel/gotablish.h
	source_subfolder/ragel/mlcodegen.h
	source_subfolder/ragel/mltable.h
	source_subfolder/ragel/mlftable.h
	source_subfolder/ragel/mlflat.h
	source_subfolder/ragel/mlfflat.h
	source_subfolder/ragel/mlgoto.h
	source_subfolder/ragel/mlfgoto.h
)

file(GLOB SRC
	source_subfolder/ragel/main.cpp
	source_subfolder/ragel/parsetree.cpp
	source_subfolder/ragel/parsedata.cpp
	source_subfolder/ragel/fsmstate.cpp
	source_subfolder/ragel/fsmbase.cpp
	source_subfolder/ragel/fsmattach.cpp
	source_subfolder/ragel/fsmmin.cpp
	source_subfolder/ragel/fsmgraph.cpp
	source_subfolder/ragel/fsmap.cpp
	source_subfolder/ragel/rlscan.cpp
	source_subfolder/ragel/rlparse.cpp
	source_subfolder/ragel/inputdata.cpp
	source_subfolder/ragel/common.cpp
	source_subfolder/ragel/redfsm.cpp
	source_subfolder/ragel/gendata.cpp
	source_subfolder/ragel/cdcodegen.cpp
	source_subfolder/ragel/cdtable.cpp
	source_subfolder/ragel/cdftable.cpp
	source_subfolder/ragel/cdflat.cpp
	source_subfolder/ragel/cdfflat.cpp
	source_subfolder/ragel/cdgoto.cpp
	source_subfolder/ragel/cdfgoto.cpp
	source_subfolder/ragel/cdipgoto.cpp
	source_subfolder/ragel/cdsplit.cpp
	source_subfolder/ragel/javacodegen.cpp
	source_subfolder/ragel/rubycodegen.cpp
	source_subfolder/ragel/rubytable.cpp
	source_subfolder/ragel/rubyftable.cpp
	source_subfolder/ragel/rubyflat.cpp
	source_subfolder/ragel/rubyfflat.cpp
	source_subfolder/ragel/rbxgoto.cpp
	source_subfolder/ragel/cscodegen.cpp
	source_subfolder/ragel/cstable.cpp
	source_subfolder/ragel/csftable.cpp
	source_subfolder/ragel/csflat.cpp
	source_subfolder/ragel/csfflat.cpp
	source_subfolder/ragel/csgoto.cpp
	source_subfolder/ragel/csfgoto.cpp
	source_subfolder/ragel/csipgoto.cpp
	source_subfolder/ragel/cssplit.cpp
	source_subfolder/ragel/dotcodegen.cpp
	source_subfolder/ragel/xmlcodegen.cpp
	source_subfolder/ragel/gocodegen.cpp
	source_subfolder/ragel/gotable.cpp
	source_subfolder/ragel/goftable.cpp
	source_subfolder/ragel/goflat.cpp
	source_subfolder/ragel/gofflat.cpp
	source_subfolder/ragel/gogoto.cpp
	source_subfolder/ragel/gofgoto.cpp
	source_subfolder/ragel/goipgoto.cpp
	source_subfolder/ragel/gotablish.cpp
	source_subfolder/ragel/mlcodegen.cpp
	source_subfolder/ragel/mltable.cpp
	source_subfolder/ragel/mlftable.cpp
	source_subfolder/ragel/mlflat.cpp
	source_subfolder/ragel/mlfflat.cpp
	source_subfolder/ragel/mlgoto.cpp
	source_subfolder/ragel/mlfgoto.cpp
)

add_executable(${CMAKE_PROJECT_NAME} ${SRC} ${HEADERS})
target_link_libraries(${CMAKE_PROJECT_NAME} PUBLIC ${CONAN_LIBS})
target_include_directories(${CMAKE_PROJECT_NAME} PRIVATE source_subfolder/aapl
												 PRIVATE ${CMAKE_BINARY_DIR})

install(TARGETS ${CMAKE_PROJECT_NAME}
        RUNTIME DESTINATION bin)
