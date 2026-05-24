// Bingo Card Generator Logic

export interface Song {
  title: string;
  artist: string;
}

export interface BingoCard {
  id: number;
  grid: Song[][]; // 5x5 grid
}

export const generateBingoCards = (
  songs: Song[],
  numCards: number,
  jackpot: boolean = false
): BingoCard[] => {
  const minRequired = jackpot ? 25 : 24;
  if (songs.length < minRequired) {
    throw new Error(
      `Not enough unique songs! Need at least ${minRequired}, but got ${songs.length}.`
    );
  }

  const cards: BingoCard[] = [];

  for (let i = 0; i < numCards; i++) {
    // 1. Select needed unique songs (shuffle and slice)
    // Create a copy to shuffle
    const shuffledPool = [...songs].sort(() => 0.5 - Math.random());
    const selection = shuffledPool.slice(0, minRequired);

    // 2. Shuffle the selection for grid placement
    const cardSongs = selection.sort(() => 0.5 - Math.random());

    // 3. Insert FREE SPACE at index 12 only if jackpot is disabled
    if (!jackpot) {
      const freeSpace: Song = { title: "FREE SPACE", artist: "" };
      cardSongs.splice(12, 0, freeSpace);
    }

    // 4. Reshape into 5x5 grid
    const grid: Song[][] = [];
    for (let row = 0; row < 5; row++) {
      grid.push(cardSongs.slice(row * 5, row * 5 + 5));
    }

    cards.push({ id: i + 1, grid });
  }

  return cards;
};
