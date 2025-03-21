from flask import render_template, request, redirect, url_for, session, send_file, flash, jsonify, request
import requests
from flask_login import login_user, login_required, logout_user, current_user
from app import app
from app.forms import *
from app.requete import Requete_BDD
from app.excel import Excel
from datetime import datetime
import os
from app.gps import class_gps
from app.login import utilisateur
import shutil
from app.historique_odm import historique_odm


@app.route('/', methods=['GET', 'POST'])
def redirect_login():
     
    return redirect('/login')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    print("Déconnexion de l'utilisateur")
    logout_user()  # Déconnecter l'utilisateur
    session.clear()
    flash('Vous êtes maintenant déconnecté.', 'success')
    return render_template('logout.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = ConfigForm()
    if request.method == 'POST':
        print("POST data reçues :", request.form.to_dict())
        print("Form validation :", form.validate())
        print("Erreurs du formulaire :", form.errors)
    if form.validate_on_submit():
        # Traitement de la soumission du formulaire
        user = form.user_username.data
        BDD = Requete_BDD()
        redirection = BDD.register()

        if redirection == 1:
            # Récupérer l'utilisateur à partir de la base de données
            user_data = BDD.get_user_by_username(user)
            if user_data:
                # Créer un objet User et connecter l'utilisateur
                user_obj = utilisateur(id=user_data[0], username=user_data[1], role=user_data[3])
                login_user(user_obj)
                flash('Connexion réussie !', 'success')
                print(session)
                return redirect('/view_bdd')
            else:
                flash("Utilisateur non trouvé", "error")
                return redirect(url_for('login'))
        
        elif redirection == 2 :
            flash("Identifiant erroné", "error")  # Affiche un message d'erreur
            return redirect(url_for('login'))
    
    return render_template('login.html', form=form)




@app.route('/view_bdd', methods=['GET', 'POST'])
@login_required  # Ajout de la protection par login
def view_bdd():
    # Initialisation par défaut
    data = []
    column_names = []
    requete = Requete_BDD()
    
    # Récupération de la sélection (POST ou GET)
    if request.method == 'POST':
        selection = request.form.get('choix')
        filtre_colonne = request.form.get('filtre_colonne', '')
        filtre_valeur = request.form.get('filtre_valeur', '').strip()
        tri_colonne = request.form.get('tri_colonne', '')
        tri_ordre = request.form.get('tri_ordre', 'asc')
    else:
        selection = request.args.get('choix', 'Personnes')
        filtre_colonne = request.args.get('filtre_colonne', '')
        filtre_valeur = request.args.get('filtre_valeur', '').strip()
        tri_colonne = request.args.get('tri_colonne', '')
        tri_ordre = request.args.get('tri_ordre', 'asc')
        
    # Récupérer les données selon la sélection avec un dictionnaire
    table_functions = {
        'Personnes': requete.afficher_personne,
        'Chantiers': requete.afficher_chantier,
        'Usines': requete.afficher_usine,
        'Agences': requete.afficher_agence
    }
    
    # Utiliser la fonction appropriée ou une valeur par défaut
    if selection in table_functions:
        data, column_names = table_functions[selection]()
    else:
        # Valeur par défaut si la sélection n'est pas valide
        data, column_names = requete.afficher_personne()
        selection = 'Personnes'
    
    # Définition des mappages de noms personnalisés par type de table
    column_mappings = {
        'Personnes': {
            'id_personne': 'ID',
            'nom': 'Nom',
            'prenom': 'Prénom',
            'matricule': 'Matricule',
            'email': 'Email',
            'telephone': "Téléphone",
            'immatriculation' : 'Immatriculation',
            'adresse': 'Adresse',
            'code_postal': 'Code postal',
            'ville': 'Ville',
            'pays': 'Pays',
            'fonction': 'Fonction',
            'charge_affaires': "Chargé d'affaires",
            'agence': 'Agence',
            'role' : 'Rôle'
        },
        'Chantiers': {
            'id_chantier': 'ID',
            'entreprise_client': 'Entreprise Client',
            'code_affaire': 'Code Affaire',
            'usine': 'Usine',
            'contact': 'Contact',
            'adresse': 'Adresse',
        },
        'Usines': {
            'id_usine': 'ID',
            'entreprise_usine': 'Entreprise Usine',
        },
        'Agences': {
            'id_agence': 'ID',
        }
    }
    
    # Récupérer le mappage pour la sélection actuelle
    current_mapping = column_mappings.get(selection, {})
    
    # Créer la liste des noms d'affichage
    display_names = []
    for col in column_names:
        # Utiliser le nom personnalisé s'il existe, sinon utiliser le nom original
        display_names.append(current_mapping.get(col, col))
    
    # Créer un mappage inverse pour les opérations de filtre et de tri
    reverse_mapping = {original: displayed for original, displayed in zip(column_names, display_names)}
    
    # Trouver la colonne originale correspondant au filtre/tri si nécessaire
    if filtre_colonne:
        filtre_colonne_original = next((original for original, displayed in reverse_mapping.items() 
                               if displayed == filtre_colonne), filtre_colonne)
    else:
        filtre_colonne_original = filtre_colonne
        
    if tri_colonne:
        tri_colonne_original = next((original for original, displayed in reverse_mapping.items() 
                               if displayed == tri_colonne), tri_colonne)
    else:
        tri_colonne_original = tri_colonne
    
    # Appliquer le filtre si nécessaire
    if filtre_colonne_original and filtre_valeur and filtre_colonne_original in column_names:
        col_index = column_names.index(filtre_colonne_original)
        data = [row for row in data if filtre_valeur.lower() in str(row[col_index]).lower()]
    
    # Appliquer le tri si nécessaire
    if tri_colonne_original and tri_colonne_original in column_names:
        col_index = column_names.index(tri_colonne_original)
        # Gestion du tri en fonction du type de données
        try:
            # Essayer de convertir en nombre pour un tri numérique
            data = sorted(data, key=lambda x: float(str(x[col_index]).replace(',', '.'))
                         if x[col_index] is not None and str(x[col_index]).replace(',', '.').replace('.', '', 1).isdigit()
                         else float('-inf'), reverse=(tri_ordre == 'desc'))
        except (ValueError, TypeError):
            # Tri par texte si la conversion numérique échoue
            data = sorted(data, key=lambda x: str(x[col_index]).lower() if x[col_index] is not None else '',
                         reverse=(tri_ordre == 'desc'))
    
    return render_template(
        'view_bdd.html',
        data=data,
        column_names=display_names,
        original_column_names=column_names,
        selection=selection,
        filtre_colonne=filtre_colonne,
        filtre_valeur=filtre_valeur,
        tri_colonne=tri_colonne,
        tri_ordre=tri_ordre
    )



@app.route('/add_user', methods=['GET', 'POST'])
@login_required  # Ajout de la protection par login
def add_user():
    if not current_user.is_authenticated:
        flash("Vous devez être connecté pour accéder à cette page", "danger")
        return redirect(url_for('login'))

    if not current_user.admin():  # Utilisation correcte
        flash("Accès refusé : vous n'êtes pas administrateur", "danger")
        return redirect(url_for('view_bdd'))

    form = ConfigFormnewUser(user_utilisateur='', user_password='', user_password2='',admin='')
    if form.validate_on_submit():
        BDD = Requete_BDD()
        BDD.insert_user()
        return redirect('/gestion_user')
    else:
        print("Formulaire non validé")
        for field, errors in form.errors.items():
            for error in errors:
                print(f"Erreur sur {field}: {error}")

     
    return render_template('add_user.html', form=form)

from datetime import datetime

# Définir un filtre pour formater les dates
@app.template_filter('date')
def format_date(value, format='%d-%m-%Y %H:%M'):
    if isinstance(value, datetime.datetime):
        return value.strftime(format)
    return value    


@app.route('/view_odm')
@login_required
def view_odm():
    odm = historique_odm()
    
    # Récupérer les fichiers Excel et PDF
    excel_files = odm.get_files(odm.odm_directory_excel)
    pdf_files = odm.get_files(odm.odm_directory_pdf)

    # Fusionner les listes pour un tri commun
    all_files = excel_files + pdf_files

    # Générer une liste unique d'années pour le filtre
    years = sorted(set(file['year'] for file in all_files if file['year']), reverse=True)

    # Filtrage par année, mois et type (paramètres GET)
    selected_year = request.args.get('year', 'all')
    selected_month = request.args.get('month', 'all')
    selected_type = request.args.get('type', 'all')

    filtered_files = [
        file for file in all_files
        if (selected_year == "all" or file['year'] == selected_year) and
           (selected_month == "all" or file['month'] == selected_month) and
           (selected_type == "all" or file['type'] == selected_type)
    ]

    return render_template('view_odm.html', files=filtered_files, years=years, selected_year=selected_year, selected_month=selected_month, selected_type=selected_type)

@app.route('/delete_file', methods=['POST'])
@login_required
def delete_file():
    # Récupérer le chemin du fichier à supprimer
    file_path = request.form['file_path']
    if os.path.exists(file_path):
        os.remove(file_path)  # Supprimer le fichier
    return redirect(url_for('view_odm'))  # Rediriger vers la page des ODM après la suppression


@app.route('/download/<folder>/<filename>')
@login_required
def download_file(folder, filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Dossier "app"
    
    # Vérifier si le dossier est valide (odm_excel ou odm_pdf)
    if folder not in ['odm_excel', 'odm_pdf']:
        return "Dossier invalide", 400  # Mauvaise requête
    
    file_path = os.path.join(base_dir, folder, filename)

    # Vérifier si le fichier existe avant d'essayer de l'envoyer
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "Fichier introuvable", 404  # Not found
    





@app.route('/gestion_user', methods=['GET', 'POST'])
def gestion_user():
    if not current_user.is_authenticated:
        flash("Vous devez être connecté pour accéder à cette page", "error")
        return redirect(url_for('login'))

    if not current_user.admin():  # Utilisation correcte
        flash("Accès refusé : vous n'êtes pas administrateur", "error")
        return redirect(url_for('view_bdd'))

    requete = Requete_BDD()
    data, column_names = requete.afficher_user()

    return render_template('gestion_user.html', data=data, column_names=column_names)


@app.route('/add_Personnes', methods=['GET', 'POST'])
@login_required  # Ajout de la protection par login
def add_Personnes():
    bdd = Requete_BDD()
    
    # Si le formulaire est soumis, récupérer la sélection depuis le formulaire
    if request.method == 'POST':
        selection = request.form.get('choix')
        print(f"POST reçu avec selection: {selection}")
        print(f"Données du formulaire: {request.form}")
        
        # Créer le bon type de formulaire selon la sélection
        if selection == 'technicien':
            form = ConfigFormnewTech()
            form.tech_agence.choices = bdd.liste_agence()
            form.tech_charge_affaires.choices = bdd.liste_charge()
            
            # Si le formulaire est validé
            if 'submit' in request.form and form.validate_on_submit():
                bdd.insert_tech(form)
                flash("Technicien inséré dans la base de données")
                return redirect(url_for('view_bdd'))
                
        elif selection == 'charge_affaires':
            form = ConfigFormnewCharge()
            form.charge_agence.choices = bdd.liste_agence()
            
            # Si le formulaire est validé
            if 'submit' in request.form and form.validate_on_submit():
                bdd.insert_charge(form)
                flash("Chargé d'affaires inséré dans la base de données")
                return redirect(url_for('view_bdd'))
                
        elif selection == 'client':
            form = ConfigFormnewClient()
            
            # Si le formulaire est validé
            if 'submit' in request.form and form.validate_on_submit():
                bdd.insert_client(form)
                flash("Client inséré dans la base de données")
                return redirect(url_for('view_bdd'))
            
        elif selection == 'contact_spie':
            form = ConfigFormnewContactSpie()
             
            # Si le formulaire est validé
            if 'submit' in request.form and form.validate_on_submit():
                bdd.insert_contactspie(form)
                flash("Contact Spie inséré dans la base de données")
                return redirect(url_for('view_bdd'))
            
        else:
            form = ConfigFormnewTech()
            form.tech_agence.choices = [('', 'Sélectionnez une agence')]
            form.tech_charge_affaires.choices = [('', 'Sélectionnez un chargé d\'affaires')]
    else:
        # GET request - formulaire vide par défaut
        selection = None
        form = ConfigFormnewTech()
        form.tech_agence.choices = [('', 'Sélectionnez une agence')]
        form.tech_charge_affaires.choices = [('', 'Sélectionnez un chargé d\'affaires')]

    return render_template('add_Personnes.html', form=form, selection=selection)

    


@app.route('/add_Chantiers', methods=['GET', 'POST'])
@login_required  # Ajout de la protection par login
def add_Chantiers():
    BDD = Requete_BDD()
    form = ConfigFormnewChantier()
    form.chantier_id_usine.choices = BDD.liste_usine()
    form.chantier_contact.choices = BDD.liste_contact()
    if form.validate_on_submit():
        BDD.insert_chantier()
        BDD.insert_affecter()
        return redirect(url_for('view_bdd', choix='Chantiers'))
     
    return render_template('add_Chantiers.html', form=form)


@app.route('/add_Usines', methods=['GET', 'POST'])
@login_required  # Ajout de la protection par login
def add_Usines():
    BDD = Requete_BDD()
    form = ConfigFormnewUsine()
    if form.validate_on_submit():
        BDD.insert_usine()
        return redirect(url_for('view_bdd', choix='Usines'))
     
    return render_template('add_Usines.html', form=form)

@app.route('/add_Agences', methods=['GET', 'POST'])
@login_required  # Ajout de la protection par login
def add_Agences():
    BDD = Requete_BDD()
    form = ConfigFormnewAgence()
    if form.validate_on_submit():
        BDD.insert_agence()
        return redirect(url_for('view_bdd', choix='Agences'))
     
    return render_template('add_Agences.html', form=form)



@app.route('/delete_item/<type>/<int:id>', methods=['POST'])
@login_required  # Ajout de la protection par login
def delete_item(type, id):
    bdd = Requete_BDD()
    if type == "Personnes":
        bdd.delete_personne(id)
    elif type == "Chantiers":
        bdd.delete_chantier(id)
    elif type == "Usines":
        bdd.delete_usine(id)
    elif type == "Agences":
        bdd.delete_agence(id)
    else:
        flash("Type inconnu, suppression impossible", "error")
        return redirect(url_for('view_bdd'))
    
    flash(f"{type[:-1]} supprimé avec succès", "success")
    # Rediriger vers view_bdd avec le paramètre 'choix' pour conserver la sélection
    return redirect(url_for('view_bdd', choix=type))

@app.route('/edit/<string:type>/<int:id>', methods=['GET', 'POST'])
@login_required  # Ajout de la protection par login
def edit_item(type, id):
    print(f"Tentative de modification : Type={type}, ID={id}")
    bdd = Requete_BDD()
    selection = None  # Initialisation de selection
    print(type)
    if type == "Personnes":
        # Récupérer les données de la personne
        data = bdd.get_personne_by_id(id)
        

        
        # Déterminer le type de personne à partir du rôle
        if data:
            role_id = data[11]
            print(role_id)
            # Convertir role_id en type de personne
            if role_id == 1:
                selection = "technicien"
                form = ConfigFormnewTech()
                form.tech_agence.choices = bdd.liste_agence()
                ville_agence=bdd.get_ville_agence_by_id(data[12])
                form.tech_charge_affaires.choices = bdd.liste_charge()
            elif role_id == 2:
                selection = "charge_affaires"
                form = ConfigFormnewCharge()
                form.charge_agence.choices = bdd.liste_agence()
                ville_agence=bdd.get_ville_agence_by_id(data[12])
            elif role_id == 3:
                selection = "client"
                form = ConfigFormnewClient() 
            elif role_id == 4:
                selection = "contact_spie"
                form = ConfigFormnewContactSpie()  
            else:
                flash("Type de personne invalide", "danger")
                return redirect(url_for('view_bdd'))
        else:
            flash("Personne non trouvée", "danger")
            return redirect(url_for('view_bdd'))
        
        template = 'edit_personne.html'
        
        # Si nous recevons un choix du formulaire de sélection
        if "choix" in request.form:
            selection = request.form["choix"]
            # Rediriger pour réinitialiser le formulaire avec le nouveau choix
            return redirect(url_for('edit_item', type=type, id=id))
            
        # Remplir le formulaire avec les données
        if data and request.method == 'GET':
            # Remplir selon le type de personne
            if selection == "technicien":
                form.tech_nom.data = data[1]          # nom (colonne 1)
                form.tech_prenom.data = data[2]       # prenom (colonne 2)
                form.tech_matricule.data = data[3]    # matricule (colonne 3)
                form.tech_telephone.data = data[4]    # telephone (colonne 4)
                form.tech_immatriculation.data = data[5]  # immatriculation (colonne 5)
                form.tech_adresse.data = data[6]      # adresse (colonne 6)
                form.tech_code_postal.data = data[7]  # code_postal (colonne 7)
                form.tech_ville.data = data[8]        # ville (colonne 8)
                form.tech_charge_affaires.data = data[9]  # charge_affaires (colonne 9)
                form.tech_email.data = data[10]       # email (colonne 10)
                form.tech_agence.data = ville_agence # id_agence (colonne 12)
                

            elif selection == "charge_affaires":
                form.charge_nom.data = data[1]          # nom (colonne 1)
                form.charge_prenom.data = data[2]       # prenom (colonne 2)
                form.charge_matricule.data = data[3]    # matricule (colonne 3)
                form.charge_telephone.data = data[4]    # telephone (colonne 4)
                form.charge_immatriculation.data = data[5]  # immatriculation (colonne 5)
                form.charge_adresse.data = data[6]      # adresse (colonne 6)
                form.charge_code_postal.data = data[7]  # code_postal (colonne 7)
                form.charge_ville.data = data[8]        # ville (colonne 8)
                form.charge_email.data = data[10]       # email (colonne 10)
                form.charge_agence.data = ville_agence # id_agence (colonne 12)

            elif selection == "client":
                form.client_nom.data = data[1]          # nom (colonne 1)
                form.client_prenom.data = data[2]       # prenom (colonne 2)
                form.client_telephone.data = data[4]    # telephone (colonne 4)
                form.client_email.data = data[10]       # email (colonne 10)

            elif selection == "contact_spie":
                form.contactspie_nom.data = data[1]          # nom (colonne 1)
                form.contactspie_prenom.data = data[2]       # prenom (colonne 2)
                form.contactspie_telephone.data = data[4]    # telephone (colonne 4)
                form.contactspie_email.data = data[10]       # email (colonne 10)
                
    elif type == "Chantiers":
        data = bdd.get_chantier_by_id(id)
        form = ConfigFormnewChantier()
        form.chantier_id_usine.choices = bdd.liste_usine()
        form.chantier_contact.choices = bdd.liste_contact()
        template = 'edit_chantier.html'
        
        if data and request.method == 'GET':
            form.chantier_entreprise_client.data = data[1]
            form.chantier_code_affaire.data = data[2]
            form.chantier_id_usine.data = data[3]
            
    elif type == "Usines":
        data = bdd.get_usine_by_id(id)
        form = ConfigFormnewUsine()
        template = 'edit_usine.html'
        
        if data and request.method == 'GET':
            form.usine_entreprise.data = data[1]
            form.usine_adresse.data = data[2]
            form.usine_code_postal.data = data[3]
            form.usine_ville.data = data[4]
            
    elif type == "Agences": 
        data = bdd.get_agence_by_id(id)
        form = ConfigFormnewAgence()
        template = 'edit_agence.html'
        
        if data and request.method == 'GET':
            form.agence_ville.data = data[1]
            
    else:
        flash("Type invalide", "danger")
        return redirect(url_for('view_bdd'))
    
    # Si le formulaire est soumis et valide
    if form.validate_on_submit():
        if type == "Personnes":
            if selection == "technicien":
                bdd.update_technicien(id, form)
            if selection == "charge_affaires":
                bdd.update_charge(id, form)
            if selection == "client":
                bdd.update_client(id, form)
            if selection == "contact_spie":
                print
                bdd.update_contact(id, form)
        elif type == "Chantiers":
            bdd.update_chantier(id, form)
            bdd.update_affecter(id, form)
        elif type == "Usines":
            bdd.update_usine(id, form)
        elif type == "Agences":
            bdd.update_agence(id, form)
        flash("Modification enregistrée", "success")
        return redirect(url_for('view_bdd'))
    else:
        if request.method == 'POST':  # Afficher l'erreur uniquement si le formulaire a été soumis
            print("Erreur de validation :", form.errors)
            flash("Erreur de validation du formulaire", "danger")  # Message d'erreur
        
        
    # Rendre le template approprié
    return render_template(template, form=form, type=type, selection=selection)




@app.route('/delete_utilisateur/<string:id_utilisateur>', methods=['GET', 'POST'])
@login_required  # Ajout de la protection par login
def delete_utilisateur(id_utilisateur):
    BDD = Requete_BDD()
    BDD.delete_utilisateur(id_utilisateur)

    # Redirection après suppression
    return redirect('/gestion_user') 



@app.route('/get_chantiers/<usine>', methods=['GET'])
@login_required  # Ajout de la protection par login
def get_chantiers(usine):
    BDD = Requete_BDD()
    try:
        # Sépare ville et chantier
        usine_entreprise, usine_ville = usine.split(" ", 1)
        liste_chantiers = BDD.liste_chantier(usine_entreprise, usine_ville)
        return jsonify({"chantiers": [('' '')] + liste_chantiers})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    


@app.route('/create_odm', methods=['GET', 'POST'])
@login_required  # Ajout de la protection par login
def create_odm():
    user = session.get('user')
    
    BDD = Requete_BDD()
    form = Recherche_BDD_ODM()
    gps = class_gps()

    # Récupérer la liste des noms et prénoms
    liste_nom_complet = BDD.liste_nom_complet()
    
    # Configurer les choix pour afficher "Nom Prénom"
    form.nom_recherche.choices = [('', '')] + liste_nom_complet

    # Gestion liste usines
    liste_usines = BDD.liste_usine()
    form.usine_recherche.choices = [('', '')] + [(usine, usine) for usine in liste_usines]

    if request.method == 'POST':
        nom = form.nom_recherche.data  
        usine = form.usine_recherche.data
        # Séparer l'entreprise et la ville
        usine_entreprise, usine_ville = usine.split(" ", 1)
        liste_chantiers=BDD.liste_chantier(usine_entreprise,usine_ville)
        form.chantier_recherche.choices = [(liste_chantier, liste_chantier) for liste_chantier in liste_chantiers]

   
    if form.validate_on_submit():
        nom = form.nom_recherche.data  
        usine = form.usine_recherche.data
        # Séparer l'entreprise et la ville
        usine_entreprise, usine_ville = usine.split(" ", 1)
        
        prenom = BDD.liste_prenom(nom)
        matricule = BDD.matricule(nom)
        immatriculation=BDD.immatriculation(nom)
        ville=BDD.ville(matricule)
        charge = BDD.charge(nom)

        id_usine = BDD.id_usine(usine_entreprise, usine_ville)
        
        nom_charge = charge
        
        adresse = BDD.adresse(nom)
        mail_charge = BDD.mail_charge(nom_charge)
        num_charge = BDD.telephone_charge(nom_charge)
        adresse_usines = BDD.adresse_usine(nom_charge)


        date_debut = form.date_debut.data
        date_fin = form.date_fin.data
        mission = form.mission.data

        # Formatage des dates
        date_debut_formatee = date_debut.strftime("%d/%m/%Y")
        date_fin_formatee = date_fin.strftime("%d/%m/%Y")
        client = form.chantier_recherche.data  
     
        
        affaire=BDD.code_affaire(client,id_usine)
        id_chantier=BDD.id_chantier(affaire)
        adresse_usine=BDD.adresse_usine(client)
        id_personne_client=BDD.id_personne_client(id_chantier)
        contact=BDD.nom_contact(id_personne_client)
        telephone_contact=BDD.telephone_contact(id_personne_client)
        email_contact=BDD.email_contact(id_personne_client)

        #calcul de la zone de déplacement
        distance = gps.calculate_distance(usine_ville, ville)
        zone=gps.calcul_zone(distance)

        # Stockage dans la session
        session['usine_entreprise'] = usine_entreprise
        session['usine_ville'] = usine_ville
        session['id_usine'] = id_usine 
        session['usine'] = usine
        session['nom'] = nom
        session['prenom'] = prenom
        session['nom_complet'] = liste_nom_complet
        session['matricule'] = matricule
        session['immatriculation'] = immatriculation
        session['charge'] = charge
        session['adresse'] = adresse
        session['mail_charge'] = mail_charge
        session['telephone_charge'] = num_charge
        session['adresse_usine'] = adresse_usines
        session['id_chantier'] = id_chantier
        session['client'] = client
        session['affaire'] = affaire
        session['adresse_usine'] = adresse_usine
        session['contact'] = contact
        session['date_debut'] = date_debut_formatee
        session['date_fin'] = date_fin_formatee
        session['mission'] = mission
        session['telephone_contact'] = telephone_contact
        session['email_contact'] = email_contact
        session['zone'] = zone


        return redirect(url_for('download_pdf'))
    
    print("Erreurs du formulaire :", form.errors)  # Débogage

    return render_template('create_odm.html', 
                         form=form,
                         user=user)


@app.route('/download_pdf')
@login_required # Ajout de la protection par login
def download_pdf():
    # Récupération des données de session
    required_keys = [
        'nom', 'prenom', 'usine', 'client', 'contact', 'telephone_contact',
        'email_contact', 'date_debut', 'date_fin', 'matricule', 'charge',
        'adresse', 'mail_charge', 'telephone_charge', 'affaire',
        'adresse_usine', 'mission', 'immatriculation', 'zone'
    ]
    # Vérification que toutes les clés de session sont présentes
    for key in required_keys:
        if key not in session:
            return f"Donnée manquante dans la session : {key}", 400
            
    # Récupération des valeurs de session
    nom = session.get('nom')
    prenom = session.get('prenom')
    date_debut = session.get('date_debut')
    date_fin = session.get('date_fin')
    affaire = session.get('affaire')
    
    # Formater les dates pour le nom de fichier (remplacer les / par des -)
    date_debut_formatted = date_debut.replace('/', '-')
    date_fin_formatted = date_fin.replace('/', '-')
    
    # Chemins dynamiques
    base_dir = os.path.dirname(os.path.abspath(__file__))
    excel_template_path = os.path.join(base_dir, "formulaire.xlsx")  # Chemin vers le modèle Excel
    odm_pdf_dir = os.path.join(base_dir, "odm_pdf")  # Dossier de sortie pour les PDF
    odm_excel_dir = os.path.join(base_dir, "odm_excel")  # Dossier de sortie pour les Excel
    
    # Création des dossiers de sortie s'ils n'existent pas
    os.makedirs(odm_pdf_dir, exist_ok=True)
    os.makedirs(odm_excel_dir, exist_ok=True)
    
    # Nom de fichier basé sur les informations de session (avec dates formatées)
    file_basename = f"ODM_{prenom}_{nom}_{date_debut_formatted}_{date_fin_formatted}_{affaire}"
    excel_filename = f"{file_basename}.xlsx"
    pdf_filename = f"{file_basename}.pdf"
    
    # Chemin complet pour les nouveaux fichiers
    excel_output_path = os.path.join(odm_excel_dir, excel_filename)
    
    # Génération de l'Excel et du PDF
    excel = Excel()
    try:
        # Copier d'abord le modèle Excel vers le nouveau fichier dans odm_excel
        shutil.copy2(excel_template_path, excel_output_path)
        
        # Appel de la méthode Comp_Excel avec les données de session et le nouveau chemin Excel
        excel.Comp_Excel(
            session['nom'], session['prenom'], session['usine'], session['client'],
            session['contact'], session['telephone_contact'], session['email_contact'],
            session['date_debut'], session['date_fin'], session['matricule'],
            session['charge'], session['adresse'], session['mail_charge'],
            session['telephone_charge'], session['affaire'], session['adresse_usine'],
            session['mission'], session['immatriculation'], session['zone'],
            excel_output_path  # Passer le nouveau chemin d'Excel
        )
        
        # Conversion en PDF directement dans le dossier odm_pdf
        pdf_path = excel.PDF(excel_output_path, odm_pdf_dir)
        
        # Vérification que le chemin du PDF est valide
        if pdf_path is None:
            return "Erreur : le chemin du fichier PDF n'a pas été généré.", 500
            
        # Vérification que le fichier PDF existe
        if not os.path.isfile(pdf_path):
            return "Erreur : le fichier PDF n'a pas été généré ou n'est pas accessible.", 500
            
        # Envoi du fichier PDF pour téléchargement
        return send_file(pdf_path, download_name=pdf_filename, as_attachment=True)
        
    except Exception as e:
        # Gestion des erreurs
        print(f"Erreur lors de la génération du PDF : {str(e)}")
        return f"Erreur lors de la génération du PDF : {str(e)}", 500


@app.route('/droits', methods=['GET', 'POST'])
@login_required  # Ajout de la protection par login
def droits():
    form = ConfigFormDroits(user_username='', droit_admin='')
    if form.validate_on_submit():
        BDD = Requete_BDD()
        BDD.droit_admin()
        return redirect('/fields_admin')
     
    return render_template('droits.html', form=form)

