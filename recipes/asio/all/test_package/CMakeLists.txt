cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(asio REQUIRED CONFIG)

if (WIN32)
  execute_process(
    COMMAND cmd /c ver
    OUTPUT_VARIABLE _win_ver
    OUTPUT_STRIP_TRAILING_WHITESPACE
  )

  if (_win_ver MATCHES "\[5\\.1]")
    add_definitions(-D_WIN32_WINNT=0x0501) # Windows XP
  elseif (_win_ver MATCHES "\[5\\.2]")
    add_definitions(-D_WIN32_WINNT=0x0502) # Windows Server 2003
  elseif (_win_ver MATCHES "\[6\\.0]")
    add_definitions(-D_WIN32_WINNT=0x0600) # Windows Vista
  elseif (_win_ver MATCHES "\[6\\.1]")
    add_definitions(-D_WIN32_WINNT=0x0601) # Windows 7
  elseif (_win_ver MATCHES "\[6\\.2]")
    add_definitions(-D_WIN32_WINNT=0x0602) # Windows 8
  elseif (_win_ver MATCHES "\[6\\.3]")
    add_definitions(-D_WIN32_WINNT=0x0603) # Windows 8.1
  elseif (_win_ver MATCHES "\[10\\.0]")
    add_definitions(-D_WIN32_WINNT=0x0A00) # Windows 10
  else()
    message(WARNING "Unknown Windows version: ${_win_ver}, defaulting to Windows 10")
    add_definitions(-D_WIN32_WINNT=0x0A00)
  endif ()
endif ()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE asio::asio)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
