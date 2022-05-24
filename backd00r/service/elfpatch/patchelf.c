#include <stdio.h>
#include <elf.h>


/**
 * Remove the "PIE" flag from elf binaries, so that they can be used both:
 * - as a stand-alone executable
 * - as a LD_PRELOAD library
 * @param argc
 * @param argv
 * @return
 */
int main(int argc, const char *argv[]) {
	if (argc < 2) {
		printf("USAGE: ./patchelf <elf-file>\n");
		return 1;
	}
	FILE *f = fopen(argv[1], "r+");
	if (!f) { perror("open"); return 1; }

	Elf64_Ehdr header;
	fread(&header, sizeof(Elf64_Ehdr), 1, f);

	fseek(f, header.e_phoff, SEEK_SET);
	for (int i = 0; i < header.e_phnum; i++) {
		Elf64_Phdr phdr;
		fread(&phdr, header.e_phentsize, 1, f);
		if (phdr.p_type == PT_DYNAMIC) {
			fseek(f, phdr.p_offset, SEEK_SET);

			Elf64_Dyn dyn;
			for (int i = 0; i < phdr.p_filesz; i += sizeof(dyn)) {
				fread(&dyn, sizeof(Elf64_Dyn), 1, f);
				if (dyn.d_tag == DT_FLAGS_1) {
					printf("flags = 0x%x, PIE=0x%x\n", dyn.d_un.d_val, DF_1_PIE);
					dyn.d_un.d_val = dyn.d_un.d_val & (~DF_1_PIE);
					fseek(f, -sizeof(Elf64_Dyn), SEEK_CUR);
					fwrite(&dyn, sizeof(Elf64_Dyn), 1, f);
					fclose(f);
					printf("Patched!\n");
					return 0;
				}
			}

			break;
		}
	}

	fclose(f);
	return 1;
}
