from flask import render_template, request, redirect, url_for, session
from app import app
from app.forms import *
import os
from mysql.connector import Error
import mysql.connector
import openpyxl
import subprocess
from openpyxl.styles import NamedStyle
from datetime import datetime
import requests

class Requete_BDD:

    def __init__(self):
        self.mycursor = None
        self.mydb = None
        self.redirect=None

    def connexion(self):
        try:  
            self.mydb = mysql.connector.connect(
                host="localhost",
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD')
            )    
        except Error as e:
            print(f"Erreur lors de la connexion à la BDD : {e}")
        self.mycursor = self.mydb.cursor()


    def register(self):
        form = ConfigForm(user_username='', user_password='')
        if form.validate_on_submit():
            self.connexion()
            user = form.user_username.data
            password = form.user_password.data
            self.mycursor.execute("USE ODM")
            requete = "SELECT password FROM utilisateurs WHERE email = %s "
            self.mycursor.execute(requete,(user,))
            resultats = self.mycursor.fetchall()
          
            for resultat in resultats:
                if resultat[0] == password:
                    return 1
                else:
                    return 2
            else:
                return 2 



    def liste_charge(self):
        self.connexion()
        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT prenom, nom FROM personnes WHERE id_role = 2")  
              
        # Créer les options en combinant nom et prénom
        liste_charge_affaires = [(f"{row[0]} {row[1]}", f"{row[0]} {row[1]}") for row in self.mycursor.fetchall()]
        
        # Debug : imprimer les choix récupérés
        print("Options de chargés d'affaire :", liste_charge_affaires)

        return liste_charge_affaires

    def liste_agence(self):
        self.connexion()
        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT ville FROM agences")
        
        # Créer les options pour les agences
        liste_agence = [(row[0], row[0]) for row in self.mycursor.fetchall()]
        
        # Debug : imprimer les choix récupérés
        print("Options d'agences :", liste_agence)

        return liste_agence
    
    def liste_role(self):
        self.connexion()
        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT nom_role FROM roles")
        
        # Créer les options pour les agences
        liste_role = [(row[0], row[0]) for row in self.mycursor.fetchall()]

        return liste_role

    def insert_tech(self, form):
        self.connexion()
        self.mycursor.execute("USE ODM")

        # Récupération des valeurs du formulaire
        nom = form.tech_nom.data
        prenom = form.tech_prenom.data
        matricule = form.tech_matricule.data
        telephone = form.tech_telephone.data
        immatriculation = form.tech_immatriculation.data
        ville = form.tech_ville.data
        adresse = form.tech_adresse.data
        code_postal = form.tech_code_postal.data
        charge_affaires = form.tech_charge_affaires.data
        agence = form.tech_agence.data
        email = form.tech_email.data
        id_role = "1"
        # Récupération de l'identifiant de l'agence
        self.mycursor.execute("SELECT id_agence FROM agences WHERE ville=%s", (agence,))
        id_agence = self.mycursor.fetchone()
        if id_agence:
            id_agence = id_agence[0]
        else:
            print("Erreur : Aucune agence trouvée pour la ville", agence)
            return  # Stopper l'insertion

        # Insertion des données dans la table `personnes`
        new = """
            INSERT INTO personnes 
            (nom, prenom, matricule, telephone, immatriculation, adresse, code_postal, ville, charge_affaires, email, id_role, id_agence) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        val = (nom, prenom, matricule, telephone, immatriculation, adresse, code_postal, ville, charge_affaires, email, id_role, id_agence)
        
        try:
            self.mycursor.execute(new, val)
            self.mydb.commit()
            print("Nouvelle entrée insérée avec succès.")
        except Exception as e:
            print("Erreur lors de l'insertion :", e)
            self.mydb.rollback()




    def insert_charge(self, form):
        self.connexion()
        self.mycursor.execute("USE ODM")

        # Récupération des valeurs du formulaire
        nom = form.charge_nom.data
        prenom = form.charge_prenom.data
        matricule = form.charge_matricule.data
        telephone = form.charge_telephone.data
        immatriculation = form.charge_immatriculation.data
        ville = form.charge_ville.data
        adresse = form.charge_adresse.data
        code_postal = form.charge_code_postal.data
        agence = form.charge_agence.data
        email = form.charge_email.data
        id_role = "2"
        # Récupération de l'identifiant de l'agence
        self.mycursor.execute("SELECT id_agence FROM agences WHERE ville=%s", (agence,))
        id_agence = self.mycursor.fetchone()
        if id_agence:
            id_agence = id_agence[0]
        else:
            print("Erreur : Aucune agence trouvée pour la ville", agence)
            return  # Stopper l'insertion

        # Insertion des données dans la table `personnes`
        new = """
            INSERT INTO personnes 
            (nom, prenom, matricule, telephone, immatriculation, adresse, code_postal, ville, email, id_role, id_agence) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        val = (nom, prenom, matricule, telephone, immatriculation, adresse, code_postal, ville, email, id_role, id_agence)
        
        try:
            self.mycursor.execute(new, val)
            self.mydb.commit()
            print("Nouvelle entrée insérée avec succès.")
        except Exception as e:
            print("Erreur lors de l'insertion :", e)
            self.mydb.rollback()

    def insert_client(self, form):
        self.connexion()
        self.mycursor.execute("USE ODM")

        # Récupération des valeurs du formulaire
        nom = form.client_nom.data
        prenom = form.client_prenom.data
        telephone = form.client_telephone.data
        email = form.client_email.data
        id_role = "3"

        # Insertion des données dans la table `personnes`
        new = "INSERT INTO personnes (`nom`, `prenom`, `telephone`, `email`, `id_role`) VALUES (%s, %s, %s, %s, %s)"
        val = (nom, prenom, telephone, email, id_role)
        
        try:
            self.mycursor.execute(new, val)
            self.mydb.commit()
            print("Nouvelle entrée insérée avec succès.")
        except Exception as e:
            print("Erreur lors de l'insertion :", e)
            self.mydb.rollback()

    def insert_contactspie(self, form):
        self.connexion()
        self.mycursor.execute("USE ODM")

        # Récupération des valeurs du formulaire
        nom = form.contactspie_nom.data
        prenom = form.contactspie_prenom.data
        telephone = form.contactspie_telephone.data
        email = form.contactspie_email.data
        id_role = "4"

        # Insertion des données dans la table `personnes`
        new = "INSERT INTO personnes (`nom`, `prenom`, `telephone`, `email`, `id_role`) VALUES (%s, %s, %s, %s, %s)"

        val = (nom, prenom,telephone, email, id_role)
        
        try:
            self.mycursor.execute(new, val)
            self.mydb.commit()
            print("Nouvelle entrée insérée avec succès.")
        except Exception as e:
            print("Erreur lors de l'insertion :", e)
            self.mydb.rollback()



    def insert_chantier(self):
        self.connexion()
        form = ConfigFormnewChantier(chantier_entreprise_client='', chantier_code_affaire='', chantier_id_usine='', chantier_contact='')
        entreprise_client = form.chantier_entreprise_client.data
        code_affaire = form.chantier_code_affaire.data
        usine= form.chantier_id_usine.data
        # Extraction de la ville uniquement
        ville = usine.split()[-1]

        #Récupération de l'identation (num) de l'usine sélectionnée
        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT id_usine FROM usines WHERE ville=%s", (ville,))
        id_usine = self.mycursor.fetchone()
        id_usine = id_usine[0]
        new = "INSERT INTO chantiers (entreprise_client, code_affaire, id_usine) VALUES (%s, %s, %s)"
        val = (entreprise_client, code_affaire, id_usine)
        self.mycursor.execute(new, val)
        self.mydb.commit()


    def insert_affecter(self):
        self.connexion()
        form = ConfigFormnewChantier(chantier_entreprise_client='', chantier_code_affaire='', chantier_id_usine='', chantier_contact='')

        code_affaire = form.chantier_code_affaire.data
        contact= form.chantier_contact.data

        contact_nom = contact.split()[0]

        #Récupération de l'identifiant du chantier
        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT id_chantier FROM chantiers WHERE code_affaire=%s", (code_affaire,))
        id_chantier = self.mycursor.fetchone()
        id_chantier = id_chantier[0]

        #Récupération de l'identifiant du contact client
        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT id_personne FROM personnes WHERE nom=%s", (contact_nom,))
        id_personne = self.mycursor.fetchone()
        id_personne = id_personne[0]

        new = "INSERT INTO affecter (id_personne, id_chantier) VALUES (%s, %s)"
        val = (id_personne, id_chantier)
        self.mycursor.execute(new, val)
        self.mydb.commit()

    def insert_usine(self):
        self.connexion()
        form = ConfigFormnewUsine(usine_entreprise='', usine_adresse='', usine_code_postal='', usine_ville='')
        entreprise_usine = form.usine_entreprise.data
        adresse = form.usine_adresse.data
        code_postal= form.usine_code_postal.data
        ville= form.usine_ville.data
        self.mycursor.execute("USE ODM")
        new = "INSERT INTO usines (entreprise_usine, adresse, code_postal, ville) VALUES (%s, %s, %s, %s)"
        val = (entreprise_usine, adresse, code_postal, ville)
        self.mycursor.execute(new, val)
        self.mydb.commit()

    def insert_agence(self):
        self.connexion()
        form = ConfigFormnewAgence(agence_ville='')
        ville = form.agence_ville.data

        self.mycursor.execute("USE ODM")

        # Correction : pas de guillemets autour de la colonne, et val = (ville,)
        new = "INSERT INTO agences (`ville`) VALUES (%s)"
        val = (ville,)

        try:
            self.mycursor.execute(new, val)
            self.mydb.commit()
            print("Nouvelle agence insérée avec succès.")
        except Exception as e:
            print("Erreur lors de l'insertion :", e)
            self.mydb.rollback()

    def insert_user(self):
        self.connexion()
        form = ConfigFormnewUser(user_utilisateur='', user_password='', user_password2='', admin='')
        utilisateur = form.user_utilisateur.data
        password = form.user_password.data
        admin=form.admin.data
        self.mycursor.execute("USE ODM")
        new = "INSERT INTO utilisateurs (email, password, admin) VALUES (%s, %s, %s)"
        val = (utilisateur, password, admin)
        self.mycursor.execute(new, val)
        self.mydb.commit()

    def delete_personne(self, id_personne):
        self.connexion()  # Connexion à la base de données
        
        
        self.mycursor.execute("USE ODM")
        # Suppression de la personne via son id
        self.mycursor.execute("DELETE FROM personnes WHERE id_personne = %s", (id_personne,))
        self.mydb.commit()

        # Vérifier si une ligne a été affectée par la suppression
        if self.mycursor.rowcount > 0:
            print("personne supprimée avec succès.")
        else:
            print("Aucune personne trouvé avec ces nom et prénom.")

    def delete_usine(self, id_usine):
        self.connexion()  # Connexion à la base de données
        
        
        self.mycursor.execute("USE ODM")
        # Suppression de la personne via son id
        self.mycursor.execute("DELETE FROM usines WHERE id_usine = %s", (id_usine,))
        self.mydb.commit()

    def delete_chantier(self, id_chantier):
        self.connexion()  # Connexion à la base de données
        
        
        self.mycursor.execute("USE ODM")
        # Suppression du chaniter dans affecter via son id
        self.mycursor.execute("DELETE FROM affecter WHERE id_chantier = %s", (id_chantier,))
        # Suppression du chaniter via son id
        self.mycursor.execute("DELETE FROM chantiers WHERE id_chantier = %s", (id_chantier,))
        self.mydb.commit()

    def delete_agence(self, id_agence):
        self.connexion()  # Connexion à la base de données
        
        
        self.mycursor.execute("USE ODM")
        # Suppression de la personne via son id
        self.mycursor.execute("DELETE FROM agences WHERE id_agence = %s", (id_agence,))
        self.mydb.commit()

    def delete_utilisateur(self, id_utilisateur):
        self.connexion()  # Connexion à la base de données
        
        self.mycursor.execute("USE ODM")
        # Suppression de l'utilisateur via son id
        self.mycursor.execute("DELETE FROM utilisateurs WHERE id_utilisateur = %s", (id_utilisateur,))
        self.mydb.commit()

        # Vérifier si une ligne a été affectée par la suppression
        if self.mycursor.rowcount > 0:
            print("Utilisateur supprimé avec succès.")
        else:
            print("Aucun utilisateur trouvé avec ces nom et prénom.")

    def get_personne_by_id(self, id):
        """Récupère une personne par son ID avec toutes les colonnes."""
        self.connexion()
        self.mycursor.execute("USE ODM")
        query = """
            SELECT 
                id_personne, nom, prenom, matricule, telephone, 
                immatriculation, adresse, code_postal, ville, 
                charge_affaires, email, id_role, id_agence 
            FROM personnes 
            WHERE id_personne = %s
        """
        self.mycursor.execute(query, (id,))
        return self.mycursor.fetchone()
    
    def get_chantier_by_id(self, id):
        self.connexion()
        self.mycursor.execute("USE ODM")
        query = "SELECT * FROM chantiers WHERE id_chantier = %s"
        self.mycursor.execute(query, (id,))
        result = self.mycursor.fetchone()
        return result

    def get_agence_by_id(self, id):
        self.connexion()
        self.mycursor.execute("USE ODM")
        query = "SELECT * FROM agences WHERE id_agence = %s"
        self.mycursor.execute(query, (id,))
        result = self.mycursor.fetchone()
        return result
    
    def get_ville_agence_by_id(self, id):
        self.connexion()
        self.mycursor.execute("USE ODM")
        query = "SELECT ville FROM agences WHERE id_agence = %s"
        self.mycursor.execute(query, (id,))
        result = self.mycursor.fetchone()
        result = result[0]
        return result


    def get_usine_by_id(self, id):
        self.connexion()
        self.mycursor.execute("USE ODM")
        query = "SELECT * FROM usines WHERE id_usine = %s"
        self.mycursor.execute(query, (id,))
        result = self.mycursor.fetchone()
        return result

    def update_technicien(self, id, form):
        self.connexion()

        #Récupération de l'identation (num) de l'agence spie sélectionnée
        agence= form.tech_agence.data
        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT id_agence FROM agences WHERE ville=%s", (agence,))
        id_agence = self.mycursor.fetchone()
        id_agence = id_agence[0]

        query = """
            UPDATE personnes
            SET nom = %s, prenom = %s, matricule = %s, telephone = %s, 
                immatriculation = %s, adresse = %s, code_postal = %s, ville = %s, 
                charge_affaires = %s, email = %s, id_agence = %s
            WHERE id_personne = %s
        """

        values = (
            form.tech_nom.data,
            form.tech_prenom.data,
            form.tech_matricule.data,
            form.tech_telephone.data,
            form.tech_immatriculation.data,
            form.tech_adresse.data,
            form.tech_code_postal.data,
            form.tech_ville.data,
            form.tech_charge_affaires.data,
            form.tech_email.data,
            id_agence,
            id
        )
        try:
            self.mycursor.execute(query, values)
            self.mydb.commit()
            print("Mise à jour réussie pour la personne", id)
        except Exception as e:
            print("Erreur lors de la mise à jour :", e)
            self.mydb.rollback()

    def update_charge(self, id, form):
        self.connexion()

        #Récupération de l'identation (num) de l'agence spie sélectionnée
        agence= form.charge_agence.data
        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT id_agence FROM agences WHERE ville=%s", (agence,))
        id_agence = self.mycursor.fetchone()
        id_agence = id_agence[0]

        query = """
            UPDATE personnes
            SET nom = %s, prenom = %s, matricule = %s, telephone = %s, 
                immatriculation = %s, adresse = %s, code_postal = %s, ville = %s, 
                email = %s, id_agence = %s
            WHERE id_personne = %s
        """

        values = (
            form.charge_nom.data,
            form.charge_prenom.data,
            form.charge_matricule.data,
            form.charge_telephone.data,
            form.charge_immatriculation.data,
            form.charge_adresse.data,
            form.charge_code_postal.data,
            form.charge_ville.data,
            form.charge_email.data,
            id_agence,
            id
        )
        try:
            self.mycursor.execute(query, values)
            self.mydb.commit()
            print("Mise à jour réussie pour la personne", id)
        except Exception as e:
            print("Erreur lors de la mise à jour :", e)
            self.mydb.rollback()
        
    def update_client(self, id, form):
        self.connexion()
        self.mycursor.execute("USE ODM")
        
        query = """
            UPDATE personnes
            SET nom = %s, prenom = %s, telephone = %s, email = %s
            WHERE id_personne = %s
        """

        values = (
            form.client_nom.data,
            form.client_prenom.data,
            form.client_telephone.data,
            form.client_email.data,
            id
        )
        try:
            self.mycursor.execute(query, values)
            self.mydb.commit()
            print("Mise à jour réussie pour la personne", id)
        except Exception as e:
            print("Erreur lors de la mise à jour :", e)
            self.mydb.rollback()

    def update_chantier(self, id, form):
        self.connexion()
    
        usine= form.chantier_id_usine.data
        # Extraction de la ville uniquement
        ville = usine.split()[-1]

        #Récupération de l'identation (num) de l'usine sélectionnée
        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT id_usine FROM usines WHERE ville=%s", (ville,))
        id_usine = self.mycursor.fetchone()
        id_usine = id_usine[0]

        query = """
            UPDATE chantiers 
            SET entreprise_client = %s, code_affaire = %s, id_usine = %s
            WHERE id_chantier = %s
        """
        val = (form.chantier_entreprise_client.data, form.chantier_code_affaire.data, id_usine, id)
        self.mycursor.execute(query, val)
        self.mydb.commit()


    def update_affecter(self, id, form):
        self.connexion()
      

        nom_complet= form.chantier_contact.data
        # Extraction du nom
        nom = nom_complet.split()[0]
        print(nom)
        print(nom)
        #Récupération de l'identation (num) de l'usine sélectionnée
        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT id_personne FROM personnes WHERE nom=%s", (nom,))
        id_personne = self.mycursor.fetchone()
        id_personne = id_personne[0]


        query = """UPDATE affecter SET id_personne = %s WHERE id_chantier = %s"""
        val = (id_personne, id)
        self.mycursor.execute(query, val)
        self.mydb.commit()

    def update_usine(self, id, form):
        self.connexion()
        self.mycursor.execute("USE ODM")
        query = """
            UPDATE usines 
            SET entreprise_usine = %s, adresse = %s, code_postal = %s, ville = %s 
            WHERE id_usine = %s
        """
        val = (
            form.usine_entreprise.data, form.usine_adresse.data, form.usine_code_postal.data, form.usine_ville.data, id
        )
        self.mycursor.execute(query, val)
        self.mydb.commit()

    def update_agence(self, id, form):
        self.connexion()
        self.mycursor.execute("USE ODM")
        query = "UPDATE agences SET ville = %s WHERE id_agence = %s"
        val = (form.agence_ville.data, id)
        self.mycursor.execute(query, val)
        self.mydb.commit()

        

    def droit_admin(self):
        self.connexion()
        
        form = ConfigFormDroits(user_username='', droit_admin='')
        user = form.user_username.data
        droit_admin = form.droit_admin.data
        self.mycursor.execute("USE ODM")
        update = "UPDATE personnes SET Droit_Admin = %s WHERE prenom = %s"
        val = (droit_admin, user)
        self.mycursor.execute(update, val)
        self.mydb.commit()


    def recherche(self):
        form = Recherche_BDD(user_recherche='', colonne_recherche='', prenom_recherche='') 
        self.connexion()
        recherches = form.user_recherche.data
        colonne = form.colonne_recherche.data
        self.mycursor.execute("USE ODM")
        requete= f"SELECT {colonne} FROM personnes WHERE prenom = %s"
        self.mycursor.execute(requete,(recherches,))
        resultat= self.mycursor.fetchall()
        data1 = resultat[0][0]
        return data1
      
        
    def nom_colonne(self):
        self.connexion()
        
        self.mycursor = self.mydb.cursor()
        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT * FROM personnes LIMIT 1")
        
        # Récupérer les noms des colonnes
        column_names = [i[0] for i in self.mycursor.description]
        self.mycursor.fetchall()
        return column_names
    
    def liste_nom_complet(self):
        self.connexion()
        
        self.mycursor = self.mydb.cursor()
        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT prenom, nom FROM personnes WHERE id_role = 1",)

        # Récupérer tous les résultats
        results = self.mycursor.fetchall()

        # Construire la liste de choix avec nom comme valeur et "Prénom Nom" comme étiquette
        liste_nom_complet = [(row[1], f"{row[0]} {row[1]}") for row in results]

        return liste_nom_complet
    
    def matricule(self, nom):
        self.connexion()
        
        self.mycursor = self.mydb.cursor()
        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT matricule FROM personnes WHERE nom = %s", (nom,))

        # Récupérer le premier résultat
        liste_matricule = self.mycursor.fetchone()

        return liste_matricule[0] 

    def immatriculation(self, nom):
        self.connexion()
        
        self.mycursor = self.mydb.cursor()
        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT immatriculation FROM personnes WHERE nom = %s", (nom,))

        # Récupérer le premier résultat
        liste_immatriculation = self.mycursor.fetchone()

        return liste_immatriculation[0]

    def ville(self, matricule):
        self.connexion()
        
        self.mycursor = self.mydb.cursor()
        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT ville FROM personnes WHERE matricule = %s", (matricule,))

        # Récupérer le premier résultat
        liste_ville = self.mycursor.fetchone()

        return liste_ville[0]    
    
    def charge(self, nom):
        self.connexion()
        self.mycursor = self.mydb.cursor()
        self.mycursor.execute("USE ODM")
        
        self.mycursor.execute("SELECT charge_affaires FROM personnes WHERE nom = %s", (nom,))
        liste_charge = self.mycursor.fetchone()

        # Vérifier si un résultat a été trouvé
        if liste_charge:
            print(f"Charge d'affaires trouvée pour {nom}: {liste_charge[0]}")
            return liste_charge[0]
        else:
            print(f"Aucune charge d'affaires trouvée pour {nom}")
            return None  # Ou une valeur par défaut 
    
    def mail_charge(self, charge):
        self.connexion()
        self.mycursor = self.mydb.cursor()
       
        charge_nom = charge.split()[-1]

        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT email FROM personnes WHERE nom = %s", (charge_nom,))
        
        mail = self.mycursor.fetchone()

        if mail:
            print(f"Email trouvé pour {charge}: {mail[0]}")
            return mail[0]
        else:
            print(f"Aucun email trouvé pour {charge}")
            return None  # Ou "Email non disponible" 
    
    def telephone_charge(self, charge):
        self.connexion()
        self.mycursor = self.mydb.cursor()

        charge_nom = charge.split()[-1]

        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT telephone FROM personnes WHERE nom = %s", (charge_nom,))
        
        telephone = self.mycursor.fetchone()

        if telephone:
            print(f"Téléphone trouvé pour {charge}: {telephone[0]}")
            return telephone[0]
        else:
            print(f"Aucun téléphone trouvé pour {charge}")
            return None  # Ou "Téléphone non disponible" 
    
    def adresse(self, nom):
        self.connexion()
        
        self.mycursor = self.mydb.cursor()
        
        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT adresse, ville, code_postal FROM personnes WHERE nom = %s", (nom,))
        
        # Récupérer le premier résultat
        result = self.mycursor.fetchone()
        
        if result:
            adresse, ville, code_postal = result
            # Formater l'adresse
            adresse_complete = f"{adresse}, {code_postal}, {ville}"
            return adresse_complete
        
        return None  # Retourne None si aucun résultat n'est trouvé

    
    def liste_prenom(self, nom):
        self.connexion()
        
        self.mycursor = self.mydb.cursor()
        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT prenom FROM personnes WHERE nom = %s", (nom,))

        # Récupérer le premier résultat
        liste_prenom = self.mycursor.fetchone()

        return liste_prenom[0] 
    
    
    def liste_contact(self):
        self.connexion()

        self.mycursor = self.mydb.cursor()
        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT nom, prenom FROM personnes WHERE id_role = 3")  
              
        # Créer les options en combinant nom et prénom
        liste_contact = [(f"{row[0]} {row[1]}", f"{row[0]} {row[1]}") for row in self.mycursor.fetchall()]
        
        # Debug : imprimer les choix récupérés

        return liste_contact
    

    def liste_usine(self):
        self.connexion()
        
        self.mycursor = self.mydb.cursor()
        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT entreprise_usine, ville FROM usines")  
        
        # Récupérer tous les résultats
        results = self.mycursor.fetchall()

        # Transformer chaque tuple en une simple chaîne
        liste_usine = [f"{row[0].replace('-', '').strip()} {row[1]}" for row in results]

        return liste_usine

    
    def liste_chantier(self,usine_entreprise,usine_ville):
        self.connexion()
        
        self.mycursor = self.mydb.cursor()
        self.mycursor.execute("USE ODM")
        self.mycursor.execute("""
            SELECT chantiers.entreprise_client 
            FROM usines 
            JOIN chantiers ON usines.id_usine = chantiers.id_usine 
            WHERE usines.ville = %s AND usines.entreprise_usine = %s
        """, (usine_ville, usine_entreprise))
        # Récupérer tous les résultats
        results = self.mycursor.fetchall()

        # Extraire les clients des résultats
        liste_chantier = [row[0] for row in results]  # row[0] correspond à la première colonne de chaque ligne
 
        return liste_chantier
        
    def nom_contact(self, id_personne_client):
        self.connexion()

        self.mycursor = self.mydb.cursor()
        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT nom, prenom FROM personnes WHERE id_personne = %s", (id_personne_client,))

   
        results = self.mycursor.fetchall()
        nom_contact = " ".join(results[0])
        
        return nom_contact
    
    def telephone_contact(self, id_personne_client):
        self.connexion()
 
        self.mycursor = self.mydb.cursor()
        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT telephone FROM personnes WHERE id_personne = %s", (id_personne_client,))

        # Récupérer tous les résultats
        results = self.mycursor.fetchall()
    
        telephone_contact = " ".join(results[0])
        
        return telephone_contact
    
    def email_contact(self, id_personne_client):
        self.connexion()
 
        self.mycursor = self.mydb.cursor()
        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT email FROM personnes WHERE id_personne = %s", (id_personne_client,))

        # Récupérer tous les résultats
        results = self.mycursor.fetchall()
    
        email_contact = " ".join(results[0])
        
        return email_contact
    
    def id_personne_client(self, id_chantier):
        self.connexion()
   
        self.mycursor = self.mydb.cursor()
        self.mycursor.execute("USE ODM")
        
        # Assurez-vous que id_chantier est un tuple d'un seul élément
        self.mycursor.execute("SELECT id_personne FROM affecter WHERE id_chantier = %s", (id_chantier,))

        # Récupérer tous les résultats
        id_personne = self.mycursor.fetchall()

        if id_personne:
            return id_personne[0][0]  # Accéder au premier élément du tuple, puis à l'élément dans ce tuple
        else:
            print("aucun résultat trouvé")
            return None  # Si aucun résultat n'est trouvé
    
    def id_usine(self,usine_entreprise,usine_ville):
        self.connexion()
        
        self.mycursor = self.mydb.cursor()
        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT id_usine FROM usines WHERE entreprise_usine = %s AND ville = %s", (usine_entreprise,usine_ville))

        # Récupérer tous les résultats
        id_usine = self.mycursor.fetchall()

        if id_usine:
            return id_usine[0][0]  # Accéder au premier élément du tuple, puis à l'élément dans ce tuple
        else:
            return None  # Si aucun résultat n'est trouvé
        
    def id_chantier(self,affaire):
        self.connexion()
        
        self.mycursor = self.mydb.cursor()
        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT id_chantier FROM chantiers WHERE code_affaire = %s ", (affaire,))

        # Récupérer tous les résultats
        id_chantier = self.mycursor.fetchall()

        if id_chantier:
            return id_chantier[0][0]  # Accéder au premier élément du tuple, puis à l'élément dans ce tuple
        else:
            return None  # Si aucun résultat n'est trouvé
    
    def code_affaire(self, client, id_usine):
        self.connexion()
        
        self.mycursor = self.mydb.cursor()
        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT code_affaire FROM chantiers WHERE entreprise_client = %s AND id_usine = %s", (client,id_usine))

        # Récupérer tous les résultats
        results = self.mycursor.fetchall()

        # Extraire les prenoms des résultats
        affaire = [row[0] for row in results]  # row[0] correspond à la première colonne de chaque ligne

        return ', '.join(affaire)
    
    def adresse_usine(self, usine):
        self.connexion()
        
        self.mycursor = self.mydb.cursor()
        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT adresse FROM usines WHERE ville = %s", (usine,))

        # Récupérer tous les résultats
        results = self.mycursor.fetchall()

        # Extraire les prenoms des résultats
        adresse = [row[0] for row in results]  # row[0] correspond à la première colonne de chaque ligne

        return ', '.join(adresse)
   
    def liste_nom(self, prenom):
        self.connexion()
        
        self.mycursor = self.mydb.cursor()
        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT nom FROM personnes WHERE prenom = %s", (prenom,))

        # Récupérer le premier résultat
        liste_nom = self.mycursor.fetchone()

        return liste_nom[0]
    
    def afficher_usine(self):
        self.connexion()
        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT * FROM usines")
        
        # Récupérer toutes les lignes
        usine = self.mycursor.fetchall()

        # Récupérer les noms de colonnes
        column_names = [i[0] for i in self.mycursor.description]
        
        return usine, column_names
    
    def afficher_agence(self):
        self.connexion()
        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT * FROM agences")
        
        # Récupérer toutes les lignes
        agence = self.mycursor.fetchall()

        # Récupérer les noms de colonnes
        column_names = [i[0] for i in self.mycursor.description]
        
        return agence, column_names
    
    
    def afficher_chantier(self):
        self.connexion()
        self.mycursor.execute("USE ODM")

        query = """
            SELECT c.id_chantier, c.entreprise_client, c.code_affaire, 
                u.entreprise_usine AS usine, 
                CONCAT(p.prenom, ' ', p.nom) AS contact
            FROM chantiers c
            LEFT JOIN usines u ON c.id_usine = u.id_usine
            LEFT JOIN affecter a ON c.id_chantier = a.id_chantier
            LEFT JOIN personnes p ON a.id_personne = p.id_personne
        """
        self.mycursor.execute(query)

        chantier = self.mycursor.fetchall()
        column_names = [i[0] for i in self.mycursor.description]

        return chantier, column_names



    def afficher_personne(self):
        self.connexion()
        self.mycursor.execute("USE ODM")

        query = """
            SELECT p.id_personne, p.nom, p.prenom, p.matricule, p.telephone, 
                p.immatriculation, p.adresse, p.code_postal, p.ville, 
                p.charge_affaires, p.email, a.ville AS agence, r.nom_role AS role
            FROM personnes p
            LEFT JOIN agences a ON p.id_agence = a.id_agence
            LEFT JOIN roles r ON p.id_role = r.id_role
        """
        self.mycursor.execute(query)

        personne = self.mycursor.fetchall()
        column_names = [i[0] for i in self.mycursor.description]

        return personne, column_names

    def afficher_user(self):
        self.connexion()
        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT id_utilisateur,email, admin FROM utilisateurs")
        
        # Récupérer toutes les lignes
        user = self.mycursor.fetchall()

        # Récupérer les noms de colonnes
        column_names = [i[0] for i in self.mycursor.description]
        
        return user, column_names
    '''
    def coordonnees_agence(self, nom):
        self.connexion()

        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT agence FROM personnes WHERE nom = %s", (nom,))
        agence = self.mycursor.fetchone()
        agence = agence[0]

        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT Latitude, Longitude FROM agences WHERE ville = %s", (agence,))
        
        # Récupérer toutes les lignes
        coordonnees_agence = self.mycursor.fetchall()

    
        return coordonnees_agence[0]
     
    def coordonnees_usine(self, nom):
        self.connexion()

        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT agence FROM personnes WHERE nom = %s", (nom,))
        agence = self.mycursor.fetchone()
        agence = agence[0]

        self.mycursor.execute("USE ODM")
        self.mycursor.execute("SELECT Latitude, Longitude FROM agences WHERE ville = %s", (agence,))
        
        # Récupérer toutes les lignes
        coordonnees_agence = self.mycursor.fetchall()

    
        return coordonnees_agence[0]
   
    def get_coordinates(self, address):
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": address,
            "format": "json",
            "addressdetails": 1,
            "limit": 1
        }
        headers = {
            "User-Agent": "MyGeocodingApp (contact@example.com)"  # Remplacez par votre email
        }
        response = requests.get(url, params=params, headers=headers)
        if response.ok and response.json():
            location = response.json()[0]
            return float(location["lat"]), float(location["lon"])
        else:
            return None
    '''
    


