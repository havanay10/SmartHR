====================================================
  SMARTRH - GUIDE D'INSTALLATION
====================================================

Ce projet est une application desktop RH (SIRH) developpee
en Python (PyQt6) avec une base PostgreSQL.

====================================================
  PREREQUIS
====================================================

1. PYTHON 3.12
   https://www.python.org/downloads/
   ATTENTION : cocher "Add Python to PATH" a l'installation
   Redemarrer le PC apres installation.

2. DOCKER DESKTOP
   https://www.docker.com/products/docker-desktop/
   - Windows : necessite WSL2 (l'installeur le propose)
   - Activer la virtualisation dans le BIOS si demande
   - Redemarrer le PC apres installation
   - Lancer Docker Desktop (attendre la baleine verte)

3. VS CODE (recommande)
   https://code.visualstudio.com/

====================================================
  INSTALLATION PAS A PAS
====================================================

--- ETAPE 1 : OUVRIR LE PROJET DANS UN TERMINAL ---

   Ouvrir le dossier du projet dans un terminal :
   - Windows : clic droit dans le dossier > "Ouvrir dans le Terminal"
   - Mac/Linux : clic droit > "Ouvrir dans le Terminal"

   Verifier :
       pwd
   Doit afficher le chemin du projet.

--- ETAPE 2 : CREER L'ENVIRONNEMENT VIRTUEL ---

   python -m venv venv

   Si erreur "python not found" : Python pas dans le PATH.
   Reinstaller Python en cochant "Add to PATH".

--- ETAPE 3 : ACTIVER L'ENVIRONNEMENT ---

   Windows PowerShell :
       .\venv\Scripts\Activate.ps1

       Si erreur "execution of scripts is disabled" :
           Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
           (taper O puis Entree)
       Puis relancer l'activation.

   Windows CMD :
       venv\Scripts\activate.bat

   Mac/Linux :
       source venv/bin/activate

   Le prompt doit afficher (venv) au debut.

--- ETAPE 4 : INSTALLER LES DEPENDANCES ---

   pip install --upgrade pip
   pip install -r requirements.txt

   (Prend 3 a 5 minutes)

--- ETAPE 5 : CREER LE FICHIER .env ---

   Windows PowerShell :
       Copy-Item .env.example .env

   Windows CMD :
       copy .env.example .env

   Mac/Linux :
       cp .env.example .env

   Puis ouvrir .env et ajouter votre cle API Groq si
   vous voulez utiliser l'IA d'import CV.

   Sans cle API, l'application fonctionne quand meme
   (analyse CV en mode classique).

--- ETAPE 6 : LANCER POSTGRES ---

   docker compose up -d

   Verifier :
       docker compose ps

   Doit afficher : smartrh_db    Up (healthy)

   Si "starting" : attendre 10 secondes et refaire.

--- ETAPE 7 : CREER LES TABLES ---

   python reset_db.py

   Doit afficher : OK - 18 tables creees

--- ETAPE 8 : CHARGER LES DONNEES DE DEMO ---

   python seed.py

   Doit afficher : Seed termine avec succes !

--- ETAPE 9 : LANCER L'APPLICATION ---

   python main.py

   La fenetre SmartRH doit s'ouvrir.

====================================================
  EN CAS DE PROBLEME
====================================================

- "python not found"
  -> Python pas installe ou pas dans le PATH
  -> Reinstaller en cochant "Add Python to PATH"

- "docker : command not found"
  -> Docker Desktop pas installe
  -> Installer depuis docker.com

- "Cannot connect to Docker daemon"
  -> Docker Desktop pas lance
  -> Ouvrir Docker Desktop, attendre la baleine verte

- "port 5432 already in use"
  -> Un autre Postgres tourne
  -> docker compose down
  -> Changer le port dans docker-compose.yml

- "ModuleNotFoundError: No module named 'app'"
  -> Vous n'etes pas dans le bon dossier
  -> cd chemin_vers_le_projet

- "psycopg2.OperationalError"
  -> Postgres pas pret
  -> docker compose up -d puis attendre 10s

- "Activate.ps1 cannot be loaded"
  -> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

====================================================
  UTILISATION DE L'IA (optionnel)
====================================================

Pour activer l'analyse de CV par IA (Groq - GRATUIT) :

1. Aller sur https://console.groq.com/
2. S'inscrire (30 secondes, sans carte bancaire)
3. Aller dans "API Keys" puis "Create API Key"
4. Copier la cle (commence par gsk_)
5. Dans .env :
       GROQ_API_KEY=gsk_votre_cle_ici
       LLM_ENABLED=True
6. Relancer l'application

Quota gratuit : 14400 requetes par jour.

====================================================
  COMMANDES UTILES
====================================================

Demarrer Postgres        : docker compose up -d
Arreter Postgres         : docker compose down
Voir les conteneurs      : docker compose ps
Voir les logs            : docker compose logs -f
Reset de la base         : python reset_db.py
Recharger les donnees    : python seed.py
Lancer l'application     : python main.py

====================================================