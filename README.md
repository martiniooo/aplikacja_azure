# Aplikacja Azure - Lista wydatków domowych

Aplikacja webowa w Pythonie (Flask) do zarządzania wydatkami domowymi, wdrożona na Azure z GitHub Actions.

## Funkcjonalności
- Rejestracja i logowanie użytkowników.
- Dodawanie, edytowanie i usuwanie wydatków z kategoriami (dla zalogowanego użytkownika).
- Podsumowania tygodniowe i miesięczne z wykresami wizualnymi (Chart.js).
- Eksport danych do CSV.
- Przechowywanie danych w Azure SQL Database.

## Uruchomienie lokalne
1. Sklonuj: `git clone https://github.com/martiniooo/aplikacja_azure.git`
2. Utwórz środowisko: `python -m venv venv`
3. Aktywuj: `venv\Scripts\activate` (Windows)
4. Zainstaluj: `pip install -r requirements.txt`
5. Skonfiguruj connection string w `database.py`.
6. Uruchom: `python app.py`
7. Zarejestruj się i zaloguj, aby korzystać z aplikacji.

## Wdrożenie
Adres: [https://aplikacja-azure-bjdzf8asgrb9dwb5.azurewebsites.net](https://aplikacja-azure-bjdzf8asgrb9dwb5.azurewebsites.net)
- Aplikacja jest automatycznie wdrażana z GitHub Actions na Azure App Service.
- Folder `templates` zawiera szablony HTML (`index.html`, `summary.html`, `edit_expense.html`, `login.html`, `register.html`).

## Technologie
- Python 3.12
- Flask
- Chart.js (dla wykresów)
- Azure App Service (Polska Środkowa)
- Azure SQL Database (Polska Środkowa, LRS)
- GitHub Actions