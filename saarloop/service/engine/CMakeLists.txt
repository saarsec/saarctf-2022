cmake_minimum_required(VERSION 3.18)
project(saarloop_engine)

set(CMAKE_CXX_STANDARD 17)

add_executable(saarloop_engine main.cpp)

target_include_directories(saarloop_engine PRIVATE /usr/include/jsoncpp)
target_link_libraries(saarloop_engine jsoncpp sndfile)
