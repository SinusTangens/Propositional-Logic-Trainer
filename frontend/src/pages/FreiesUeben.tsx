import { useState } from 'react';
import { User, ArrowLeft, Lock, BookOpen, ArrowRight, Shuffle } from 'lucide-react';
import { hkaLogo } from '../assets';
import { Button } from '../components/ui/button';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface ExerciseCardProps {
  title: string;
  description: string;
  formula?: string;
  isCaseSplit?: boolean;
  levels: number[];
  onStart: (level: number | 'random') => void;
}

function ExerciseCard({ title, description, formula, isCaseSplit, levels, onStart }: ExerciseCardProps) {
  const [selectedLevel, setSelectedLevel] = useState<number | 'random'>('random');

  return (
    <div className="bg-white border border-gray-200 rounded-2xl shadow-lg p-8 flex flex-col items-center text-center hover:shadow-xl transition-shadow">
      <h2 className="text-3xl font-semibold mb-8">{title}</h2>
      
      {/* Symbol/Formula Display */}
      <div className="mb-8 h-32 flex items-center justify-center">
        {isCaseSplit ? (
          <svg width="200" height="100" viewBox="0 0 200 100" className="mx-auto">
            {/* Central point */}
            <circle cx="20" cy="50" r="8" fill="black" />
            
            {/* Curved line to True (upper branch) */}
            <path d="M 28 50 C 50 50, 50 25, 85 25" stroke="black" strokeWidth="3" fill="none" />
            {/* Arrow head for True */}
            <polygon points="85,25 72,17 72,33" fill="black" />
            
            {/* Curved line to False (lower branch) */}
            <path d="M 28 50 C 50 50, 50 75, 85 75" stroke="black" strokeWidth="3" fill="none" />
            {/* Arrow head for False */}
            <polygon points="85,75 72,67 72,83" fill="black" />
            
            {/* Text labels */}
            <text x="95" y="30" fontSize="22" fill="black" fontFamily="system-ui" fontWeight="500">True</text>
            <text x="95" y="80" fontSize="22" fill="black" fontFamily="system-ui" fontWeight="500">False</text>
          </svg>
        ) : (
          <div className="text-5xl">{formula}</div>
        )}
      </div>
      
      <p className="text-lg text-gray-700 mb-6 max-w-md leading-relaxed">
        {description}
      </p>

      {/* Level Selection */}
      <div className="w-full mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-3">Level auswählen:</label>
        <div className="flex flex-wrap gap-2 justify-center">
          {/* Random option */}
          <button
            onClick={() => setSelectedLevel('random')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg border-2 transition-all ${
              selectedLevel === 'random'
                ? 'border-red-600 bg-red-50 text-red-700'
                : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
            }`}
          >
            <Shuffle className="w-4 h-4" />
            Zufällig
          </button>
          
          {/* Level buttons */}
          {levels.map((level) => (
            <button
              key={level}
              onClick={() => setSelectedLevel(level)}
              className={`px-4 py-2 rounded-lg border-2 transition-all min-w-[60px] ${
                selectedLevel === level
                  ? 'border-red-600 bg-red-50 text-red-700 font-semibold'
                  : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
              }`}
            >
              Level {level}
            </button>
          ))}
        </div>
      </div>
      
      <Button
        onClick={() => onStart(selectedLevel)}
        className="w-full bg-red-600 hover:bg-red-700 text-white text-xl py-6 border-none"
      >
        Starten
      </Button>
    </div>
  );
}

export default function FreiesUeben() {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();

  // Progress prüfen - Freies Üben nur wenn Lernpfad abgeschlossen
  const progress = user?.progress || [];
  const unitPropProgress = progress.find(p => p.task_type === 'DIRECT_INFERENCE');
  const caseSplitProgress = progress.find(p => p.task_type === 'CASE_SPLIT');
  const isLernpfadCompleted = unitPropProgress?.isCompleted && caseSplitProgress?.isCompleted;

  const handleAccountClick = () => {
    navigate('/account');
  };

  // Gesperrte Ansicht wenn Lernpfad nicht abgeschlossen
  if (!isLernpfadCompleted) {
    return (
      <div className="min-h-screen bg-white">
        <header className="container mx-auto px-4 py-6 flex justify-between items-center">
          <div className="flex items-center cursor-pointer" onClick={() => navigate('/')}>
            <img src={hkaLogo} alt="Hochschule Karlsruhe - University of Applied Sciences" className="h-48 w-auto object-contain" />
          </div>
          
          <Button 
            onClick={handleAccountClick}
            className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white border-none px-5 py-3 text-base"
          >
            {isAuthenticated && user?.avatar?.url ? (
              <img src={user.avatar.url} alt="Avatar" className="w-6 h-6 rounded-full" />
            ) : (
              <User className="w-4 h-4" />
            )}
            Account
          </Button>
        </header>

        <main className="container mx-auto px-4 py-8">
          <div className="flex items-center gap-4 mb-8">
            <Button
              onClick={() => navigate(-1)}
              className="flex items-center gap-2 bg-gray-200 hover:bg-gray-300 text-black border-none"
            >
              <ArrowLeft className="w-4 h-4" />
              Zurück
            </Button>
          </div>
          
          <div className="max-w-2xl mx-auto text-center py-16">
            {/* Lock Icon */}
            <div className="mb-8">
              <div className="w-32 h-32 mx-auto bg-gray-200 rounded-full flex items-center justify-center">
                <Lock className="w-16 h-16 text-gray-400" />
              </div>
            </div>
            
            <h1 className="text-4xl font-bold mb-4 text-gray-800">Freies Üben gesperrt</h1>
            
            <p className="text-xl text-gray-600 mb-8">
              Schließe zuerst den Lernpfad ab, um Zugang zum Freien Üben zu erhalten.
            </p>
            
            {/* Progress Info */}
            <div className="bg-gray-50 border border-gray-200 rounded-xl p-6 mb-8 text-left">
              <div className="flex items-center gap-3 mb-4">
                <BookOpen className="w-6 h-6 text-red-600" />
                <h3 className="text-lg font-semibold">Dein Fortschritt im Lernpfad</h3>
              </div>
              
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-gray-700">Unit Propagation</span>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    unitPropProgress?.isCompleted 
                      ? 'bg-green-100 text-green-700' 
                      : 'bg-gray-100 text-gray-600'
                  }`}>
                    {unitPropProgress?.isCompleted 
                      ? '✓ Abgeschlossen' 
                      : `Level ${unitPropProgress?.currentLevel || 1}/${unitPropProgress?.totalLevels || 4}`
                    }
                  </span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-gray-700">Case Split</span>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    caseSplitProgress?.isCompleted 
                      ? 'bg-green-100 text-green-700' 
                      : caseSplitProgress?.isUnlocked 
                        ? 'bg-gray-100 text-gray-600'
                        : 'bg-gray-100 text-gray-400'
                  }`}>
                    {caseSplitProgress?.isCompleted 
                      ? '✓ Abgeschlossen' 
                      : caseSplitProgress?.isUnlocked
                        ? `Level ${caseSplitProgress?.currentLevel || 1}/${caseSplitProgress?.totalLevels || 3}`
                        : '🔒 Gesperrt'
                    }
                  </span>
                </div>
              </div>
            </div>
            
            <Button
              onClick={() => navigate('/lernpfad')}
              className="bg-red-600 hover:bg-red-700 text-white text-lg px-8 py-4 border-none flex items-center gap-2 mx-auto"
            >
              Zum Lernpfad
              <ArrowRight className="w-5 h-5" />
            </Button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <header className="container mx-auto px-4 py-6 flex justify-between items-center">
        <div className="flex items-center cursor-pointer" onClick={() => navigate('/')}>
          <img src={hkaLogo} alt="Hochschule Karlsruhe - University of Applied Sciences" className="h-48 w-auto object-contain" />
        </div>
        
        <Button 
          onClick={handleAccountClick}
          className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white border-none px-5 py-3 text-base"
        >
          {isAuthenticated && user?.avatar?.url ? (
            <img src={user.avatar.url} alt="Avatar" className="w-6 h-6 rounded-full" />
          ) : (
            <User className="w-4 h-4" />
          )}
          Account
        </Button>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="flex items-center gap-4 mb-8">
          <Button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 bg-gray-200 hover:bg-gray-300 text-black border-none"
          >
            <ArrowLeft className="w-4 h-4" />
            Zurück
          </Button>
        </div>
        
        <h1 className="text-5xl mb-4">Freies Üben</h1>
        <p className="text-xl text-gray-700 mb-12">
          Wähle einen Aufgabentyp und ein Level aus, um gezielt zu üben.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-6xl">
          <ExerciseCard
            title="Unit Propagation"
            formula="A → B"
            description="Ziehe direkte Schlussfolgerungen aus einzelnen Fakten und vereinfache die Formel."
            levels={[1, 2, 3, 4]}
            onStart={(level) => navigate(`/unit-propagation?mode=free&level=${level}`)}
          />
          
          <ExerciseCard
            title="Case Split"
            isCaseSplit
            description="Löse komplexe Probleme, indem du verschiedene Fälle systematisch untersuchst."
            levels={[1, 2, 3]}
            onStart={(level) => navigate(`/case-split?mode=free&level=${level}`)}
          />
        </div>
      </main>
    </div>
  );
}
