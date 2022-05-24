cmake_minimum_required(VERSION 3.5)
project(SaarCloud CXX)

include(CheckIncludeFileCXX)

check_include_file_cxx(any HAS_ANY)
check_include_file_cxx(string_view HAS_STRING_VIEW)
check_include_file_cxx(coroutine HAS_COROUTINE)
if (HAS_ANY AND HAS_STRING_VIEW AND HAS_COROUTINE)
    set(CMAKE_CXX_STANDARD 20)
elseif (HAS_ANY AND HAS_STRING_VIEW)
    set(CMAKE_CXX_STANDARD 17)
else ()
    set(CMAKE_CXX_STANDARD 14)
endif ()

set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

link_directories(third_party/v8)
add_definitions(-DV8_COMPRESS_POINTERS)

add_executable(${PROJECT_NAME}
        main.cc
        jsengine/caching.h
        jsengine/JSExecutionEngine.h
        jsengine/JSExecutionEngine.cpp
        jsengine/LambdaRequest.h
		jsengine/DatabaseEngine.h
        jsengine/DatabaseEngine.cpp)

# ##############################################################################
# If you include the drogon source code locally in your project, use this method
# to add drogon 
# add_subdirectory(drogon) 
# target_link_libraries(${PROJECT_NAME} PRIVATE drogon)
#
# and comment out the following lines
#find_package(Drogon CONFIG REQUIRED)
#target_link_libraries(${PROJECT_NAME} PRIVATE Drogon::Drogon)

# Fetch Drogon
include(FetchContent)
FetchContent_Declare(drogon GIT_REPOSITORY https://github.com/drogonframework/drogon.git GIT_TAG v1.7.5)
FetchContent_GetProperties(drogon)
if (NOT drogon_POPULATED)
    FetchContent_Populate(drogon)
    message("Retrieved drogon to \"${drogon_SOURCE_DIR}\"")

    # Patch drogon (add callback to new database connections)
    file(READ ${drogon_SOURCE_DIR}/orm_lib/src/sqlite3_impl/Sqlite3Connection.cc filedata)
    string(REGEX REPLACE "sqlite3_extended_result_codes" "harden_new_sqlite3_connection(tmp); // PATCHED\n\t\t\tsqlite3_extended_result_codes" filedata "${filedata}")
    string(REGEX REPLACE "#include <regex>" "#include <regex>\n#include \"../../../../sqlite3_hardening.h\" // PATCHED" filedata "${filedata}")
    file(WRITE ${drogon_SOURCE_DIR}/orm_lib/src/sqlite3_impl/Sqlite3Connection.cc "${filedata}")
    # Patch drogon (enable brotli compression for all requests)
    file(READ ${drogon_SOURCE_DIR}/lib/src/HttpResponseImpl.cc filedata)
    string(REPLACE "getBody().length() < 1024" "getBody().length() < 64" filedata "${filedata}")
    file(WRITE ${drogon_SOURCE_DIR}/lib/src/HttpResponseImpl.cc "${filedata}")
    message("Patched drogon")
endif ()

add_subdirectory(${drogon_SOURCE_DIR})
include_directories(${drogon_SOURCE_DIR}/lib/src)
target_link_libraries(${PROJECT_NAME} PRIVATE drogon)

# Fetch pre-compiled v8 JS engine
if (NOT EXISTS "${CMAKE_SOURCE_DIR}/third_party/v8")
    if (NOT EXISTS "${CMAKE_SOURCE_DIR}/v8_bundle.tar.xz")
        file(DOWNLOAD "https://ctf.saarland/static/v8_bundle.tar.xz" "${CMAKE_SOURCE_DIR}/v8_bundle.tar.xz" TIMEOUT 120 TLS_VERIFY ON)
    endif()
    file(ARCHIVE_EXTRACT INPUT "${CMAKE_SOURCE_DIR}/v8_bundle.tar.xz" DESTINATION "${CMAKE_SOURCE_DIR}/third_party")
    file(RENAME "${CMAKE_SOURCE_DIR}/third_party/v8_bundle" "${CMAKE_SOURCE_DIR}/third_party/v8")
endif()
include_directories(third_party/v8/include)
target_link_libraries(${PROJECT_NAME} PRIVATE v8_monolith)
add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_SOURCE_DIR}/third_party/v8/icudtl.dat ${CMAKE_CURRENT_BINARY_DIR}/icudtl.dat)



# ##############################################################################

if (CMAKE_CXX_STANDARD LESS 17)
    # With C++14, use boost to support any and string_view
    message(STATUS "use c++14")
    find_package(Boost 1.61.0 REQUIRED)
    target_include_directories(${PROJECT_NAME} PRIVATE ${Boost_INCLUDE_DIRS})
elseif (CMAKE_CXX_STANDARD LESS 20)
    message(STATUS "use c++17")
else ()
    message(STATUS "use c++20")
endif ()

aux_source_directory(controllers CTL_SRC)
aux_source_directory(filters FILTER_SRC)
aux_source_directory(plugins PLUGIN_SRC)
aux_source_directory(models MODEL_SRC)

drogon_create_views(${PROJECT_NAME} ${CMAKE_CURRENT_SOURCE_DIR}/views
                    ${CMAKE_CURRENT_BINARY_DIR})
# use the following line to create views with namespaces.
# drogon_create_views(${PROJECT_NAME} ${CMAKE_CURRENT_SOURCE_DIR}/views
#                     ${CMAKE_CURRENT_BINARY_DIR} TRUE)

target_include_directories(${PROJECT_NAME}
                           PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}
                                   ${CMAKE_CURRENT_SOURCE_DIR}/models)
target_sources(${PROJECT_NAME}
               PRIVATE
               ${SRC_DIR}
               ${CTL_SRC}
               ${FILTER_SRC}
               ${PLUGIN_SRC}
               ${MODEL_SRC})
# ##############################################################################
# uncomment the following line for dynamically loading views 
# set_property(TARGET ${PROJECT_NAME} PROPERTY ENABLE_EXPORTS ON)
