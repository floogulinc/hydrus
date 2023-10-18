import os
import tempfile
import threading

from hydrus.core import HydrusData
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
    

HYDRUS_TEMP_DIR = None

def GetHydrusTempDir():
    
    path = tempfile.mkdtemp( prefix = 'hydrus' )
    
    global HYDRUS_TEMP_DIR
    
    if HYDRUS_TEMP_DIR is None:
        
        HYDRUS_TEMP_DIR = path
        
    
    return path
    

def SetEnvTempDir( path ):
    
    if os.path.exists( path ) and not os.path.isdir( path ):
        
        raise Exception( 'The given temp directory, "{}", does not seem to be a directory!'.format( path ) )
        
    
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
    
    global HYDRUS_TEMP_DIR
    
    return tempfile.mkdtemp( prefix = prefix, dir = HYDRUS_TEMP_DIR )
    

def GetTempPath( suffix = '', dir = None ):
    
    global HYDRUS_TEMP_DIR
    
    if dir is None and HYDRUS_TEMP_DIR is not None:
        
        dir = HYDRUS_TEMP_DIR
        
        if not os.path.exists( dir ):
            
            HYDRUS_TEMP_DIR = None
            
            dir = GetHydrusTempDir()
            
        
    
    return tempfile.mkstemp( suffix = suffix, prefix = 'hydrus', dir = dir )
    
