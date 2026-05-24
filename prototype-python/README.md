# Music Bingo App

A tool to generate printable music bingo sheets from digital playlists (local .m3u or YouTube Music).

## Features
- **Input:** Local `.m3u` files or YouTube Music playlist URLs.
- **Output:** Printable PDF with randomized 5x5 bingo cards.
- **Layout:** 2 cards per A4 page.
- **Uniqueness:** Guarantees unique cards.

## Setup
1. Create a virtual environment: `python3 -m venv venv`
2. Activate it: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
3. Install dependencies: `pip install -r requirements.txt`
4. Run the app: `streamlit run src/app.py`
