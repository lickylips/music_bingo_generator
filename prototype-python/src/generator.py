import random

class BingoGenerator:
    def generate_cards(self, songs, num_cards, jackpot=False):
        """
        Generates 'num_cards' unique bingo grids.
        songs: list of {'title': str, 'artist': str}
        Returns: list of 5x5 matrices (lists of lists of dicts).
        """
        min_required = 25 if jackpot else 24
        if len(songs) < min_required:
            raise ValueError(f"Not enough unique songs! Need at least {min_required}, but got {len(songs)}.")

        cards = []
        for _ in range(num_cards):
            # 1. Select unique songs
            selection = random.sample(songs, min_required)
            
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