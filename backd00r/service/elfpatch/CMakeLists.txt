cmake_minimum_required(VERSION 3.0.0 FATAL_ERROR)

project("r00t-client" VERSION 0.1.0 LANGUAGES C)
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_FLAGS "-Werror=implicit-function-declaration")

list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")

set(SOURCES patchelf.c)

add_executable(patchelf ${SOURCES})
