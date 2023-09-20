import typing

from hydrus.core import HydrusExceptions

def BaseGenerateThumbnailNumPyFromSVGPath( path: str, target_resolution: typing.Tuple[int, int], clip_rect = None ) -> bytes:
    
    raise HydrusExceptions.NoThumbnailFileException()
    

def BaseGetSVGResolution( path: str ):
    
    raise HydrusExceptions.NoResolutionFileException()
    

GenerateThumbnailNumPyFromSVGPath = BaseGenerateThumbnailNumPyFromSVGPath
GetSVGResolution = BaseGetSVGResolution
