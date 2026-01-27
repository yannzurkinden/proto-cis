# Sécurité et Conformité - CIS

## 1. Vue d'Ensemble

### 1.1 Objectifs de Sécurité

| Objectif | Description |
|----------|-------------|
| **Confidentialité** | Seules les personnes autorisées accèdent aux données |
| **Intégrité** | Les données ne peuvent être modifiées que par des utilisateurs autorisés |
| **Disponibilité** | Le système est accessible pendant les heures de travail |
| **Traçabilité** | Toutes les actions sont enregistrées et auditables |
| **Conformité** | Respect de la LPD suisse et bonnes pratiques |

### 1.2 Données Sensibles Identifiées

| Catégorie | Exemples | Niveau de sensibilité |
|-----------|----------|----------------------|
| Données médicales | Médication, restrictions, diagnostics | Très élevé |
| Données financières | Salaire, rente AI | Élevé |
| Comportements à risque | Incidents, alertes | Élevé |
| Données personnelles | Nom, adresse, téléphone | Standard |
| Données professionnelles | Objectifs, formations | Standard |

---

## 2. Authentification

### 2.1 Politique de Mots de Passe

```python
# Configuration
PASSWORD_MIN_LENGTH = 12
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_DIGIT = True
PASSWORD_REQUIRE_SPECIAL = True
PASSWORD_MAX_AGE_DAYS = 90
PASSWORD_HISTORY_COUNT = 5  # Empêche réutilisation
```

### 2.2 Implémentation JWT

```python
# Configuration tokens
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7
ALGORITHM = "HS256"

# Structure du token
{
    "sub": "user_id",
    "email": "user@example.ch",
    "role": "MSP",
    "unit_id": 1,
    "permissions": ["read:beneficiary", "write:journal"],
    "exp": 1705320000,
    "iat": 1705319100,
    "jti": "unique-token-id"
}
```

### 2.3 Flux d'Authentification

```
1. Login
   Client → POST /auth/login (email, password)
   Server → Vérifie credentials
   Server → Génère access_token + refresh_token
   Server → Retourne access_token dans body
   Server → Set refresh_token en cookie httpOnly

2. Requêtes authentifiées
   Client → Authorization: Bearer <access_token>
   Server → Vérifie signature et expiration
   Server → Extrait user_id et permissions

3. Refresh
   Client → POST /auth/refresh (cookie refresh_token)
   Server → Vérifie refresh_token
   Server → Génère nouveau access_token
   Server → Optionnel: rotation du refresh_token

4. Logout
   Client → POST /auth/logout
   Server → Invalide refresh_token (blacklist)
   Server → Clear cookie
```

### 2.4 Protection Anti-Brute Force

```python
# Configuration rate limiting
LOGIN_MAX_ATTEMPTS = 5
LOGIN_LOCKOUT_MINUTES = 15
LOGIN_RATE_LIMIT = "5/minute"

# Implémentation Redis
async def check_login_attempts(email: str) -> bool:
    key = f"login_attempts:{email}"
    attempts = await redis.incr(key)
    if attempts == 1:
        await redis.expire(key, 60 * LOGIN_LOCKOUT_MINUTES)
    return attempts <= LOGIN_MAX_ATTEMPTS
```

### 2.5 Authentification à Deux Facteurs (Optionnel)

```python
# TOTP (Google Authenticator compatible)
import pyotp

# Génération secret pour l'utilisateur
secret = pyotp.random_base32()
totp = pyotp.TOTP(secret)

# Vérification code
def verify_2fa(user_secret: str, code: str) -> bool:
    totp = pyotp.TOTP(user_secret)
    return totp.verify(code, valid_window=1)
```

---

## 3. Autorisation (RBAC)

### 3.1 Matrice des Permissions

| Permission | ADMIN | RUA | RES | MSP | CONSULT |
|------------|-------|-----|-----|-----|---------|
| `users:manage` | ✓ | - | - | - | - |
| `units:manage` | ✓ | ✓ | - | - | - |
| `beneficiary:create` | ✓ | ✓ | ✓ | - | - |
| `beneficiary:read` | ✓ | ✓* | ✓* | ✓* | ✓* |
| `beneficiary:update` | ✓ | ✓* | ✓* | ✓** | - |
| `beneficiary:delete` | ✓ | - | - | - | - |
| `medical:read` | ✓ | ✓* | ✓* | ✓** | - |
| `medical:write` | ✓ | ✓* | ✓* | ✓** | - |
| `journal:create` | ✓ | ✓ | ✓ | ✓ | - |
| `journal:read` | ✓ | ✓* | ✓* | ✓* | ✓* |
| `objective:manage` | ✓ | ✓* | ✓* | ✓** | - |
| `report:generate` | ✓ | ✓ | ✓ | ✓ | - |
| `audit:read` | ✓ | ✓ | - | - | - |

*\* Limité à son unité*
*\*\* Limité à ses bénéficiaires référés*

### 3.2 Implémentation des Permissions

```python
# dependencies.py
from fastapi import Depends, HTTPException, status
from typing import List

class PermissionChecker:
    def __init__(self, required_permissions: List[str]):
        self.required_permissions = required_permissions

    async def __call__(self, current_user: User = Depends(get_current_user)):
        user_permissions = get_user_permissions(current_user)

        for permission in self.required_permissions:
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{permission}' required"
                )
        return current_user

# Utilisation
@router.get("/beneficiaries/{id}/medical")
async def get_medical_data(
    id: int,
    current_user: User = Depends(PermissionChecker(["medical:read"]))
):
    # Vérification supplémentaire: est-ce son bénéficiaire?
    beneficiary = await get_beneficiary(id)
    if not can_access_beneficiary(current_user, beneficiary):
        raise HTTPException(status_code=403, detail="Access denied")
    ...
```

### 3.3 Contrôle d'Accès aux Données

```python
# Filtrage automatique par unité/référent
async def get_accessible_beneficiaries(user: User) -> Query:
    query = select(Beneficiary)

    if user.role == "ADMIN":
        return query  # Accès total

    if user.role in ["RUA", "RES"]:
        # Accès à son unité
        return query.where(Beneficiary.unit_id == user.unit_id)

    if user.role == "MSP":
        # Accès à ses référés + lecture inter-unités
        return query.where(
            or_(
                Beneficiary.referent_id == user.id,
                Beneficiary.unit_id == user.unit_id
            )
        )

    if user.role == "CONSULT":
        return query.where(Beneficiary.unit_id == user.unit_id)
```

---

## 4. Protection des Données

### 4.1 Chiffrement au Repos

```python
# Chiffrement AES-256 pour données médicales
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class DataEncryption:
    def __init__(self, master_key: str):
        # Dérivation de clé
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=settings.ENCRYPTION_SALT.encode(),
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
        self.cipher = Fernet(key)

    def encrypt(self, data: str) -> str:
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        return self.cipher.decrypt(encrypted_data.encode()).decode()

# Utilisation dans le modèle
class BeneficiaryMedicalData(Base):
    __tablename__ = "beneficiary_medical_data"

    _medication = Column("medication", Text)  # Stocké chiffré

    @property
    def medication(self) -> str:
        if self._medication:
            return encryption.decrypt(self._medication)
        return None

    @medication.setter
    def medication(self, value: str):
        if value:
            self._medication = encryption.encrypt(value)
        else:
            self._medication = None
```

### 4.2 Chiffrement en Transit

```nginx
# nginx.conf - Configuration SSL/TLS
server {
    listen 443 ssl http2;
    server_name cis.example.ch;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    # Protocoles et ciphers sécurisés
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers on;

    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Autres headers sécurité
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';";
}
```

### 4.3 Anonymisation des Données

```python
# Pour exports statistiques ou suppression RGPD/LPD
def anonymize_beneficiary(beneficiary_id: int):
    """Anonymise un bénéficiaire tout en conservant les statistiques"""
    beneficiary = get_beneficiary(beneficiary_id)

    # Remplacement par données anonymes
    beneficiary.first_name = "ANONYME"
    beneficiary.last_name = f"#{beneficiary.id}"
    beneficiary.date_of_birth = anonymize_date(beneficiary.date_of_birth)
    beneficiary.address = None
    beneficiary.phone = None
    beneficiary.email = None
    beneficiary.photo_url = None

    # Suppression données médicales
    delete_medical_data(beneficiary_id)

    # Marquage
    beneficiary.is_anonymized = True
    beneficiary.anonymized_at = datetime.utcnow()
```

---

## 5. Protection OWASP Top 10

### 5.1 Injection SQL

```python
# ❌ Vulnérable
query = f"SELECT * FROM users WHERE email = '{email}'"

# ✓ Sécurisé avec SQLAlchemy
query = select(User).where(User.email == email)

# ✓ Sécurisé avec paramètres
query = text("SELECT * FROM users WHERE email = :email")
result = session.execute(query, {"email": email})
```

### 5.2 Cross-Site Scripting (XSS)

```python
# Backend: échappement automatique Pydantic
class JournalEntryCreate(BaseModel):
    title: str
    content: str

    @validator('content')
    def sanitize_content(cls, v):
        # Autoriser certaines balises HTML sécurisées
        import bleach
        return bleach.clean(
            v,
            tags=['p', 'br', 'strong', 'em', 'ul', 'ol', 'li'],
            strip=True
        )
```

```typescript
// Frontend: React échappe automatiquement
// ✓ Sécurisé
<div>{userInput}</div>

// ❌ Dangereux - éviter
<div dangerouslySetInnerHTML={{__html: userInput}} />
```

### 5.3 Cross-Site Request Forgery (CSRF)

```python
# Protection via tokens
from fastapi_csrf_protect import CsrfProtect

@app.post("/beneficiaries")
async def create_beneficiary(
    request: Request,
    csrf_protect: CsrfProtect = Depends()
):
    await csrf_protect.validate_csrf(request)
    ...
```

```typescript
// Frontend: envoi du token CSRF
axios.defaults.headers.common['X-CSRF-Token'] = getCsrfToken();
```

### 5.4 Broken Authentication

```python
# Sessions sécurisées
SESSION_CONFIG = {
    "cookie_name": "cis_session",
    "cookie_httponly": True,
    "cookie_secure": True,  # HTTPS only
    "cookie_samesite": "strict",
    "max_age": 3600 * 8,  # 8 heures
}

# Invalidation sessions à la déconnexion
async def logout(user_id: int, session_id: str):
    await redis.delete(f"session:{session_id}")
    await redis.sadd(f"invalidated_sessions:{user_id}", session_id)
```

### 5.5 Security Misconfiguration

```python
# config.py - Configuration sécurisée
class Settings(BaseSettings):
    # Pas de valeurs par défaut pour les secrets
    SECRET_KEY: str
    DATABASE_URL: str

    # Debug désactivé en production
    DEBUG: bool = False

    # CORS restrictif
    CORS_ORIGINS: List[str] = ["https://cis.example.ch"]

    class Config:
        env_file = ".env"
        case_sensitive = True
```

```yaml
# docker-compose.prod.yml
services:
  backend:
    environment:
      - DEBUG=false
      - ENVIRONMENT=production
    # Pas de ports exposés directement
    expose:
      - "8000"
```

### 5.6 Sensitive Data Exposure

```python
# Filtrage des réponses API
class BeneficiaryResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    # Pas de données sensibles par défaut

    class Config:
        # Exclure les champs sensibles
        fields = {
            'hashed_password': {'exclude': True},
            'ai_number': {'exclude': True},
        }

# Endpoint séparé pour données sensibles
@router.get("/beneficiaries/{id}/sensitive")
@require_permissions(["medical:read"])
async def get_sensitive_data(id: int):
    ...
```

---

## 6. Audit et Traçabilité

### 6.1 Structure des Logs d'Audit

```python
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(50))  # create, read, update, delete, login, export
    resource_type = Column(String(50))  # beneficiary, objective, journal, etc.
    resource_id = Column(Integer)
    old_values = Column(JSONB)  # Avant modification
    new_values = Column(JSONB)  # Après modification
    ip_address = Column(INET)
    user_agent = Column(Text)
    request_id = Column(String(36))  # UUID pour traçabilité

# Middleware d'audit automatique
@app.middleware("http")
async def audit_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    response = await call_next(request)

    # Log async en arrière-plan
    if should_audit(request):
        background_tasks.add_task(
            create_audit_log,
            request_id=request_id,
            user_id=request.state.user_id,
            action=get_action(request.method),
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )

    return response
```

### 6.2 Actions Auditées

| Action | Événement | Données enregistrées |
|--------|-----------|---------------------|
| Authentification | login, logout, failed_login | IP, user-agent, timestamp |
| Lecture données sensibles | read_medical, read_risk | user_id, beneficiary_id |
| Modifications | create, update, delete | old_values, new_values |
| Exports | export_pdf, export_excel | type, filtres, count |
| Administration | user_create, permission_change | details |

### 6.3 Rétention des Logs

```python
# Politique de rétention
AUDIT_RETENTION_DAYS = 730  # 2 ans

# Tâche de nettoyage périodique
@celery.task
def cleanup_old_audit_logs():
    cutoff_date = datetime.utcnow() - timedelta(days=AUDIT_RETENTION_DAYS)

    # Archivage avant suppression
    archive_audit_logs(before=cutoff_date)

    # Suppression
    AuditLog.query.filter(AuditLog.timestamp < cutoff_date).delete()
```

---

## 7. Conformité LPD (Loi sur la Protection des Données)

### 7.1 Principes LPD Appliqués

| Principe | Implémentation |
|----------|----------------|
| **Licéité** | Traitement uniquement pour accompagnement socioprofessionnel |
| **Bonne foi** | Transparence sur les traitements effectués |
| **Proportionnalité** | Collecte limitée aux données nécessaires |
| **Finalité** | Données utilisées uniquement pour leur but déclaré |
| **Exactitude** | Possibilité de correction par les utilisateurs |
| **Sécurité** | Mesures techniques et organisationnelles |

### 7.2 Droits des Personnes Concernées

```python
# Droit d'accès
@router.get("/privacy/my-data")
async def export_my_data(beneficiary_id: int):
    """Exporte toutes les données d'un bénéficiaire (format JSON/PDF)"""
    data = await collect_all_beneficiary_data(beneficiary_id)
    return generate_data_export(data)

# Droit de rectification
@router.patch("/privacy/rectify")
async def rectify_data(beneficiary_id: int, corrections: dict):
    """Permet de corriger des données inexactes"""
    await apply_corrections(beneficiary_id, corrections)
    await log_rectification(beneficiary_id, corrections)

# Droit à l'effacement
@router.post("/privacy/erase")
async def erase_data(beneficiary_id: int, reason: str):
    """Anonymise les données (conservation statistique)"""
    await anonymize_beneficiary(beneficiary_id)
    await log_erasure(beneficiary_id, reason)
```

### 7.3 Registre des Traitements

```python
# Documentation des traitements
PROCESSING_REGISTRY = {
    "beneficiary_management": {
        "purpose": "Suivi accompagnement socioprofessionnel",
        "legal_basis": "Contrat de prise en charge",
        "data_categories": ["identité", "contact", "professionnel"],
        "recipients": ["MSP", "Direction"],
        "retention": "5 ans après sortie",
        "security_measures": ["chiffrement", "contrôle accès", "audit"]
    },
    "medical_data": {
        "purpose": "Adaptation accompagnement selon contraintes médicales",
        "legal_basis": "Consentement explicite",
        "data_categories": ["santé"],
        "recipients": ["MSP référent uniquement"],
        "retention": "Durée accompagnement",
        "security_measures": ["chiffrement AES-256", "accès restreint", "audit renforcé"]
    }
}
```

### 7.4 Gestion du Consentement

```python
class Consent(Base):
    __tablename__ = "consents"

    id = Column(Integer, primary_key=True)
    beneficiary_id = Column(Integer, ForeignKey("beneficiaries.id"))
    consent_type = Column(String(50))  # medical_data, photo, data_sharing
    granted = Column(Boolean)
    granted_at = Column(DateTime)
    revoked_at = Column(DateTime, nullable=True)
    granted_by = Column(String(100))  # Nom de la personne ayant donné consentement
    witness = Column(String(100))  # Témoin si nécessaire
    document_id = Column(Integer, ForeignKey("documents.id"))  # Formulaire signé

# Vérification avant accès données médicales
async def check_medical_consent(beneficiary_id: int) -> bool:
    consent = await get_active_consent(beneficiary_id, "medical_data")
    return consent is not None and consent.granted
```

---

## 8. Gestion des Incidents

### 8.1 Procédure de Réponse

```
1. DÉTECTION
   - Alertes monitoring (Sentry, logs)
   - Signalement utilisateur
   - Détection automatique (patterns anormaux)

2. ÉVALUATION
   - Gravité (faible, moyenne, élevée, critique)
   - Données impactées
   - Nombre d'utilisateurs affectés

3. CONTAINMENT
   - Isolation du système si nécessaire
   - Révocation des accès compromis
   - Sauvegarde des preuves (logs)

4. NOTIFICATION
   - Direction (immédiat si critique)
   - Autorité de surveillance si données personnelles (72h)
   - Personnes concernées si risque élevé

5. REMÉDIATION
   - Correction de la vulnérabilité
   - Restauration des données si nécessaire
   - Mise à jour des procédures

6. POST-MORTEM
   - Analyse root cause
   - Documentation
   - Amélioration des contrôles
```

### 8.2 Classification des Incidents

| Niveau | Description | Délai réponse | Notification |
|--------|-------------|---------------|--------------|
| Critique | Breach données sensibles, système down | Immédiat | Direction + Autorités |
| Élevé | Tentative intrusion, données exposées | 1 heure | Direction |
| Moyen | Vulnérabilité détectée, anomalie accès | 4 heures | Équipe IT |
| Faible | Tentative login échouée, erreur config | 24 heures | Log uniquement |

---

## 9. Sauvegardes et Continuité

### 9.1 Stratégie de Backup

```bash
# Backup quotidien PostgreSQL
#!/bin/bash
BACKUP_DIR="/backup/postgres"
DATE=$(date +%Y%m%d_%H%M%S)

# Dump avec chiffrement
pg_dump -h localhost -U cis -d cis | \
  gpg --encrypt --recipient backup@example.ch > \
  "${BACKUP_DIR}/cis_${DATE}.sql.gpg"

# Rétention: 30 jours local, 1 an archive
find ${BACKUP_DIR} -name "*.gpg" -mtime +30 -delete
```

### 9.2 Plan de Reprise

| Scénario | RTO | RPO | Actions |
|----------|-----|-----|---------|
| Panne serveur | 4h | 24h | Restauration backup sur serveur secondaire |
| Corruption BDD | 2h | 1h | Restauration dernier backup valide |
| Ransomware | 8h | 24h | Isolation, restauration depuis backup offline |
| Catastrophe site | 24h | 24h | Activation site DR |

---

## 10. Checklist de Déploiement Sécurité

### 10.1 Avant Mise en Production

- [ ] Secrets en variables d'environnement (pas dans le code)
- [ ] DEBUG=false
- [ ] HTTPS activé avec certificat valide
- [ ] Headers de sécurité configurés (CSP, HSTS, etc.)
- [ ] Rate limiting activé
- [ ] CORS configuré restrictivement
- [ ] Logs d'audit activés
- [ ] Backup automatique configuré
- [ ] Monitoring/alerting configuré
- [ ] Scan de vulnérabilités passé
- [ ] Tests de pénétration effectués
- [ ] Documentation sécurité à jour
- [ ] Procédure incident documentée
- [ ] Formation utilisateurs effectuée

### 10.2 Contrôles Réguliers

| Fréquence | Contrôle |
|-----------|----------|
| Quotidien | Vérification backups, revue alertes |
| Hebdomadaire | Revue logs d'accès, mises à jour sécurité |
| Mensuel | Revue des permissions, audit accès |
| Trimestriel | Test de restauration, revue vulnérabilités |
| Annuel | Audit sécurité complet, test pénétration |
