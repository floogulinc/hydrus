from hydrus.core.files.images import HydrusImageInit # right up top

import hashlib
import io
import numpy
import typing
import warnings

from PIL import ImageFile as PILImageFile
from PIL import Image as PILImage
from PIL.Image import Resampling as PILResampling

try:
    
    from pillow_heif import register_heif_opener
    from pillow_heif import register_avif_opener
    
    register_heif_opener(thumbnails=False)
    register_avif_opener(thumbnails=False)
    
    HEIF_OK = True
    
except:
    
    HEIF_OK = False
    

from hydrus.core import HydrusConstants as HC
from hydrus.core import HydrusData
from hydrus.core import HydrusExceptions
from hydrus.core import HydrusGlobals as HG
from hydrus.core.files import HydrusKritaHandling
from hydrus.core.files import HydrusPSDHandling
from hydrus.core.files.images import HydrusImageColours
from hydrus.core.files.images import HydrusImageMetadata
from hydrus.core.files.images import HydrusImageNormalisation
from hydrus.core.files.images import HydrusImageOpening

def EnableLoadTruncatedImages():
    
    if hasattr( PILImageFile, 'LOAD_TRUNCATED_IMAGES' ):
        
        # this can now cause load hangs due to the trunc load code adding infinite fake EOFs to the file stream, wew lad
        # hence debug only
        PILImageFile.LOAD_TRUNCATED_IMAGES = True
        
        return True
        
    else:
        
        return False
        
    

OLD_PIL_MAX_IMAGE_PIXELS = PILImage.MAX_IMAGE_PIXELS
PILImage.MAX_IMAGE_PIXELS = None # this turns off decomp check entirely, wew


PIL_ONLY_MIMETYPES = { HC.ANIMATION_GIF, HC.IMAGE_ICON, HC.IMAGE_WEBP, HC.IMAGE_QOI, HC.IMAGE_BMP }.union( HC.PIL_HEIF_MIMES )

def MakeClipRectFit( image_resolution, clip_rect ):
    
    ( im_width, im_height ) = image_resolution
    ( x, y, clip_width, clip_height ) = clip_rect
    
    x = max( 0, x )
    y = max( 0, y )
    
    clip_width = min( clip_width, im_width )
    clip_height = min( clip_height, im_height )
    
    if x + clip_width > im_width:
        
        x = im_width - clip_width
        
    
    if y + clip_height > im_height:
        
        y = im_height - clip_height
        
    
    return ( x, y, clip_width, clip_height )
    
def ClipNumPyImage( numpy_image: numpy.array, clip_rect ):
    
    if len( numpy_image.shape ) == 3:
        
        ( im_height, im_width, depth ) = numpy_image.shape
        
    else:
        
        ( im_height, im_width ) = numpy_image.shape
        
    
    ( x, y, clip_width, clip_height ) = MakeClipRectFit( ( im_width, im_height ), clip_rect )
    
    return numpy_image[ y : y + clip_height, x : x + clip_width ]
    

def ClipPILImage( pil_image: PILImage.Image, clip_rect ):
    
    ( x, y, clip_width, clip_height ) = MakeClipRectFit( pil_image.size, clip_rect )
    
    return pil_image.crop( box = ( x, y, x + clip_width, y + clip_height ) )
    

def GenerateNumPyImage( path, mime, force_pil = False ) -> numpy.array:
    
    if HG.media_load_report_mode:
        
        HydrusData.ShowText( 'Loading media: ' + path )
        
    
    if mime == HC.APPLICATION_PSD:
        
        if HG.media_load_report_mode:
            
            HydrusData.ShowText( 'Loading PSD' )
            
        
        pil_image = HydrusPSDHandling.MergedPILImageFromPSD( path )
        
        return GenerateNumPyImageFromPILImage( pil_image )
        
    
    if mime == HC.APPLICATION_KRITA:
        
        if HG.media_load_report_mode:
            
            HydrusData.ShowText( 'Loading KRA' )
            
        
        pil_image = HydrusKritaHandling.MergedPILImageFromKra( path )
        
        return GenerateNumPyImageFromPILImage( pil_image )
        
        
    
    if HG.media_load_report_mode:
            
            HydrusData.ShowText( 'Loading with PIL' )
        
    
    pil_image = GeneratePILImage( path )
    
    numpy_image = GenerateNumPyImageFromPILImage( pil_image )
        
        
    
    return numpy_image
    
    
def GenerateNumPyImageFromPILImage( pil_image: PILImage.Image, strip_useless_alpha = True ) -> numpy.array:
    
    try:
        
        # this seems to magically work, I guess asarray either has a match for Image or Image provides some common shape/datatype properties that it can hook into
        numpy_image = numpy.asarray( pil_image )
        
    except IOError:
        
        raise HydrusExceptions.DamagedOrUnusualFileException( 'Looks like a truncated file that PIL could not handle!' )
        
    
    if numpy_image.shape == ():
        
        raise HydrusExceptions.DamagedOrUnusualFileException( 'Looks like a weird truncated file!' )
        
    
    if strip_useless_alpha:
        
        numpy_image = HydrusImageNormalisation.StripOutAnyUselessAlphaChannel( numpy_image )
        
    
    return numpy_image
    

def GeneratePILImage( path: typing.Union[ str, typing.BinaryIO ], dequantize = True ) -> PILImage.Image:
    
    pil_image = HydrusImageOpening.RawOpenPILImage( path )
    
    try:
        
        pil_image = HydrusImageNormalisation.RotateEXIFPILImage( pil_image )
        
        if dequantize:
            
            if pil_image.mode in ( 'I', 'F' ):
                
                # 'I' = greyscale, uint16
                # 'F' = float, np.float32
                
                # calling "pil_image.convert( 'L' )" and similar on an I doesn't seem to normalise the intensity, it just blows out the image crazy???
                # so we'll hack it ourselves. these are so rare it is fine if we are a bit weird and lose the extra metadata
                
                numpy_image = GenerateNumPyImageFromPILImage( pil_image )
                
                numpy_image = HydrusImageNormalisation.NormaliseNumPyImageToUInt8( numpy_image )
                
                pil_image = GeneratePILImageFromNumPyImage( numpy_image )
                
            
            # note this destroys animated gifs atm, it collapses down to one frame
            pil_image = HydrusImageNormalisation.DequantizePILImage( pil_image )
            
        
        return pil_image
        
    except IOError:
        
        raise HydrusExceptions.DamagedOrUnusualFileException( 'Looks like a truncated file that PIL could not handle!' )
        
    

def GeneratePILImageFromNumPyImage( numpy_image: numpy.array ) -> PILImage.Image:
    
    if len( numpy_image.shape ) == 2:
        
        ( h, w ) = numpy_image.shape
        
        format = 'L'
        
    else:
        
        ( h, w, depth ) = numpy_image.shape
        
        if depth == 1:
            
            format = 'L'
            
        elif depth == 2:
            
            format = 'LA'
            
        elif depth == 3:
            
            format = 'RGB'
            
        elif depth == 4:
            
            format = 'RGBA'
            
        
    
    pil_image = PILImage.frombytes( format, ( w, h ), numpy_image.data.tobytes() )
    
    return pil_image
    

def GenerateThumbnailNumPyFromStaticImagePath( path, target_resolution, mime ):
    
    numpy_image = GenerateNumPyImage( path, mime )
    
    thumbnail_numpy_image = ResizeNumPyImage( numpy_image, target_resolution )
    
    return thumbnail_numpy_image
    

def GenerateThumbnailBytesFromNumPy( numpy_image ) -> bytes:
    
    pil_image = GeneratePILImageFromNumPyImage( numpy_image )
    
    return GenerateThumbnailBytesFromPIL( pil_image )
        
    

def GenerateThumbnailBytesFromPIL( pil_image: PILImage.Image ) -> bytes:
    
    f = io.BytesIO()
    
    if HydrusImageColours.PILImageHasTransparency( pil_image ):
        
        pil_image.save( f, 'PNG' )
        
    else:
        
        pil_image.save( f, 'JPEG', quality = 92 )
        
    
    f.seek( 0 )
    
    thumbnail_bytes = f.read()
    
    f.close()
    
    return thumbnail_bytes
    

def GeneratePNGBytesPIL( pil_image ) -> bytes:
    
    f = io.BytesIO()
    
    pil_image.save( f, 'PNG' )
    
    f.seek( 0 )
    
    png_bytes = f.read()
    
    f.close()
    
    return png_bytes
    

def GeneratePNGBytesNumPy( numpy_image ) -> bytes:
    
    pil_image = GeneratePILImageFromNumPyImage( numpy_image )
    
    return GeneratePNGBytesPIL( pil_image )
        
    

def GetImagePixelHash( path, mime ) -> bytes:
    
    numpy_image = GenerateNumPyImage( path, mime )
    
    return GetImagePixelHashNumPy( numpy_image )
    

def GetImagePixelHashNumPy( numpy_image ):
    
    return hashlib.sha256( numpy_image.data.tobytes() ).digest()
    

def GetImageResolution( path, mime ):
    
    # PIL first here, rather than numpy, as it loads image headers real quick
    try:
        
        pil_image = GeneratePILImage( path, dequantize = False )
        
        ( width, height ) = pil_image.size
        
    except HydrusExceptions.DamagedOrUnusualFileException:
        
        # desperate situation
        numpy_image = GenerateNumPyImage( path, mime )
        
        if len( numpy_image.shape ) == 3:
            
            ( height, width, depth ) = numpy_image.shape
            
        else:
            
            ( height, width ) = numpy_image.shape
            
        
    
    width = max( width, 1 )
    height = max( height, 1 )
    
    return ( width, height )
    

def GetResolutionNumPy( numpy_image ):
    
    ( image_height, image_width, depth ) = numpy_image.shape
    
    return ( image_width, image_height )
    

THUMBNAIL_SCALE_DOWN_ONLY = 0
THUMBNAIL_SCALE_TO_FIT = 1
THUMBNAIL_SCALE_TO_FILL = 2

thumbnail_scale_str_lookup = {
    THUMBNAIL_SCALE_DOWN_ONLY : 'scale down only',
    THUMBNAIL_SCALE_TO_FIT : 'scale to fit',
    THUMBNAIL_SCALE_TO_FILL : 'scale to fill'
}

def GetThumbnailResolution( image_resolution: typing.Tuple[ int, int ], bounding_dimensions: typing.Tuple[ int, int ], thumbnail_scale_type: int, thumbnail_dpr_percent: int ) -> typing.Tuple[ int, int ]:
    
    ( im_width, im_height ) = image_resolution
    ( bounding_width, bounding_height ) = bounding_dimensions
    
    if thumbnail_dpr_percent != 100:
        
        thumbnail_dpr = thumbnail_dpr_percent / 100
        
        bounding_height = int( bounding_height * thumbnail_dpr )
        bounding_width = int( bounding_width * thumbnail_dpr )
        
    
    # this is appropriate for the crazy (0x0) svg or whatever we have, since we will _try_ to render it properly later on
    # but if it fails to render, we'll still get a fairly nice filetype.png or hydrus.png fallback
    # we don't want to pass around 0x0 and have a handler everywhere
    if im_width is None or im_width == 0 or im_height is None or im_height == 0:
        
        im_width = bounding_width
        im_height = bounding_width
        
    
    # TODO SVG thumbs should always scale up to the bounding dimensions
    
    if thumbnail_scale_type == THUMBNAIL_SCALE_DOWN_ONLY:
        
        if bounding_width >= im_width and bounding_height >= im_height:
            
            return ( im_width, im_height )
            
        
    
    image_ratio = im_width / im_height
    
    width_ratio = im_width / bounding_width
    height_ratio = im_height / bounding_height
    
    image_is_wider_than_bounding_box = width_ratio > height_ratio
    image_is_taller_than_bounding_box = height_ratio > width_ratio
    
    thumbnail_width = bounding_width
    thumbnail_height = bounding_height
    
    if thumbnail_scale_type in ( THUMBNAIL_SCALE_DOWN_ONLY, THUMBNAIL_SCALE_TO_FIT ):
        
        if image_is_taller_than_bounding_box: # i.e. the height will be at bounding height
            
            thumbnail_width = im_width / height_ratio
            
        elif image_is_wider_than_bounding_box: # i.e. the width will be at bounding width
            
            thumbnail_height = im_height / width_ratio
            
        
    elif thumbnail_scale_type == THUMBNAIL_SCALE_TO_FILL:
        
        # we do min 5.0 here to stop really tall and thin images getting zoomed in from width 1px to 150 and getting a thumbnail with a height of 75,000 pixels
        # in this case the line image is already crazy distorted, so we don't mind squishing it
        
        if image_is_taller_than_bounding_box: # i.e. the width will be at bounding width, the height will spill over
            
            thumbnail_height = bounding_width * min( 5.0, 1 / image_ratio )
            
        elif image_is_wider_than_bounding_box: # i.e. the height will be at bounding height, the width will spill over
            
            thumbnail_width = bounding_height * min( 5.0, image_ratio )
            
        
        # old stuff that actually clipped the size of the thing
        '''
        clip_x = 0
        clip_y = 0
        clip_width = im_width
        clip_height = im_height
        
        if width_ratio > height_ratio:
            
            clip_width = max( int( im_width * height_ratio / width_ratio ), 1 )
            clip_x = ( im_width - clip_width ) // 2
            
        elif height_ratio > width_ratio:
            
            clip_height = max( int( im_height * width_ratio / height_ratio ), 1 )
            clip_y = ( im_height - clip_height ) // 2
            
        
        clip_rect = ( clip_x, clip_y, clip_width, clip_height )
        '''
        
    
    thumbnail_width = int( thumbnail_width )
    thumbnail_height = int( thumbnail_height )
    
    thumbnail_width = max( thumbnail_width, 1 )
    thumbnail_height = max( thumbnail_height, 1 )
    
    return ( thumbnail_width, thumbnail_height )
    

def IsDecompressionBomb( path ) -> bool:
    
    # there are two errors here, the 'Warning' and the 'Error', which atm is just a test vs a test x 2 for number of pixels
    # 256MB bmp by default, ( 1024 ** 3 ) // 4 // 3
    # we'll set it at 512MB, and now catching error should be about 1GB
    
    PILImage.MAX_IMAGE_PIXELS = ( 512 * ( 1024 ** 2 ) ) // 3
    
    warnings.simplefilter( 'error', PILImage.DecompressionBombError )
    
    try:
        
        HydrusImageOpening.RawOpenPILImage( path )
        
    except ( PILImage.DecompressionBombError ):
        
        return True
        
    except:
        
        # pil was unable to load it, which does not mean it was a decomp bomb
        return False
        
    finally:
        
        PILImage.MAX_IMAGE_PIXELS = None
        
        warnings.simplefilter( 'ignore', PILImage.DecompressionBombError )
        
    
    return False
    

def ResizeNumPyImage( numpy_image: numpy.array, target_resolution:  typing.Tuple[ int, int ], forced_interpolation: PILResampling = None ) -> numpy.array:
    
    ( target_width, target_height ) = target_resolution
    ( image_width, image_height ) = GetResolutionNumPy( numpy_image )
    
    if target_width == image_width and target_height == target_width:
        
        return numpy_image
        
    elif target_width > image_height or target_height > image_width:
        
        interpolation = PILResampling.LANCZOS
        
    else:
        
        interpolation = PILResampling.LANCZOS
        
    
    if forced_interpolation is not None:
        
        interpolation = forced_interpolation
        
    
    pil_image = GeneratePILImageFromNumPyImage( numpy_image )
        
    pil_image = ResizePILImage( target_resolution, interpolation )
    
    return GenerateNumPyImageFromPILImage( pil_image, strip_useless_alpha = False )
    

def ResizePILImage(pil_image: PILImage.Image, target_resolution:  typing.Tuple[ int, int ], forced_interpolation: PILResampling = None) -> PILImage.Image:
    
    if target_resolution == pil_image.size:
        
        return pil_image
    
    interpolation = forced_interpolation if not None else PILResampling.LANCZOS
    
    return pil_image.resize( target_resolution, interpolation )
