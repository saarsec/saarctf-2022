# BIG THANK YOU TO THE ORIGINAL AUTHOR
# https://gitlab.com/christophacham/cmake-kernel-module

# Find the kernel release
execute_process(
		COMMAND uname -r
		OUTPUT_VARIABLE KERNEL_RELEASE
		OUTPUT_STRIP_TRAILING_WHITESPACE
)
string(REPLACE "-amd64" "-common" KERNEL_RELEASE_COMMON ${KERNEL_RELEASE})

# Find the headers
#find_path(KERNELHEADERS_DIR
#		include/linux/user.h
#		PATHS
#		/usr/src/linux-headers-${KERNEL_RELEASE}
#		/usr/src/linux-headers-${KERNEL_RELEASE_COMMON}
#		)
set(KERNELHEADERS_DIR1 /usr/src/linux-headers-${KERNEL_RELEASE})
set(KERNELHEADERS_DIR2 /usr/src/linux-headers-${KERNEL_RELEASE_COMMON})

message(STATUS "Kernel release: ${KERNEL_RELEASE}")
message(STATUS "Kernel headers: ${KERNELHEADERS_DIR}")

if (KERNELHEADERS_DIR1)
	set(KERNELHEADERS_INCLUDE_DIRS
			${KERNELHEADERS_DIR2}/arch/x86/include
			${KERNELHEADERS_DIR1}/arch/x86/include/generated
			${KERNELHEADERS_DIR2}/include
			${KERNELHEADERS_DIR1}/include
			${KERNELHEADERS_DIR2}/arch/x86/include/uapi
			${KERNELHEADERS_DIR1}/arch/x86/include/generated/uapi
			${KERNELHEADERS_DIR2}/include/uapi
			${KERNELHEADERS_DIR1}/include/generated/uapi
			CACHE PATH "Kernel headers include dirs"
			)
	set(KERNELHEADERS_FOUND 1 CACHE STRING "Set to 1 if kernel headers were found")
else (KERNELHEADERS_DIR1)
	set(KERNELHEADERS_FOUND 0 CACHE STRING "Set to 1 if kernel headers were found")
endif (KERNELHEADERS_DIR1)

mark_as_advanced(KERNELHEADERS_FOUND)
