from collections import namedtuple
import struct

import numpy as np

class Pcx:
    rle_bit = 192
    color_table_size = 256
    palette_offset = -768
    
    Header = namedtuple('Header', 'manufacturer version encoding bits_per_pixel x_min y_min x_max y_max hres vres ega_palette reserved color_planes bytes_per_line palette_type filler')
    
    def from_file(self, filename):
        with open(filename, 'rb') as f:
            self.header = self._read_header(f)
            
            if self.header.version == 5 and self.header.bits_per_pixel == 8 and self.header.encoding == 1 and self.header.color_planes == 1:
                self.image_data = self._read_image(f)
                self.palette = self._read_palette(f)
            else:
                raise ValueError('Unsupported PCX file format')                    
        
    def get_display_size(self):
        return (self.header.x_max - self.header.x_min + 1, self.header.y_max - self.header.y_min + 1)        
    
    def _read_palette(self, f):
        # seek to the end of the file and then back 768 bytes to read the palette
        f.seek(self.palette_offset, 2)
        data = f.read(self.color_table_size * 3)
        return np.frombuffer(data, dtype=np.uint8).reshape((self.color_table_size, 3)).tolist()
    
    def _read_image(self, f):
        x_size = self.header.x_max - self.header.x_min + 1
        y_size = self.header.y_max - self.header.y_min + 1
        
        image_data = np.zeros(x_size * y_size, dtype=np.uint8)
        
        decoded_bytes_read = 0
        
        while decoded_bytes_read < x_size * y_size:
            # When the process byte is less then 192 then it is an index into the palette.
            # If it greater then 192, then there are (byte - 192) number of entries
            # in the color of the *next* byte
            byte = f.read(1)[0]
            
            if byte >= Pcx.rle_bit:
                count = byte - Pcx.rle_bit
                byte = f.read(1)[0]
                
                for i in range(count):
                    image_data[decoded_bytes_read] = byte
                    decoded_bytes_read += 1
            else:
                image_data[decoded_bytes_read] = byte
                decoded_bytes_read += 1
        
        return image_data.reshape((y_size, x_size))
                    
    def _read_header(self, f):
        data = f.read(128)
        return Pcx.Header._make(struct.unpack('<BBBBHHHHHH48sBBHH58s', data))