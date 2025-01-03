# TradeFlow

TradeFlow est une application web Django conçue pour faciliter les flux commerciaux. Ce projet est dockerisé pour simplifier le déploiement et la gestion.

## Prérequis

Avant de commencer, assurez-vous d'avoir les outils suivants installés sur votre machine :

- Docker : [Installation](https://docs.docker.com/get-docker/)
- Docker Compose : [Installation](https://docs.docker.com/compose/install/)

---

## Installation et utilisation

### Étape 1 : Accerder au repertoire racine

```bash
cd TradeFlow
```

### Étape 2 : Construire les images Docker

Construisez les images Docker à partir du fichier `docker-compose.yml` :

```bash
docker-compose build
```

### Étape 3 : Lancer les conteneurs

Démarrez les conteneurs pour l'application :

```bash
docker-compose up
```

### Étape 4 : Accéder à l'application

L'application sera accessible via votre navigateur à l'adresse :

```
http://localhost:80
```

---

## Gestion des fichiers statiques et médias

- **Fichiers statiques :** Les fichiers statiques sont collectés dans le dossier `static/` grâce à la commande suivante (exécutée dans un conteneur) :

  ```bash
  docker-compose exec web python3 manage.py collectstatic --noinput
  ```
---

## Commandes utiles

### Effectuer des migrations

Appliquez les migrations pour synchroniser la base de données :

```bash
docker-compose exec web python3 manage.py migrate
```

### Arrêter les conteneurs

Pour arrêter l'application, utilisez :

```bash
docker-compose down
```


### Modification des dépendances

Ajoutez ou mettez à jour les dépendances Python dans le fichier `requirements.txt`, puis reconstruisez l'image Docker :

```bash
docker-compose build
```

---

## Contribuer

Les contributions sont les bienvenues ! Veuillez soumettre une issue ou une pull request pour proposer des améliorations ou signaler des problèmes.

---

## Licence

Ce projet est sous licence [MIT](LICENSE). Vous êtes libre de l'utiliser et de le modifier.


## Admin User
-Email : ronel2@gmail.com
-Name : ronel
-Password : 1234
-role : Admin

## Customer User
-Email : custom1@gmail.com
-name : custom1
-Password : 1234
-role : Customer

