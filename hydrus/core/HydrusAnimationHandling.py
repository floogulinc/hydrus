import io
import typing

import struct

from PIL import Image as PILImage

from hydrus.core import HydrusConstants as HC
from hydrus.core import HydrusExceptions
from hydrus.core import HydrusImageHandling

def GetAnimationProperties( path, mime ):
    
    pil_image = HydrusImageHandling.GeneratePILImage( path )
    
    ( width, height ) = pil_image.size
    
    width = max( width, 1 )
    height = max( height, 1 )
    
    if mime == HC.ANIMATION_APNG:
        
        ( duration, num_frames ) = GetAPNGDurationAndNumFrames( path )
        
    else:
        
        ( durations, times_to_play ) = GetFrameDurationsPILAnimation( path )
        
        duration = sum( durations )
        num_frames = len( durations )
        
    
    return ( ( width, height ), duration, num_frames )
    

def GetAPNGChunks( file_header_bytes: bytes ) ->list:
    
    # https://wiki.mozilla.org/APNG_Specification
    # a chunk is:
    # 4 bytes of data size, unsigned int
    # 4 bytes of chunk name
    # n bytes of data
    # 4 bytes of CRC
    
    # ok this method went super slow when given a 200MB giga png
    # it turns out list slicing on a very large bytes object is extremely slow
    # so we'll move to a file-like BytesIO and just read the stream like a file
    
    # note lol that if you debug this you'll still get the mega slowdown as your IDE copies the giganto bytes around over and over for variable inspection
    
    chunks = []
    
    buffer = io.BytesIO( file_header_bytes )
    
    # lop off 8 bytes of 'this is a PNG' at the top
    buffer.read( 8 )
    
    while True:
        
        chunk_num_bytes = buffer.read( 4 )
        
        chunk_name = buffer.read( 4 )
        
        if len( chunk_num_bytes ) < 4 or len( chunk_name ) < 4:
            
            break
            
        
        ( num_data_bytes, ) = struct.unpack( '>I', chunk_num_bytes )
        
        chunk_data = buffer.read( num_data_bytes )
        
        if len( chunk_data ) < num_data_bytes:
            
            break
            
        
        buffer.read( 4 )
        
        chunks.append( ( chunk_name, chunk_data ) )
        
    
    # old solution
    '''
    remaining_chunk_bytes = file_header_bytes[8:]
    
    while len( remaining_chunk_bytes ) > 12:
        
        ( num_data_bytes, ) = struct.unpack( '>I', remaining_chunk_bytes[ : 4 ] )
        
        chunk_name = remaining_chunk_bytes[ 4 : 8 ]
        
        chunk_data = remaining_chunk_bytes[ 8 : 8 + num_data_bytes ]
        
        chunks.append( ( chunk_name, chunk_data ) )
        
        remaining_chunk_bytes = remaining_chunk_bytes[ 8 + num_data_bytes + 4 : ]
        
    '''
    
    return chunks
    

def GetAPNGACTLChunkData( file_header_bytes: bytes ) -> typing.Optional[ bytes ]:
    
    # the acTL chunk can be in different places, but it has to be near the top
    # although it is almost always in fixed position (I think byte 29), we have seen both pHYs and sRGB chunks appear before it
    # so to be proper we need to parse chunks and find the right one
    apng_actl_chunk_header = b'acTL'
    
    chunks = GetAPNGChunks( file_header_bytes )
    
    chunks = dict( chunks )
    
    if apng_actl_chunk_header in chunks:
        
        return chunks[ apng_actl_chunk_header ]
        
    else:
        
        return None
        
    

def GetAPNGDuration( apng_bytes: bytes ) -> float:
    
    frame_control_chunk_name = b'fcTL'
    
    chunks = GetAPNGChunks( apng_bytes )
    
    total_duration = 0
    
    CRAZY_FRAME_TIME = 0.1
    MIN_FRAME_TIME = 0.001
    
    for ( chunk_name, chunk_data ) in chunks:
        
        if chunk_name == frame_control_chunk_name and len( chunk_data ) >= 24:
            
            ( delay_numerator, ) = struct.unpack( '>H', chunk_data[20:22] )
            ( delay_denominator, ) = struct.unpack( '>H', chunk_data[22:24] )
            
            if delay_denominator == 0:
                
                duration = CRAZY_FRAME_TIME
                
            else:
                
                duration = max( delay_numerator / delay_denominator, MIN_FRAME_TIME )
                
            
            total_duration += duration
            
        
    
    return total_duration
    

def GetAPNGNumFrames( apng_actl_bytes: bytes ) -> int:
    
    ( num_frames, ) = struct.unpack( '>I', apng_actl_bytes[ : 4 ] )
    
    return num_frames
    

def GetAPNGDurationAndNumFrames( path ):
    
    with open( path, 'rb' ) as f:
        
        file_header_bytes = f.read( 256 )
        
    
    apng_actl_bytes = GetAPNGACTLChunkData( file_header_bytes )
    
    if apng_actl_bytes is None:
        
        raise HydrusExceptions.DamagedOrUnusualFileException( 'This APNG had an unusual file header!' )
        
    
    num_frames = GetAPNGNumFrames( apng_actl_bytes )
    
    with open( path, 'rb' ) as f:
        
        file_bytes = f.read()
        
    
    duration = GetAPNGDuration( file_bytes )
    
    duration_in_ms_float = duration * 1000
    
    duration_in_ms = int( duration * 1000 )
    
    if duration_in_ms == 0 and duration_in_ms_float > 0:
        
        duration_in_ms = 1
        
    
    return ( duration_in_ms, num_frames )
    

def GetFrameDurationsPILAnimation( path ):
    
    pil_image = HydrusImageHandling.RawOpenPILImage( path )
    
    times_to_play = GetTimesToPlayPILAnimationFromPIL( pil_image )
    
    frame_durations = []
    
    i = 0
    
    while True:
        
        try:
            
            pil_image.seek( i )
            
        except:
            
            break
            
        
        if 'duration' not in pil_image.info:
            
            duration = 83 # (83ms -- 1000 / 12) Set a 12 fps default when duration is missing or too funky to extract. most stuff looks ok at this.
            
        else:
            
            duration = pil_image.info[ 'duration' ]
            
            # In the gif frame header, 10 is stored as 1ms. This 1 is commonly as utterly wrong as 0.
            if duration in ( 0, 10 ):
                
                duration = 83
                
            
        
        frame_durations.append( duration )
        
        i += 1
        
    
    return ( frame_durations, times_to_play )
    

def GetTimesToPlayAPNG( path: str ) -> int:
    
    with open( path, 'rb' ) as f:
        
        file_header_bytes = f.read( 256 )
        
    
    apng_actl_bytes = GetAPNGACTLChunkData( file_header_bytes )
    
    if apng_actl_bytes is None:
        
        return 0
        
    
    ( num_plays, ) = struct.unpack( '>I', apng_actl_bytes[ 4 : 8 ] )
    
    return num_plays
    

def GetTimesToPlayPILAnimation( path ) -> int:
    
    try:
        
        pil_image = HydrusImageHandling.RawOpenPILImage( path )
        
    except HydrusExceptions.UnsupportedFileException:
        
        return 1
        
    
    return GetTimesToPlayPILAnimationFromPIL( pil_image )
    

def GetTimesToPlayPILAnimationFromPIL( pil_image: PILImage.Image ) -> int:
    
    if 'loop' in pil_image.info:
        
        times_to_play = pil_image.info[ 'loop' ]
        
    else:
        
        times_to_play = 1
        
    
    return times_to_play
    

def PILAnimationHasDuration( path ):
    
    pil_image = HydrusImageHandling.GeneratePILImage( path, dequantize = False )
    
    try:
        
        pil_image.seek( 1 )
        pil_image.seek( 0 )
        
        return True
        
    except:
        
        return False
        
    

def IsPNGAnimated( file_header_bytes ):
    
    apng_actl_bytes = GetAPNGACTLChunkData( file_header_bytes )
    
    if apng_actl_bytes is not None:
        
        # this is an animated png
        
        # acTL chunk in an animated png is 4 bytes of num frames, then 4 bytes of num times to loop
        # https://wiki.mozilla.org/APNG_Specification#.60acTL.60:_The_Animation_Control_Chunk
        
        num_frames = GetAPNGNumFrames( apng_actl_bytes )
        
        if num_frames > 1:
            
            return True
            
        
    
    return False
    
