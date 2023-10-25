import io
import json
import typing

from hydrus.core import HydrusArchiveHandling
from hydrus.core import HydrusExceptions
from hydrus.core.images import HydrusImageHandling
from hydrus.core import HydrusText

from PIL import Image as PILImage

def GetUgoiraJSON( path ):
  
    jsonFile = HydrusArchiveHandling.GetZipAsPath( path, 'animation.json' )

    if not jsonFile.exists():
        
        raise HydrusExceptions.DamagedOrUnusualFileException( 'Zip file has no animation.json!' )
  
    with jsonFile.open('rb') as jsonData:

        return json.load( jsonData )


def ZipLooksLikeUgoira( path ):

    try:

        ugoiraJson = GetUgoiraJSON( path )

        return 'frames' in ugoiraJson and len(ugoiraJson['frames']) > 0

    except:

        return False
  


# dict of {file: "000000.jpg", "delay": 100} where delay is in ms
def GetUgoiraFrameData( path ):

    ugoiraJson = GetUgoiraJSON( path )

    return ugoiraJson['frames']


def GetUgoiraFramePIL( path, frameName ) -> PILImage.Image:

    frameFromZip =  HydrusArchiveHandling.GetZipAsPath( path, frameName ).open( 'rb' )

    pil_image = HydrusImageHandling.GeneratePILImage( frameFromZip )

    return pil_image


def GetUgoiraFirstFrame( path ):

    frameData = GetUgoiraFrameData( path )
    
    firstFrameName = frameData[0]['file']

    return GetUgoiraFramePIL( path, firstFrameName )


def GenerateThumbnailNumPyFromUgoiraPath( path: str, target_resolution: typing.Tuple[int, int], clip_rect = None ):

    pil_image = GetUgoiraFirstFrame( path )

    if clip_rect is not None:
        
        pil_image = HydrusImageHandling.ClipPILImage( pil_image, clip_rect )
        
    
    thumbnail_pil_image = pil_image.resize( target_resolution, PILImage.LANCZOS )
    
    numpy_image = HydrusImageHandling.GenerateNumPyImageFromPILImage( thumbnail_pil_image )
    
    return numpy_image
    

def GetUgoiraProperties( path ):

    durations = GetFrameDurationsUgoira( path )

    duration = sum( durations )
    num_frames = len( durations )

    firstFrame = GetUgoiraFirstFrame( path )

    return ( firstFrame.size, duration, num_frames )
    

def GetFrameDurationsUgoira( path ): 

    frameData = GetUgoiraFrameData( path )

    durations = [data['delay'] for data in frameData]

    return durations


class UgoiraRenderer(object):

    def __init__( self, path, num_frames, target_resolution ):

        self._path = path
        self._num_frames = num_frames
        self._target_resolution = target_resolution

        self._next_render_index = 0

        self._frame_data = GetUgoiraFrameData( path )

    def set_position( self, index ):

        self._next_render_index = index

    def Stop(self):

        pass

    def read_frame(self):

        frame_name = self._frame_data[self._next_render_index]['file']

        pil_image = GetUgoiraFramePIL(self._path, frame_name)

        numpy_image = HydrusImageHandling.GenerateNumPyImageFromPILImage( pil_image )

        numpy_image = HydrusImageHandling.ResizeNumPyImage( numpy_image, self._target_resolution )

        self._next_render_index = ( self._next_render_index + 1 ) % self._num_frames

        return numpy_image
