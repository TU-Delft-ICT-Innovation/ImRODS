from irods.session import iRODSSession
import ssl
import os


class TuRODSSession(iRODSSession):
    

    def __init__(self, client_user=None):
        
        
        
        host = os.environ.get('IRODS_HOST', '')
        port = os.environ.get('IRODS_PORT', '')
        user = os.environ.get('IRODS_USER', '')
        password = os.environ.get('IRODS_PWD', '')
        zone = os.environ.get('IRODS_ZONE', '')
        

        context = ssl.create_default_context(
            purpose=ssl.Purpose.SERVER_AUTH, 
            cafile="/etc/irods/crt-sara-tud.crt", 
            capath=None, 
            cadata=None)

        ssl_settings = {
            'client_server_negotiation': 'request_server_negotiation',
            'client_server_policy': 'CS_NEG_REQUIRE',
            'encryption_algorithm': 'AES-256-CBC',
            'encryption_key_size': 32,
            'encryption_num_hash_rounds': 16,
            'encryption_salt_size': 8,                        
            'ssl_context': context}
    
        super(TuRODSSession, self).__init__(
            host=host, 
            port=port, 
            user=user, 
            password=password, 
            zone=zone, 
            client_user=client_user,
            **ssl_settings
            )
