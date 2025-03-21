import os
import re
from datetime import datetime
from flask import render_template, request
from flask_login import login_required
from app import app


class historique_odm:
    def __init__(self):
        self.odm_directory_excel = os.path.join(app.root_path, 'odm_excel')
        self.odm_directory_pdf = os.path.join(app.root_path, 'odm_pdf')

    def get_files(self, directory):
        files = []
        if not os.path.exists(directory):
            return files

        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                # Extraire la date de début et l'affaire depuis le nom du fichier
                date_match = re.search(r'(\d{2}-\d{2}-\d{4})', filename)
                affaire_match = re.search(r'_(A\d+)\.', filename)  # Cherche "_Axxxx." avant l'extension

                if date_match:
                    date_str = date_match.group(1)  # Ex: "12-05-2025"
                    try:
                        date_obj = datetime.strptime(date_str, "%d-%m-%Y")
                        date_iso = date_obj.strftime('%Y-%m-%d')  # Format ISO pour tri/filtrage
                    except ValueError:
                        date_iso = None
                else:
                    date_iso = None  # Fichier sans date valide

                affaire = affaire_match.group(1) if affaire_match else "Non défini"  # Ex: "A0526"

                file_info = {
                    'filename': filename,
                    'path': file_path,
                    'date_iso': date_iso,
                    'year': date_iso.split('-')[0] if date_iso else None,
                    'month': date_iso.split('-')[1] if date_iso else None,
                    'affaire': affaire,
                    'type': 'pdf' if filename.lower().endswith('.pdf') else 'xlsx'
                }
                files.append(file_info)

        # Trier les fichiers par date (du plus récent au plus ancien)
        files.sort(key=lambda x: x['date_iso'] or "0000-00-00", reverse=True)
        return files