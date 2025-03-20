from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from app.requete import Requete_BDD
from app import app


# Initialiser Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirection si un utilisateur non authentifié tente d'accéder à une page protégée


class utilisateur(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

    def admin(self):
        return self.role == 'oui'  # Vérifie si l'utilisateur est admin


    @staticmethod
    def get(user_id):
        BDD = Requete_BDD()
        user_data = BDD.get_user_by_id(user_id)
        if user_data:
            return utilisateur(id=user_data['id'], username=user_data['username'], role=user_data['role'])
        return None

    @login_manager.user_loader
    def load_user(user_id):
        BDD = Requete_BDD()
        user_data = BDD.get_user_by_id(user_id)  
        if user_data:
            return utilisateur(id=user_data[0], username=user_data[1], role=user_data[3])  # Correction ici
        return None