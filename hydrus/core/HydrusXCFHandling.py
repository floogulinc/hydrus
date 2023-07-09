from gimpformats.gimpXcfDocument import GimpDocument

from PIL import Image as PILImage

from hydrus.core import HydrusExceptions
from hydrus.core import HydrusImageHandling

def GenerateThumbnailBytesFromXCFPath(path: str, target_resolution: tuple[int, int], clip_rect = None) -> bytes:
    
    try:

        project = GimpDocument(path)

    except:

        raise HydrusExceptions.DamagedOrUnusualFileException('Could not load XCF file')


    pil_image: PILImage = project.image

    if clip_rect is not None:
        
        pil_image = HydrusImageHandling.ClipPILImage( pil_image, clip_rect )
        
    
    thumbnail_pil_image = pil_image.resize( target_resolution, PILImage.ANTIALIAS )
    
    thumbnail_bytes = HydrusImageHandling.GenerateThumbnailBytesPIL( thumbnail_pil_image )
    
    return thumbnail_bytes

def GetXCFResolution(path:str):
    
    try:

        project = GimpDocument(path)

    except:

        raise HydrusExceptions.DamagedOrUnusualFileException('Could not load XCF file')


    resolution = (project.width, project.height)

    print(resolution)

    return resolution