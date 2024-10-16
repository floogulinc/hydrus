from hydrus.core import HydrusConstants as HC
from hydrus.core import HydrusExceptions
from hydrus.core.networking import HydrusNetworkVariableHandling
from hydrus.core.networking import HydrusServerRequest
from hydrus.core.networking import HydrusServerResources

from hydrus.client import ClientAPI
from hydrus.client import ClientConstants as CC
from hydrus.client import ClientGlobals as CG
from hydrus.client import ClientLocation
from hydrus.client.media import ClientMedia
from hydrus.client.media import ClientMediaFileFilter
from hydrus.client.metadata import ClientContentUpdates
from hydrus.client.networking.api import ClientLocalServerCore
from hydrus.client.networking.api import ClientLocalServerResources


class HydrusResourceClientAPIRestrictedManageFileRelationships( ClientLocalServerResources.HydrusResourceClientAPIRestricted ):
    
    def _CheckAPIPermissions( self, request: HydrusServerRequest.HydrusRequest ):
        
        request.client_api_permissions.CheckPermission( ClientAPI.CLIENT_API_PERMISSION_MANAGE_FILE_RELATIONSHIPS )
        
    

class HydrusResourceClientAPIRestrictedManageFileRelationshipsGetRelationships( HydrusResourceClientAPIRestrictedManageFileRelationships ):
    
    def _threadDoGETJob( self, request: HydrusServerRequest.HydrusRequest ):
        
        location_context = ClientLocalServerCore.ParseLocationContext( request, ClientLocation.LocationContext.STATICCreateSimple( CC.COMBINED_LOCAL_MEDIA_SERVICE_KEY ) )
        
        hashes = ClientLocalServerCore.ParseHashes( request )
        
        # maybe in future we'll just get the media results and dump the dict from there, but whatever
        hashes_to_file_duplicates = CG.client_controller.Read( 'file_relationships_for_api', location_context, hashes )
        
        body_dict = { 'file_relationships' : hashes_to_file_duplicates }
        
        body = ClientLocalServerCore.Dumps( body_dict, request.preferred_mime )
        
        response_context = HydrusServerResources.ResponseContext( 200, mime = request.preferred_mime, body = body )
        
        return response_context
        
    

class HydrusResourceClientAPIRestrictedManageFileRelationshipsGetPotentialsCount( HydrusResourceClientAPIRestrictedManageFileRelationships ):
    
    def _threadDoGETJob( self, request: HydrusServerRequest.HydrusRequest ):
        
        (
            file_search_context_1,
            file_search_context_2,
            dupe_search_type,
            pixel_dupes_preference,
            max_hamming_distance
        ) = ClientLocalServerCore.ParseDuplicateSearch( request )
        
        count = CG.client_controller.Read( 'potential_duplicates_count', file_search_context_1, file_search_context_2, dupe_search_type, pixel_dupes_preference, max_hamming_distance )
        
        body_dict = { 'potential_duplicates_count' : count }
        
        body = ClientLocalServerCore.Dumps( body_dict, request.preferred_mime )
        
        response_context = HydrusServerResources.ResponseContext( 200, mime = request.preferred_mime, body = body )
        
        return response_context
        
    

class HydrusResourceClientAPIRestrictedManageFileRelationshipsGetPotentialPairs( HydrusResourceClientAPIRestrictedManageFileRelationships ):
    
    def _threadDoGETJob( self, request: HydrusServerRequest.HydrusRequest ):
        
        (
            file_search_context_1,
            file_search_context_2,
            dupe_search_type,
            pixel_dupes_preference,
            max_hamming_distance
        ) = ClientLocalServerCore.ParseDuplicateSearch( request )
        
        max_num_pairs = request.parsed_request_args.GetValue( 'max_num_pairs', int, default_value = CG.client_controller.new_options.GetInteger( 'duplicate_filter_max_batch_size' ) )
        
        filtering_pairs_media_results = CG.client_controller.Read( 'duplicate_pairs_for_filtering', file_search_context_1, file_search_context_2, dupe_search_type, pixel_dupes_preference, max_hamming_distance, max_num_pairs = max_num_pairs )
        
        filtering_pairs_hashes = [ ( m1.GetHash().hex(), m2.GetHash().hex() ) for ( m1, m2 ) in filtering_pairs_media_results ]
        
        body_dict = { 'potential_duplicate_pairs' : filtering_pairs_hashes }
        
        body = ClientLocalServerCore.Dumps( body_dict, request.preferred_mime )
        
        response_context = HydrusServerResources.ResponseContext( 200, mime = request.preferred_mime, body = body )
        
        return response_context
        
    

class HydrusResourceClientAPIRestrictedManageFileRelationshipsGetRandomPotentials( HydrusResourceClientAPIRestrictedManageFileRelationships ):
    
    def _threadDoGETJob( self, request: HydrusServerRequest.HydrusRequest ):
        
        (
            file_search_context_1,
            file_search_context_2,
            dupe_search_type,
            pixel_dupes_preference,
            max_hamming_distance
        ) = ClientLocalServerCore.ParseDuplicateSearch( request )
        
        hashes = CG.client_controller.Read( 'random_potential_duplicate_hashes', file_search_context_1, file_search_context_2, dupe_search_type, pixel_dupes_preference, max_hamming_distance )
        
        body_dict = { 'random_potential_duplicate_hashes' : [ hash.hex() for hash in hashes ] }
        
        body = ClientLocalServerCore.Dumps( body_dict, request.preferred_mime )
        
        response_context = HydrusServerResources.ResponseContext( 200, mime = request.preferred_mime, body = body )
        
        return response_context
        
    

class HydrusResourceClientAPIRestrictedManageFileRelationshipsRemovePotentials( HydrusResourceClientAPIRestrictedManageFileRelationships ):
    
    def _threadDoPOSTJob( self, request: HydrusServerRequest.HydrusRequest ):
        
        hashes = ClientLocalServerCore.ParseHashes( request )
        
        CG.client_controller.WriteSynchronous( 'remove_potential_pairs', hashes )
        
        response_context = HydrusServerResources.ResponseContext( 200 )
        
        return response_context
        
    

class HydrusResourceClientAPIRestrictedManageFileRelationshipsSetKings( HydrusResourceClientAPIRestrictedManageFileRelationships ):
    
    def _threadDoPOSTJob( self, request: HydrusServerRequest.HydrusRequest ):
        
        hashes = ClientLocalServerCore.ParseHashes( request )
        
        for hash in hashes:
            
            CG.client_controller.WriteSynchronous( 'duplicate_set_king', hash )
            
        
        response_context = HydrusServerResources.ResponseContext( 200 )
        
        return response_context
        
    

class HydrusResourceClientAPIRestrictedManageFileRelationshipsSetRelationships( HydrusResourceClientAPIRestrictedManageFileRelationships ):
    
    def _threadDoPOSTJob( self, request: HydrusServerRequest.HydrusRequest ):
        
        database_write_rows = []
        
        raw_rows = []
        
        # TODO: now I rewangled this to remove the pair_rows parameter, let's get an object or dict bouncing around so we aren't handling a mega-tuple
        
        raw_relationship_dicts = request.parsed_request_args.GetValue( 'relationships', list, expected_list_type = dict, default_value = [] )
        
        for raw_relationship_dict in raw_relationship_dicts:
            
            duplicate_type = HydrusNetworkVariableHandling.GetValueFromDict( raw_relationship_dict, 'relationship', int )
            hash_a_hex = HydrusNetworkVariableHandling.GetValueFromDict( raw_relationship_dict, 'hash_a', str )
            hash_b_hex = HydrusNetworkVariableHandling.GetValueFromDict( raw_relationship_dict, 'hash_b', str )
            do_default_content_merge = HydrusNetworkVariableHandling.GetValueFromDict( raw_relationship_dict, 'do_default_content_merge', bool )
            delete_a = HydrusNetworkVariableHandling.GetValueFromDict( raw_relationship_dict, 'delete_a', bool, default_value = False )
            delete_b = HydrusNetworkVariableHandling.GetValueFromDict( raw_relationship_dict, 'delete_b', bool, default_value = False )
            
            raw_rows.append( ( duplicate_type, hash_a_hex, hash_b_hex, do_default_content_merge, delete_a, delete_b ) )
            
        
        allowed_duplicate_types = {
            HC.DUPLICATE_FALSE_POSITIVE,
            HC.DUPLICATE_ALTERNATE,
            HC.DUPLICATE_BETTER,
            HC.DUPLICATE_WORSE,
            HC.DUPLICATE_SAME_QUALITY,
            HC.DUPLICATE_POTENTIAL
        }
        
        all_hashes = set()
        
        # variable type testing
        for row in raw_rows:
            
            ( duplicate_type, hash_a_hex, hash_b_hex, do_default_content_merge, delete_first, delete_second ) = row
            
            HydrusNetworkVariableHandling.TestVariableType( 'relationship', duplicate_type, int, allowed_values = allowed_duplicate_types )
            HydrusNetworkVariableHandling.TestVariableType( 'hash_a', hash_a_hex, str )
            HydrusNetworkVariableHandling.TestVariableType( 'hash_b', hash_b_hex, str )
            HydrusNetworkVariableHandling.TestVariableType( 'do_default_content_merge', do_default_content_merge, bool )
            HydrusNetworkVariableHandling.TestVariableType( 'delete_first', delete_first, bool )
            HydrusNetworkVariableHandling.TestVariableType( 'delete_second', delete_second, bool )
            
            try:
                
                hash_a = bytes.fromhex( hash_a_hex )
                hash_b = bytes.fromhex( hash_b_hex )
                
            except:
                
                raise HydrusExceptions.BadRequestException( 'Sorry, did not understand one of the hashes {} or {}!'.format( hash_a_hex, hash_b_hex ) )
                
            
            ClientLocalServerCore.CheckHashLength( ( hash_a, hash_b ) )
            
            all_hashes.update( ( hash_a, hash_b ) )
            
        
        media_results = CG.client_controller.Read( 'media_results', all_hashes )
        
        hashes_to_media_results = { media_result.GetHash() : media_result for media_result in media_results }
        
        for row in raw_rows:
            
            ( duplicate_type, hash_a_hex, hash_b_hex, do_default_content_merge, delete_first, delete_second ) = row
            
            hash_a = bytes.fromhex( hash_a_hex )
            hash_b = bytes.fromhex( hash_b_hex )
            
            content_update_packages = []
            
            first_media = ClientMedia.MediaSingleton( hashes_to_media_results[ hash_a ] )
            second_media = ClientMedia.MediaSingleton( hashes_to_media_results[ hash_b ] )
            
            file_deletion_reason = 'From Client API (duplicates processing).'
            
            if do_default_content_merge:
                
                duplicate_content_merge_options = CG.client_controller.new_options.GetDuplicateContentMergeOptions( duplicate_type )
                
                content_update_packages.append( duplicate_content_merge_options.ProcessPairIntoContentUpdatePackage( first_media, second_media, file_deletion_reason = file_deletion_reason, delete_first = delete_first, delete_second = delete_second ) )
                
            elif delete_first or delete_second:
                
                content_update_package = ClientContentUpdates.ContentUpdatePackage()
                
                deletee_media = set()
                
                if delete_first:
                    
                    deletee_media.add( first_media )
                    
                
                if delete_second:
                    
                    deletee_media.add( second_media )
                    
                
                for media in deletee_media:
                    
                    if media.HasDeleteLocked():
                        
                        ClientMediaFileFilter.ReportDeleteLockFailures( [ media ] )
                        
                        continue
                        
                    
                    if media.GetLocationsManager().IsTrashed():
                        
                        deletee_service_keys = ( CC.COMBINED_LOCAL_FILE_SERVICE_KEY, )
                        
                    else:
                        
                        local_file_service_keys = CG.client_controller.services_manager.GetServiceKeys( ( HC.LOCAL_FILE_DOMAIN, ) )
                        
                        deletee_service_keys = media.GetLocationsManager().GetCurrent().intersection( local_file_service_keys )
                        
                    
                    for deletee_service_key in deletee_service_keys:
                        
                        content_update = ClientContentUpdates.ContentUpdate( HC.CONTENT_TYPE_FILES, HC.CONTENT_UPDATE_DELETE, media.GetHashes(), reason = file_deletion_reason )
                        
                        content_update_package.AddContentUpdate( deletee_service_key, content_update )
                        
                    
                
                content_update_packages.append( content_update_package )
                
            
            database_write_rows.append( ( duplicate_type, hash_a, hash_b, content_update_packages ) )
            
        
        if len( database_write_rows ) > 0:
            
            CG.client_controller.WriteSynchronous( 'duplicate_pair_status', database_write_rows )
            
        
        response_context = HydrusServerResources.ResponseContext( 200 )
        
        return response_context
        
    