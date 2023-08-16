#include <fontconfig/fontconfig.h>
#include <stdio.h>
#include <stdlib.h>

int main() {
	FcConfig* config = FcInitLoadConfigAndFonts();
	FcPattern* pat = FcNameParse((const FcChar8*)"Arial");
	FcConfigSubstitute(config, pat, FcMatchPattern);
	FcDefaultSubstitute(pat);
	char* fontFile;
	FcResult result;
	FcPattern* font = FcFontMatch(config, pat, &result);
	if (font) {
		FcChar8* file = NULL;
		if (FcPatternGetString(font, FC_FILE, 0, &file) == FcResultMatch) {
			fontFile = (char*)file;
			printf("%s\n",fontFile);
		}
	} else {
        printf("Ops! I can't find any font!\n");
    }
	FcPatternDestroy(pat);
    return EXIT_SUCCESS;
}
