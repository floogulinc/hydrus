import zipfile
import json
import typing

from hydrus.core import HydrusConstants as HC
from hydrus.core import HydrusExceptions
from hydrus.core import HydrusTemp
from hydrus.core.files import HydrusArchiveHandling
from hydrus.core.files.images import HydrusImageHandling

from PIL import Image as PILImage


# handle getting a list of frame paths from a ugoira without json metadata:
def GetFramePathsFromUgoiraZip( path ):
    
    with zipfile.ZipFile( path ) as zip_handle:
        
        paths = [ zip_info.filename for zip_info in zip_handle.infolist() if (not zip_info.is_dir()) and HydrusArchiveHandling.filename_has_image_ext(zip_info.filename) ]
        
        if len( paths ) == 0:
            
            raise HydrusExceptions.DamagedOrUnusualFileException( 'This Ugoira seems to be empty! It has probably been corrupted!' )
            
        
        paths.sort()
        
        return paths
        
    

def GetUgoiraProperties( path_to_zip ):
    
    # try to get properties from json file first:
    try:
        
        properties = GetUgoiraPropertiesFromJSON( path_to_zip )
        
        return properties
    
    except:
        
        pass
    
    try:
        
        pil_image = GetUgoiraFramePIL( path_to_zip, 0 )
        
        ( width, height ) = pil_image.size
        
    except:
        
        ( width, height ) = ( 100, 100 )
        
    
    try:
        
        num_frames = len(GetFramePathsFromUgoiraZip( path_to_zip ))
        
    except:
        
        num_frames = None
    
    return ( ( width, height ), None, num_frames )
    

def ZipLooksLikeUgoira( path_to_zip ):
    
    # Check zip for valid ugoira json first:
    try:
        
        frames = GetUgoiraFrameDataJSON( path_to_zip )
                
        if len( frames ) > 0 and all(('delay' in frame and 'file' in frame) for frame in frames):
            
            return True
            
        
    except:
        
        pass

    # what does an Ugoira look like? it has a standard, but this is not always followed, so be somewhat forgiving
    # it is a list of images named in the format 000123.jpg. this is 6-figure, starting at 000000
    # I have seen 'Ugoiras' that are zero-padded with 4 digits and/or 1-indexed instead of 0-indexed, but this is so atypical we are assuming these are ancient handmade artifacts and actually incorrect
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
            
        
        if len( image_number_strings ) <= 1:
            
            return False
            
        
        number_of_digits = 6
        
        for ( expected_image_number, image_number_string ) in enumerate( image_number_strings ):
            
            string_we_expect = str( expected_image_number ).zfill( number_of_digits )
            
            if image_number_string != string_we_expect:
                
                return False
                
            
        
        try:
            
            path = HydrusArchiveHandling.GetCoverPagePath( zip_handle )
            
            with zip_handle.open( path ) as reader:
                
                reader.read()
                
            
        except:
            
            return False
            
        
    
    return True
    




### Handling ugoira files with frame data json:

def GetUgoiraJSON( path ):

    jsonFile = HydrusArchiveHandling.GetZipAsPath( path, 'animation.json' )

    if not jsonFile.exists():

        raise HydrusExceptions.LimitedSupportFileException( 'Zip file has no animation.json!' )

    with jsonFile.open('rb') as jsonData:

        return json.load( jsonData )
    



UgoiraFrame = typing.TypedDict('UgoiraFrame', {'file': str, 'delay': int})

# list of {file: "000000.jpg", "delay": 100} where delay is in ms
def GetUgoiraFrameDataJSON( path ) -> typing.List[UgoiraFrame]:

    ugoiraJson = GetUgoiraJSON( path )
    
    
    # JSON from gallery-dl is just the array
    if isinstance(ugoiraJson, list):
        
        return ugoiraJson
    
    else:
        
        return ugoiraJson['frames']
    



def GetUgoiraPropertiesFromJSON( path ):

    frameData = GetUgoiraFrameDataJSON( path )

    durations = [data['delay'] for data in frameData]

    duration = sum( durations )
    num_frames = len( durations )

    firstFrame = GetUgoiraFramePIL( path, 0 )

    return ( firstFrame.size, duration, num_frames )


# Combined Ugoira functions:

def GetFrameDurationsUgoira( path ): 
    
    try:
        
        frameData = GetUgoiraFrameDataJSON( path )

        durations = [data['delay'] for data in frameData]

        return durations
    
    except:
        
        paths = GetFramePathsFromUgoiraZip( path )
        
        return [HC.UGOIRA_DEFAULT_FRAME_DURATION_MS] * len(paths)
        

def GetFramePathsUgoira( path ): 

    try:
        
        frameData = GetUgoiraFrameDataJSON( path )

        return [data['file'] for data in frameData]
    
    except:
        
        return GetFramePathsFromUgoiraZip( path )
    


def GetUgoiraFramePIL( path: str, frameIndex: int ) -> PILImage.Image:
    
    framePaths = GetFramePathsUgoira( path )

    frameName = framePaths[frameIndex]
        
    frameFromZip = HydrusArchiveHandling.GetZipAsPath( path, frameName ).open( 'rb' )
    
    return HydrusImageHandling.GeneratePILImage( frameFromZip )
    


def GenerateThumbnailNumPyFromUgoiraPath( path: str, target_resolution: typing.Tuple[int, int], frame_index: int ):

    pil_image = GetUgoiraFramePIL( path, frame_index )

    thumbnail_pil_image = pil_image.resize( target_resolution, PILImage.LANCZOS )

    numpy_image = HydrusImageHandling.GenerateNumPyImageFromPILImage( thumbnail_pil_image )

    return numpy_image


class UgoiraRenderer(object):

    def __init__( self, path, num_frames, target_resolution ):

        self._path = path
        self._num_frames = num_frames
        self._target_resolution = target_resolution

        self._next_render_index = 0

        self._frame_data = GetFramePathsUgoira( path )

        self._zip = HydrusArchiveHandling.GetZipAsPath( path )

    def set_position( self, index ):

        self._next_render_index = index

    def Stop(self):

        pass

    def read_frame(self):

        frame_name = self._frame_data[self._next_render_index]

        with self._zip.joinpath(frame_name).open('rb') as frame_from_zip:

            pil_image = HydrusImageHandling.GeneratePILImage( frame_from_zip )

            numpy_image = HydrusImageHandling.GenerateNumPyImageFromPILImage( pil_image )

        numpy_image = HydrusImageHandling.ResizeNumPyImage( numpy_image, self._target_resolution )

        self._next_render_index = ( self._next_render_index + 1 ) % self._num_frames

        return numpy_image
