cmake_minimum_required(VERSION 3.0.0 FATAL_ERROR)

project("r00t-kernel" VERSION 0.1.0 LANGUAGES C)
set(CMAKE_C_STANDARD 90)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Find kernel headers
list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")
find_package(KernelHeaders REQUIRED)


# find MODULE_LICENSE("GPL"), MODULE_AUTHOR() etc.
# thanks to "merseyviking" from stack overflow
add_definitions(-D__KERNEL__ -DMODULE)
add_definitions(-D__KERNEL__ -DCONFIG_X86_X32_ABI -DCC_USING_FENTRY -DMODULE -DKBUILD_BASENAME=\"r00t\" -DKBUILD_MODNAME=\"r00t\")

# this is needed in order for CLion IDE to provide syntax highlightning
# this is independent from the actual kernel object that is built
add_executable(r00t
		# add all *.h and *.c files here that # CLion should cover
		r00t-module.c
		)

add_custom_target(make ALL COMMAND sh -c "make" WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}/r00t-kernel")
add_custom_target(make_test ALL COMMAND sh -c "make test" WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}/r00t-kernel")
add_dependencies(make_test r00t-raw-client)
add_custom_target(make_install ALL COMMAND sh -c "make install" WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}/r00t-kernel")

# CLion IDE will find symbols from <linux/*>
message("Include dirs: ${KERNELHEADERS_INCLUDE_DIRS}")
target_include_directories("r00t" PRIVATE ${KERNELHEADERS_INCLUDE_DIRS})

