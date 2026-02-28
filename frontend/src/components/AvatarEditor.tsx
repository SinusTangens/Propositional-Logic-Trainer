import { useState, useEffect } from 'react';
import { X, Shuffle, Check, ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from './ui/button';
import { AvatarSettings, updateAvatar } from '../services/api';

interface AvatarEditorProps {
  isOpen: boolean;
  onClose: () => void;
  currentAvatar: AvatarSettings;
  onAvatarUpdate: (avatar: AvatarSettings) => void;
}

// Avatar-Optionen für DiceBear Avataaars
const AVATAR_OPTIONS = {
  skinColor: {
    label: 'Hautfarbe',
    options: [
      { value: 'ffdbb4', label: 'Hell', color: '#FFDBB4' },
      { value: 'edb98a', label: 'Leicht', color: '#EDB98A' },
      { value: 'd08b5b', label: 'Gebräunt', color: '#D08B5B' },
      { value: 'ae5d29', label: 'Braun', color: '#AE5D29' },
      { value: '614335', label: 'Dunkelbraun', color: '#614335' },
      { value: '3c2416', label: 'Schwarz', color: '#3C2416' },
    ]
  },
  hairColor: {
    label: 'Haarfarbe',
    options: [
      { value: '2c1b18', label: 'Schwarz', color: '#2C1B18' },
      { value: '4a312c', label: 'Dunkelbraun', color: '#4A312C' },
      { value: '724133', label: 'Braun', color: '#724133' },
      { value: 'a55728', label: 'Kastanie', color: '#A55728' },
      { value: 'c93305', label: 'Rot', color: '#C93305' },
      { value: 'b58143', label: 'Blond', color: '#B58143' },
      { value: 'd6b370', label: 'Goldblond', color: '#D6B370' },
      { value: 'ecdcbf', label: 'Platin', color: '#ECDCBF' },
    ]
  },
  top: {
    label: 'Frisur / Kopf',
    options: [
      // Kurzhaar
      { value: 'shortFlat', label: 'Kurz Flach', category: 'Kurzhaar' },
      { value: 'shortCurly', label: 'Kurz Lockig', category: 'Kurzhaar' },
      { value: 'shortRound', label: 'Kurz Rund', category: 'Kurzhaar' },
      { value: 'shortWaved', label: 'Kurz Wellig', category: 'Kurzhaar' },
      { value: 'sides', label: 'Seiten', category: 'Kurzhaar' },
      { value: 'dreads01', label: 'Dreads 1', category: 'Kurzhaar' },
      { value: 'dreads02', label: 'Dreads 2', category: 'Kurzhaar' },
      { value: 'frizzle', label: 'Gelockt', category: 'Kurzhaar' },
      { value: 'theCaesar', label: 'Caesar', category: 'Kurzhaar' },
      { value: 'theCaesarAndSidePart', label: 'Caesar Seite', category: 'Kurzhaar' },
      { value: 'shaggy', label: 'Struppig', category: 'Kurzhaar' },
      { value: 'shaggyMullet', label: 'Vokuhila', category: 'Kurzhaar' },
      // Langhaar
      { value: 'bob', label: 'Bob', category: 'Langhaar' },
      { value: 'bun', label: 'Dutt', category: 'Langhaar' },
      { value: 'curly', label: 'Lockig Lang', category: 'Langhaar' },
      { value: 'curvy', label: 'Wellig Lang', category: 'Langhaar' },
      { value: 'dreads', label: 'Dreads Lang', category: 'Langhaar' },
      { value: 'fro', label: 'Afro', category: 'Langhaar' },
      { value: 'froBand', label: 'Afro + Band', category: 'Langhaar' },
      { value: 'straight01', label: 'Glatt 1', category: 'Langhaar' },
      { value: 'straight02', label: 'Glatt 2', category: 'Langhaar' },
      { value: 'straightAndStrand', label: 'Glatt Strähne', category: 'Langhaar' },
      { value: 'miaWallace', label: 'Mia', category: 'Langhaar' },
      { value: 'longButNotTooLong', label: 'Mittel', category: 'Langhaar' },
      { value: 'bigHair', label: 'Volumen', category: 'Langhaar' },
      { value: 'frida', label: 'Frida', category: 'Langhaar' },
      { value: 'shavedSides', label: 'Rasierte Seiten', category: 'Langhaar' },
      // Kopfbedeckung
      { value: 'hat', label: 'Hut', category: 'Kopfbedeckung' },
      { value: 'hijab', label: 'Hijab', category: 'Kopfbedeckung' },
      { value: 'turban', label: 'Turban', category: 'Kopfbedeckung' },
      { value: 'winterHat1', label: 'Wintermütze 1', category: 'Kopfbedeckung' },
      { value: 'winterHat02', label: 'Wintermütze 2', category: 'Kopfbedeckung' },
      { value: 'winterHat03', label: 'Wintermütze 3', category: 'Kopfbedeckung' },
      { value: 'winterHat04', label: 'Wintermütze 4', category: 'Kopfbedeckung' },
    ]
  },
  accessories: {
    label: 'Accessoires',
    options: [
      { value: '', label: 'Keine' },
      { value: 'prescription01', label: 'Brille 1' },
      { value: 'prescription02', label: 'Brille 2' },
      { value: 'round', label: 'Runde Brille' },
      { value: 'sunglasses', label: 'Sonnenbrille' },
      { value: 'wayfarers', label: 'Wayfarer' },
      { value: 'kurt', label: 'Kurt-Brille' },
    ]
  },
  facialHair: {
    label: 'Bart',
    options: [
      { value: '', label: 'Kein Bart' },
      { value: 'beardLight', label: 'Leichter Bart' },
      { value: 'beardMedium', label: 'Mittlerer Bart' },
      { value: 'beardMajestic', label: 'Voller Bart' },
      { value: 'moustacheFancy', label: 'Schnurrbart Edel' },
      { value: 'moustacheMagnum', label: 'Schnurrbart Magnum' },
    ]
  },
  eyes: {
    label: 'Augen',
    options: [
      { value: 'default', label: 'Normal' },
      { value: 'happy', label: 'Fröhlich' },
      { value: 'wink', label: 'Zwinkern' },
      { value: 'winkWacky', label: 'Verrückt' },
      { value: 'squint', label: 'Zugekniffen' },
      { value: 'surprised', label: 'Überrascht' },
      { value: 'side', label: 'Seitlich' },
      { value: 'hearts', label: 'Herzen' },
      { value: 'closed', label: 'Geschlossen' },
      { value: 'cry', label: 'Tränen' },
      { value: 'xDizzy', label: 'Schwindelig' },
      { value: 'eyeRoll', label: 'Rollen' },
    ]
  },
  eyebrows: {
    label: 'Augenbrauen',
    options: [
      { value: 'default', label: 'Normal' },
      { value: 'defaultNatural', label: 'Natürlich' },
      { value: 'flatNatural', label: 'Flach' },
      { value: 'raisedExcited', label: 'Angehoben' },
      { value: 'raisedExcitedNatural', label: 'Erstaunt' },
      { value: 'sadConcerned', label: 'Traurig' },
      { value: 'sadConcernedNatural', label: 'Besorgt' },
      { value: 'angry', label: 'Wütend' },
      { value: 'angryNatural', label: 'Ärgerlich' },
      { value: 'upDown', label: 'Hoch/Tief' },
      { value: 'upDownNatural', label: 'Asymmetrisch' },
      { value: 'unibrowNatural', label: 'Monobraue' },
    ]
  },
  mouth: {
    label: 'Mund',
    options: [
      { value: 'default', label: 'Normal' },
      { value: 'smile', label: 'Lächeln' },
      { value: 'twinkle', label: 'Breit Lächeln' },
      { value: 'serious', label: 'Ernst' },
      { value: 'concerned', label: 'Besorgt' },
      { value: 'disbelief', label: 'Ungläubig' },
      { value: 'sad', label: 'Traurig' },
      { value: 'grimace', label: 'Grimasse' },
      { value: 'eating', label: 'Essend' },
      { value: 'tongue', label: 'Zunge' },
      { value: 'screamOpen', label: 'Schreien' },
      { value: 'vomit', label: 'Krank' },
    ]
  },
  clothing: {
    label: 'Kleidung',
    options: [
      { value: 'blazerAndShirt', label: 'Blazer + Hemd' },
      { value: 'blazerAndSweater', label: 'Blazer + Pullover' },
      { value: 'collarAndSweater', label: 'Kragen-Pullover' },
      { value: 'hoodie', label: 'Hoodie' },
      { value: 'overall', label: 'Overall' },
      { value: 'shirtCrewNeck', label: 'Rundhals-Shirt' },
      { value: 'shirtScoopNeck', label: 'Ausschnitt-Shirt' },
      { value: 'shirtVNeck', label: 'V-Ausschnitt' },
      { value: 'graphicShirt', label: 'Grafik-Shirt' },
    ]
  },
  clothingColor: {
    label: 'Kleidungsfarbe',
    options: [
      { value: '262e33', label: 'Schwarz', color: '#262E33' },
      { value: '65c9ff', label: 'Blau Hell', color: '#65C9FF' },
      { value: '929598', label: 'Grau', color: '#929598' },
      { value: '3c4f5c', label: 'Heather', color: '#3C4F5C' },
      { value: 'ffffff', label: 'Weiß', color: '#FFFFFF' },
      { value: 'ff5c5c', label: 'Rot', color: '#FF5C5C' },
      { value: 'ffafb9', label: 'Pastell Rot', color: '#FFAFB9' },
      { value: '5199e4', label: 'Blau', color: '#5199E4' },
      { value: '25557c', label: 'Blau Dunkel', color: '#25557C' },
      { value: 'b1e2ff', label: 'Pastell Blau', color: '#B1E2FF' },
      { value: 'a7ffc4', label: 'Pastell Grün', color: '#A7FFC4' },
      { value: 'ffdeb5', label: 'Pastell Orange', color: '#FFDEB5' },
      { value: 'ffffb1', label: 'Pastell Gelb', color: '#FFFFB1' },
      { value: 'ff488e', label: 'Pink', color: '#FF488E' },
      { value: 'e6544f', label: 'HKA Rot', color: '#E6544F' },
    ]
  },
};

type AvatarField = keyof typeof AVATAR_OPTIONS;

export default function AvatarEditor({ isOpen, onClose, currentAvatar, onAvatarUpdate }: AvatarEditorProps) {
  const [avatar, setAvatar] = useState<Omit<AvatarSettings, 'url'>>(() => ({
    skinColor: currentAvatar.skinColor,
    hairColor: currentAvatar.hairColor,
    top: currentAvatar.top,
    accessories: currentAvatar.accessories,
    facialHair: currentAvatar.facialHair,
    clothing: currentAvatar.clothing,
    clothingColor: currentAvatar.clothingColor,
    eyes: currentAvatar.eyes,
    eyebrows: currentAvatar.eyebrows,
    mouth: currentAvatar.mouth,
  }));
  const [activeTab, setActiveTab] = useState<AvatarField>('skinColor');
  const [loading, setLoading] = useState(false);
  const [previewUrl, setPreviewUrl] = useState(currentAvatar.url);
  const [error, setError] = useState<string | null>(null);

  // Synchronisiere State wenn Modal geöffnet wird
  useEffect(() => {
    if (isOpen) {
      setAvatar({
        skinColor: currentAvatar.skinColor,
        hairColor: currentAvatar.hairColor,
        top: currentAvatar.top,
        accessories: currentAvatar.accessories,
        facialHair: currentAvatar.facialHair,
        clothing: currentAvatar.clothing,
        clothingColor: currentAvatar.clothingColor,
        eyes: currentAvatar.eyes,
        eyebrows: currentAvatar.eyebrows,
        mouth: currentAvatar.mouth,
      });
      setActiveTab('skinColor');
      setError(null);
    }
  }, [isOpen, currentAvatar]);

  const tabs: { key: AvatarField; label: string; icon: string }[] = [
    { key: 'skinColor', label: 'Haut', icon: '👤' },
    { key: 'hairColor', label: 'Haarfarbe', icon: '🎨' },
    { key: 'top', label: 'Frisur', icon: '💇' },
    { key: 'accessories', label: 'Brille', icon: '👓' },
    { key: 'facialHair', label: 'Bart', icon: '🧔' },
    { key: 'eyes', label: 'Augen', icon: '👁️' },
    { key: 'eyebrows', label: 'Brauen', icon: '🤨' },
    { key: 'mouth', label: 'Mund', icon: '👄' },
    { key: 'clothing', label: 'Kleidung', icon: '👔' },
    { key: 'clothingColor', label: 'Farbe', icon: '🎨' },
  ];

  // Preview-URL aktualisieren wenn sich Avatar ändert (DiceBear 9.x Parameter)
  useEffect(() => {
    const params: string[] = [
      `skinColor=${avatar.skinColor}`,
      `hairColor=${avatar.hairColor}`,
      `top=${avatar.top}`,
      `eyes=${avatar.eyes}`,
      `eyebrows=${avatar.eyebrows}`,
      `mouth=${avatar.mouth}`,
      `clothing=${avatar.clothing}`,
      `clothesColor=${avatar.clothingColor}`,
    ];
    // Optionale Felder nur hinzufügen wenn gesetzt
    if (avatar.accessories) {
      params.push(`accessories=${avatar.accessories}`);
      params.push('accessoriesProbability=100');
    }
    if (avatar.facialHair) {
      params.push(`facialHair=${avatar.facialHair}`);
      params.push('facialHairProbability=100');
    }
    setPreviewUrl(`https://api.dicebear.com/9.x/avataaars/svg?${params.join('&')}`);
  }, [avatar]);

  const handleOptionSelect = (field: AvatarField, value: string) => {
    setAvatar(prev => ({ ...prev, [field]: value }));
    setError(null);
  };

  const handleRandomize = () => {
    // Client-seitige Randomisierung - nur Vorschau, kein Speichern
    const getRandomOption = (options: readonly { value: string }[]) => {
      const randomIndex = Math.floor(Math.random() * options.length);
      return options[randomIndex].value;
    };
    
    setAvatar({
      skinColor: getRandomOption(AVATAR_OPTIONS.skinColor.options),
      hairColor: getRandomOption(AVATAR_OPTIONS.hairColor.options),
      top: getRandomOption(AVATAR_OPTIONS.top.options),
      accessories: getRandomOption(AVATAR_OPTIONS.accessories.options),
      facialHair: getRandomOption(AVATAR_OPTIONS.facialHair.options),
      clothing: getRandomOption(AVATAR_OPTIONS.clothing.options),
      clothingColor: getRandomOption(AVATAR_OPTIONS.clothingColor.options),
      eyes: getRandomOption(AVATAR_OPTIONS.eyes.options),
      eyebrows: getRandomOption(AVATAR_OPTIONS.eyebrows.options),
      mouth: getRandomOption(AVATAR_OPTIONS.mouth.options),
    });
    setError(null);
  };

  const handleSave = async () => {
    setLoading(true);
    setError(null);
    const result = await updateAvatar(avatar);
    setLoading(false);
    
    if (result.data) {
      onAvatarUpdate(result.data.avatar);
      onClose();
    } else {
      setError(result.error || 'Fehler beim Speichern des Avatars');
    }
  };

  const currentTabIndex = tabs.findIndex(t => t.key === activeTab);

  const goToPrevTab = () => {
    const newIndex = currentTabIndex > 0 ? currentTabIndex - 1 : tabs.length - 1;
    setActiveTab(tabs[newIndex].key);
  };

  const goToNextTab = () => {
    const newIndex = currentTabIndex < tabs.length - 1 ? currentTabIndex + 1 : 0;
    setActiveTab(tabs[newIndex].key);
  };

  if (!isOpen) return null;

  const currentOptions = AVATAR_OPTIONS[activeTab];

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold">Avatar anpassen</h2>
          <button 
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="flex flex-1 overflow-hidden">
          {/* Preview Section */}
          <div className="w-1/3 bg-gradient-to-b from-gray-100 to-gray-200 p-6 flex flex-col items-center justify-center border-r border-gray-200">
            <div className="w-48 h-48 rounded-full overflow-hidden bg-white shadow-lg border-4 border-red-600 mb-6">
              <img 
                src={previewUrl} 
                alt="Avatar Vorschau" 
                className="w-full h-full"
              />
            </div>
            
            <Button
              onClick={handleRandomize}
              disabled={loading}
              className="flex items-center gap-2 bg-gray-800 hover:bg-gray-900 text-white mb-3"
            >
              <Shuffle className="w-4 h-4" />
              Zufällig
            </Button>
          </div>

          {/* Editor Section */}
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Tab Navigation */}
            <div className="flex items-center justify-between px-4 py-3 bg-gray-50 border-b border-gray-200">
              <button
                onClick={goToPrevTab}
                className="p-2 hover:bg-gray-200 rounded-full transition-colors"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              
              <div className="flex gap-1 overflow-x-auto px-2">
                {tabs.map((tab) => (
                  <button
                    key={tab.key}
                    onClick={() => setActiveTab(tab.key)}
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap flex items-center gap-1 ${
                      activeTab === tab.key
                        ? 'bg-red-600 text-white'
                        : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
                    }`}
                  >
                    <span>{tab.icon}</span>
                    <span className="hidden md:inline">{tab.label}</span>
                  </button>
                ))}
              </div>

              <button
                onClick={goToNextTab}
                className="p-2 hover:bg-gray-200 rounded-full transition-colors"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>

            {/* Options Grid */}
            <div className="flex-1 overflow-y-auto p-4">
              <h3 className="text-lg font-semibold mb-4">{currentOptions.label}</h3>
              
              {/* Color Selector für Skin/Hair/Clothing Color */}
              {(activeTab === 'skinColor' || activeTab === 'hairColor' || activeTab === 'clothingColor') && (
                <div className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 gap-3">
                  {currentOptions.options.map((option) => (
                    <button
                      key={option.value}
                      onClick={() => handleOptionSelect(activeTab, option.value)}
                      className={`relative w-12 h-12 rounded-full border-3 transition-all ${
                        avatar[activeTab] === option.value
                          ? 'ring-4 ring-red-500 ring-offset-2 scale-110'
                          : 'hover:scale-105'
                      }`}
                      style={{ backgroundColor: 'color' in option ? option.color : '#ccc' }}
                      title={option.label}
                    >
                      {avatar[activeTab] === option.value && (
                        <div className="absolute inset-0 flex items-center justify-center">
                          <Check className="w-5 h-5 text-white drop-shadow-lg" />
                        </div>
                      )}
                    </button>
                  ))}
                </div>
              )}

              {/* Option Selector für andere Felder */}
              {activeTab !== 'skinColor' && activeTab !== 'hairColor' && activeTab !== 'clothingColor' && (
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                  {currentOptions.options.map((option) => (
                    <button
                      key={option.value}
                      onClick={() => handleOptionSelect(activeTab, option.value)}
                      className={`p-3 rounded-lg text-sm font-medium transition-all border-2 ${
                        avatar[activeTab] === option.value
                          ? 'bg-red-50 border-red-500 text-red-700 shadow-md'
                          : 'bg-white border-gray-200 text-gray-700 hover:border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        {avatar[activeTab] === option.value && (
                          <Check className="w-4 h-4 text-red-500" />
                        )}
                        <span className={avatar[activeTab] === option.value ? '' : 'ml-6'}>{option.label}</span>
                      </div>
                      {'category' in option && (
                        <span className="text-xs text-gray-400 mt-1 block">{option.category}</span>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="px-4 py-2 bg-red-50 border-t border-red-200">
            <p className="text-red-600 text-sm text-center">{error}</p>
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 p-4 border-t border-gray-200 bg-gray-50">
          <Button
            onClick={onClose}
            className="px-6 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 border-none"
          >
            Abbrechen
          </Button>
          <Button
            onClick={handleSave}
            disabled={loading}
            className="px-6 py-2 bg-red-600 hover:bg-red-700 text-white border-none flex items-center gap-2"
          >
            {loading ? (
              <>Speichern...</>
            ) : (
              <>
                <Check className="w-4 h-4" />
                Speichern
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
