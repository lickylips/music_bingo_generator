import random

class BingoGenerator:
    def generate_cards(self, songs, num_cards):
        """
        Generates 'num_cards' unique bingo grids.
        songs: list of {'title': str, 'artist': str}
        Returns: list of 5x5 matrices (lists of lists of dicts).
        """
        if len(songs) < 24:
            raise ValueError(f"Not enough unique songs! Need at least 24, but got {len(songs)}.")

        cards = []
        for _ in range(num_cards):
            # 1. Select 24 unique songs
            # Note: If len(songs) == 24, we just use them all.
            # If > 24, we pick a random subset.
            selection = random.sample(songs, 24)
            
            # 2. Shuffle the selection for grid placement
            # (Sample already shuffles if we picked a subset, but explicit shuffle is safe)
            random.shuffle(selection)
            
            # 3. Insert FREE SPACE at index 12 (Center of 5x5)
            # Center of 5x5 (indices 0-24) is 12.
            selection.insert(12, {'title': "FREE SPACE", 'artist': ""})
            
            # 4. Reshape into 5x5 grid
            grid = []
            for i in range(0, 25, 5):
                row = selection[i : i+5]
                grid.append(row)
            
            cards.append(grid)
            
        return cards