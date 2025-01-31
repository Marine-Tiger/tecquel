import unicodedata

def supprimer_accents_majuscules_fichier(entree, sortie):
    try:
        # Lire le contenu du fichier d'entrée
        with open(entree, 'r', encoding='utf-8') as f:
            texte = f.read()
        
        # Supprimer les accents et convertir en minuscules
        texte = ''.join(c for c in unicodedata.normalize('NFD', texte) if unicodedata.category(c) != 'Mn')
        texte = texte.lower()
        
        # Écrire le texte modifié dans le fichier de sortie
        with open(sortie, 'w', encoding='utf-8') as f:
            f.write(texte)
        
        print(f"Transformation terminée. Résultat enregistré dans '{sortie}'.")
    except Exception as e:
        print(f"Erreur : {e}")

# Exemple d'utilisation
fichier_entree = "Ground_truth/Spinec_1688"
fichier_sortie = "GT_1688_cleaned.txt"

supprimer_accents_majuscules_fichier(fichier_entree, fichier_sortie)
