cmake_minimum_required(VERSION 3.8)
project(Miniscript LANGUAGES C CXX)

set(MINISCRIPT_SRC
    ${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/MiniScript/Dictionary.cpp
    ${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/MiniScript/List.cpp
    ${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/MiniScript/MiniscriptInterpreter.cpp
    ${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/MiniScript/MiniscriptIntrinsics.cpp
    ${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/MiniScript/MiniscriptKeywords.cpp
    ${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/MiniScript/MiniscriptLexer.cpp
    ${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/MiniScript/MiniscriptParser.cpp
    ${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/MiniScript/MiniscriptTAC.cpp
    ${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/MiniScript/MiniscriptTypes.cpp
    ${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/MiniScript/QA.cpp
    ${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/MiniScript/SimpleString.cpp
    ${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/MiniScript/SimpleVector.cpp
    ${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/MiniScript/SplitJoin.cpp
    ${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/MiniScript/UnicodeUtil.cpp
    ${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/MiniScript/UnitTest.cpp
)

set(MINISCRIPT_INC
    ${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/MiniScript/Dictionary.h
    ${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/MiniScript/List.h
    ${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/MiniScript/MiniscriptErrors.h
    ${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/MiniScript/MiniscriptInterpreter.h
    ${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/MiniScript/MiniscriptIntrinsics.h
    ${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/MiniScript/MiniscriptKeywords.h
    ${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/MiniScript/MiniscriptLexer.h
    ${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/MiniScript/MiniscriptParser.h
    ${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/MiniScript/MiniscriptTAC.h
    ${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/MiniScript/MiniscriptTypes.h
    ${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/MiniScript/QA.h
    ${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/MiniScript/RefCountedStorage.h
    ${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/MiniScript/SimpleString.h
    ${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/MiniScript/SimpleVector.h
    ${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/MiniScript/SplitJoin.h
    ${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/MiniScript/UnicodeUtil.h
    ${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/MiniScript/UnitTest.h
)

add_library(miniscript-cpp ${MINISCRIPT_SRC})
target_include_directories(miniscript-cpp PRIVATE ${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src)
set_target_properties(miniscript-cpp PROPERTIES
    PUBLIC_HEADER "${MINISCRIPT_INC}"
    C_EXTENSIONS OFF
)
target_compile_features(miniscript-cpp PRIVATE cxx_std_11)

if(MSVC)
    target_compile_options(miniscript-cpp PRIVATE /EHsc /wd4068)
endif()

find_library(LIBM m)
target_link_libraries(miniscript-cpp PRIVATE $<$<BOOL:${LIBM}>:${LIBM}>)

set(MINICMD_HEADERS
	${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/OstreamSupport.h
	${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/ShellIntrinsics.h
	${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/editline/editline.h
	${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/editline/unix.h
)

if(NOT WIN32)
	set(EDITLINE_SRC
		${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/editline/complete.c
		${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/editline/editline.c
		${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/editline/sysunix.c
	)
endif()

add_executable(minicmd
	${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/main.cpp
	${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/OstreamSupport.cpp
	${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/ShellIntrinsics.cpp
	${EDITLINE_SRC}
	${MINICMD_HEADERS}
)
target_include_directories(minicmd PRIVATE ${MINISCRIPT_SRC_DIR}/MiniScript-cpp/src/editline)
target_link_libraries(minicmd PRIVATE miniscript-cpp)
target_compile_features(minicmd PRIVATE cxx_std_11)

include(GNUInstallDirs)
install(
    TARGETS miniscript-cpp minicmd
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/MiniScript
)
