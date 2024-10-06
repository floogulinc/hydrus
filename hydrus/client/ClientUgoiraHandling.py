from hydrus.core.files import HydrusUgoiraHandling
from hydrus.core.files.images import HydrusImageHandling
from hydrus.core.files import HydrusArchiveHandling
from hydrus.client.media import ClientMedia
from hydrus.client import ClientGlobals as CG
from hydrus.client import ClientFiles

import json
import typing

UGOIRA_DEFAULT_FRAME_DURATION_MS = 125

def GetFrameDurationsUgoira( media: ClientMedia.MediaSingleton ): 
    
    client_files_manager: ClientFiles.ClientFilesManager = CG.client_controller.client_files_manager
        
    path = client_files_manager.GetFilePath( media.GetHash(), media.GetMime() )
        
    try:
        
        frameData = HydrusUgoiraHandling.GetUgoiraFrameDataJSON( path )

        durations = [data['delay'] for data in frameData]

        return durations
    
    except:
        
        try:
            
            durations = GetFrameTimesFromNote(media)
            
            if durations is not None:
                
                return durations
            
        except:
            
            pass
        
        num_frames = media.GetNumFrames()
        
        return [UGOIRA_DEFAULT_FRAME_DURATION_MS] * num_frames
        
    
def GetFrameTimesFromNote(media: ClientMedia.MediaSingleton):
    
    if not media.HasNotes():
        
        return None
    
    noteManager = media.GetNotesManager()
    
    notes = noteManager.GetNamesToNotes()
    
    if 'ugoira json' in notes:
        
        try:
            
            ugoiraJson = json.loads(notes['ugoira json'])
        
            frameData: typing.List[HydrusUgoiraHandling.UgoiraFrame] = ugoiraJson['frames']
            
            return [data['delay'] for data in frameData]
        
        except:
            
            pass
        
    if 'ugoira frame delays json' in notes:
        
        try:
            
            ugoiraJson = json.loads(notes['ugoira frame delays json'])
        
            frameData: typing.List[int] = ugoiraJson
            
            return frameData
        
        except:
            
            pass
        
    return None
        

class UgoiraRenderer(object):

    def __init__( self, path, num_frames, target_resolution ):

        self._path = path
        self._num_frames = num_frames
        self._target_resolution = target_resolution

        self._next_render_index = 0

        self._frame_data = HydrusUgoiraHandling.GetFramePathsUgoira( path )

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

