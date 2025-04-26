# Proiect_IDP

## Proiect
Sistem de microservicii pentru gestionarea unui magazin digital de publicații, implementat în Python folosind FastAPI și Docker.

## Status
Proiect în dezvoltare activă, în prezent la Milestone 2.

## Descriere
Acest proiect reprezintă un sistem modern de gestionare a unui magazin digital de publicații, construit pe arhitectură de microservicii. Sistemul oferă funcționalități pentru:
- Autentificare și autorizare utilizatori
- Gestionarea produselor (publicații)
- Procesarea plăților
- Gestionarea bazei de date

Tehnologii principale utilizate:
- FastAPI pentru dezvoltarea API-urilor
- JWT pentru autentificare
- PostgreSQL pentru baza de date
- Docker și Docker Compose pentru containerizare
- Kong ca API Gateway
- GitHub Actions pentru CI/CD

## Arhitectura
Sistemul este bazat pe o arhitectură modernă de microservicii:

1. **API Gateway (Kong)** - Punctul central de acces pentru toate serviciile, gestionând rutarea și autorizarea
2. **Serviciul de Autentificare** - Gestionează înregistrarea utilizatorilor, autentificarea și generarea token-urilor JWT
3. **Serviciul de Bază de Date** - Interfață pentru interacțiunea cu baza de date PostgreSQL
4. **Serviciul de Produse** - Gestionează listarea și căutarea publicațiilor
5. **Serviciul de Plăți** - Procesează tranzacțiile pentru achiziționarea publicațiilor

Toate serviciile sunt containerizate folosind Docker și orchestrate prin Docker Compose.

## Contribuiri
Proiectul este dezvoltat de:
- Florin Romulescu (@Florin Romulescu) - Serviciu de autentificare, Kong API Gateway, CI/CD
- @ioio21 - Serviciu de bază de date, Serviciu de produse

Pentru a contribui la proiect:
1. Clonați repository-ul
2. Creați un branch nou pentru funcționalitatea dorită
3. Implementați schimbările
4. Trimiteți un pull request

Toate contribuțiile trebuie să respecte standardele de cod și să treacă testele automate din pipeline-ul CI/CD.
