# Define Main Function
if __name__ == "__main__":
    # Importing Python Module:S1
    try:
        from pathlib import Path
        from dotenv import load_dotenv
        from azure.storage.blob import BlobServiceClient, ContentSettings
        from azure.core.exceptions import ResourceExistsError
        import os
        import hashlib
        import requests
    except ImportError as error:
        print(f'ERROR - [BLOB-Test:S1] - {str(error)}')

    # Define System Path:S2
    try:
        parent_folder_path = Path.cwd()
        env_file_path = parent_folder_path / '.env'
        input_folder_path = parent_folder_path / 'FilesUpload'
        output_folder_path = parent_folder_path / 'FilesDownload'
    except Exception as error:
        print(f'ERROR - [BLOB-Test:S2] - {str(error)}')

    # Loading Environment Variables:S3
    try:
        load_dotenv(dotenv_path = env_file_path)
    except Exception as error:
        print(f'ERROR - [BLOB-Test:S3] - {str(error)}')

    # Loop Through All Files Inside "FilesUpload" Folder:S4
    try:
        file_paths_list = [file_path for file_path in input_folder_path.iterdir() if file_path.is_file()]
        print(f'SUCCESS - Found {len(file_paths_list)} File(s) In "FilesUpload" Folder:')
    except Exception as error:
        print(f'ERROR - [BLOB-Test:S4] - {str(error)}')

    # Define "calculate_md5" Function:S5
    try:
        def calculate_md5(file_path, chunk_size=4 * 1024 * 1024):
            md5_hash = hashlib.md5()
            with open(file_path, 'rb') as check_file:
                while chunk := check_file.read(chunk_size):
                    md5_hash.update(chunk)
            return md5_hash.digest()
    except Exception as error:
        print(f'ERROR - [BLOB-Test:S5] - {str(error)}')

    # Loop Through All Files Inside "FilesUpload" Folder
    for file_path in file_paths_list:
        # Retrive File Size And MD5 Hash Value:S6
        try:
            local_file_size = file_path.stat().st_size
            local_md5_hash = calculate_md5(file_path)
        except Exception as error:
            print(f'ERROR - [BLOB-Test:S6] - {str(error)}')

        # Create BLOB Client:S7
        try:
            upload_blob_service_client = BlobServiceClient.from_connection_string(os.getenv('CONNECTION_STRING'))
            upload_blob_container_client = upload_blob_service_client.get_container_client(os.getenv('CONTAINER_NAME'))
        except Exception as error:
            print(f'ERROR - [BLOB-Test:S7] - {str(error)}')
        
        # Create BLOB Container If Not Exists:S8
        try:
            upload_blob_container_client.create_container()
        except ResourceExistsError:
            pass

        # Upload File To Azure BLOB Storage With MD5 Hash Value Stored In BLOB Properties:S9
        try:
            upload_file_blob_name = f'IncidentFiles/{file_path.name}'
            upload_file_blob_client = upload_blob_container_client.get_blob_client(upload_file_blob_name)
            with open(file_path, 'rb') as local_file_data:
                upload_file_blob_client.upload_blob(
                    local_file_data,
                    overwrite = True,
                    content_settings = ContentSettings(content_md5 = local_md5_hash)
                )
        except Exception as error:
            print(f'ERROR - [BLOB-Test:S9] - {str(error)}')

        # Fetching BLOB Properties And Verifying File Integrity After Upload:S10
        try:
            if ((local_file_size == upload_file_blob_client.get_blob_properties().size) and (upload_file_blob_client.get_blob_properties().content_settings.content_md5 == local_md5_hash)):
                print(f'SUCCESS - File "{file_path.name}" Uploaded Successfully With Verified Integrity.')
            else:
                print(f'ERROR - File "{file_path.name}" Uploaded But Failed Integrity Verification.')
        except Exception as error:
            print(f'ERROR - [BLOB-Test:S10] - {str(error)}')

    print(f'\nINFO - Starting To Download {len(file_paths_list)} File(s) From Azure Blob Storage...')

    # Define BLOB Download Client Object:S11
    try:
        download_blob_service_client = BlobServiceClient.from_connection_string(os.getenv('CONNECTION_STRING'))
        download_blob_container_client = download_blob_service_client.get_container_client(os.getenv('CONTAINER_NAME'))
    except Exception as error:
        print(f'ERROR - [BLOB-Test:S11] - {str(error)}')

    # Download All Files From Azure Blob Storage And Save To "output" Folder:S11
    try:
        for file_path in file_paths_list:
            download_file_blob_name = f'IncidentFiles/{file_path.name}'
            output_file_path = output_folder_path / file_path.name
            download_file_blob_client = download_blob_container_client.get_blob_client(download_file_blob_name)
            with open(output_file_path, 'wb') as output_file:
                download_file_stream = download_file_blob_client.download_blob()
                output_file.write(download_file_stream.readall())
            print(f'SUCCESS - File "{file_path.name}" Downloaded')
    except Exception as error:
        print(f'ERROR - [BLOB-Test:S11] - {str(error)}')

    # Define BLOB Delete Client Object:S12
    try:
        delete_blob_service_client = BlobServiceClient.from_connection_string(os.getenv('CONNECTION_STRING'))
        delete_blob_container_client = delete_blob_service_client.get_container_client(os.getenv('CONTAINER_NAME'))
    except Exception as error:
        print(f'ERROR - [BLOB-Test:S12] - {str(error)}')

    # Delete All Files From Azure Blob Storage:S13
    try:
        print(f'\nINFO - Starting To Delete {len(file_paths_list)} File(s) From Azure Blob Storage...')
        for file_path in file_paths_list:
            delete_file_blob_name = f'IncidentFiles/{file_path.name}'
            delete_file_blob_client = delete_blob_container_client.get_blob_client(delete_file_blob_name)
            delete_file_blob_client.delete_blob()
            print(f'SUCCESS - File "{file_path.name}" Deleted From Blob Storage')
    except Exception as error:
        print(f'ERROR - [BLOB-Test:S13] - {str(error)}')

    # Define BLOB Archive Client Object:S14
    try:
        archive_blob_service_client = BlobServiceClient.from_connection_string(os.getenv('CONNECTION_STRING'))
        archive_blob_container_client = archive_blob_service_client.get_container_client(os.getenv('CONTAINER_NAME'))
    except Exception as error:
        print(f'ERROR - [BLOB-Test:S14] - {str(error)}')

    # Move All Uploaded Files To Archive Access Tier:S15
    try:
        print(f'\nINFO - Starting To Move {len(file_paths_list)} File(s) To Archive Access Tier...')
        for file_path in file_paths_list:
            archive_file_blob_name = f'IncidentFiles/{file_path.name}'
            archive_file_blob_client = archive_blob_container_client.get_blob_client(archive_file_blob_name)
            archive_file_blob_client.set_standard_blob_tier('Archive')
            print(f'SUCCESS - File "{file_path.name}" Moved To Archive Access Tier')
    except Exception as error:
        print(f'ERROR - [BLOB-Test:S15] - {str(error)}')

    # Define BLOB Hot Access Tier Client Object:S16
    try:
        hot_blob_service_client = BlobServiceClient.from_connection_string(os.getenv('CONNECTION_STRING'))
        hot_blob_container_client = hot_blob_service_client.get_container_client(os.getenv('CONTAINER_NAME'))
    except Exception as error:
        print(f'ERROR - [BLOB-Test:S16] - {str(error)}')

    # Move All Files From Archive Back To Hot Access Tier:S17
    try:
        print(f'\nINFO - Starting To Move {len(file_paths_list)} File(s) From Archive To Hot Access Tier...')
        for file_path in file_paths_list:
            hot_file_blob_name = f'IncidentFiles/{file_path.name}'
            hot_file_blob_client = hot_blob_container_client.get_blob_client(hot_file_blob_name)
            hot_file_blob_client.set_standard_blob_tier('Hot')
            print(f'SUCCESS - File "{file_path.name}" Moved To Hot Access Tier')
    except Exception as error:
        print(f'ERROR - [BLOB-Test:S17] - {str(error)}')

    # Define BLOB Check Access Tier Client Object:S18
    try:
        check_blob_service_client = BlobServiceClient.from_connection_string(os.getenv('CONNECTION_STRING'))
        check_blob_container_client = check_blob_service_client.get_container_client(os.getenv('CONTAINER_NAME'))
    except Exception as error:
        print(f'ERROR - [BLOB-Test:S18] - {str(error)}')

    # Check Current Access Tier For All Files:S19
    try:
        print(f'\nINFO - Starting To Check Current Access Tier For {len(file_paths_list)} File(s)...')
        for file_path in file_paths_list:
            check_file_blob_name = f'IncidentFiles/{file_path.name}'
            check_file_blob_client = check_blob_container_client.get_blob_client(check_file_blob_name)
            blob_properties = check_file_blob_client.get_blob_properties()
            access_tier = blob_properties.blob_tier
            archive_status = blob_properties.archive_status if hasattr(blob_properties, 'archive_status') else 'N/A'
            print(f'INFO - File "{file_path.name}" - Access Tier: {access_tier}, Archive Status: {archive_status}')
    except Exception as error:
        print(f'ERROR - [BLOB-Test:S19] - {str(error)}')