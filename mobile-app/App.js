import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, Button, Alert, ScrollView, SafeAreaView, Platform, TextInput, Switch, ActivityIndicator, Keyboard, TouchableOpacity } from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import * as FileSystem from 'expo-file-system';
import * as Print from 'expo-print';
import * as Sharing from 'expo-sharing';
import { useState } from 'react';
import { parseM3U, parseWPL } from './src/utils/parser';
import { generateBingoCards } from './src/utils/generator';
import { fetchYouTubePlaylist, getPlaylistIdFromUrl } from './src/utils/youtube';

export default function App() {
  const [songs, setSongs] = useState([]);
  const [cards, setCards] = useState([]);
  const [numCards, setNumCards] = useState('10');
  const [showArtist, setShowArtist] = useState(true);
  const [jackpot, setJackpot] = useState(false);
  
  const [ytUrl, setYtUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const [isDarkMode, setIsDarkMode] = useState(false);
  
  const [playlistName, setPlaylistName] = useState('Music Bingo');
  const [suffix, setSuffix] = useState('Round 1');
  const [pageSize, setPageSize] = useState('A4');
  const [cardsPerSheet, setCardsPerSheet] = useState('2');

  const getCardsPerSheetOptions = (size) => {
    switch (size) {
      case 'A3':
        return ['1', '2', '4', '6', '8'];
      case 'A5':
        return ['1', '2'];
      case 'A4':
      case 'Letter':
      case 'Legal':
      default:
        return ['1', '2', '4'];
    }
  };

  const theme = {
    background: isDarkMode ? '#121212' : '#fff',
    text: isDarkMode ? '#eee' : '#000',
    container: isDarkMode ? '#1e1e1e' : '#f5f5f5',
    inputBackground: isDarkMode ? '#333' : '#fff',
    border: isDarkMode ? '#444' : '#ccc',
    placeholder: isDarkMode ? '#888' : '#666'
  };

  const pickDocument = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: ['*/*'], // M3U mime types can be tricky, */* is safer for now
        copyToCacheDirectory: true,
      });

      if (result.canceled) {
        return;
      }

      const fileUri = result.assets[0].uri;
      const fileContent = await FileSystem.readAsStringAsync(fileUri);
      
      const fileName = result.assets[0].name || "Playlist";
      const isWpl = fileName.toLowerCase().endsWith('.wpl');
      const parsedSongs = isWpl ? parseWPL(fileContent) : parseM3U(fileContent);
      setSongs(parsedSongs);
      setCards([]); // Reset cards on new import
      setYtUrl(''); // Clear URL input to avoid confusion
      
      const nameWithoutExt = fileName.replace(/\.[^/.]+$/, "");
      setPlaylistName(nameWithoutExt);
      
      Alert.alert('Success', `Loaded ${parsedSongs.length} songs from file!`);
      
    } catch (error) {
      console.error(error);
      Alert.alert('Error', 'Failed to read or parse file.');
    }
  };

  const handleYoutubeLoad = async () => {
    Keyboard.dismiss();
    const id = getPlaylistIdFromUrl(ytUrl);
    
    if (!id) {
      Alert.alert('Invalid URL', 'Please paste a valid YouTube Music playlist URL.');
      return;
    }

    setIsLoading(true);
    try {
      const { tracks, playlistName: fetchedName } = await fetchYouTubePlaylist(id);
      if (tracks.length === 0) {
        Alert.alert('No Songs Found', 'Could not extract songs. Is the playlist private?');
      } else {
        setSongs(tracks);
        setCards([]);
        if (fetchedName) {
          setPlaylistName(fetchedName);
        } else {
          setPlaylistName('YouTube Playlist');
        }
        Alert.alert('Success', `Loaded ${tracks.length} songs from YouTube!`);
      }
    } catch (error) {
      console.error(error);
      Alert.alert('Error', error.message || 'Failed to fetch playlist.');
    } finally {
      setIsLoading(false);
    }
  };

  const generateCards = () => {
    try {
      const count = parseInt(numCards);
      if (isNaN(count) || count < 1) {
        Alert.alert('Error', 'Please enter a valid number of cards.');
        return;
      }
      const generatedCards = generateBingoCards(songs, count, jackpot);
      setCards(generatedCards);
      Alert.alert('Generated', `Created ${generatedCards.length} bingo card(s)!`);
    } catch (error) {
      Alert.alert('Error', error.message);
    }
  };

  const generatePDF = async () => {
    try {
      const html = createHTML(cards);
      const { uri } = await Print.printToFileAsync({ html });
      console.log('File has been saved to:', uri);
      await Sharing.shareAsync(uri, { UTI: '.pdf', mimeType: 'application/pdf' });
    } catch (error) {
      console.error(error);
      Alert.alert('Error', 'Failed to generate PDF');
    }
  };

  const createHTML = (bingoCards) => {
    const countPerSheet = parseInt(cardsPerSheet);
    let sheetsHtml = '';
    
    for (let i = 0; i < bingoCards.length; i += countPerSheet) {
      const sheetCards = bingoCards.slice(i, i + countPerSheet);
      let sheetContent = '';
      
      sheetCards.forEach((card) => {
        let gridHtml = '';
        card.grid.forEach((row, rowIndex) => {
          row.forEach((cell, colIndex) => {
            let content = cell.title;
            if (showArtist && cell.artist) {
              content += `<br/><span class="artist">${cell.artist}</span>`;
            }
            const isFreeSpace = !jackpot && rowIndex === 2 && colIndex === 2;
            const cellClass = isFreeSpace ? 'cell free-space' : 'cell';
            gridHtml += `<div class="${cellClass}">${content}</div>`;
          });
        });
        
        sheetContent += `
          <div class="card">
            <div class="header">${playlistName} - ${suffix}</div>
            <div class="grid">
              ${gridHtml}
            </div>
          </div>
        `;
      });
      
      sheetsHtml += `
        <div class="sheet sheet-${countPerSheet}">
          ${sheetContent}
        </div>
      `;
    }

    let headerFontSize = '18px';
    let cellFontSize = '11px';
    let artistFontSize = '9px';
    let paddingSize = '8px';

    const count = parseInt(cardsPerSheet);
    const pageOrientation = (count === 1 || count === 4) ? 'landscape' : 'portrait';

    if (count === 1) {
      headerFontSize = '24px';
      cellFontSize = '14px';
      artistFontSize = '11px';
      paddingSize = '12px';
    } else if (count === 2) {
      headerFontSize = '18px';
      cellFontSize = '11px';
      artistFontSize = '9px';
      paddingSize = '8px';
    } else if (count === 4) {
      headerFontSize = '14px';
      cellFontSize = '8px';
      artistFontSize = '6.5px';
      paddingSize = '5px';
    } else { // 6 or 8
      headerFontSize = '10px';
      cellFontSize = '6.5px';
      artistFontSize = '5px';
      paddingSize = '3px';
    }

    return `
      <html>
        <head>
          <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no" />
          <style>
            @page { 
              size: ${pageSize} ${pageOrientation}; 
              margin: 0; 
            }
            body { 
              font-family: Helvetica, sans-serif; 
              -webkit-print-color-adjust: exact; 
              margin: 0;
              padding: 0;
              background-color: #fff;
            }
            .sheet {
              width: 100vw;
              height: 100vh;
              box-sizing: border-box;
              page-break-after: always;
              padding: 6mm;
              display: grid;
              gap: 4mm;
            }
            .sheet-1 {
              grid-template-columns: 1fr;
              grid-template-rows: 1fr;
            }
            .sheet-2 {
              grid-template-columns: 1fr;
              grid-template-rows: 1fr 1fr;
            }
            .sheet-4 {
              grid-template-columns: 1fr 1fr;
              grid-template-rows: 1fr 1fr;
            }
            .sheet-6 {
              grid-template-columns: 1fr 1fr;
              grid-template-rows: 1fr 1fr 1fr;
            }
            .sheet-8 {
              grid-template-columns: 1fr 1fr;
              grid-template-rows: 1fr 1fr 1fr 1fr;
            }
            .card { 
              display: flex; 
              flex-direction: column; 
              border: 2px solid #333; 
              box-sizing: border-box;
              width: 100%;
              height: 100%;
              overflow: hidden;
            }
            .header { 
              text-align: center; 
              font-weight: bold; 
              font-size: ${headerFontSize}; 
              padding: ${paddingSize}; 
              background-color: #eee;
              border-bottom: 1px solid #333;
            }
            .grid { 
              display: grid; 
              grid-template-columns: repeat(5, 1fr); 
              grid-template-rows: repeat(5, 1fr); 
              flex: 1; 
            }
            .cell { 
              border: 1px solid #ccc; 
              display: flex; 
              flex-direction: column;
              align-items: center; 
              justify-content: center; 
              text-align: center; 
              padding: 2px; 
              font-size: ${cellFontSize}; 
              overflow: hidden;
              box-sizing: border-box;
            }
            .free-space {
              background-color: #eee;
              font-weight: bold;
            }
            .artist {
              font-size: ${artistFontSize};
              color: #555;
              margin-top: 1px;
            }
          </style>
        </head>
        <body>
          ${sheetsHtml}
        </body>
      </html>
    `;
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.background }]}>
      <View style={styles.content}>
        <Text style={[styles.title, { color: theme.text }]}>Music Bingo Generator</Text>
        
        {/* YouTube Section */}
        <View style={styles.inputContainer}>
           <Text style={[styles.label, { color: theme.text }]}>YouTube Playlist URL:</Text>
           <View style={styles.rowContainer}>
             <TextInput
               style={[styles.input, { flex: 1, marginRight: 10, width: 'auto', backgroundColor: theme.inputBackground, color: theme.text, borderColor: theme.border }]}
               placeholder="https://music.youtube.com/..."
               placeholderTextColor={theme.placeholder}
               value={ytUrl}
               onChangeText={setYtUrl}
               autoCapitalize="none"
               autoCorrect={false}
             />
             <Button 
               title={isLoading ? "..." : "Load"} 
               onPress={handleYoutubeLoad} 
               disabled={isLoading}
             />
           </View>
        </View>

        <Text style={[styles.orText, { color: theme.placeholder }]}>- OR -</Text>

        {/* File Picker Section */}
        <View style={styles.buttonContainer}>
          <Button title="Select Playlist File (.m3u/.wpl)" onPress={pickDocument} />
        </View>

        <Text style={[styles.stats, { color: theme.text }]}>
          {songs.length > 0 ? `${songs.length} songs loaded` : 'No playlist loaded'}
        </Text>

        <View style={[styles.settingsContainer, { backgroundColor: theme.container }]}>
           <View style={styles.settingRow}>
              <Text style={{ color: theme.text }}>Playlist Name:</Text>
              <TextInput
                style={[styles.input, { width: 180, backgroundColor: theme.inputBackground, color: theme.text, borderColor: theme.border }]}
                value={playlistName}
                onChangeText={setPlaylistName}
              />
           </View>
           <View style={styles.settingRow}>
              <Text style={{ color: theme.text }}>Title Suffix:</Text>
              <TextInput
                style={[styles.input, { width: 180, backgroundColor: theme.inputBackground, color: theme.text, borderColor: theme.border }]}
                value={suffix}
                onChangeText={setSuffix}
              />
           </View>
           <View style={styles.settingRow}>
              <Text style={{ color: theme.text }}>Page Size:</Text>
              <View style={styles.pillContainer}>
                {['A3', 'A4', 'A5', 'Letter', 'Legal'].map((size) => {
                  const isSelected = pageSize === size;
                  return (
                    <TouchableOpacity
                      key={size}
                      style={[
                        styles.pill,
                        { backgroundColor: isSelected ? '#007AFF' : theme.inputBackground, borderColor: theme.border }
                      ]}
                      onPress={() => {
                        setPageSize(size);
                        const allowed = getCardsPerSheetOptions(size);
                        if (!allowed.includes(cardsPerSheet)) {
                          setCardsPerSheet(allowed[allowed.length - 1]);
                        }
                      }}
                    >
                      <Text style={[styles.pillText, { color: isSelected ? '#fff' : theme.text }]}>{size}</Text>
                    </TouchableOpacity>
                  );
                })}
              </View>
           </View>
           <View style={styles.settingRow}>
              <Text style={{ color: theme.text }}>Cards per Sheet:</Text>
              <View style={styles.pillContainer}>
                {getCardsPerSheetOptions(pageSize).map((num) => {
                  const isSelected = cardsPerSheet === num;
                  return (
                    <TouchableOpacity
                      key={num}
                      style={[
                        styles.pill,
                        { backgroundColor: isSelected ? '#007AFF' : theme.inputBackground, borderColor: theme.border }
                      ]}
                      onPress={() => setCardsPerSheet(num)}
                    >
                      <Text style={[styles.pillText, { color: isSelected ? '#fff' : theme.text }]}>{num}</Text>
                    </TouchableOpacity>
                  );
                })}
              </View>
           </View>
           <View style={styles.settingRow}>
              <Text style={{ color: theme.text }}>Number of Cards:</Text>
              <TextInput
                style={[styles.numberInput, { backgroundColor: theme.inputBackground, color: theme.text, borderColor: theme.border }]}
                value={numCards}
                onChangeText={setNumCards}
                keyboardType="numeric"
              />
           </View>
           <View style={styles.settingRow}>
              <Text style={{ color: theme.text }}>Show Artist:</Text>
              <Switch
                value={showArtist}
                onValueChange={setShowArtist}
              />
           </View>
           <View style={styles.settingRow}>
              <Text style={{ color: theme.text }}>Jackpot Mode:</Text>
              <Switch
                value={jackpot}
                onValueChange={setJackpot}
              />
           </View>
           <View style={styles.settingRow}>
              <Text style={{ color: theme.text }}>Dark Mode:</Text>
              <Switch
                value={isDarkMode}
                onValueChange={setIsDarkMode}
              />
           </View>
        </View>

        <View style={styles.buttonContainer}>
          <Button 
            title="Generate Bingo Cards" 
            onPress={generateCards} 
            disabled={songs.length < (jackpot ? 25 : 24)}
          />
        </View>

        {cards.length > 0 && (
          <View style={styles.buttonContainer}>
            <Button 
              title="Save / Share PDF" 
              onPress={generatePDF} 
            />
          </View>
        )}

        {cards.length > 0 && (
          <ScrollView style={[styles.preview, { borderColor: theme.border }]}>
            <Text style={[styles.previewTitle, { color: theme.text }]}>Preview Card 1:</Text>
            {cards[0].grid.map((row, rIndex) => (
              <View key={rIndex} style={styles.row}>
                {row.map((cell, cIndex) => {
                  const isFreeSpace = !jackpot && rIndex === 2 && cIndex === 2;
                  return (
                    <Text 
                      key={cIndex} 
                      style={[
                        styles.cell, 
                        { color: theme.text, borderColor: theme.border },
                        isFreeSpace && { backgroundColor: isDarkMode ? '#333' : '#eee', fontWeight: 'bold' }
                      ]} 
                      numberOfLines={2}
                    >
                      {cell.title}
                      {showArtist && cell.artist ? `\n${cell.artist}` : ''}
                    </Text>
                  );
                })}
              </View>
            ))}
          </ScrollView>
        )}
        
        <StatusBar style={isDarkMode ? "light" : "auto"} />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    flex: 1,
    padding: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    marginTop: 40,
  },
  buttonContainer: {
    marginVertical: 10,
    width: '100%',
  },
  inputContainer: {
    width: '100%',
    marginVertical: 10,
  },
  rowContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  label: {
    fontWeight: 'bold',
    marginBottom: 5,
  },
  orText: {
    marginVertical: 10,
  },
  stats: {
    marginVertical: 10,
    fontSize: 16,
  },
  settingsContainer: {
    width: '100%',
    padding: 10,
    borderRadius: 8,
    marginVertical: 10,
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginVertical: 5,
  },
  input: {
    borderWidth: 1,
    borderRadius: 5,
    padding: 8,
  },
  numberInput: {
    borderWidth: 1,
    borderRadius: 5,
    padding: 5,
    width: 60,
    textAlign: 'center',
  },
  preview: {
    marginTop: 20,
    width: '100%',
    maxHeight: 250,
    borderWidth: 1,
  },
  previewTitle: {
    fontWeight: 'bold',
    padding: 10,
  },
  row: {
    flexDirection: 'row',
  },
  cell: {
    flex: 1,
    fontSize: 10,
    borderWidth: 0.5,
    padding: 2,
    height: 40,
    textAlign: 'center',
    textAlignVertical: 'center',
  },
  pillContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'flex-end',
    flex: 0.7,
  },
  pill: {
    borderWidth: 1,
    borderRadius: 15,
    paddingHorizontal: 8,
    paddingVertical: 4,
    marginLeft: 5,
    marginBottom: 5,
    alignItems: 'center',
    justifyContent: 'center',
  },
  pillText: {
    fontSize: 11,
    fontWeight: 'bold',
  },
});