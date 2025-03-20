import os
from app import app


class historique_ODM:
    def __init__(self):
        pass

    def get_files_in_directory(self, directory):
        # Vérifier si le dossier existe, sinon le créer
        if not os.path.exists(directory):
            print(f"Le dossier {directory} n'existe pas, création du dossier.")
            os.makedirs(directory)
        
        files = []
        # Parcours tous les fichiers du répertoire
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                file_info = {
                    'filename': filename,
                    'path': file_path,
                    'modified': os.path.getmtime(file_path)  # Date de dernière modification
                }
                files.append(file_info)
        
        # Trie les fichiers par date de modification (du plus récent au plus ancien)
        files.sort(key=lambda x: x['modified'], reverse=True)
        return files