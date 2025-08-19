# 🚀 Système d’Audit Numérique pour les Coopératives Informelles
Un outil numérique innovant conçu pour simplifier la gestion des finances et des adhérents au sein des coopératives informelles. Ce système aide à suivre les cotisations, les prêts, les remboursements, et permet un audit automatisé grâce à l'IA avec **LangChain**.
## 🖥️ **Tech Stack**
- **Backend** : Django REST Framework (DRF)
- **Frontend** : React SPA
- **Intelligence Artificielle** : LangChain (OpenAI GPT)
- **Base de données** : PostgreSQL
- **Temps réel** : Django Channels + WebSockets
- **Tâches en arrière-plan** : Celery avec Redis
- **Graphiques** : Chart.js / Recharts

## ✨ **Fonctionnalités Clés**
### 🎯 **Modules principaux :**
- **Gestion des adhérents** : Ajout, mise à jour et suspension des membres.
- **Saisie des transactions** :
    - Enregistrement des cotisations, prêts, et remboursements via formulaires React.

- **Détection d’anomalies avec IA** :
    - Audit basé sur LangChain pour automatiser la détection des irrégularités financières.

- **Dashboard Financier** :
    - Consultation des journaux, soldes et graphiques simples pour un aperçu financier.

- **Messagerie interne** : Notifications pour les membres et les administrateurs.
- **Rapports automatisés** : Exportation de rapports financiers en csv.
- **Chatbot IA** :
    - Explication d’écarts financiers.
    - Génération de rapports mensuels à la demande.

## 📖 **Architecture & Flux**
1. **Frontend React SPA** :
    - Gestion des formulaires (adhérents, cotisations, etc.).
    - Intégration avec DRF pour consommer les API REST.
    - Visualisation des données via graphiques dynamiques.

2. **Backend Django REST Framework** :
    - Exposition des API REST associées à chaque module.
    - Sécurisation via JWT pour l’authentification des utilisateurs.
    - Gestion des rôles et permissions.

3. **LangChain pour l’IA** :
    - Intégration avec OpenAI GPT.
    - Audit et chatbot pour expliquer les anomalies ou générer des résumés.

4. **Tâches asynchrones** :
    - Utilisation de Celery pour planifier et exécuter des audits périodiques.

5. **Temps réel** :
    - Notifications via Django Channels et WebSockets.

## 📋 **Installation**
### Prérequis :
- **Python 3.11+**
- **Node.js 16+**
- **Redis** pour les tâches asynchrones
- **PostgreSQL** comme base de données

### Étapes d'installation :
1. Clonez le projet :
```
git clone https://github.com/reyptz/audit_numerique_django.git
cd audit_numerique_django
```
2. Configurez l’environnement Python :
```
python -m venv env
source env/bin/activate  # Sous Windows : env\Scripts\activate
pip install -r requirements.txt
```
3. Configurez la base de données PostgreSQL : Mettez à jour les paramètres dans : `settings.py`
``` 
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'audit',
           'USER': 'postgres',
           'PASSWORD': 'votre-mot-de-passe',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
```
4. Appliquez les migrations :
```
python manage.py makemigrations
python manage.py migrate
```
5. Lancez le projet :
``` 
python manage.py runserver
```
6. Configurez Redis (si Celery est utilisé) :
```
# Démarrez Redis
redis-server
```
7. Démarrez Celery :
```
celery -A Audit_Numerique worker --loglevel=info
```
## 🛠️ **Fonctionnement des Modules**
### 1️⃣ **Authentification (JWT)** :
- Utilisateurs :
    - Administrateurs (superuser Django).
    - Membres (adhérents de la coopérative).

- Rôles pris en charge : Administrateur, Trésorier, Secrétaire, Membre.

### 2️⃣ **Saisie et Audit des Transactions** :
- Enregistrement par type :
    - **Cotisations régulières**.
    - **Prêts et Remboursements**.

- L’audit vérifie :
    - Retards de paiement.
    - Transactions incohérentes (montant ou type).

### 3️⃣ **Tableau de Bord** :
- **Statistiques clés** :
    - Total des cotisations et des prêts.
    - Solde de la coopérative.
    - Historique des transactions.

- **Graphiques dynamiques** :
    - Répartition des dépenses.
    - Comparaison des cotisations au fil du temps.

### 4️⃣ **Chatbot IA (LangChain)** :
- Explications personnalisées pour toute transaction suspecte.
- Résumés financiers générés automatiquement pour une période donnée.

### 5️⃣ **Notifications et Rapports** :
- Génération de rapports financiers :
    - Exportables en formats **CSV**.

- Notifications envoyées en temps réel aux administrateurs et membres.

## 🛡️ DevSecOps & MLOps

- **DevSecOps** :
  - Analyse statique et formatage automatique via `pre-commit` (Black, Flake8, Isort, Bandit).
  - Intégration continue avec GitHub Actions (`.github/workflows/ci.yml`).
  - Conteneurisation avec Docker et déploiement via Gunicorn.

- **MLOps** :
  - Exemple de pipeline de machine learning avec `scikit-learn` et `MLflow` dans `mlops/train.py`.
  - Dépendances ML isolées dans `mlops/requirements-ml.txt`.
  
## 🧑‍💻 **Contribution**
1. Forkez le dépôt.
2. Créez une nouvelle branche :
``` 
   git checkout -b feature/votre-feature
```
3. Poussez vos modifications :
``` 
   git commit -m "Ajout de ma nouvelle fonctionnalité"
   git push origin feature/votre-feature
```
4. Soumettez une Pull Request 🚀.

## 📄 **Licence**
Ce projet est sous licence [MIT](LICENSE). Vous êtes libre de l’utiliser, de le modifier et de le distribuer. 🎉
## 📞 **Contact**
Pour toute question ou suggestion, contactez-nous :
- 📧 Email : reyptz@gmail.com | madoumadeltitokone77@gmail.com