from tkinter import *
from tkinter import messagebox
import os
import sys
import subprocess
import smtplib
from email.message import EmailMessage
from PIL import Image, ImageTk

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def send_email(recipient_email, sender_email, subject, body):
    smtp_server = "smtp-relay.occitanet.fr"
    smtp_port = 25

    message = EmailMessage()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject
    message.set_content(body)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.send_message(message)
        print(f"Email envoyé à {recipient_email}.")
    except Exception as e:
        print(f"Erreur d'envoi d'email : {str(e)}")

def create_user():
    firstname_input = entry_firstname.get().strip()
    lastname_input = entry_lastname.get().strip()

    firstname_cap = firstname_input.capitalize()
    lastname_upper = lastname_input.upper()
    display_name = f"{lastname_upper} {firstname_cap}"

    firstname_lower = firstname_input.lower().replace(" ", "")
    lastname_lower = lastname_input.lower().replace(" ", "")
    
    username = f"{firstname_lower}.{lastname_lower}"
    
    if len(username) > 20:
        firstname_abbr = firstname_lower[0]
        username = f"{firstname_abbr}.{lastname_lower}"
        if len(username) > 20:
            lastname_abbr = lastname_lower[:15]
            username = f"{firstname_abbr}.{lastname_abbr}"
    
    login_name = f"{username}@pedagocric.cric.asso.fr"
    password = "CRIC-2025!!!"  # Mot de passe fixe

    valid_to = entry_valid_to.get().strip()

    # Adresses e-mails saisies par l'utilisateur
    recipient_email = entry_recipient_email.get().strip()
    sender_email = "support@altsysnet.com"  # Expéditeur fixe

    selected_label = selected_ou.get()
    # Chercher le chemin complet correspondant à l'étiquette sélectionnée
    user_ou = ou_mapping.get(selected_label, "CN=Users,DC=pedagocric,DC=cric,DC=asso,DC=fr")

    ps_command = f'''
$username = "{username}"
$firstname = "{firstname_cap}"
$lastname = "{lastname_upper}"
$displayname = "{display_name}"
$password = "{password}"
$securePassword = ConvertTo-SecureString $password -AsPlainText -Force
$userOU = "{user_ou}"
$validTo = "{valid_to}"
$userPrincipalName = "{login_name}"

New-ADUser -Name $displayname -GivenName $firstname -Surname $lastname -DisplayName $displayname -UserPrincipalName $userPrincipalName -SamAccountName $username -Path $userOU

Set-ADAccountPassword -Identity $username -NewPassword $securePassword -Reset

Enable-ADAccount -Identity $username

Set-ADUser -Identity $username -ChangePasswordAtLogon $true

if ($validTo -ne "") {{
    Set-ADUser -Identity $username -AccountExpirationDate $validTo
}}
'''

    try:
        result = subprocess.run(['powershell', '-Command', ps_command], capture_output=True, text=True)
        if result.returncode == 0:
            messagebox.showinfo("Succès", f"Utilisateur créé avec succès !\nNom d'utilisateur : {login_name}\nMot de passe : {password}")
            subject = "Informations de connexion pour le nouvel utilisateur"
            body = f"""
Bonjour,

Un nouvel utilisateur a été créé avec les informations suivantes :

Nom complet : {display_name}
Nom d'utilisateur : {login_name}
Mot de passe : {password}

Veuillez transmettre ces informations à l'utilisateur de manière sécurisée.

Cordialement,
L'équipe informatique
"""
            send_email(recipient_email, sender_email, subject, body)
        else:
            error_message = f"Erreur lors de la création de l'utilisateur : {result.stderr}"
            print(error_message)
            messagebox.showerror("Erreur", error_message)
            subject = "Erreur lors de la création d'un utilisateur"
            body = f"""
Bonjour,

Une erreur s'est produite lors de la création d'un utilisateur.

Détails de l'erreur :
{error_message}

Cordialement,
L'équipe informatique
"""
            send_email(recipient_email, sender_email, subject, body)
    except Exception as e:
        error_message = f"Erreur : {str(e)}"
        messagebox.showerror("Erreur", error_message)
        subject = "Erreur lors de l'exécution du script"
        body = f"""
Bonjour,

Une erreur s'est produite lors de l'exécution du script.

Détails de l'erreur :
{error_message}

Cordialement,
L'équipe informatique
"""
        send_email(recipient_email, sender_email, subject, body)

# Initialisation de l'interface Tkinter
root = Tk()
root.title("Créateur d'utilisateurs AD")

# Chargement de l'image de logo après avoir initialisé la fenêtre
try:
    logo_path = get_resource_path("logo.jpg")
    logo_image = Image.open(logo_path)
    logo_photo = ImageTk.PhotoImage(logo_image)
except Exception as e:
    print(f"Erreur lors du chargement du logo : {e}")

if 'logo_photo' in locals():
    label_logo = Label(root, image=logo_photo)
    label_logo.pack()

label_firstname = Label(root, text="Prénom :")
entry_firstname = Entry(root)
label_lastname = Label(root, text="Nom :")
entry_lastname = Entry(root)
label_valid_to = Label(root, text="Date de fin (YYYY-MM-DD) :")
entry_valid_to = Entry(root)

# Liste complète des chemins LDAP
ou_list = [
    "OU=Utilisateurs,OU=PYR,DC=pedagocric,DC=cric,DC=asso,DC=fr",
    "OU=OVT,OU=Utilisateurs,OU=PYR,DC=pedagocric,DC=cric,DC=asso,DC=fr",
    "OU=PREO,OU=Utilisateurs,OU=PYR,DC=pedagocric,DC=cric,DC=asso,DC=fr"
]

# Création d'un mapping entre étiquettes et chemins complets
ou_mapping = {entry.split(",")[0].replace("OU=", ""): entry for entry in ou_list}

# Récupérer uniquement les étiquettes à afficher
ou_labels = list(ou_mapping.keys())

selected_ou = StringVar()
selected_ou.set("")  # Aucun choix par défaut

# Champs pour les e-mails
label_recipient_email = Label(root, text="E-mail(s) du ou des destinataires :")
entry_recipient_email = Entry(root)

label_ou = Label(root, text="Sélectionnez l'OU :")
ou_menu = OptionMenu(root, selected_ou, *ou_labels)

button_create = Button(root, text="Créer l'utilisateur", command=create_user)

label_firstname.pack()
entry_firstname.pack()
label_lastname.pack()
entry_lastname.pack()
label_valid_to.pack()
entry_valid_to.pack()
label_recipient_email.pack()
entry_recipient_email.pack()
label_ou.pack()
ou_menu.pack()
button_create.pack()

contact_message = "En cas de problème, contacter Altsysnet 09 72 54 05 47"
label_contact = Label(root, text=contact_message)
label_contact.pack(side=BOTTOM)

root.mainloop()
