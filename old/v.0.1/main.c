#include <gtk/gtk.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <png.h>



//Global variables
unsigned char *loadBMB=NULL;               //Loaded image block
unsigned char *oldBMB=NULL;                //Input image block
unsigned char *newBMB=NULL;                //Output image block
unsigned Xin, Yin;                         //X and Y values for the input image
unsigned Xout, Yout;                       //X and Y values for the output image
//char filename_in[1024] = "example.png";    //Input filename
//char filename_out[1024] = "output.png";    //Output filename
char *filename_in;                         //Input filename (pointer)
char *filename_out;                        //Output filename (pointer)
char *dat_filename_out;                     //Output dat filename (pointer)
//Relating to system operation, global
unsigned int pakSize = 0;                  //Tilesize
unsigned int pakIreg = 0;                  //Is the image irregularly sized? 0 = no, 1 = yes
unsigned int pakOrient = 0;                //Orientation for odd shaped buildings, 0 is north, 1 is east, 2 is south, 3 is west
unsigned int tileX = 0;                    //Length of the building in tiles (North-South)
unsigned int tileY = 0;                    //Width of the building in tiles (East-West)
unsigned int tileZ = 0;                    //Height of the building in tiles (override)



int MaskXY (unsigned int toX, unsigned int toY, unsigned int newBmpX, unsigned int newBmpY, unsigned int maskType);

int write_dat(char *dat_file_name, char *file_name, int X, int Y, int Z, int Ireg, int Orient) {
int a, b, c, d, e, q;

  
  FILE *fdat = fopen(dat_file_name, "w");
  if (fdat == NULL) {
    printf("\nERROR: Could not open dat file \"%s\" for writing!\nAborting dat file write...\n", dat_file_name);
    return(1);
  }
  fprintf(fdat, "Partial dat file, this file will NOT compile with makeobj!\n\nCreated with TileCutter - http://simutrans.entropy.me.uk/tilecutter\n\n");
  fprintf(fdat, "Dims=%i,%i\n", Y, X);
//  if (Ireg == 0) {    
    for (a = 0; a < X; a++) {
      for (b = 0; b < Y; b++) {
        fprintf(fdat, "BackImage[0][%i][%i][0][0]=%s", a, b, file_name);
        fseek(fdat, -3, SEEK_CUR);
        fprintf(fdat, "%i.%i\n", b, (X - a - 1));
      }
    }
    if (Z > 1) {
      if (pakIreg == 0) {q = 1;} else {q = 0;}
      for (c = 0; c < (Z - 1); c++) {
        for (a = 0; a < 1; a++) {
          for (b = 0; b < Y; b++) {
            fprintf(fdat, "BackImage[0][%i][%i][%i][0]=%s", a, b, (Z - c - 1), file_name);
            fseek(fdat, -3, SEEK_CUR);
            d = (X - (b + 1));
            e = (Y + 2 + (c - q) * 2);
            fprintf(fdat, "%i.%i\n", e, d);
          }
        }
//        printf("Done row A\n\n");
        for (a = 1; a < X; a++) {
          fprintf(fdat, "BackImage[0][%i][%i][%i][0]=%s", a, 0, (Z - c - 1), file_name);
          fseek(fdat, -3, SEEK_CUR);
            d = (X - (a + 1));
            e = (Y + 3 + (c - q) * 2);
          fprintf(fdat, "%i.%i\n", e, d);
        }
//        printf("Done row B\n\n");
      }
    }    

  fclose(fdat);
  printf("Dat file write complete!\n");
}
//===========================================

int LoadImage () {
  printf("Reading png file...");
  FILE *fpng = fopen(filename_in, "rb");
  if(fpng == NULL) {
    printf("\nERROR: Could not open png file \"%s\" for reading!\nAborting png file read...", filename_in);
    return(1);
  }
  if(oldBMB != NULL) {
    free(oldBMB);
  }
  
  read_png(&loadBMB, &Xin, &Yin, fpng );
  fclose(fpng);
  printf("Png read complete!\n");
  
}
//===========================================
//Make a new bitmap, ready for writing to by the cutter	
int NewBitmap (unsigned int newbmpX, unsigned int newbmpY) {
  printf("Making new image...\n");
  int size = (newbmpX * newbmpY * 3);
  if(newBMB!=NULL) {
    free(newBMB);
  }
  
//  newBMB = calloc(size, 1);  
  newBMB = realloc(newBMB, size);
 
  int n;
  for (n = 0; n < size; n = (n + 3)) {
    newBMB[n] = 231;
    newBMB[(n + 1)] = 255;
    newBMB[(n + 2)] = 255;   
  }
//  int i;
//  for (i = 0; i < size; i++) {
//      printf("%i", i); 
//      printf("%c ", newBMB[i]); 
//  }
  printf("Make new image complete!\n");   
  return (0);
}


//===========================================

int CopyXY (unsigned int fromX, unsigned int fromY, unsigned int toX, unsigned int toY, unsigned int newBmpX, unsigned int newBmpY) {
  int n, m;
  for (n = 0; n < (pakSize); n++) {
    for (m = 0; m < (pakSize * 3); m++) {
      int fromVal = (((Xin * 3) * (n + fromY)) + (m + (fromX * 3)));
      int toVal = (((Xout * 3) * (n + toY)) + (m + (toX * 3)));

      newBMB[toVal] = oldBMB[fromVal];
    }
  }

/*  for (n = 0; n < (Xout * Yout * 3); n = (n + 3)) {
    newBMB[n] = 231;
    newBMB[(n + 1)] = 255;
    newBMB[(n + 2)] = 255;   
  }*/
  return (0);
}
//===========================================
void showhelp(int term) {
  printf("\n  ---- TileCutter Instructions ----\n");
  printf("Type program name (tilecutter) followed by (in this order):\n");
  printf("input filename - e.g. \"example.png\", output png filename - e.g. \"output.png\", output dat filename - e.g. \"output.dat\"\n");
  printf("Required switches:\n");
  printf(" -pakSize XX | Where XX is a multiple of 16 between 16 and 240\n");
  printf("Optional switches:\n");
  printf(" -i XX YY    | Irregular building switch, use for non-square buildings.\n");
  printf("             | XX and YY are the length (N-S) and width (E-W)in tiles\n");
  printf("             | This switch is *required* for non-symmetrical buildings!\n");
  printf(" -f X        | Orientation switch, specifies the facing direction\n");
  printf("             | in the dat file. X is the orientation of the building:\n");
  printf("             | 0 = North, 1 = East, 2 = South, 3 = West\n");
  printf("             |       West  /\\   North\n");
  printf("             |     '-i 3'/    \\'-i 0'\n");
  printf("             |          <      >\n");
  printf("             |     '-i 2'\\    /'-i 1'\n");
  printf("             |      South  \\/ East\n");
  printf(" -h X        | Where X is the height of the building in tiles between 1 and 4\n");
  printf("             | The -h switch overrides automatic height detection!\n");
  if (term = 1) {abort();}
}

//===========================================
int main( int   argc,
          char *argv[] )
{
int returnval;    
int i;

//Deal with command line parameters...

//Parameters are - "filename" (filename for input), "filenameout" (filename for output), 
// "-pakSize XX" (paksize), "-i OrientVal" (irregular + OrientVal), 
//Orientation for odd shaped buildings, 0 is north, 1 is east, 2 is south, 3 is west

if(argc < 6) {
  showhelp(1);
} else {
  
  printf("\nTileCutter version 0.1\nhttp://simutrans.entropy.me.uk/tilecutter\n\n");
  
  filename_in = argv[1];
  filename_out = argv[2];
  dat_filename_out = argv[3];
  
  int loop;
  for (loop = 4; loop < argc; loop++) {
  
    //Checks for the -pakSize parameter
    if (memcmp(argv[loop], "-pakSize", 9) == 0) {

      if (memcmp(argv[(loop + 1)], "16", 3) == 0) {pakSize = 16;}
      if (memcmp(argv[(loop + 1)], "32", 3) == 0) {pakSize = 32;}
      if (memcmp(argv[(loop + 1)], "48", 3) == 0) {pakSize = 48;}
      if (memcmp(argv[(loop + 1)], "64", 3) == 0) {pakSize = 64;}
      if (memcmp(argv[(loop + 1)], "80", 3) == 0) {pakSize = 80;}
      if (memcmp(argv[(loop + 1)], "96", 3) == 0) {pakSize = 96;}
      if (memcmp(argv[(loop + 1)], "112", 4) == 0) {pakSize = 112;}
      if (memcmp(argv[(loop + 1)], "128", 4) == 0) {pakSize = 128;}
      if (memcmp(argv[(loop + 1)], "144", 4) == 0) {pakSize = 144;}
      if (memcmp(argv[(loop + 1)], "160", 4) == 0) {pakSize = 160;}
      if (memcmp(argv[(loop + 1)], "176", 4) == 0) {pakSize = 176;}
      if (memcmp(argv[(loop + 1)], "192", 4) == 0) {pakSize = 192;}
      if (memcmp(argv[(loop + 1)], "208", 4) == 0) {pakSize = 208;}
      if (memcmp(argv[(loop + 1)], "224", 4) == 0) {pakSize = 224;}
      if (memcmp(argv[(loop + 1)], "240", 4) == 0) {pakSize = 240;}

      if (pakSize == 0) {
        printf("\nERROR: pakSize not supplied or incorrect, please check!\n");
        showhelp(1);
      }
    }
  
    //Code for -f (Orientation) switch...
    if (memcmp(argv[loop], "-f", 3) == 0) {
      if (memcmp(argv[(loop + 1)], "0", 2) == 0) {pakOrient = 0;}
      if (memcmp(argv[(loop + 1)], "1", 2) == 0) {pakOrient = 1;}
      if (memcmp(argv[(loop + 1)], "2", 2) == 0) {pakOrient = 2;}
      if (memcmp(argv[(loop + 1)], "3", 2) == 0) {pakOrient = 3;}
    }
  
    //Code for -i (Irregular) switch...
    if (memcmp(argv[loop], "-i", 3) == 0) {
      pakIreg = 1;
      //X value comes first after switch...  
      if (memcmp(argv[(loop + 1)], "1", 2) == 0) {tileX = 1;}
      if (memcmp(argv[(loop + 1)], "2", 2) == 0) {tileX = 2;} 
      if (memcmp(argv[(loop + 1)], "3", 2) == 0) {tileX = 3;} 
      if (memcmp(argv[(loop + 1)], "4", 2) == 0) {tileX = 4;} 
      if (memcmp(argv[(loop + 1)], "5", 2) == 0) {tileX = 5;} 
      if (memcmp(argv[(loop + 1)], "6", 2) == 0) {tileX = 6;} 
      if (memcmp(argv[(loop + 1)], "7", 2) == 0) {tileX = 7;} 
      if (memcmp(argv[(loop + 1)], "8", 2) == 0) {tileX = 8;} 
      if (memcmp(argv[(loop + 1)], "9", 2) == 0) {tileX = 9;} 
      if (memcmp(argv[(loop + 1)], "10", 3) == 0) {tileX = 10;} 
      if (memcmp(argv[(loop + 1)], "11", 3) == 0) {tileX = 11;} 
      if (memcmp(argv[(loop + 1)], "12", 3) == 0) {tileX = 12;} 
      if (memcmp(argv[(loop + 1)], "13", 3) == 0) {tileX = 13;} 
      if (memcmp(argv[(loop + 1)], "14", 3) == 0) {tileX = 14;} 
      if (memcmp(argv[(loop + 1)], "15", 3) == 0) {tileX = 15;} 
      if (memcmp(argv[(loop + 1)], "16", 3) == 0) {tileX = 16;}   
      //Y value comes second...  
      if (memcmp(argv[(loop + 2)], "1", 2) == 0) {tileY = 1;}
      if (memcmp(argv[(loop + 2)], "2", 2) == 0) {tileY = 2;} 
      if (memcmp(argv[(loop + 2)], "3", 2) == 0) {tileY = 3;} 
      if (memcmp(argv[(loop + 2)], "4", 2) == 0) {tileY = 4;} 
      if (memcmp(argv[(loop + 2)], "5", 2) == 0) {tileY = 5;} 
      if (memcmp(argv[(loop + 2)], "6", 2) == 0) {tileY = 6;} 
      if (memcmp(argv[(loop + 2)], "7", 2) == 0) {tileY = 7;} 
      if (memcmp(argv[(loop + 2)], "8", 2) == 0) {tileY = 8;} 
      if (memcmp(argv[(loop + 2)], "9", 2) == 0) {tileY = 9;} 
      if (memcmp(argv[(loop + 2)], "10", 3) == 0) {tileY = 10;} 
      if (memcmp(argv[(loop + 2)], "11", 3) == 0) {tileY = 11;} 
      if (memcmp(argv[(loop + 2)], "12", 3) == 0) {tileY = 12;} 
      if (memcmp(argv[(loop + 2)], "13", 3) == 0) {tileY = 13;} 
      if (memcmp(argv[(loop + 2)], "14", 3) == 0) {tileY = 14;} 
      if (memcmp(argv[(loop + 2)], "15", 3) == 0) {tileY = 15;} 
      if (memcmp(argv[(loop + 2)], "16", 3) == 0) {tileY = 16;} 
    }
    //Code for -h (Height override) switch
    if (memcmp(argv[loop], "-h", 3) == 0) {
      if (memcmp(argv[(loop + 1)], "1", 2) == 0) {tileZ = 1;}
      if (memcmp(argv[(loop + 1)], "2", 2) == 0) {tileZ = 2;}
      if (memcmp(argv[(loop + 1)], "3", 2) == 0) {tileZ = 3;}
      if (memcmp(argv[(loop + 1)], "4", 2) == 0) {tileZ = 4;}
    }
  }
}
//Check that inputted values are correct...
if (pakIreg == 1) {
  if (tileX == 0) {
    printf("ERROR: Ireg flag set, but no value or incorrect value for tileX!");
    showhelp(1);
  }
  if (tileY == 0) {
    printf("ERROR: Ireg flag set, but no value or incorrect value for tileY!");
    showhelp(1);
  }
}
if (pakSize == 0) {
  printf("ERROR: pakSize not supplied or bad value!");
  showhelp(1);
}
//Finish CLI input and emit sucess message and debug
printf("CLI read complete... \npakSize = %i, pakIreg = %i, pakOrient = %i, tileX = %i, tileY = %i, tileZ = %i\nInput Filename = %s\nOutput Filename = %s\n\n", 
  pakSize, pakIreg, pakOrient, tileX, tileY, tileZ, filename_in, filename_out);
  
  
  
  
  
//Load a png image 
  returnval = LoadImage();

//Ensure image conforms to the correct dimensions, as set out in pakSize...
  int bmpArrayX;
  int bmpArrayY;
  int bmpArrayZ;
  
  if ((Xin % (pakSize / 2)) != 0) {                //Is the image width a multiple of p/2? If not, abort

    printf("\nERROR: Invalid File Width\nInput file width must be a multiple of half the pak size!\n\n");
    showhelp(1);
    
  } else {                                         //Otherwise, continue... Is the image width grater than p*16? (Simutrans limit)
    if (pakIreg == 0) {                            //Also, if Ireg not set then must be a multiple of p
      if ((Xin % pakSize) != 0) {
        printf("\nERROR: Invalid File Width\nInput File Width must be a multiple of the pakSize, unless Ireg flag is set!\n\n");
        showhelp(1);
      }
    }

    if (Xin > (pakSize * 16)) {
       printf("\nERROR: Invalid File Width\nInput file width must not exceed 16 times the pak size!\n\n");
       showhelp(1);
    } else {                                       //Width seems ok, move onto height
      if (Yin <= ((Xin / 2) + (pakSize / 2))) {      //Is image of minimum height? (w/2 + p/2), if not, enlarge to w/2 + p/2    
/*        if (Yin == ((Xin / 2) + (pakSize / 2))) {
       
          int size = (Xin * (Xin + (pakSize / 2)) * 3);
        } else {
          int size = (Xin * (Xin + (pakSize / 2)) * 3);
        }*/
        int size = (Xin * (Xin + (pakSize / 2)) * 3);
        oldBMB = realloc(oldBMB, size);
     
        int diff = (size - (Xin * Yin * 3));
        int t;
        for (t = 0; t < diff; t = t + 3) {
          oldBMB[t] = 231;
          oldBMB[(t + 1)] = 255;
          oldBMB[(t + 2)] = 255; 
        }
        for (t = diff; t < size; t++) {    
          oldBMB[t] = loadBMB[(t - diff)];
        }
        bmpArrayZ = 1;
        Yin = Xin;
                
      } else {                                               //Otherwise, enlarge to nearest p and return a higher Z-index 
        int dime;
        int dimerem;
        int Yrem;
        
        if (Yin <= ((Xin / 2) + (3 * pakSize) + (pakSize / 2))) {    //If the image is smaller than maximum, enlarge to nearest p

          
          if (Xin % pakSize != 0) {           // If width not a multiple of the pak size...
            dimerem = pakSize - ((Yin - (Xin / 2)) % pakSize);
            dime = ((Yin - (Xin / 2)) / pakSize);
            printf("Alpha\n");
          } else {
            printf("Beta\n");                 // Width is a mutiple of paksize      
              Yrem = (Yin - (Xin / 2) - (pakSize / 2));
//              dimerem = pakSize - ((Yin - (Xin / 2) + (pakSize / 2)) % pakSize);
              
              dimerem = pakSize - (Yrem % pakSize);
              printf("Yrem = %i, dimerem = %i\n", Yrem, dimerem);
              if (dimerem == pakSize) {dimerem = 0;}
//              dime = ((Yin - (Xin / 2) + (pakSize / 2)) / pakSize);
              
              printf("Yrem = %i, dimerem = %i\n", Yrem, dimerem);
              if (dimerem == 0) {       
                dime = 1 + (Yrem / pakSize);
              } else {
                printf("meh");
                dime = 2 + (Yrem / pakSize);
              }
                 
              
              printf("Delta\n");

          }
//                  if (dimerem > (pakSize - 1)) {dimerem = dimerem - pakSize;}
          
          printf("dime: %i, dimerem: %i\n", dime, dimerem);

            int size = (Xin * (Yin + dimerem) * 3);
            oldBMB = realloc(oldBMB, size);
     
            int diff = (size - (Xin * Yin * 3));
            int t;
            for (t = 0; t < diff; t = t + 3) {
              oldBMB[t] = 231;
              oldBMB[(t + 1)] = 255;
              oldBMB[(t + 2)] = 255; 
            }
            for (t = diff; t < size; t++) {    
              oldBMB[t] = loadBMB[(t - diff)];
            }

          bmpArrayZ = dime; 
//          if (bmpArrayZ == 0) {bmpArrayZ = 1;}
          Yin = Yin + dimerem;
//          printf("\n\nYin: %i\n\n", Yin);
          
        } else {                             //If the image is taller than the maximum, reduce it
          dime = 4;
          dimerem = 0;
          Yin = (Xin + (pakSize * 2));
          printf("ERROR: Image too large vertically! (debug code 115)\n");
          abort();
        }
        
      }
    }
  }
  free(loadBMB);
//  if (tileZ != 0) {
//    bmpArrayZ = tileZ;
//  }

//Analyze the loaded image, to determine dimensions for cutting

if (pakIreg == 0) {
  bmpArrayX = (Xin / pakSize);
  bmpArrayY = (Xin / pakSize);
} else {
  bmpArrayX = tileX;
  bmpArrayY = tileY;
}

//  printf("\nbmpArrayX: %i bmpArrayY: %i bmpArrayZ: %i\n", bmpArrayX, bmpArrayY, bmpArrayZ);

//Width and height for new bitmap    
if (bmpArrayX < bmpArrayY) {              //For irregular images, the width of the produced image should be the largest
  Xout = (bmpArrayY * pakSize * 3);       //input dimension.
} else {
  Xout = (bmpArrayX * pakSize * 3);
}

if (tileZ != 0) {
  Yout = ((bmpArrayY + ((tileZ - 1) * 2)) * pakSize);
} else {
  Yout = ((bmpArrayY + ((bmpArrayZ - 1) * 2)) * pakSize);  
}
//  Height =   Width   +   Height index -1 * 2  * pakSize
//                                        times 2 for space for high tiles...
    
//Make a new bitmap ready for writing    
    returnval = NewBitmap (Xout, Yout);
//    printf("Xout: %i (%i), Yout: %i\n", Xout, (Xout / 3), Yout);
    
    Xout = Xout / 3; //No idea why this works...

//Copy bits from the old bitmap to the new one in the right order
  int fromX = 0;
  int fromY = 0;
  int toX = 0;
  int toY = 0;
  int x, y, z;
//Stage 1 - Main image (hieght level 1)
  printf("Copying tiles - CopyXY INIT - bmpArrayX: %i bmpArrayY: %i bmpArrayZ: %i...\n", bmpArrayX, bmpArrayY, bmpArrayZ);
  for (x = 0; x < bmpArrayX; x++) {
    for (y = 0; y < bmpArrayY; y++) {

      fromX = ((bmpArrayX * (pakSize / 2)) - (pakSize / 2) - (x * (pakSize / 2)) + (y * (pakSize / 2)));
      fromY = ((x * (pakSize / 4)) + (y * (pakSize / 4))) + pakSize + ((bmpArrayZ + (bmpArrayZ - 2)) * (pakSize / 2));
      
      if (pakIreg == 1) {fromY = fromY + (pakSize / 2);} //Hack to make irregular buildings cut properly
      
      toX = ((bmpArrayX - (x + 1)) * pakSize);
//      toY = ((y * pakSize) + (((bmpArrayZ - 1) * 2) * pakSize));
      toY = (y * pakSize);
      returnval = CopyXY (fromX, fromY, toX, toY, Xout, Yout);
      printf("CopyXY - fromX: %i fromY %i toX: %i toY: %i Error: %i\n", fromX, fromY, toX, toY, returnval);
    }
  }

//Stage 2 - If building is high, also do this to copy additional parts...
  if (tileZ != 0) {
    bmpArrayZ = tileZ;
  }
    if (bmpArrayZ > 1) {
      for (z = 0; z < (bmpArrayZ - 1); z++) {
        for (x = 0; x < 1; x++) {
          for (y = 0; y < bmpArrayY; y++) {
//            fromX = ((bmpArrayX * (pakSize / 2)) - (pakSize / 2) + (x * (pakSize / 2)));
//            fromY = ((x * (pakSize / 4)) + (bmpArrayY * (pakSize / 4))) + ((z + (z - 2)) * (pakSize / 4)); //works ok
            fromX = ((bmpArrayX * (pakSize / 2)) - (pakSize / 2) - (x * (pakSize / 2)) + (y * (pakSize / 2)));
            fromY = ((x * (pakSize / 4)) + (y * (pakSize / 4))) + pakSize + (((z+1) + ((z+1) - 2)) * (pakSize / 2));
            
            if (pakIreg == 1) {fromY = fromY + (pakSize / 2);} //Hack to make irregular buildings cut properly
            
            toX = ((bmpArrayX - (y + 1)) * pakSize);
            toY = ((bmpArrayY * pakSize) + (pakSize * 2) + (pakSize * (z - 1) * 2));
            returnval = CopyXY (fromX, fromY, toX, toY, Xout, Yout);
            printf("AACopyXY - fromX: %i fromY %i toX: %i toY: %i Error: %i\n", fromX, fromY, toX, toY, returnval);
          }
        }

        for (x = 1; x < bmpArrayX; x++) {
          for (y = 0; y < 1; y++) {
//          fromX = ((bmpArrayX * (pakSize / 2)) - (pakSize / 2) + (bmpArrayX * (pakSize / 2)) - ((y + 1) * (pakSize / 2)));          
//          fromY = ((bmpArrayX * (pakSize / 4)) + (y * (pakSize / 4))) + pakSize + ((z + (z - 2)) * (pakSize / 4));//works ok
            fromX = ((bmpArrayX * (pakSize / 2)) - (pakSize / 2) - (x * (pakSize / 2)) + (y * (pakSize / 2)));
            fromY = ((x * (pakSize / 4)) + (y * (pakSize / 4))) + pakSize + (((z+1) + ((z+1) - 2)) * (pakSize / 2));
            
            if (pakIreg == 1) {fromY = fromY + (pakSize / 2);} //Hack to make irregular buildings cut properly
            
            toX = ((bmpArrayX - (x + 1)) * pakSize);
            toY = ((bmpArrayY * pakSize) + (pakSize * 3) + (pakSize * (z - 1) * 2));                  
            returnval = CopyXY (fromX, fromY, toX, toY, Xout, Yout);
            printf("BBCopyXY - fromX: %i fromY %i toX: %i toY: %i Error: %i\n", fromX, fromY, toX, toY, returnval);          
          }
        }

      }
    }
printf("Tile copy complete!\n");

//Apply the mask of the right type to the copied image
//Masks for first level first...
printf("Applying masks...\n");
  for (x = 0; x < bmpArrayX; x++) {
    for (y = 0; y < bmpArrayY; y++) {
      toX = ((bmpArrayX - (x + 1)) * pakSize);
//      toY = ((y * pakSize) + ((bmpArrayZ + (bmpArrayZ - 2)) * (pakSize)));
      toY = ((y * pakSize));
      int maskType = 1;

      if (y == (0)) {
        if (x == 0) {
          maskType = 4;
        } else {
          maskType = 2;
        }
      } else {
        if (x == 0) {
          maskType = 3;
        } else {
          maskType = 1;
        }
      }
      returnval = MaskXY (toX, toY, Xout, Yout, maskType);
      printf("MaskXY - toX: %i toY: %i Xout: %i Yout: %i maskType: %i Error: %i\n", toX, toY, Xout, Yout, maskType, returnval);
    }
  } 
  
//Now the masks for the upper levels...
//Mask 5 = top left, 6 = top right, 7 = top middle...
if (bmpArrayZ > 1) {
for (z = 0; z < (bmpArrayZ - 1); z++) {
  for (x = 0; x < 1; x++) {
    for (y = 0; y < bmpArrayY; y++) {
      toX = ((bmpArrayX - (y + 1)) * pakSize);
      toY = ((bmpArrayY * pakSize) + (pakSize * 2) + (pakSize * (z - 1) * 2));
      int maskType;

      if (y == 0) {
        maskType = 7;
      } else {
        maskType = 6;
      }
      returnval = MaskXY (toX, toY, Xout, Yout, maskType);
      printf("AAMaskXY - toX: %i toY: %i Xout: %i Yout: %i maskType: %i Error: %i\n", toX, toY, Xout, Yout, maskType, returnval);
    }
  } 
  for (x = 1; x < bmpArrayX; x++) {
      toX = ((bmpArrayX - (x + 1)) * pakSize);
      toY = ((bmpArrayY * pakSize) + (pakSize * 3) + (pakSize * (z - 1) * 2));

      returnval = MaskXY (toX, toY, Xout, Yout, 5);
      printf("BBMaskXY - toX: %i toY: %i Xout: %i Yout: %i maskType: %i Error: %i\n", toX, toY, Xout, Yout, 5, returnval);
  } 
}
}
printf("Mask application complete...\n");

//Write the output png file (direct call) 
    printf("Writing png file - Xout: %i Yout: %i...\n", Xout, Yout);  
    write_png(filename_out, Xout, Yout, newBMB);
//    write_png("debug.png", Xin, Yin, oldBMB);
//Write the output dat file...
    printf("Writing dat file...\n");
    write_dat(dat_filename_out, filename_out, bmpArrayX, bmpArrayY, bmpArrayZ, pakIreg, pakOrient);

    printf("\nSuccess! Operation completed.\n\n");
    
    system("PAUSE");
    return 0;
}









int MaskXY (unsigned int toX, unsigned int toY, unsigned int newBmpX, unsigned int newBmpY, unsigned int maskType) {

  switch (maskType) {
    int n, m;
    //Mask type 1, tile only visible
    case 1:
      //Box mask at top (left - right)
      for (n = 0; n <= (pakSize / 2); n++) {
        for (m = 1; m <= ((pakSize * 3) / 2); m = m + 3) {
          int x = (((newBmpX * 3) * (n + toY)) + (m + (toX * 3)));
          newBMB[(x - 1)] = 231; newBMB[(x)] = 255; newBMB[(x + 1)] = 255;
        }
        for (m = (((pakSize * 3) / 2) + 1); m <= (pakSize * 3); m = m + 3) {
          int x = (((newBmpX * 3) * (n + toY)) + (m + (toX * 3)));
          newBMB[(x - 1)] = 231; newBMB[(x)] = 255; newBMB[(x + 1)] = 255;
        }
      }

      //Top Triangles (left - right)
      for (n = (pakSize / 2); n < ((pakSize / 2) + (pakSize / 4)); n++) {
        for (m = 1; m <= (((pakSize / 2) - (2 * (n - (pakSize / 2)))) * 3); m = m + 3) {
          int x = (((newBmpX * 3) * (n + toY)) + (m + (toX * 3)));
          newBMB[(x - 1)] = 231; newBMB[(x)] = 255; newBMB[(x + 1)] = 255;
        }
        for (m = ((((pakSize / 2) + (2 * (n - (pakSize / 2)))) * 3) + 1); m <= (pakSize * 3); m = m + 3) {
          int x = (((newBmpX * 3) * (n + toY)) + (m + (toX * 3)));
          newBMB[(x - 1)] = 231; newBMB[(x)] = 255; newBMB[(x + 1)] = 255;
        }
      }

      //Bottom Triangles (left - right)
      for (n = ((pakSize / 2) + (pakSize / 4)); n < pakSize; n++) {
        for (m = 1; m <= (((2 * (n - ((pakSize / 2) + (pakSize / 4))))) * 3); m = m + 3) {
          int x = (((newBmpX * 3) * (n + toY)) + (m + (toX * 3)));
          newBMB[(x - 1)] = 231; newBMB[(x)] = 255; newBMB[(x + 1)] = 255;
        }
        for (m = (((pakSize - (2 * (n - ((pakSize / 2) + (pakSize / 4))))) * 3) + 1); m <= (pakSize * 3); m = m + 3) {
          int x = (((newBmpX * 3) * (n + toY)) + (m + (toX * 3)));
          newBMB[(x - 1)] = 231; newBMB[(x)] = 255; newBMB[(x + 1)] = 255;
        }
      }
      break;





    //Mask type 2, as 1 but only right half of box and top triangle
    case 2:
      //Box mask at top (right)
      for (n = 0; n <= (pakSize / 2); n++) {
        for (m = (((pakSize * 3) / 2) + 1); m <= (pakSize * 3); m = m + 3) {
          int x = (((newBmpX * 3) * (n + toY)) + (m + (toX * 3)));
          newBMB[(x - 1)] = 231; newBMB[(x)] = 255; newBMB[(x + 1)] = 255;
        }
      }

      //Top Triangles (right)
      for (n = (pakSize / 2); n < ((pakSize / 2) + (pakSize / 4)); n++) {
        for (m = ((((pakSize / 2) + (2 * (n - (pakSize / 2)))) * 3) + 1); m <= (pakSize * 3); m = m + 3) {
          int x = (((newBmpX * 3) * (n + toY)) + (m + (toX * 3)));
          newBMB[(x - 1)] = 231; newBMB[(x)] = 255; newBMB[(x + 1)] = 255;
        }
      }

      //Bottom Triangles (left - right)
      for (n = ((pakSize / 2) + (pakSize / 4)); n < pakSize; n++) {
        for (m = 1; m <= (((2 * (n - ((pakSize / 2) + (pakSize / 4))))) * 3); m = m + 3) {
          int x = (((newBmpX * 3) * (n + toY)) + (m + (toX * 3)));
          newBMB[(x - 1)] = 231; newBMB[(x)] = 255; newBMB[(x + 1)] = 255;
        }
        for (m = (((pakSize - (2 * (n - ((pakSize / 2) + (pakSize / 4))))) * 3) + 1); m <= (pakSize * 3); m = m + 3) {
          int x = (((newBmpX * 3) * (n + toY)) + (m + (toX * 3)));
          newBMB[(x - 1)] = 231; newBMB[(x)] = 255; newBMB[(x + 1)] = 255;
        }
      }
      break;

    //Mask type 3, as 1 but only left half of box and top triangle
    case 3:
      //Box mask at top (left)
      for (n = 0; n <= (pakSize / 2); n++) {
        for (m = 1; m <= ((pakSize * 3) / 2); m = m + 3) {
          int x = (((newBmpX * 3) * (n + toY)) + (m + (toX * 3)));
          newBMB[(x - 1)] = 231; newBMB[(x)] = 255; newBMB[(x + 1)] = 255;
        }
      }

      //Top Triangles (left)
      for (n = (pakSize / 2); n < ((pakSize / 2) + (pakSize / 4)); n++) {
        for (m = 1; m <= (((pakSize / 2) - (2 * (n - (pakSize / 2)))) * 3); m = m + 3) {
          int x = (((newBmpX * 3) * (n + toY)) + (m + (toX * 3)));
          newBMB[(x - 1)] = 231; newBMB[(x)] = 255; newBMB[(x + 1)] = 255;
        }
      }

      //Bottom Triangles (left - right)
      for (n = ((pakSize / 2) + (pakSize / 4)); n < pakSize; n++) {
        for (m = 1; m <= (((2 * (n - ((pakSize / 2) + (pakSize / 4))))) * 3); m = m + 3) {
          int x = (((newBmpX * 3) * (n + toY)) + (m + (toX * 3)));
          newBMB[(x - 1)] = 231; newBMB[(x)] = 255; newBMB[(x + 1)] = 255;
        }
        for (m = (((pakSize - (2 * (n - ((pakSize / 2) + (pakSize / 4))))) * 3) + 1); m <= (pakSize * 3); m = m + 3) {
          int x = (((newBmpX * 3) * (n + toY)) + (m + (toX * 3)));
          newBMB[(x - 1)] = 231; newBMB[(x)] = 255; newBMB[(x + 1)] = 255;
        }
      }
      break;

    //Mask type 4, only bottom triangles ---------------------------------------------------------------------
    case 4:
      //Box mask at top (none)

      //Top Triangles (none)

      //Bottom Triangles (left - right)
      for (n = ((pakSize / 2) + (pakSize / 4)); n < pakSize; n++) {
        for (m = 1; m <= (((2 * (n - ((pakSize / 2) + (pakSize / 4))))) * 3); m = m + 3) {
          int x = (((newBmpX * 3) * (n + toY)) + (m + (toX * 3)));
          newBMB[(x - 1)] = 231; newBMB[(x)] = 255; newBMB[(x + 1)] = 255;
        }
        for (m = (((pakSize - (2 * (n - ((pakSize / 2) + (pakSize / 4))))) * 3) + 1); m <= (pakSize * 3); m = m + 3) {
          int x = (((newBmpX * 3) * (n + toY)) + (m + (toX * 3)));
          newBMB[(x - 1)] = 231; newBMB[(x)] = 255; newBMB[(x + 1)] = 255;
        }
      }
      break;
      
    //Top left box (bottom half masked) ---------------------------------------------------------------------
    case 5:
      //Box mask at bottom (left - right)
      for (n = (pakSize / 2); n < pakSize; n++) {
/*        for (m = 1; m <= ((pakSize * 3) / 2); m = m + 3) {
          int x = (((newBmpX * 3) * (n + toY)) + (m + (toX * 3)));
          newBMB[(x - 1)] = 231; newBMB[(x)] = 255; newBMB[(x + 1)] = 255;
        }*/
        for (m = (((pakSize * 3) / 2) + 1); m <= (pakSize * 3); m = m + 3) {
          int x = (((newBmpX * 3) * (n + toY)) + (m + (toX * 3)));
          newBMB[(x - 1)] = 231; newBMB[(x)] = 255; newBMB[(x + 1)] = 255;
        }
      } 
      
      //Box mask at top (right)
      for (n = 0; n <= (pakSize / 2); n++) {
        for (m = (((pakSize * 3) / 2) + 1); m <= (pakSize * 3); m = m + 3) {
          int x = (((newBmpX * 3) * (n + toY)) + (m + (toX * 3)));
          newBMB[(x - 1)] = 231; newBMB[(x)] = 255; newBMB[(x + 1)] = 255;
        }
      } 
      break;
      
    //Top right box (bottom half masked) ---------------------------------------------------------------------
    case 6:
      //Box mask at bottom (left - right)
      for (n = (pakSize / 2); n < pakSize; n++) {
        for (m = 1; m <= ((pakSize * 3) / 2); m = m + 3) {
          int x = (((newBmpX * 3) * (n + toY)) + (m + (toX * 3)));
          newBMB[(x - 1)] = 231; newBMB[(x)] = 255; newBMB[(x + 1)] = 255;
        }
/*        for (m = (((pakSize * 3) / 2) + 1); m <= (pakSize * 3); m = m + 3) {
          int x = (((newBmpX * 3) * (n + toY)) + (m + (toX * 3)));
          newBMB[(x - 1)] = 231; newBMB[(x)] = 255; newBMB[(x + 1)] = 255;
        }*/
      } 

      //Box mask at top (left)
      for (n = 0; n <= (pakSize / 2); n++) {
        for (m = 1; m <= ((pakSize * 3) / 2); m = m + 3) {
          int x = (((newBmpX * 3) * (n + toY)) + (m + (toX * 3)));
          newBMB[(x - 1)] = 231; newBMB[(x)] = 255; newBMB[(x + 1)] = 255;
        }
      }    
      break;
      
    //Top middle box (bottom half masked) ---------------------------------------------------------------------
    case 7:
      //Box mask at bottom (left - right)
/*      for (n = (pakSize / 2); n < pakSize; n++) {
        for (m = 1; m <= ((pakSize * 3) / 2); m = m + 3) {
          int x = (((newBmpX * 3) * (n + toY)) + (m + (toX * 3)));
          newBMB[(x - 1)] = 231; newBMB[(x)] = 255; newBMB[(x + 1)] = 255;
        }
        for (m = (((pakSize * 3) / 2) + 1); m <= (pakSize * 3); m = m + 3) {
          int x = (((newBmpX * 3) * (n + toY)) + (m + (toX * 3)));
          newBMB[(x - 1)] = 231; newBMB[(x)] = 255; newBMB[(x + 1)] = 255;
        }
      }     */
      break;

    default:
      break;
  }

return (0);
}

