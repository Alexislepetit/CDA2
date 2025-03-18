from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, Regexp, EqualTo, InputRequired
from wtforms import StringField, PasswordField, SelectField, SubmitField, DateField, TextAreaField

#=================================================================
class ConfigForm(FlaskForm):
    user_username = StringField('Utilisateur', validators=[DataRequired()])
    user_password = PasswordField('Mot de passe', validators=[DataRequired()])
    submit = SubmitField('Valider')

class ConfigFormnewTech(FlaskForm):
    tech_nom = StringField('Nom', validators=[DataRequired()])
    tech_prenom = StringField('Prénom', validators=[DataRequired()])
    tech_matricule = StringField('Matricule', validators=[DataRequired()])
    tech_telephone = StringField('telephone', validators=[DataRequired()])
    tech_immatriculation = StringField('Immatriculation du véhicule', validators=[DataRequired()])
    tech_email = StringField('E-mail', validators=[DataRequired()])
    tech_ville = StringField('Ville', validators=[DataRequired()])
    tech_code_postal = StringField('Code postal', validators=[DataRequired(),Length(min=5, max=5, message="Le code postal doit contenir exactement 5 chiffres."),Regexp(r'^\d+$', message="Le code postal doit contenir uniquement des chiffres.")])
    tech_adresse = StringField('Adresse', validators=[DataRequired()])
    tech_charge_affaires = SelectField('Chargé d\'affaire', validators=[DataRequired()])
    tech_agence = SelectField('Agence de rattachement', validators=[DataRequired()])
    submit = SubmitField('Valider')

class ConfigFormnewClient(FlaskForm):
    client_nom = StringField('Nom', validators=[DataRequired()])
    client_prenom = StringField('Prénom', validators=[DataRequired()])
    client_telephone = StringField('telephone', validators=[DataRequired()])
    client_email = StringField('E-mail', validators=[DataRequired()])
    submit = SubmitField('Valider')
    
class ConfigFormnewContactSpie(FlaskForm):
    contactspie_nom = StringField('Nom', validators=[DataRequired()])
    contactspie_prenom = StringField('Prénom', validators=[DataRequired()])
    contactspie_telephone = StringField('telephone', validators=[DataRequired()])
    contactspie_email = StringField('E-mail', validators=[DataRequired()])
    submit = SubmitField('Valider')

class ConfigFormnewCharge(FlaskForm):
    charge_nom = StringField('Nom', validators=[DataRequired()])
    charge_prenom = StringField('Prénom', validators=[DataRequired()])
    charge_matricule = StringField('Matricule', validators=[DataRequired()])
    charge_telephone = StringField('telephone', validators=[DataRequired()])
    charge_immatriculation = StringField('Immatriculation du véhicule', validators=[DataRequired()])
    charge_email = StringField('E-mail', validators=[DataRequired()])
    charge_ville = StringField('Ville', validators=[DataRequired()])
    charge_code_postal = StringField('Code postal', validators=[DataRequired(),
                                   Length(min=5, max=5, message="Le code postal doit contenir exactement 5 chiffres."),
                                   Regexp(r'^\d+$', message="Le code postal doit contenir uniquement des chiffres.")])
    charge_adresse = StringField('Adresse', validators=[DataRequired()])
    charge_agence = SelectField('Agence de rattachement', 
                              choices=[('', 'Sélectionnez une agence')], 
                              validators=[DataRequired()])
    submit = SubmitField('Valider')


class ConfigFormnewChantier(FlaskForm):
    chantier_entreprise_client = StringField('Entreprise cliente', validators=[DataRequired()])
    chantier_code_affaire = StringField('Code affaire', validators=[DataRequired()])
    chantier_id_usine = SelectField('Usine', validators=[DataRequired()])
    chantier_contact=SelectField('Contact client sur place', validators=[DataRequired()])
    submit = SubmitField('Valider')

class ConfigFormnewUsine(FlaskForm):
    usine_entreprise = StringField('Entreprise', validators=[DataRequired()])
    usine_adresse = StringField('Adresse', validators=[DataRequired()])
    usine_code_postal = StringField('Code postal', validators=[DataRequired()])
    usine_ville=StringField('Ville', validators=[DataRequired()])
    submit = SubmitField('Valider')
    
class ConfigFormnewAgence(FlaskForm):
    agence_ville = StringField('Ville', validators=[DataRequired()])
    submit = SubmitField('Valider')

class ConfigFormnewUser(FlaskForm):
    user_utilisateur = StringField('Nouvel utilisateur', validators=[DataRequired()])
    user_password = PasswordField('Mot de passe', validators=[DataRequired()])
    user_password2 = PasswordField('Confirmer le mot de passe', validators=[DataRequired(), EqualTo('user_password', message="Les mots de passe doivent correspondre.")])
    admin = SelectField('Administrateur ?', choices=[('oui', 'Oui'), ('non', 'Non')], validators=[DataRequired()])
    submit = SubmitField('Valider')


class ConfigFormDroits(FlaskForm):
    user_username = StringField('Utilisateur', validators=[DataRequired()])
    droit_admin = StringField('Droits admin', validators=[DataRequired()])
    submit = SubmitField('Valider')

class Recherche_BDD(FlaskForm):
    user_recherche = StringField('Nom ', validators=[DataRequired()])
    colonne_recherche = SelectField('Information à afficher',  choices=[], validators=[DataRequired()])
    prenom_recherche = SelectField('Prenom du technicien',  choices=[], validators=[DataRequired()])
    submit = SubmitField('Valider')

class Recherche_BDD_ODM(FlaskForm):
    usine_recherche = SelectField('Lieu du chantier', choices=[], validators=[InputRequired()])
    nom_recherche = SelectField('Prenom du technicien', choices=[], validators=[InputRequired()])
    chantier_recherche = SelectField('Chantier', choices=[], validators=[InputRequired()])
    date_debut = DateField('Date de début d\'intervention', format='%Y-%m-%d', validators=[DataRequired()])
    date_fin = DateField('Date de fin d\'intervention', format='%Y-%m-%d', validators=[DataRequired()])
    mission = TextAreaField('Mission')
    submit = SubmitField('Valider')

 