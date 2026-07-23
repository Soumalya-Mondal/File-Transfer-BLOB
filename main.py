# Define Main Function
if __name__ == "__main__":
    # Importing Python Module:S1
    try:
        from pathlib import Path
        from dotenv import load_dotenv
        from azure.storage.blob import BlobServiceClient, ContentSettings
        import os
        import hashlib
    except ImportError as error:
        print(f'ERROR - [File-Transfer-BLOB:S1] - {str(error)}')
        exit(1)

    # Define System Path:S2
    try:
        parent_folder_path = Path.cwd()
        env_file_path = parent_folder_path / '.env'
        files_upload_folder_path = parent_folder_path / 'FilesUpload'
        files_download_folder_path = parent_folder_path / 'FilesDownload'
        files_upload_folder_path.mkdir(parents = True, exist_ok = True)
        files_download_folder_path.mkdir(parents = True, exist_ok = True)
    except Exception as error:
        print(f'ERROR - [File-Transfer-BLOB:S2] - {str(error)}')
        exit(1)

    # Loading Environment Variables:S3
    try:
        load_dotenv(dotenv_path = env_file_path)
    except Exception as error:
        print(f'ERROR - [File-Transfer-BLOB:S3] - {str(error)}')
        exit(1)

    # Creating Azure BLOB Service Client:S4
    try:
        blob_service_client = BlobServiceClient.from_connection_string(str(os.getenv('BLOB_CONNECTION_STRING')))
        blob_container_client = blob_service_client.get_container_client(str(os.getenv('BLOB_CONTAINER_NAME')))
    except Exception as error:
        print(f'ERROR - [File-Transfer-BLOB:S4] - {str(error)}')
        exit(1)

    # Define "calculate_md5" Function:S5
    try:
        def calculate_md5(file_path, chunk_size=4 * 1024 * 1024):
            md5_hash = hashlib.md5()
            with open(file_path, 'rb') as check_file:
                while chunk := check_file.read(chunk_size):
                    md5_hash.update(chunk)
            return md5_hash.digest()
    except Exception as error:
        print(f'ERROR - [File-Transfer-BLOB:S5] - {str(error)}')
        exit(1)

    # Define "get_blob_list" Function:S6
    try:
        def get_blob_list():
            return list(blob_container_client.list_blobs())
    except Exception as error:
        print(f'ERROR - [File-Transfer-BLOB:S6] - {str(error)}')
        exit(1)

    # Ask User For Operation Choice:S7
    try:
        user_choice = input('Please Choose Operation (U for Upload / D for Download): ').strip().lower()
        if user_choice not in ('u', 'd'):
            raise ValueError(f'Invalid choice: {user_choice}. Please enter "U" or "D".')
        user_choice = 'Upload' if user_choice == 'u' else 'Download'
        print(f'INFO - Selected Operation: {user_choice}')
    except Exception as error:
        print(f'ERROR - [File-Transfer-BLOB:S7] - {str(error)}')
        exit(1)

    if user_choice == 'Upload':
        # Loop Through All Files Inside "FilesUpload" Folder:S8
        try:
            file_paths_list = [file_path for file_path in files_upload_folder_path.iterdir() if file_path.is_file()]
            print(f'SUCCESS - Found {len(file_paths_list)} File(s) In "FilesUpload" Folder:')
        except Exception as error:
            print(f'ERROR - [File-Transfer-BLOB:S8] - {str(error)}')
            exit(1)

        print(f'\nINFO - Starting To Upload {len(file_paths_list)} File(s) To Azure Blob Storage...')

        # Loop Through All Files Inside "FilesUpload" Folder
        for file_path in file_paths_list:
            # List Existing BLOBs:S9
            try:
                blob_list = get_blob_list()
                blob_exists = file_path.name in [blob.name for blob in blob_list]
            except Exception as error:
                print(f'ERROR - [File-Transfer-BLOB:S9] - {str(error)}')
                exit(1)

            # Delete Existing BLOB If User Confirms:S10
            try:
                if blob_exists:
                    delete_choice = input(f'File "{file_path.name}" Already Exists In BLOB. Do You Want To Delete It? (Y/N): ').strip().lower()
                    if delete_choice in ('y', 'yes'):
                        blob_container_client.delete_blob(file_path.name)
                        print(f'INFO - Existing BLOB "{file_path.name}" Deleted. Proceeding With Upload.')
                    else:
                        print(f'INFO - Execution Stopped By User. File "{file_path.name}" Was Not Uploaded.')
                        exit(1)
            except Exception as error:
                print(f'ERROR - [File-Transfer-BLOB:S10] - {str(error)}')
                exit(1)

            # Retrive File Size And MD5 Hash Value:S11
            try:
                local_file_size = file_path.stat().st_size
                local_md5_hash = calculate_md5(file_path)
            except Exception as error:
                print(f'ERROR - [File-Transfer-BLOB:S11] - {str(error)}')
                exit(1)

            # Upload File To Azure BLOB Storage With MD5 Hash Value Stored In BLOB Properties:S12
            try:
                upload_file_blob_client = blob_container_client.get_blob_client(file_path.name)
                with open(file_path, 'rb') as local_file_data:
                    upload_file_blob_client.upload_blob(
                        local_file_data,
                        overwrite = True,
                        content_settings = ContentSettings(content_md5 = local_md5_hash) #type: ignore
                    )
            except Exception as error:
                print(f'ERROR - [File-Transfer-BLOB:S12] - {str(error)}')
                exit(1)

            # Fetching BLOB Properties And Verifying File Integrity After Upload:S13
            try:
                if ((local_file_size == upload_file_blob_client.get_blob_properties().size) and (upload_file_blob_client.get_blob_properties().content_settings.content_md5 == local_md5_hash)):
                    print(f'SUCCESS - File "{file_path.name}" Uploaded Successfully With Verified Integrity.')
                else:
                    print(f'ERROR - File "{file_path.name}" Uploaded But Failed Integrity Verification.')
            except Exception as error:
                print(f'ERROR - [File-Transfer-BLOB:S13] - {str(error)}')
                exit(1)

    elif user_choice == 'Download':
        print(f'\nINFO - Starting To Download File(s) From Azure Blob Storage...')

        # List Available Blobs In Container:S14
        try:
            blob_list = get_blob_list()
            print(f'SUCCESS - Found {len(blob_list)} Blob(s) In Container:')
        except Exception as error:
            print(f'ERROR - [File-Transfer-BLOB:S14] - {str(error)}')
            exit(1)

        # Download All Files From Azure Blob Storage And Save To "FilesDownload" Folder
        for blob in blob_list:
            # Retrive BLOB Size And MD5 Hash Value From BLOB Properties:S15
            try:
                output_file_path = files_download_folder_path / blob.name #type: ignore
                download_file_blob_client = blob_container_client.get_blob_client(blob.name)
                blob_properties = download_file_blob_client.get_blob_properties()
                blob_file_size = blob_properties.size
                blob_md5_hash = blob_properties.content_settings.content_md5
            except Exception as error:
                print(f'ERROR - [File-Transfer-BLOB:S15] - {str(error)}')
                exit(1)

            # Download File From Azure BLOB Storage:S16
            try:
                with open(output_file_path, 'wb') as output_file:
                    download_file_stream = download_file_blob_client.download_blob()
                    output_file.write(download_file_stream.readall())
            except Exception as error:
                print(f'ERROR - [File-Transfer-BLOB:S16] - {str(error)}')
                exit(1)

            # Retrive Downloaded File Size And MD5 Hash Value:S17
            try:
                local_file_size = output_file_path.stat().st_size
                local_md5_hash = calculate_md5(output_file_path)
            except Exception as error:
                print(f'ERROR - [File-Transfer-BLOB:S17] - {str(error)}')
                exit(1)

            # Verify File Integrity After Download:S18
            try:
                if ((local_file_size == blob_file_size) and (local_md5_hash == blob_md5_hash)):
                    print(f'SUCCESS - File "{blob.name}" Downloaded Successfully With Verified Integrity.')
                else:
                    print(f'ERROR - File "{blob.name}" Downloaded But Failed Integrity Verification.')
            except Exception as error:
                print(f'ERROR - [File-Transfer-BLOB:S18] - {str(error)}')
                exit(1)
