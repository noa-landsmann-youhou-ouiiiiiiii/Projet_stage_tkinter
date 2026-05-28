from tkinter import *


def valider_et_traiter(*args):
    # 1. Récupérer la valeur actuelle
    texte = texte_var.get()

    # 2. Exemple de traitement : conversion en majuscules en temps réel
    resultat_var.set(f"{texte}.aze")

    # 3. Exemple de validation visuelle (si plus de 10 caractères, on change la couleur)
    if len(texte) > 10:
        label_erreur.config(text="Trop long !", fg="red")
    else:
        label_erreur.config(text="", fg="black")


# --- Configuration de la fenêtre ---
root = Tk()
root.title("Traitement en temps réel")
root.geometry("400x200")

# 1. Création de la variable de contrôle
texte_var = StringVar()

# 2. Liaison de la variable à la fonction de traitement
# "write" signifie que la fonction se déclenche à chaque modification
texte_var.trace_add("write", valider_et_traiter)

# 3. Création du champ de saisie lié à la variable
Label(root, text="Saisissez votre texte :").pack(pady=5)
entry = Entry(root, textvariable=texte_var)
entry.pack(pady=5)

# Zone d'affichage du résultat
resultat_var = StringVar()
label_resultat = Label(root, textvariable=resultat_var, font=("Helvetica", 12, "bold"))
label_resultat.pack(pady=10)

label_erreur = Label(root, text="")
label_erreur.pack()

root.mainloop()