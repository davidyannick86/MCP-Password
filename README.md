# MCP Password Generator

Un serveur MCP simple mais puissant pour générer des mots de passe sécurisés et mémorable, utilisant le protocole Streamable HTTP pour une intégration facile avec Docker, Claude Desktop et Raycast.

## Installation

### Prérequis
- Python 3.10+
- `pip`

### Configuration

1.  **Installer les dépendances**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Lancer le serveur**
    ```bash
    python server.py
    ```
    Le serveur démarrera sur `http://0.0.0.0:8000`.

### Evaluation de force

Chaque mot de passe généré est automatiquement analysé par `zxcvbn` pour estimer sa robustesse. Un score de 0 à 4 est ajouté à la réponse (ex: `[Strength: 4/4]`).

## Utilisation

Le serveur expose deux outils principaux :

1.  **`generate_random_password`**
    - `length` (int, défaut: 16) : Longueur du mot de passe.
    - `use_upper` (bool, défaut: True) : Inclure des majuscules.
    - `use_digits` (bool, défaut: True) : Inclure des chiffres.
    - `use_symbols` (bool, défaut: True) : Inclure des symboles.
    - `use_emojis` (bool, défaut: False) : Inclure des emojis (🎲, 🚀, etc.) pour plus de fun et de sécurité entropique.

2.  **`generate_memorable_password`**
    - `words` (int, défaut: 5) : Nombre de mots.
    - `separator` (str, défaut: "-") : Séparateur (ex: `-`, `_`, `.`, ` `).
    - `use_upper` (bool, défaut: False) : Capitaliser chaque mot.
    - `use_digits` (bool, défaut: False) : Ajouter un chiffre à chaque mot.


## Exemples de Prompts

Voici quelques exemples de ce que vous pouvez demander à votre assistant (Claude, Raycast AI, etc.) une fois le serveur connecté :

### Mots de passe aléatoires
- "Génère un mot de passe sécurisé de 20 caractères."
- "Crée un mot de passe simple de 8 lettres sans symboles."
- "J'ai besoin d'un mot de passe complexe avec des majuscules, des chiffres et des symboles."
- "Génère un mot de passe fun avec des émojis."
- "Crée un mot de passe de 12 caractères avec des symboles et des émojis."

### Mots de passe mémorables
- "Donne-moi un mot de passe facile à retenir composé de 5 mots."
- "Génère un mot de passe type 'correct-horse' avec 4 mots et des séparateurs points."
- "Crée une passphrase de 6 mots, avec des majuscules et des chiffres à la fin de chaque mot."
- "Génère un mot de passe mémorable mélangeant mots anglais et français."



## Troubleshooting

Si vous rencontrez des erreurs `400 Bad Request` ou `406 Not Acceptable`, assurez-vous que votre client envoie bien les en-têtes suivants (requis par le protocole Streamable HTTP) :

```bash
Content-Type: application/json
Accept: application/json, text/event-stream
```

**Exemple curl :**
```bash
curl -X POST http://localhost:8000/mcp \
     -H "Content-Type: application/json" \
     -H "Accept: application/json, text/event-stream" \
     -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'
```

### 3. Vérification (SSE)
Vous pouvez vérifier que l'endpoint SSE répond bien :

```bash
curl -N http://192.168.1.111:8004/sse
```
*Si vous voyez des événements `endpoint`, c'est gagné.*

## Explication "SSE vs Streamable HTTP"

Raycast utilise le mode **SSE** standard. Pour que cela fonctionne, le serveur doit exposer un endpoint `/sse`.

**Configuration requise :**
1.  **Serveur** : Mode `sse_app` (déjà configuré dans `server.py`).
2.  **Client (Raycast)** :
    - **Transport** : Choisir **SSE** (pas HTTP).
    - **URL** : `http://192.168.1.111:8004/sse`

⚠️ *Ne pas utiliser l'endpoint `/mcp` ou le mode "Streamable HTTP" avec Raycast, cela cause l'erreur "Invalid SSE response".*

## Intégration

### Claude Desktop

Ajoutez la configuration suivante à votre fichier `claude_desktop_config.json` :

```json
{
  "mcpServers": {
    "password-generator": {
      "command": "python",
      "args": [
        "/absolute/path/to/MCP-Password/server.py"
      ]
    }
  }
}
```
*Note : Si vous utilisez Docker ou lancez le serveur séparément, Claude Desktop ne supporte pas encore nativement le SSE/HTTP distant facilement sans proxy, mais FastMCP en mode `uvicorn` est prêt pour ces usages.*

### Raycast

Pour utiliser ce serveur avec Raycast, vous pouvez créer une extension ou utiliser un client MCP générique.
Si vous développez une extension Raycast, pointez vers l'endpoint HTTP :

URL: `http://localhost:8000/mcp` (Streamable HTTP)

Cependant, la méthode la plus simple pour Raycast actuellement est d'exécuter le script python en local via l'intégration MCP CLI si disponible, ou simplement d'utiliser le serveur en mode HTTP avec l'endpoint ci-dessus.

**Exemple de manifest Raycast (imaginaire)** :
```json
{
    "name": "Password Generator",
    "source": {
        "url": "http://localhost:8000/mcp"
    }
}
```

## Déploiement sur VM Linux (AMD64)

### 1. Transférer les fichiers
Utilisez cette commande `scp` pour copier tous les fichiers nécessaires sur votre serveur :

```bash
# Créer le dossier distant d'abord (optionnel mais conseillé)
ssh david@192.168.1.111 "mkdir -p /home/david/mcp-servers/passwords"

# Copier les fichiers
scp -r server.py requirements.txt eff_large_wordlist.txt Dockerfile compose.yaml david@192.168.1.111:/home/david/mcp-servers/passwords/
```

### 2. Lancer avec Docker Compose
Connectez-vous à votre serveur et lancez le conteneur :

```bash
ssh david@192.168.1.111
cd /home/david/mcp-servers/passwords
docker compose up -d --build
```

Le serveur sera accessible sur le port **8004** de votre VM.
Assurez-vous que votre pare-feu autorise le trafic entrant sur ce port.

### 3. Vérification
```bash
curl -X POST http://192.168.1.111:8004/mcp \
     -H "Content-Type: application/json" \
     -H "Accept: application/json, text/event-stream" \
     -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'
```
