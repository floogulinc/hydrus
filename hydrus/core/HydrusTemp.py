import os
import tempfile
import threading

from hydrus.core import HydrusData
from hydrus.core import HydrusGlobals as HG
from hydrus.core import HydrusPaths
from hydrus.core import HydrusTime

TEMP_PATH_LOCK = threading.Lock()
IN_USE_TEMP_PATHS = set()

def CleanUpTempPath( os_file_handle, temp_path ):
    
    try:
        
        os.close( os_file_handle )
        
    except OSError:
        
        try:
            
            os.close( os_file_handle )
            
        except OSError:
            
            HydrusData.Print( 'Could not close the temporary file ' + temp_path )
            
            return
            
        
    
    try:
        
        os.remove( temp_path )
        
    except OSError:
        
        with TEMP_PATH_LOCK:
            
            IN_USE_TEMP_PATHS.add( ( HydrusTime.GetNow(), temp_path ) )
            
        
    

def CleanUpOldTempPaths():
    
    with TEMP_PATH_LOCK:
        
        data = list( IN_USE_TEMP_PATHS )
        
        for row in data:
            
            ( time_failed, temp_path ) = row
            
            if HydrusTime.TimeHasPassed( time_failed + 60 ):
                
                try:
                    
                    os.remove( temp_path )
                    
                    IN_USE_TEMP_PATHS.discard( row )
                    
                except OSError:
                    
                    if HydrusTime.TimeHasPassed( time_failed + 1200 ):
                        
                        IN_USE_TEMP_PATHS.discard( row )
                        
                    
                
            
        
    

def GetCurrentTempDir():
    
    return tempfile.gettempdir()
    

def InitialiseHydrusTempDir():
    
    return tempfile.mkdtemp( prefix = 'hydrus' )
    

def SetEnvTempDir( path ):
    
    if os.path.isfile( path ):
        
        raise Exception( 'The given temp directory, "{}", seems to be a file already, not a directory!'.format( path ) )
        
    
    try:
        
        HydrusPaths.MakeSureDirectoryExists( path )
        
    except Exception as e:
        
        raise Exception( 'Could not create the temp dir: {}'.format( e ) )
        
    
    if not HydrusPaths.DirectoryIsWriteable( path ):
        
        raise Exception( 'The given temp directory, "{}", does not seem to be writeable-to!'.format( path ) )
        
    
    for tmp_name in ( 'TMPDIR', 'TEMP', 'TMP' ):
        
        if tmp_name in os.environ:
            
            os.environ[ tmp_name ] = path
            
        
    
    tempfile.tempdir = path
    

def GetSubTempDir( prefix = '' ):
    
    hydrus_temp_dir = HG.client_controller.GetHydrusTempDir()
    
    return tempfile.mkdtemp( prefix = prefix, dir = hydrus_temp_dir )
    

def GetTempPath( suffix = '', dir = None ):
    
    if dir is None:
        
        dir = HG.client_controller.GetHydrusTempDir()
        
    
    return tempfile.mkstemp( suffix = suffix, prefix = 'hydrus', dir = dir )
    
