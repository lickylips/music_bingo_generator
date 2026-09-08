import random

class BingoGenerator:
    def generate_cards(self, songs, num_cards, jackpot=False):
        """
        Generates 'num_cards' unique bingo grids.
        songs: list of {'title': str, 'artist': str}
        Returns: list of 5x5 matrices (lists of lists of dicts).
        """
        # Deduplicate songs based on title and artist (case-insensitive)
        unique_songs = []
        seen = set()
        for s in songs:
            title_clean = s['title'].strip().lower()
            artist_clean = s['artist'].strip().lower() if s['artist'] else ""
            identifier = (title_clean, artist_clean)
            if identifier not in seen:
                seen.add(identifier)
                unique_songs.append(s)

        min_required = 25 if jackpot else 24
        if len(unique_songs) < min_required:
            raise ValueError(f"Not enough unique songs! Need at least {min_required}, but only got {len(unique_songs)}.")

        cards = []
        for _ in range(num_cards):
            # 1. Select unique songs
            selection = random.sample(unique_songs, min_required)
            
            # 2. Shuffle the selection for grid placement
            random.shuffle(selection)
            
            # 3. Insert FREE SPACE at index 12 (Center of 5x5) only if jackpot is disabled
            if not jackpot:
                selection.insert(12, {'title': "FREE SPACE", 'artist': ""})
            
            # 4. Reshape into 5x5 grid
            grid = []
            for i in range(0, 25, 5):
                row = selection[i : i+5]
                grid.append(row)
            
            cards.append(grid)
            
        return cards