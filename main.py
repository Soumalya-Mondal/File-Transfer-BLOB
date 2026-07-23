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
        input_folder_path = parent_folder_path / 'FilesUpload'
        output_folder_path = parent_folder_path / 'FilesDownload'
    except Exception as error:
        print(f'ERROR - [File-Transfer-BLOB:S2] - {str(error)}')
        exit(1)

    # Loading Environment Variables:S3
    try:
        load_dotenv(dotenv_path = env_file_path)
    except Exception as error:
        print(f'ERROR - [File-Transfer-BLOB:S3] - {str(error)}')
        exit(1)

    # Ask User For Operation Choice:S4
    try:
        user_choice = input('Please Choose Operation (U for Upload / D for Download): ').strip().lower()
        if user_choice not in ('u', 'd'):
            raise ValueError(f'Invalid choice: {user_choice}. Please enter "U" or "D".')
        user_choice = 'Upload' if user_choice == 'u' else 'Download'
        print(f'INFO - Selected Operation: {user_choice}')
    except Exception as error:
        print(f'ERROR - [File-Transfer-BLOB:S4] - {str(error)}')
        exit(1)

    if user_choice == 'Upload':
        # Loop Through All Files Inside "FilesUpload" Folder:S5
        try:
            file_paths_list = [file_path for file_path in input_folder_path.iterdir() if file_path.is_file()]
            print(f'SUCCESS - Found {len(file_paths_list)} File(s) In "FilesUpload" Folder:')
        except Exception as error:
            print(f'ERROR - [File-Transfer-BLOB:S5] - {str(error)}')
            exit(1)

        print(f'\nINFO - Starting To Upload {len(file_paths_list)} File(s) To Azure Blob Storage...')

        # Define "calculate_md5" Function:S6
        try:
            def calculate_md5(file_path, chunk_size=4 * 1024 * 1024):
                md5_hash = hashlib.md5()
                with open(file_path, 'rb') as check_file:
                    while chunk := check_file.read(chunk_size):
                        md5_hash.update(chunk)
                return md5_hash.digest()
        except Exception as error:
            print(f'ERROR - [File-Transfer-BLOB:S6] - {str(error)}')
            exit(1)

        # Loop Through All Files Inside "FilesUpload" Folder
        for file_path in file_paths_list:
            # Retrive File Size And MD5 Hash Value:S7
            try:
                local_file_size = file_path.stat().st_size
                local_md5_hash = calculate_md5(file_path)
            except Exception as error:
                print(f'ERROR - [File-Transfer-BLOB:S7] - {str(error)}')
                exit(1)

            # Create BLOB Client:S8
            try:
                upload_blob_service_client = BlobServiceClient.from_connection_string(str(os.getenv('BLOB_CONNECTION_STRING')))
                upload_blob_container_client = upload_blob_service_client.get_container_client(str(os.getenv('BLOB_CONTAINER_NAME')))
            except Exception as error:
                print(f'ERROR - [File-Transfer-BLOB:S8] - {str(error)}')
                exit(1)

            # Upload File To Azure BLOB Storage With MD5 Hash Value Stored In BLOB Properties:S9
            try:
                upload_file_blob_client = upload_blob_container_client.get_blob_client(file_path.name)
                with open(file_path, 'rb') as local_file_data:
                    upload_file_blob_client.upload_blob(
                        local_file_data,
                        overwrite = True,
                        content_settings = ContentSettings(content_md5 = local_md5_hash) #type: ignore
                    )
            except Exception as error:
                print(f'ERROR - [File-Transfer-BLOB:S9] - {str(error)}')
                exit(1)

            # Fetching BLOB Properties And Verifying File Integrity After Upload:S10
            try:
                if ((local_file_size == upload_file_blob_client.get_blob_properties().size) and (upload_file_blob_client.get_blob_properties().content_settings.content_md5 == local_md5_hash)):
                    print(f'SUCCESS - File "{file_path.name}" Uploaded Successfully With Verified Integrity.')
                else:
                    print(f'ERROR - File "{file_path.name}" Uploaded But Failed Integrity Verification.')
            except Exception as error:
                print(f'ERROR - [File-Transfer-BLOB:S10] - {str(error)}')
                exit(1)

    elif user_choice == 'Download':
        print(f'\nINFO - Starting To Download File(s) From Azure Blob Storage...')

        # Define BLOB Download Client Object:S11
        try:
            download_blob_service_client = BlobServiceClient.from_connection_string(str(os.getenv('BLOB_CONNECTION_STRING')))
            download_blob_container_client = download_blob_service_client.get_container_client(str(os.getenv('BLOB_CONTAINER_NAME')))
        except Exception as error:
            print(f'ERROR - [File-Transfer-BLOB:S11] - {str(error)}')
            exit(1)

        # List Available Blobs In Container:S12
        try:
            blob_list = list(download_blob_container_client.list_blobs())
            print(f'SUCCESS - Found {len(blob_list)} Blob(s) In Container:')
        except Exception as error:
            print(f'ERROR - [File-Transfer-BLOB:S12] - {str(error)}')
            exit(1)

        # Download All Files From Azure Blob Storage And Save To "FilesDownload" Folder:S13
        try:
            for blob in blob_list:
                output_file_path = output_folder_path / blob.name #type: ignore
                download_file_blob_client = download_blob_container_client.get_blob_client(blob.name)
                with open(output_file_path, 'wb') as output_file:
                    download_file_stream = download_file_blob_client.download_blob()
                    output_file.write(download_file_stream.readall())
                print(f'SUCCESS - File "{blob.name}" Downloaded')
        except Exception as error:
            print(f'ERROR - [File-Transfer-BLOB:S13] - {str(error)}')
            exit(1)