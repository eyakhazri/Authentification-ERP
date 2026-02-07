import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from backend.app.core.config import settings
from app.core.security import get_password_hash
from app.models import create_all_indexes
 
# Sample data
USERS = [
    {
        "nom": "Admin",
        "prenom": "System",
        "email": "admin@ragchat.com",
        "passwordHash": get_password_hash("admin123"),
        "actif": True,
        "role": "ADMIN",
        "dateCreation": datetime.utcnow()
    },
    {
        "nom": "Dupont",
        "prenom": "Marie",
        "email": "marie@ragchat.com",
        "passwordHash": get_password_hash("marie123"),
        "actif": True,
        "role": "SUPERVISEUR",
        "dateCreation": datetime.utcnow()
    },
    {
        "nom": "Martin",
        "prenom": "Jean",
        "email": "jean@ragchat.com",
        "passwordHash": get_password_hash("jean123"),
        "actif": True,
        "role": "EMPLOYE",
        "dateCreation": datetime.utcnow()
    },
    {
        "nom": "Bernard",
        "prenom": "Sophie",
        "email": "sophie@ragchat.com",
        "passwordHash": get_password_hash("sophie123"),
        "actif": True,
        "role": "EMPLOYE",
        "dateCreation": datetime.utcnow()
    }
]
 
CATEGORIES = [
    {"nom": "Logiciels", "description": "Logiciels et applications", "dateCreation": datetime.utcnow()},
    {"nom": "Services", "description": "Services de conseil et support", "dateCreation": datetime.utcnow()},
    {"nom": "Formation", "description": "Formations et certifications", "dateCreation": datetime.utcnow()},
    {"nom": "Matériel", "description": "Équipements informatiques", "dateCreation": datetime.utcnow()}
]
 
CLIENTS = [
    {
        "nom": "Dubois",
        "prenom": "Pierre",
        "email": "pierre@client.com",
        "telephone": "0612345678",
        "entreprise": "Dubois SARL",
        "adresse": "12 Rue de Paris, 75001 Paris",
        "type": "ENTREPRISE",
        "dateCreation": datetime.utcnow()
    },
    {
        "nom": "Lefebvre",
        "prenom": "Marie",
        "email": "marie.l@email.com",
        "telephone": "0698765432",
        "entreprise": "",
        "adresse": "45 Avenue des Champs, Lyon",
        "type": "PARTICULIER",
        "dateCreation": datetime.utcnow()
    },
    {
        "nom": "Moreau",
        "prenom": "Lucas",
        "email": "lucas@techcorp.fr",
        "telephone": "0678901234",
        "entreprise": "TechCorp",
        "adresse": "78 Boulevard Industriel, Marseille",
        "type": "ENTREPRISE",
        "dateCreation": datetime.utcnow()
    }
]
 
PROSPECTS = [
    {
        "nom": "Garcia",
        "prenom": "Ana",
        "email": "ana@prospect.com",
        "telephone": "0633445566",
        "entreprise": "Garcia Design",
        "statut": "CONTACTE",
        "dateCreation": datetime.utcnow()
    },
    {
        "nom": "Lambert",
        "prenom": "Marc",
        "email": "marc.lambert@email.com",
        "telephone": "0677889900",
        "entreprise": "",
        "statut": "NOUVEAU",
        "dateCreation": datetime.utcnow()
    }
]
 
 
async def init_database():
    """Initialize database with sample data."""
    print("Connecting to MongoDB...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
   
    print("Creating indexes...")
    await create_all_indexes(db)
   
    print("Clearing existing data...")
    await db.authentification.delete_many({})
    await db.categories.delete_many({})
    await db.clients.delete_many({})
    await db.prospects.delete_many({})
    await db.produits.delete_many({})
    await db.commandes.delete_many({})
    await db.lignes_commande.delete_many({})
    await db.factures.delete_many({})
    await db.paiements.delete_many({})
    await db.interactions.delete_many({})
    await db.rapports.delete_many({})
   
    print("Inserting users...")
    result = await db.authentification.insert_many(USERS)
    user_ids = [str(id) for id in result.inserted_ids]
   
    print("Inserting categories...")
    result = await db.categories.insert_many(CATEGORIES)
    category_ids = [str(id) for id in result.inserted_ids]
   
    print("Inserting products...")
    products = [
        {
            "nom": "Licence CRM Pro",
            "description": "Licence professionnelle CRM",
            "prix": 299,
            "stock": 999,
            "disponible": True,
            "categorieId": category_ids[0],
            "dateCreation": datetime.utcnow()
        },
        {
            "nom": "Licence CRM Enterprise",
            "description": "Licence entreprise CRM",
            "prix": 799,
            "stock": 999,
            "disponible": True,
            "categorieId": category_ids[0],
            "dateCreation": datetime.utcnow()
        },
        {
            "nom": "Support Technique",
            "description": "Support technique annuel",
            "prix": 1200,
            "stock": 999,
            "disponible": True,
            "categorieId": category_ids[1],
            "dateCreation": datetime.utcnow()
        },
        {
            "nom": "Formation Utilisateur",
            "description": "Formation complète utilisateur",
            "prix": 500,
            "stock": 50,
            "disponible": True,
            "categorieId": category_ids[2],
            "dateCreation": datetime.utcnow()
        }
    ]
    result = await db.produits.insert_many(products)
    product_ids = [str(id) for id in result.inserted_ids]
   
    print("Inserting clients...")
    result = await db.clients.insert_many(CLIENTS)
    client_ids = [str(id) for id in result.inserted_ids]
   
    print("Inserting prospects...")
    await db.prospects.insert_many(PROSPECTS)
   
    print("Inserting sample orders...")
    orders = [
        {
            "dateCommande": "2024-03-01",
            "statut": "LIVREE",
            "montantTotal": 2099,
            "notes": "Installation incluse",
            "clientId": client_ids[0],
            "userId": user_ids[2],
            "dateCreation": datetime.utcnow()
        },
        {
            "dateCommande": "2024-03-05",
            "statut": "CONFIRMEE",
            "montantTotal": 299,
            "notes": "",
            "clientId": client_ids[1],
            "userId": user_ids[2],
            "dateCreation": datetime.utcnow()
        }
    ]
    result = await db.commandes.insert_many(orders)
    order_ids = [str(id) for id in result.inserted_ids]
   
    print("Inserting order lines...")
    order_lines = [
        {
            "quantite": 1,
            "prixUnitaire": 799,
            "sousTotal": 799,
            "commandeId": order_ids[0],
            "produitId": product_ids[1],
            "dateCreation": datetime.utcnow()
        },
        {
            "quantite": 1,
            "prixUnitaire": 1200,
            "sousTotal": 1200,
            "commandeId": order_ids[0],
            "produitId": product_ids[2],
            "dateCreation": datetime.utcnow()
        },
        {
            "quantite": 1,
            "prixUnitaire": 299,
            "sousTotal": 299,
            "commandeId": order_ids[1],
            "produitId": product_ids[0],
            "dateCreation": datetime.utcnow()
        }
    ]
    await db.lignes_commande.insert_many(order_lines)
   
    print("Inserting invoices...")
    invoices = [
        {
            "numeroFacture": "FAC-2024-001",
            "dateEmission": "2024-03-01",
            "montantTotal": 2099,
            "statutPaiement": "PAYEE",
            "datePaiement": "2024-03-05",
            "commandeId": order_ids[0],
            "clientId": client_ids[0],
            "dateCreation": datetime.utcnow()
        },
        {
            "numeroFacture": "FAC-2024-002",
            "dateEmission": "2024-03-05",
            "montantTotal": 299,
            "statutPaiement": "EN_ATTENTE",
            "commandeId": order_ids[1],
            "clientId": client_ids[1],
            "dateCreation": datetime.utcnow()
        }
    ]
    result = await db.factures.insert_many(invoices)
    invoice_ids = [str(id) for id in result.inserted_ids]
   
    print("Inserting payments...")
    payments = [
        {
            "montant": 2099,
            "methode": "VIREMENT",
            "datePaiement": "2024-03-05",
            "reference": "VIR-001",
            "factureId": invoice_ids[0],
            "dateCreation": datetime.utcnow()
        }
    ]
    await db.paiements.insert_many(payments)
   
    print("Inserting interactions...")
    interactions = [
        {
            "type": "APPEL",
            "description": "Présentation produit",
            "date": "2024-03-02",
            "userId": user_ids[2],
            "clientId": client_ids[0],
            "dateCreation": datetime.utcnow()
        },
        {
            "type": "EMAIL",
            "description": "Envoi devis",
            "date": "2024-03-03",
            "userId": user_ids[2],
            "dateCreation": datetime.utcnow()
        }
    ]
    await db.interactions.insert_many(interactions)
   
    print("\n✅ Database initialized successfully!")
    print(f"Created {len(USERS)} users")
    print(f"Created {len(CATEGORIES)} categories")
    print(f"Created {len(products)} products")
    print(f"Created {len(CLIENTS)} clients")
    print(f"Created {len(PROSPECTS)} prospects")
    print("\nTest credentials:")
    print("  Admin: admin@ragchat.com / admin123")
    print("  Manager: marie@ragchat.com / marie123")
    print("  Employee: jean@ragchat.com / jean123")
   
    client.close()
 
 
if __name__ == "__main__":
    asyncio.run(init_database())