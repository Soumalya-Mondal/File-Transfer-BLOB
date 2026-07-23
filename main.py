# Define Main Function
if __name__ == "__main__":
    # Importing Python Module:S1
    try:
        from pathlib import Path
        from dotenv import load_dotenv
        import os
        import hashlib
        from azure.storage.blob import BlobServiceClient, ContentSettings
    except Exception as error:
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

    # Terminal Output Styling Helpers
    class _TermStyle:
        RESET = '\033[0m'
        BLUE = '\033[94m'
        GREEN = '\033[92m'
        RED = '\033[91m'
        YELLOW = '\033[93m'

    _LEVEL_COLORS = {
        'INFO': _TermStyle.BLUE,
        'SUCCESS': _TermStyle.GREEN,
        'ERROR': _TermStyle.RED,
        'WARN': _TermStyle.YELLOW,
    }

    def log(level, message):
        """Print a stylized log line with a colored level label."""
        color = _LEVEL_COLORS.get(level, _TermStyle.RESET)
        print(f'{color} {level:<7} {_TermStyle.RESET}{message}')

    def print_thick_separator():
        """Print a thick horizontal separator line."""
        print('═' * 60)

    def print_thin_separator():
        """Print a thin horizontal separator line."""
        print('─' * 60)

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
        user_choice = input('Please Choose Operation (U for Upload / D for Download / R for Remove): ').strip().lower()
        if user_choice not in ('u', 'd', 'r'):
            raise ValueError(f'Invalid choice: {user_choice}. Please enter "U", "D", or "R".')
        if user_choice == 'u':
            user_choice = 'Upload'
        elif user_choice == 'd':
            user_choice = 'Download'
        else:
            user_choice = 'Remove'
        print_thick_separator()
        log('INFO', f'Selected Operation: {user_choice}')
    except Exception as error:
        print(f'ERROR - [File-Transfer-BLOB:S7] - {str(error)}')
        exit(1)

    if user_choice == 'Upload':
        # Loop Through All Files Inside "FilesUpload" Folder:S8
        try:
            file_paths_list = [file_path for file_path in files_upload_folder_path.iterdir() if file_path.is_file()]
            log('SUCCESS', f'Found {len(file_paths_list)} File(s) In "FilesUpload" Folder:')
            print_thin_separator()
        except Exception as error:
            print(f'ERROR - [File-Transfer-BLOB:S8] - {str(error)}')
            exit(1)

        print_thick_separator()
        log('INFO', f'Starting To Upload {len(file_paths_list)} File(s) To Azure Blob Storage...')

        # Loop Through All Files Inside "FilesUpload" Folder
        for index, file_path in enumerate(file_paths_list, 1):
            total_files = len(file_paths_list)
            print_thin_separator()
            log('INFO', f'[{index}/{total_files}] {file_path.name}')

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
                        log('INFO', f'Existing BLOB "{file_path.name}" Deleted. Proceeding With Upload.')
                    else:
                        log('WARN', f'Execution Stopped By User. File "{file_path.name}" Was Not Uploaded.')
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
                    log('SUCCESS', f'File "{file_path.name}" Uploaded Successfully With Verified Integrity.')
                    print_thin_separator()
                else:
                    log('ERROR', f'File "{file_path.name}" Uploaded But Failed Integrity Verification.')
                    print_thin_separator()
            except Exception as error:
                print(f'ERROR - [File-Transfer-BLOB:S13] - {str(error)}')
                exit(1)

    elif user_choice == 'Download':
        print_thick_separator()
        log('INFO', 'Starting To Download File(s) From Azure Blob Storage...')

        # List Available Blobs In Container:S14
        try:
            blob_list = get_blob_list()
            log('SUCCESS', f'Found {len(blob_list)} Blob(s) In Container:')
            print_thin_separator()
        except Exception as error:
            print(f'ERROR - [File-Transfer-BLOB:S14] - {str(error)}')
            exit(1)

        # Download All Files From Azure Blob Storage And Save To "FilesDownload" Folder
        for index, blob in enumerate(blob_list, 1):
            total_blobs = len(blob_list)
            print_thin_separator()
            log('INFO', f'[{index}/{total_blobs}] {blob.name}')

            # Retrive BLOB Properties:S15
            try:
                output_file_path = files_download_folder_path / blob.name #type: ignore
                download_file_blob_client = blob_container_client.get_blob_client(blob.name)
                blob_properties = download_file_blob_client.get_blob_properties()
            except Exception as error:
                print(f'ERROR - [File-Transfer-BLOB:S15] - {str(error)}')
                exit(1)

            # Check If Local File With Same Name Exists And Ask User:S16
            try:
                if output_file_path.exists():
                    overwrite_choice = input(f'File "{blob.name}" Already Exists In "FilesDownload" Folder. Do You Want To Overwrite It? (Y/N): ').strip().lower()
                    if overwrite_choice in ('y', 'yes'):
                        output_file_path.unlink()
                        log('INFO', f'Existing Local File "{blob.name}" Deleted. Proceeding With Download.')
                    else:
                        log('WARN', f'Execution Stopped By User. File "{blob.name}" Was Not Downloaded.')
                        exit(1)
            except Exception as error:
                print(f'ERROR - [File-Transfer-BLOB:S16] - {str(error)}')
                exit(1)

            # Download File From Azure BLOB Storage:S17
            try:
                with open(output_file_path, 'wb') as output_file:
                    download_file_stream = download_file_blob_client.download_blob()
                    output_file.write(download_file_stream.readall())
            except Exception as error:
                print(f'ERROR - [File-Transfer-BLOB:S17] - {str(error)}')
                exit(1)

            # Retrive Downloaded File Size And MD5 Hash Value:S18
            try:
                local_file_size = output_file_path.stat().st_size
                local_md5_hash = calculate_md5(output_file_path)
            except Exception as error:
                print(f'ERROR - [File-Transfer-BLOB:S18] - {str(error)}')
                exit(1)

            # Verify File Integrity After Download:S19
            try:
                if ((local_file_size == blob_properties.size) and (local_md5_hash == blob_properties.content_settings.content_md5)):
                    log('SUCCESS', f'File "{blob.name}" Downloaded Successfully With Verified Integrity.')
                    print_thin_separator()
                else:
                    log('ERROR', f'File "{blob.name}" Downloaded But Failed Integrity Verification.')
                    print_thin_separator()
            except Exception as error:
                print(f'ERROR - [File-Transfer-BLOB:S19] - {str(error)}')
                exit(1)

    elif user_choice == 'Remove':
        print_thick_separator()
        log('INFO', 'Preparing To Remove File(s) From Azure Blob Storage...')

        # List Available Blobs In Container:S20
        try:
            blob_list = get_blob_list()
            if not blob_list:
                log('WARN', 'No Blobs Found In Container. Nothing To Remove.')
                exit(0)
            log('SUCCESS', f'Found {len(blob_list)} Blob(s) That Will Be Removed:')
            print_thin_separator()
            for blob in blob_list:
                log('INFO', f'- {blob.name}')
        except Exception as error:
            print(f'ERROR - [File-Transfer-BLOB:S20] - {str(error)}')
            exit(1)

        print_thick_separator()

        # Ask For Bulk Confirmation Before Removing:S21
        try:
            remove_choice = input(f'Are You Sure You Want To Delete All {len(blob_list)} Blob(s)? (Y/N): ').strip().lower()
            if remove_choice not in ('y', 'yes'):
                log('WARN', 'Execution Stopped By User. No Blobs Were Removed.')
                exit(0)
        except Exception as error:
            print(f'ERROR - [File-Transfer-BLOB:S21] - {str(error)}')
            exit(1)

        print_thick_separator()
        log('INFO', f'Starting To Remove {len(blob_list)} Blob(s) From Azure Blob Storage...')

        # Remove All Blobs From Azure Blob Storage:S22
        for index, blob in enumerate(blob_list, 1):
            total_blobs = len(blob_list)
            print_thin_separator()
            log('INFO', f'[{index}/{total_blobs}] {blob.name}')

            try:
                blob_container_client.delete_blob(blob.name)
                log('SUCCESS', f'BLOB "{blob.name}" Removed Successfully.')
            except Exception as error:
                print(f'ERROR - [File-Transfer-BLOB:S22] - {str(error)}')
                exit(1)
