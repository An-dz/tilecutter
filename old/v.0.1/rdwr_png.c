
/*
 * read defines
 */

#include <png.h>
#include <stdlib.h>


//#include "rdwr_png.h"


static int bit_depth, color_type, interlace_type;

void
read_png(unsigned char **block, png_uint_32 *width, png_uint_32 *height, FILE *file)
{
    png_structp png_ptr;
    png_infop   info_ptr;
    png_bytep *row_pointers;
    unsigned row, x, y;
    int rowbytes;
    char *dst;

    png_ptr = png_create_read_struct(PNG_LIBPNG_VER_STRING,NULL,NULL,NULL);
    if (png_ptr == NULL) {
	printf("\nERROR: read_png: Could not create read struct.\n");
	exit(1);
    }

    info_ptr = png_create_info_struct(png_ptr);
    if (info_ptr == NULL) {
	printf("\nERROR: read_png: Could not create info struct.\n");
	png_destroy_read_struct(&png_ptr, (png_infopp)NULL, (png_infopp)NULL);
	exit(1);
    }


    if (setjmp(png_ptr->jmpbuf)) {

	printf("\nERROR: read_png: fatal error.\n");
        png_destroy_read_struct(&png_ptr, &info_ptr, (png_info **)0);
        /* free pointers before returning, if necessary */
        free(png_ptr);
        free(info_ptr);

	exit(1);
    }

    /* Set up the input control if you are using standard C streams */
    png_init_io(png_ptr, file);


    /* The call to png_read_info() gives us all of the information from the
     * PNG file before the first IDAT (image data chunk).  REQUIRED
     */
    png_read_info(png_ptr, info_ptr);

    png_get_IHDR(png_ptr, info_ptr, width, height, &bit_depth, &color_type, &interlace_type, NULL, NULL);

    // printf("read_png: width=%d, height=%d, bit_depth=%d\n", width, height, bit_depth);
    // printf("read_png: color_type=%d, interlace_type=%d\n", color_type, interlace_type);
    
    // strip alpha information
    if (color_type & PNG_COLOR_MASK_ALPHA) {
        png_set_strip_alpha(png_ptr);
    }

//    /* tell libpng to strip 16 bit/color files down to 8 bits/color */
//    png_set_strip_16(png_ptr);

    /* Extract multiple pixels with bit depths of 1, 2, and 4 from a single
     * byte into separate bytes (useful for paletted and grayscale images).
     */
    png_set_packing(png_ptr);

    /* Expand paletted colors into true RGB triplets */
    png_set_expand(png_ptr);

    png_start_read_image(png_ptr);

    /* The easiest way to read the image: */

    rowbytes = png_get_rowbytes(png_ptr, info_ptr) * 3;
    row_pointers = (png_bytep *)malloc((*height) * sizeof(*row_pointers));

    row_pointers[0] = (png_bytep)malloc(rowbytes * (*height) * 2);

    for(row = 1; row < (*height); row++) {
	row_pointers[row] = row_pointers[row - 1] + rowbytes*2;
    }
    /* Read the entire image in one go */
    png_read_image(png_ptr, row_pointers);

    // we use fixed height here because block is of limited, fixed size
    // not fixed any more

    *block = realloc(*block, *height * *width * 3);

    // *block = malloc(*height * *width * 6);

    dst = *block;
    for(y = 0; y < *height; y++) {
	for(x = 0; x < *width * 3; x++) {
	  *dst++ = row_pointers[y][x];

	  // *dst++ = 0;
	}
    }
  
    free(row_pointers[0]);
    free(row_pointers);

    /* read rest of file, and get additional chunks in info_ptr - REQUIRED */
    png_read_end(png_ptr, info_ptr);

    /* At this point you have read the entire image */

    /* clean up after the read, and free any memory allocated - REQUIRED */
    png_destroy_read_struct(&png_ptr, &info_ptr, (png_infopp)NULL);
}



void write_png(char *file_name, int w, int h, void *data )
{
//  w = 128; h = 128;
	unsigned row, x, y;
	int rowbytes;
	char *dst;
	FILE *fp = fopen(file_name, "wb");
	png_bytep row_pointers[5280];

	if (!fp)
	{
		printf("\nERROR: write_png: Could not create output file.\n");
		exit(1);
	}

	png_structp png_ptr = png_create_write_struct( PNG_LIBPNG_VER_STRING, NULL, NULL, NULL );
	if (!png_ptr)
	{
		printf("\nERROR: write_png: Could not create write struct.\n");
		exit(1);
	}

	png_infop info_ptr = png_create_info_struct(png_ptr);
	if (!info_ptr)
	{
		printf("\nERROR: write_png: Could not create info struct.\n");
		png_destroy_write_struct(&png_ptr, (png_infopp)NULL);
		exit(1);
	}

	if (setjmp(png_ptr->jmpbuf)) {
		printf("\nERROR: write_png: fatal error.\n");
		png_destroy_read_struct(&png_ptr, &info_ptr, (png_info **)0);
		exit(1);
	}

	/* Set up the input control if you are using standard C streams */
	png_init_io(png_ptr, fp);

	// set the image format
	png_set_IHDR(png_ptr, info_ptr, w, h, 8, PNG_COLOR_TYPE_RGB, PNG_INTERLACE_NONE, PNG_COMPRESSION_TYPE_DEFAULT, PNG_FILTER_TYPE_DEFAULT );

	png_write_info(png_ptr, info_ptr);

	// set the ouptut lines
	for(  y=0;  y<h;  y++ ) {
		unsigned char *p = data;
		row_pointers[y] =  p+(y* (w*3) );
	}
    	png_write_image(png_ptr, row_pointers);

	// finally write
	png_write_end(png_ptr, info_ptr);

    /* clean up after the read, and free any memory allocated - REQUIRED */
    png_destroy_write_struct(&png_ptr, &info_ptr);
}



