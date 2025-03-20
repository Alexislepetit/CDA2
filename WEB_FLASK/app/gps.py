from flask import render_template, request
import requests
import math

ADDOK_URL = 'http://api-adresse.data.gouv.fr/search/'

class class_gps:

    def get_gps_coordinates(self, adresse):
        """
        Cette fonction prend une adresse en entrée, envoie une requête à l'API d'adresse du gouvernement,
        et renvoie les coordonnées GPS (latitude, longitude) du premier résultat trouvé.
        """
        print("Adresse saisie : ", adresse)  # Affiche l'adresse saisie par l'utilisateur
        
        params = {
            'q': adresse,
            'limit': 5
        }
        print(f"Paramètres de la requête : {params}")  # Affiche les paramètres de la requête
        
        try:
            # Envoie la requête à l'API
            response = requests.get(ADDOK_URL, params=params)
            print(f"Réponse reçue : {response}")  # Affiche l'objet réponse complet
            print(f"Code statut de la réponse : {response.status_code}")  # Affiche le code de statut HTTP de la réponse
            
            if response.status_code == 200:
                print("Requête réussie !")  # Indique que la requête s'est bien passée
            else:
                print(f"Erreur lors de la requête : {response.status_code}")  # Affiche un code d'erreur si la requête échoue

            # Si la réponse est OK (status 200), on parse le JSON
            j = response.json()
            print(f"Réponse JSON de l'API : {j}")  # Affiche la réponse brute sous forme JSON
            
            # Si des résultats sont retournés
            if len(j.get('features')) > 0:
                first_result = j.get('features')[0]
                lon, lat = first_result.get('geometry').get('coordinates')
                
                # Stocke la longitude et la latitude dans des variables
                longitude = lon
                latitude = lat
                print(f"Longitude : {longitude}, Latitude : {latitude}")  # Affiche la longitude et la latitude

                # Combine les informations pour les transmettre au template
                first_result_all_infos = { **first_result.get('properties'), **{"lon": longitude, "lat": latitude} }
                return latitude, longitude  # Renvoie latitude et longitude
            else:
                print("Aucun résultat trouvé.")  # Affiche un message si aucun résultat n'est retourné par l'API
                return None, None  # Aucun résultat trouvé
            
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la requête API : {e}")  # Affiche l'erreur si la requête échoue
            return None, None  # Retourne None en cas d'erreur lors de la requête API
            
        
    def haversine(self, lat1, lon1, lat2, lon2):
        """
        Cette fonction calcule la distance à vol d'oiseau entre deux points GPS (latitude, longitude)
        en utilisant la formule Haversine.
        """
        # Rayon moyen de la Terre (en kilomètres)
        R = 6371.0
        # Convertir les degrés en radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        # Différences de coordonnées
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        # Calcul de la distance
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        # Calcul de la distance en kilomètres
        distance = R * c
        return distance

    def calculate_distance(self, adresse1, adresse2):
        """
        Cette fonction prend deux adresses, récupère leurs coordonnées GPS respectives,
        puis calcule la distance à vol d'oiseau entre elles.
        """
        # Récupérer les coordonnées GPS des deux adresses
        lat1, lon1 = self.get_gps_coordinates(adresse1)
        lat2, lon2 = self.get_gps_coordinates(adresse2)
        
        # Si les deux adresses ont des coordonnées valides, calculer la distance
        if lat1 is not None and lat2 is not None:
            print(f"Calcul de la distance entre {adresse1} et {adresse2}...")
            distance_km = self.haversine(lat1, lon1, lat2, lon2)
            print(f"La distance à vol d'oiseau entre les deux adresses est de {distance_km:.2f} km")
            return distance_km
        else:
            print("Erreur lors de la récupération des coordonnées.")
            return None
    
    def calcul_zone(self, distance):
        """
        Cette fonction prend une distance en entrée et renvoie la zone correspondante.
        """
        if distance is not None:
            if distance < 50:
                return "Zone A"
            elif distance < 100:
                return "Zone B"
            else:
                return "Grand déplacement"
        else:
            return "Erreur de calcul"
        