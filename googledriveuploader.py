from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class GoogleDriveUploader:
    def __init__(self, credentials_path, drive_folder_id):
        self.credentials_path = credentials_path
        self.drive_folder_id = drive_folder_id
        self.service = self._authenticate()

    def _authenticate(self):
        try:
            creds = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=["https://www.googleapis.com/auth/drive.file"]
            )
            service = build('drive', 'v3', credentials=creds)
            print("Autenticação realizada com sucesso.")
            return service
        except Exception as e:
            print(f"Erro ao autenticar na API do Google Drive: {e}")
            return None

    def upload_file(self, file_path, file_name=None):
        if not self.service:
            print("Serviço não autenticado. Verifique as credenciais.")
            return

        file_name = file_name or file_path.split("/")[-1]

        file_metadata = {
            'name': file_name,
            'parents': [self.drive_folder_id]
        }

        try:
            media = MediaFileUpload(file_path, mimetype='text/csv')
            upload_file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()

            print(f"Arquivo '{file_name}' carregado com sucesso! ID do arquivo: {upload_file.get('id')}")
        except Exception as e:
            print(f"Erro ao carregar o arquivo para o Google Drive: {e}")
