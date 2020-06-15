cmake_minimum_required(VERSION 3.10)
project(find_boost_components)

#set(CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR};${BOOST_ROOT}/lib/cmake/Boost-${BOOST_VERSION};${CMAKE_MODULE_PATH}")
set(CMAKE_MODULE_PATH "${BOOST_ROOT}/lib/cmake/Boost-${BOOST_VERSION};${CMAKE_CURRENT_SOURCE_DIR}")

message(STATUS "Find module = ${BOOST_VERSION}")
message(STATUS "Find module = ${CMAKE_MODULE_PATH}")

set(Boost_NO_SYSTEM_PATHS ON)
set(Boost_DEBUG ON)
if(BOOST_VERSION VERSION_LESS "1.70.0")
  set(Boost_NO_BOOST_CMAKE ON)
  list(
      APPEND
      components

      atomic
      chrono
      container
      context
      contract
      coroutine
      date_time
      exception
      filesystem
      graph
      iostreams
      locale
      log
      log_setup
      math_tr1
      math_tr1l
      math_tr1f
      math_c99
      math_c99l
      math_c99f
      program_options
      random
      regex
      serialization
      system
      test_exec_monitor
      thread
      timer
      type_erasure
      unit_test_framework
      wave
  )

  if( MSVC )
    list(APPEND components fiber)
  endif()

  find_package(
    Boost ${BOOST_VERSION}
    COMPONENTS ${components}
  )

  unset(Boost_LIBRARIES)
  foreach(component IN LISTS components)
    list(APPEND Boost_LIBRARIES "Boost::${component}")
  endforeach()
else()
  find_package(Boost ${BOOST_VERSION} COMPONENTS ALL)
endif()

if( NOT Boost_FOUND )
  message(FATAL_ERROR "Boost not found")
endif()
message(STATUS "Boost_LIBRARIES = ${Boost_LIBRARIES}")

set(dependencies_yml "${CMAKE_BINARY_DIR}/BoostComponents.yml")
file(WRITE ${dependencies_yml} "Boost:\n")
foreach(full_component IN LISTS Boost_LIBRARIES)
  string(REPLACE "Boost::" "" component ${full_component})
  file(APPEND ${dependencies_yml} "  '${component}':\n")

  get_target_property(target_type ${full_component} TYPE)
  message(STATUS "${full_component} is ${target_type}")

  get_target_property(dependencies ${full_component} INTERFACE_LINK_LIBRARIES)
  message(STATUS "${component} dependencies = ${dependencies}")
  if(dependencies)
    file(APPEND ${dependencies_yml} "    requires:\n")
    foreach(dependency IN LISTS dependencies)
      string(REPLACE "Boost::" "" dependency_component ${dependency})
      file(APPEND ${dependencies_yml} "      - '${dependency_component}'\n")
    endforeach()
  endif()

  if( NOT target_type STREQUAL "INTERFACE_LIBRARY")
      string(TOUPPER ${CMAKE_BUILD_TYPE} upper_build_type)
      get_target_property(libraries ${full_component} "IMPORTED_LOCATION_${upper_build_type}")
      message(STATUS "${component} libraries = ${libraries}")
      if(libraries)
        file(APPEND ${dependencies_yml} "    libs:\n")
        foreach(library IN LISTS libraries)
          file(APPEND ${dependencies_yml} "      - '${library}'\n")
        endforeach()
      endif()
  endif()

  get_target_property(include_directories ${full_component} INTERFACE_INCLUDE_DIRECTORIES)
  if(include_directories)
    file(APPEND ${dependencies_yml} "    includes:\n")
    foreach(include IN LISTS include_directories)
      file(APPEND ${dependencies_yml} "      - '${include}'\n")
    endforeach()
  endif()

  get_target_property(compile_definitions ${full_component} INTERFACE_COMPILE_DEFINITIONS)
  if(compile_definitions)
    file(APPEND ${dependencies_yml} "    definitions:\n")
    foreach(definition IN LISTS compile_definitions)
      file(APPEND ${dependencies_yml} "      - '${definition}'\n")
    endforeach()
  endif()

  if( NOT dependencies AND NOT libraries)
    file(APPEND ${dependencies_yml} " null\n")
  endif()
endforeach()
