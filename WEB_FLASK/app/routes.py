from flask import render_template, request, redirect, url_for, session, send_file, flash, jsonify
from flask_login import LoginManager
from app import app
from app.forms import *
from app.requete import Requete_BDD
from app.excel import Excel
from datetime import datetime
import os

#BDD = Requete_BDD()
#BDD.connexion()

@app.route('/', methods=['GET', 'POST'])
def redirect_login():
     
    return redirect('/login')



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
        if redirection == 1 :
            session['user'] = user
            return redirect('/view_bdd')
        if redirection == 2 :
            flash("Identifiant erroné", "error")  # Affiche un message d'erreur
            return redirect(url_for('login'))
    return render_template('login.html', form=form)




@app.route('/view_bdd', methods=['GET', 'POST'])
def view_bdd():
    # Initialisation par défaut
    selection = None
    data = []
    column_names = []
    requete = Requete_BDD()
    
    if request.method == 'POST':
        selection = request.form.get('choix')
    elif request.method == 'GET':
        selection = request.args.get('choix')  # Récupérer le paramètre choix de l'URL
    
    # Si aucune sélection n'est définie, utiliser 'Personnes' par défaut
    if selection is None or selection == '':
        selection = 'Personnes'
        
    # Récupérer les données selon la sélection
    if selection == 'Personnes':
        data, column_names = requete.afficher_personne()
    elif selection == 'Chantiers':
        data, column_names = requete.afficher_chantier()
    elif selection == 'Usines':
        data, column_names = requete.afficher_usine()
    elif selection == 'Agences':
        data, column_names = requete.afficher_agence()
        
    return render_template('view_bdd.html', data=data, column_names=column_names, selection=selection)




@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
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



@app.route('/gestion_user', methods=['GET', 'POST'])
def gestion_user():

    
    requete = Requete_BDD()
    data, column_names = requete.afficher_user()

    return render_template('gestion_user.html', data=data, column_names=column_names)


@app.route('/add_Personnes', methods=['GET', 'POST'])
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
def add_Usines():
    BDD = Requete_BDD()
    form = ConfigFormnewUsine()
    if form.validate_on_submit():
        BDD.insert_usine()
        return redirect(url_for('view_bdd', choix='Usines'))
     
    return render_template('add_Usines.html', form=form)

@app.route('/add_Agences', methods=['GET', 'POST'])
def add_Agences():
    BDD = Requete_BDD()
    form = ConfigFormnewAgence()
    if form.validate_on_submit():
        BDD.insert_agence()
        return redirect(url_for('view_bdd', choix='Agences'))
     
    return render_template('add_Agences.html', form=form)



@app.route('/delete_item/<type>/<int:id>', methods=['POST'])
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
                form.tech_charge_affaires.choices = bdd.liste_charge()
            elif role_id == 2:
                selection = "charge_affaires"
                form = ConfigFormnewCharge()
                form.charge_agence.choices = bdd.liste_agence()
            elif role_id == 3:
                selection = "client"
                form = ConfigFormnewClient()  # Assurez-vous d'avoir cette classe
            elif role_id == 4:
                selection = "contact_spie"
                form = ConfigFormnewContactSpie()  # Assurez-vous d'avoir cette classe
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
            print(selection)
            print(selection)
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
                form.tech_agence.data = data[12] # id_agence (colonne 12)

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
                form.charge_agence.data = data[12] # id_agence (colonne 12)

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
        template = 'edit_chantier.html'
        
        if data and request.method == 'GET':
            form.chantier_entreprise_client.data = data[1]
            form.chantier_code_affaire.data = data[2]
            form.chantier_id_usine.data = str(data[3])
            form.chantier_contact.data = str(data[4])
            
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
        print("1111111111111")
        if type == "Personnes":
            bdd.update_personne(id, form)
        elif type == "Chantiers":
            bdd.update_chantier(id, form)
        elif type == "Usines":
            bdd.update_usine(id, form)
        elif type == "Agences":
            bdd.update_agence(id, form)
        
        flash("Modification enregistrée", "success")
        return redirect(url_for('view_bdd'))
    
    # Rendre le template approprié
    return render_template(template, form=form, type=type, selection=selection)




@app.route('/delete_utilisateur/<string:id_utilisateur>', methods=['GET', 'POST'])
def delete_utilisateur(id_utilisateur):
    BDD = Requete_BDD()
    BDD.delete_utilisateur(id_utilisateur)

    # Redirection après suppression
    return redirect('/gestion_user') 



@app.route('/get_chantiers/<usine>', methods=['GET'])
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
def create_odm():
    user = session.get('user')
    
    BDD = Requete_BDD()
    form = Recherche_BDD_ODM()

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

        return redirect(url_for('download_pdf'))
    
    print("Erreurs du formulaire :", form.errors)  # Débogage

    return render_template('create_odm.html', 
                         form=form,
                         user=user)


@app.route('/view_odm', methods=['GET', 'POST'])
def view_odm():
 
     
    return render_template('view_odm.html')

@app.route('/creation_odm2', methods=['GET', 'POST'] ) # decorators
def ODM2():
    user = session.get('user')
    BDD = Requete_BDD()
    form = Recherche_BDD_ODM()

    prenom = session.get('prenom')
    usine = session.get('usine')
    nom = session.get('nom')
    usine_entreprise = session.get('usine_entreprise')
    usine_ville = session.get('usine_ville')
    id_usine = session.get('id_usine')
   
    adresse_usine = session.get('adresse usine')

    
    #gestion liste clients
    liste_chantiers=BDD.liste_chantier(usine_entreprise,usine_ville)
    form.chantier_recherche.choices = [(liste_chantier, liste_chantier) for liste_chantier in liste_chantiers]

    if form.validate_on_submit():

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
        contact=BDD.liste_contact(id_personne_client)


        session['id_chantier'] = id_chantier
        session['client'] = client
        session['affaire'] = affaire
        session['adresse_usine'] = adresse_usine
        session['contact'] = contact
        session['date_debut'] = date_debut_formatee
        session['date_fin'] = date_fin_formatee
        session['mission'] = mission
    

        return render_template('/creation_odm3.html', form=form)
    
    
    return render_template('creation_odm2.html', form=form, user=user,liste_chantier=liste_chantiers, nom=nom, prenom=prenom, usine=usine )


@app.route('/creation_odm3', methods=['GET', 'POST'] ) # decorators
def ODM3():
    user = session.get('user')

        
    return render_template('creation_odm3.html')


@app.route('/download_pdf')
def download_pdf():
    # Récupération des données de session
    required_keys = [
        'nom', 'prenom', 'usine', 'client', 'contact', 'telephone_contact', 
        'email_contact', 'date_debut', 'date_fin', 'matricule', 'charge', 
        'adresse', 'mail_charge', 'telephone_charge', 'affaire', 
        'adresse_usine', 'mission', 'immatriculation'
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

    # Chemins dynamiques
    base_dir = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(base_dir, "formulaire.xlsx")  # Chemin vers le fichier Excel
    pdf_output_dir = os.path.join(base_dir, "pdf_output")   # Dossier de sortie pour les PDF

    # Création du dossier de sortie s'il n'existe pas
    os.makedirs(pdf_output_dir, exist_ok=True)

    # Génération de l'Excel et du PDF
    excel = Excel()
    try:
        # Appel de la méthode Comp_Excel avec les données de session
        excel.Comp_Excel(
            session['nom'], session['prenom'], session['usine'], session['client'],
            session['contact'], session['telephone_contact'], session['email_contact'], 
            session['date_debut'], session['date_fin'], session['matricule'], 
            session['charge'], session['adresse'], session['mail_charge'], 
            session['telephone_charge'], session['affaire'], session['adresse_usine'], 
            session['mission'], session['immatriculation']
        )

        # Conversion en PDF
        pdf_path = excel.PDF(excel_path, pdf_output_dir)

        # Vérification que le chemin du PDF est valide
        if pdf_path is None:
            return "Erreur : le chemin du fichier PDF n'a pas été généré.", 500

        # Vérification que le fichier PDF existe
        if not os.path.isfile(pdf_path):
            return "Erreur : le fichier PDF n'a pas été généré ou n'est pas accessible.", 500

        # Création d'un nom de fichier basé sur les informations de session
        nom_fichier = f"ODM_{prenom}_{nom}_{date_debut}_{date_fin}.pdf"

        # Envoi du fichier PDF pour téléchargement
        return send_file(pdf_path, download_name=nom_fichier, as_attachment=True)

    except Exception as e:
        # Gestion des erreurs
        print(f"Erreur lors de la génération du PDF : {str(e)}")
        return f"Erreur lors de la génération du PDF : {str(e)}", 500


@app.route('/droits', methods=['GET', 'POST'])
def droits():
    form = ConfigFormDroits(user_username='', droit_admin='')
    if form.validate_on_submit():
        BDD = Requete_BDD()
        BDD.droit_admin()
        return redirect('/fields_admin')
     
    return render_template('droits.html', form=form)

@app.route('/maquette', methods=['GET', 'POST'])
def maquette():

    return render_template('maquette.html')