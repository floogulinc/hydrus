import zipfile

from hydrus.core import HydrusArchiveHandling
from hydrus.core import HydrusConstants as HC
from hydrus.core import HydrusExceptions
from hydrus.core import HydrusTemp
from hydrus.core.images import HydrusImageHandling

def ExtractFrame( path_to_zip, frame_index, extract_path ):
    
    # this is too ugly to use for an animation thing, but it'll work for fetching a thumb fine
    
    with zipfile.ZipFile( path_to_zip ) as zip_handle:
        
        all_file_paths = [ zip_info.filename for zip_info in zip_handle.infolist() if not zip_info.is_dir() ]
        
        if len( all_file_paths ) == 0:
            
            raise HydrusExceptions.DamagedOrUnusualFileException( 'This Ugoira seems to be empty! It has probably been corrupted!' )
            
        
        all_file_paths.sort()
        
        frame_index = min( frame_index, len( all_file_paths ) - 1 )
        
        frame_path = all_file_paths[ frame_index ]
        
        with zip_handle.open( frame_path ) as reader:
            
            with open( extract_path, 'wb' ) as writer:
                
                writer.write( reader.read() )
                
            
        
    

def GetUgoiraProperties( path_to_zip ):
    
    ( os_file_handle, temp_path ) = HydrusTemp.GetTempPath()
    
    try:
        
        try:
            
            HydrusArchiveHandling.ExtractCoverPage( path_to_zip, temp_path )
            
            pil_image = HydrusImageHandling.GeneratePILImage( temp_path, dequantize = False )
            
            ( width, height ) = pil_image.size
            
        except:
            
            ( width, height ) = ( 100, 100 )
            
        
        try:
            
            with zipfile.ZipFile( path_to_zip ) as zip_handle:
                
                num_frames = len( zip_handle.infolist() )
                
            
        except:
            
            num_frames = None
            
        
    finally:
        
        HydrusTemp.CleanUpTempPath( os_file_handle, temp_path )
        
    
    return ( ( width, height ), num_frames )
    

def ZipLooksLikeUgoira( path_to_zip ):
    
    # what does an Ugoira look like? it has a standard, but this is not always followed, so be somewhat forgiving
    # it is a list of images named in the format 000123.jpg. this is very typically 6-figure, starting at 000000, but it may be shorter and start at 0001
    # no directories
    # we can forgive a .json or .js file, nothing else
    
    our_image_ext = None
    
    with zipfile.ZipFile( path_to_zip ) as zip_handle:
        
        zip_infos = zip_handle.infolist()
        
        if True in ( zip_info.is_dir() for zip_info in zip_infos ):
            
            return False
            
        
        image_number_strings = []
        
        filenames = [ zip_info.filename for zip_info in zip_infos ]
        
        for filename in filenames:
            
            if '.' not in filename:
                
                return False
                
            
            number = '.'.join( filename.split( '.' )[:-1] )
            ext = '.' + filename.split( '.' )[-1]
            
            if ext in ( '.js', '.json' ):
                
                continue
                
            
            if ext not in HC.IMAGE_FILE_EXTS:
                
                return False
                
            
            if our_image_ext is None:
                
                our_image_ext = ext
                
            
            if ext != our_image_ext:
                
                return False
                
            
            image_number_strings.append( number )
            
        
        if len( image_number_strings ) == 0:
            
            return False
            
        
        image_number_strings.sort()
        
        try:
            
            current_image_number = int( image_number_strings[0] )
            
        except:
            
            return False
            
        
        number_of_digits = len( image_number_strings[0] )
        
        for image_number_string in image_number_strings:
            
            string_we_expect = str( current_image_number ).zfill( number_of_digits )
            
            if image_number_string != string_we_expect:
                
                return False
                
            
            current_image_number += 1
            
        
    
    return True
    