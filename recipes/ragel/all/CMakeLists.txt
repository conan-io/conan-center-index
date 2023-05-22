cmake_minimum_required(VERSION 3.0)
project(ragel LANGUAGES CXX)

file(GLOB HEADERS
	${RAGEL_SOURCE_DIR}/ragel/buffer.h
	${RAGEL_SOURCE_DIR}/ragel/cdgoto.h
	${RAGEL_SOURCE_DIR}/ragel/cscodegen.h
	${RAGEL_SOURCE_DIR}/ragel/csipgoto.h
	${RAGEL_SOURCE_DIR}/ragel/inputdata.h
	${RAGEL_SOURCE_DIR}/ragel/rbxgoto.h
	${RAGEL_SOURCE_DIR}/ragel/rubyflat.h
	${RAGEL_SOURCE_DIR}/ragel/cdcodegen.h
	${RAGEL_SOURCE_DIR}/ragel/cdipgoto.h
	${RAGEL_SOURCE_DIR}/ragel/csfflat.h
	${RAGEL_SOURCE_DIR}/ragel/cssplit.h
	${RAGEL_SOURCE_DIR}/ragel/javacodegen.h
	${RAGEL_SOURCE_DIR}/ragel/redfsm.h
	${RAGEL_SOURCE_DIR}/ragel/rubyftable.h
	${RAGEL_SOURCE_DIR}/ragel/cdfflat.h
	${RAGEL_SOURCE_DIR}/ragel/cdsplit.h
	${RAGEL_SOURCE_DIR}/ragel/csfgoto.h
	${RAGEL_SOURCE_DIR}/ragel/cstable.h
	${RAGEL_SOURCE_DIR}/ragel/parsedata.h
	${RAGEL_SOURCE_DIR}/ragel/rlparse.h
	${RAGEL_SOURCE_DIR}/ragel/rubytable.h
	${RAGEL_SOURCE_DIR}/ragel/cdfgoto.h
	${RAGEL_SOURCE_DIR}/ragel/cdtable.h
	${RAGEL_SOURCE_DIR}/ragel/csflat.h
	${RAGEL_SOURCE_DIR}/ragel/dotcodegen.h
	${RAGEL_SOURCE_DIR}/ragel/parsetree.h
	${RAGEL_SOURCE_DIR}/ragel/rlscan.h
	${RAGEL_SOURCE_DIR}/ragel/version.h
	${RAGEL_SOURCE_DIR}/ragel/cdflat.h
	${RAGEL_SOURCE_DIR}/ragel/common.h
	${RAGEL_SOURCE_DIR}/ragel/csftable.h
	${RAGEL_SOURCE_DIR}/ragel/fsmgraph.h
	${RAGEL_SOURCE_DIR}/ragel/pcheck.h
	${RAGEL_SOURCE_DIR}/ragel/rubycodegen.h
	${RAGEL_SOURCE_DIR}/ragel/xmlcodegen.h
	${RAGEL_SOURCE_DIR}/ragel/cdftable.h
	${RAGEL_SOURCE_DIR}/ragel/csgoto.h
	${RAGEL_SOURCE_DIR}/ragel/gendata.h
	${RAGEL_SOURCE_DIR}/ragel/ragel.h
	${RAGEL_SOURCE_DIR}/ragel/rubyfflat.h
	${RAGEL_SOURCE_DIR}/ragel/gocodegen.h
	${RAGEL_SOURCE_DIR}/ragel/gotable.h
	${RAGEL_SOURCE_DIR}/ragel/goftable.h
	${RAGEL_SOURCE_DIR}/ragel/goflat.h
	${RAGEL_SOURCE_DIR}/ragel/gofflat.h
	${RAGEL_SOURCE_DIR}/ragel/gogoto.h
	${RAGEL_SOURCE_DIR}/ragel/gofgoto.h
	${RAGEL_SOURCE_DIR}/ragel/goipgoto.h
	${RAGEL_SOURCE_DIR}/ragel/gotablish.h
	${RAGEL_SOURCE_DIR}/ragel/mlcodegen.h
	${RAGEL_SOURCE_DIR}/ragel/mltable.h
	${RAGEL_SOURCE_DIR}/ragel/mlftable.h
	${RAGEL_SOURCE_DIR}/ragel/mlflat.h
	${RAGEL_SOURCE_DIR}/ragel/mlfflat.h
	${RAGEL_SOURCE_DIR}/ragel/mlgoto.h
	${RAGEL_SOURCE_DIR}/ragel/mlfgoto.h
)

file(GLOB SRC
	${RAGEL_SOURCE_DIR}/ragel/main.cpp
	${RAGEL_SOURCE_DIR}/ragel/parsetree.cpp
	${RAGEL_SOURCE_DIR}/ragel/parsedata.cpp
	${RAGEL_SOURCE_DIR}/ragel/fsmstate.cpp
	${RAGEL_SOURCE_DIR}/ragel/fsmbase.cpp
	${RAGEL_SOURCE_DIR}/ragel/fsmattach.cpp
	${RAGEL_SOURCE_DIR}/ragel/fsmmin.cpp
	${RAGEL_SOURCE_DIR}/ragel/fsmgraph.cpp
	${RAGEL_SOURCE_DIR}/ragel/fsmap.cpp
	${RAGEL_SOURCE_DIR}/ragel/rlscan.cpp
	${RAGEL_SOURCE_DIR}/ragel/rlparse.cpp
	${RAGEL_SOURCE_DIR}/ragel/inputdata.cpp
	${RAGEL_SOURCE_DIR}/ragel/common.cpp
	${RAGEL_SOURCE_DIR}/ragel/redfsm.cpp
	${RAGEL_SOURCE_DIR}/ragel/gendata.cpp
	${RAGEL_SOURCE_DIR}/ragel/cdcodegen.cpp
	${RAGEL_SOURCE_DIR}/ragel/cdtable.cpp
	${RAGEL_SOURCE_DIR}/ragel/cdftable.cpp
	${RAGEL_SOURCE_DIR}/ragel/cdflat.cpp
	${RAGEL_SOURCE_DIR}/ragel/cdfflat.cpp
	${RAGEL_SOURCE_DIR}/ragel/cdgoto.cpp
	${RAGEL_SOURCE_DIR}/ragel/cdfgoto.cpp
	${RAGEL_SOURCE_DIR}/ragel/cdipgoto.cpp
	${RAGEL_SOURCE_DIR}/ragel/cdsplit.cpp
	${RAGEL_SOURCE_DIR}/ragel/javacodegen.cpp
	${RAGEL_SOURCE_DIR}/ragel/rubycodegen.cpp
	${RAGEL_SOURCE_DIR}/ragel/rubytable.cpp
	${RAGEL_SOURCE_DIR}/ragel/rubyftable.cpp
	${RAGEL_SOURCE_DIR}/ragel/rubyflat.cpp
	${RAGEL_SOURCE_DIR}/ragel/rubyfflat.cpp
	${RAGEL_SOURCE_DIR}/ragel/rbxgoto.cpp
	${RAGEL_SOURCE_DIR}/ragel/cscodegen.cpp
	${RAGEL_SOURCE_DIR}/ragel/cstable.cpp
	${RAGEL_SOURCE_DIR}/ragel/csftable.cpp
	${RAGEL_SOURCE_DIR}/ragel/csflat.cpp
	${RAGEL_SOURCE_DIR}/ragel/csfflat.cpp
	${RAGEL_SOURCE_DIR}/ragel/csgoto.cpp
	${RAGEL_SOURCE_DIR}/ragel/csfgoto.cpp
	${RAGEL_SOURCE_DIR}/ragel/csipgoto.cpp
	${RAGEL_SOURCE_DIR}/ragel/cssplit.cpp
	${RAGEL_SOURCE_DIR}/ragel/dotcodegen.cpp
	${RAGEL_SOURCE_DIR}/ragel/xmlcodegen.cpp
	${RAGEL_SOURCE_DIR}/ragel/gocodegen.cpp
	${RAGEL_SOURCE_DIR}/ragel/gotable.cpp
	${RAGEL_SOURCE_DIR}/ragel/goftable.cpp
	${RAGEL_SOURCE_DIR}/ragel/goflat.cpp
	${RAGEL_SOURCE_DIR}/ragel/gofflat.cpp
	${RAGEL_SOURCE_DIR}/ragel/gogoto.cpp
	${RAGEL_SOURCE_DIR}/ragel/gofgoto.cpp
	${RAGEL_SOURCE_DIR}/ragel/goipgoto.cpp
	${RAGEL_SOURCE_DIR}/ragel/gotablish.cpp
	${RAGEL_SOURCE_DIR}/ragel/mlcodegen.cpp
	${RAGEL_SOURCE_DIR}/ragel/mltable.cpp
	${RAGEL_SOURCE_DIR}/ragel/mlftable.cpp
	${RAGEL_SOURCE_DIR}/ragel/mlflat.cpp
	${RAGEL_SOURCE_DIR}/ragel/mlfflat.cpp
	${RAGEL_SOURCE_DIR}/ragel/mlgoto.cpp
	${RAGEL_SOURCE_DIR}/ragel/mlfgoto.cpp
)

add_executable(${CMAKE_PROJECT_NAME} ${SRC} ${HEADERS})
target_link_libraries(${CMAKE_PROJECT_NAME} PUBLIC ${CONAN_LIBS})
target_include_directories(${CMAKE_PROJECT_NAME} PRIVATE ${RAGEL_SOURCE_DIR}/aapl
                                                 PRIVATE ${CMAKE_SOURCE_DIR}
                                                 PRIVATE ${CMAKE_BINARY_DIR})

install(TARGETS ${CMAKE_PROJECT_NAME}
        RUNTIME DESTINATION bin)
