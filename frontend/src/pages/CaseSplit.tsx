import { useState, useEffect } from 'react';
import { User, ArrowLeft, Check, X, Info, HelpCircle, CheckCircle2, Shuffle } from 'lucide-react';
import { hkaLogo } from '../assets';
import { Button } from '../components/ui/button';
import { RadioGroup, RadioGroupItem } from '../components/ui/radio-group';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { 
  generateTask, 
  solveTask, 
  getFeedback,
  Task, 
  SolveResponse
} from '../services/api';

const TOTAL_LEVELS = 3;

export default function CaseSplit() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { user, refreshUser } = useAuth();
  
  // URL Parameter
  const mode = searchParams.get('mode'); // 'free' für Freies Üben
  const levelParam = searchParams.get('level'); // '1', '2', '3' oder 'random'
  
  // Zustände
  const [currentLevel, setCurrentLevel] = useState<number>(1);
  const [isRandomMode, setIsRandomMode] = useState(false);
  const [currentTask, setCurrentTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Aufgaben-Zustand
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [solveResult, setSolveResult] = useState<SolveResponse | null>(null);
  const [feedbackTexts, setFeedbackTexts] = useState<Record<string, string>>({});
  const [showFeedback, setShowFeedback] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);

  // Level aus URL-Parameter lesen und Aufgabe starten
  useEffect(() => {
    if (mode === 'free' && levelParam) {
      if (levelParam === 'random') {
        setIsRandomMode(true);
        const randomLevel = Math.floor(Math.random() * TOTAL_LEVELS) + 1;
        setCurrentLevel(randomLevel);
        loadTask(randomLevel);
      } else {
        const level = parseInt(levelParam);
        if (level >= 1 && level <= TOTAL_LEVELS) {
          setIsRandomMode(false);
          setCurrentLevel(level);
          loadTask(level);
        }
      }
    }
  }, [mode, levelParam]);

  // Aufgabe laden
  const loadTask = async (level: number) => {
    setLoading(true);
    setError(null);
    
    const response = await generateTask({ task_type: 'CASE_SPLIT', level });
    
    if (response.data) {
      setCurrentTask(response.data);
      setAnswers({});
      setSolveResult(null);
      setFeedbackTexts({});
      setSubmitted(false);
      setShowFeedback(null);
    } else {
      setError(response.error || 'Fehler beim Generieren der Aufgabe');
    }
    
    setLoading(false);
  };

  // Aufgabe prüfen
  const handleSubmit = async () => {
    if (!currentTask) return;
    
    // Prüfen ob alle Variablen beantwortet wurden
    const unanswered = currentTask.variables.filter(v => !answers[v]);
    if (unanswered.length > 0) {
      setError(`Bitte beantworte alle Variablen: ${unanswered.join(', ')}`);
      return;
    }
    
    setLoading(true);
    setError(null);
    
    const response = await solveTask({
      task_id: currentTask.id,
      answers: answers
    });
    
    if (response.data) {
      setSolveResult(response.data);
      setSubmitted(true);
      
      // Benutzer-Statistiken aktualisieren
      await refreshUser();
      
      // Feedback für falsche Antworten laden
      for (const [variable, result] of Object.entries(response.data.results)) {
        if (!result.is_correct) {
          const feedbackResponse = await getFeedback(
            currentTask.id,
            variable,
            answers[variable]
          );
          if (feedbackResponse.data) {
            setFeedbackTexts(prev => ({
              ...prev,
              [variable]: feedbackResponse.data!.feedback
            }));
          }
        }
      }
    } else {
      setError(response.error || 'Fehler beim Prüfen der Antwort');
    }
    
    setLoading(false);
  };

  // Nächste Aufgabe
  const handleNextTask = () => {
    if (isRandomMode) {
      const randomLevel = Math.floor(Math.random() * TOTAL_LEVELS) + 1;
      setCurrentLevel(randomLevel);
      loadTask(randomLevel);
    } else {
      loadTask(currentLevel);
    }
  };

  // Level wechseln
  const handleLevelChange = (level: number | 'random') => {
    if (level === 'random') {
      setIsRandomMode(true);
      const randomLevel = Math.floor(Math.random() * TOTAL_LEVELS) + 1;
      setCurrentLevel(randomLevel);
      loadTask(randomLevel);
    } else {
      setIsRandomMode(false);
      setCurrentLevel(level);
      loadTask(level);
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <header className="container mx-auto px-4 py-6 flex justify-between items-center">
        <div className="flex items-center cursor-pointer" onClick={() => navigate('/')}>
          <img src={hkaLogo} alt="Hochschule Karlsruhe - University of Applied Sciences" className="h-48 w-auto object-contain" />
        </div>
        
        <Button 
          onClick={() => navigate('/account')}
          className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white border-none px-5 py-3 text-base"
        >
          {user?.avatar?.url ? (
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
            onClick={() => navigate('/freies-ueben')}
            className="flex items-center gap-2 bg-gray-200 hover:bg-gray-300 text-black border-none"
          >
            <ArrowLeft className="w-4 h-4" />
            Zurück
          </Button>
          <h1 className="text-4xl font-bold">Case Split</h1>
          <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium">
            Freies Üben
          </span>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {/* Level Selection & Stats */}
        <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
          {/* Level Auswahl */}
          <div className="flex items-center gap-2">
            <span className="text-gray-600 font-medium">Level:</span>
            <div className="flex gap-2">
              <button
                onClick={() => handleLevelChange('random')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg border-2 transition-all ${
                  isRandomMode
                    ? 'border-purple-600 bg-purple-50 text-purple-700'
                    : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
                }`}
              >
                <Shuffle className="w-4 h-4" />
                Zufällig
              </button>
              {[1, 2, 3].map((level) => (
                <button
                  key={level}
                  onClick={() => handleLevelChange(level)}
                  className={`px-4 py-2 rounded-lg border-2 transition-all min-w-[50px] ${
                    !isRandomMode && currentLevel === level
                      ? 'border-purple-600 bg-purple-50 text-purple-700 font-semibold'
                      : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {level}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Level Badge */}
        <div className="flex items-center gap-6 mb-8">
          <div className="flex items-center justify-center w-24 h-24 rounded-full text-white bg-purple-600">
            <div className="text-center">
              <div className="text-sm">Level</div>
              <div className="text-3xl font-bold">{currentLevel}</div>
            </div>
          </div>
          
          {isRandomMode && (
            <div className="flex items-center gap-2 text-gray-600">
              <Shuffle className="w-5 h-5" />
              <span>Zufälliges Level</span>
            </div>
          )}
        </div>

        {/* Lade-Zustand */}
        {loading && !currentTask && (
          <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-12 max-w-4xl text-center">
            <div className="animate-pulse text-gray-600">Lade Aufgabe...</div>
          </div>
        )}

        {/* Exercise Card */}
        {currentTask && (
          <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-12 max-w-4xl">
            {/* Formula/Premises */}
            <div className="flex flex-col items-start mb-12 max-w-xl">
              <h3 className="text-lg font-semibold text-gray-600 mb-4">Gegeben:</h3>
              {currentTask.premises.map((premise, idx) => (
                <div key={idx} className="text-2xl mb-2 flex gap-4 font-mono">
                  <span className="inline-block w-12 text-gray-500">(P{idx + 1})</span>
                  <span>{premise}</span>
                </div>
              ))}
            </div>

            <div className="border-t border-gray-300 pt-8 mb-8" />

            <h3 className="text-lg font-semibold text-gray-600 mb-6">
              Welche Schlüsse können gezogen werden?
            </h3>

            {/* Variable Inputs */}
            {currentTask.variables.map((variable) => {
              const result = solveResult?.results[variable];
              const isCorrect = result?.is_correct;
              const feedback = feedbackTexts[variable];
              
              return (
                <div key={variable} className="mb-8">
                  <div className="flex items-center gap-8 mb-2">
                    <label className="text-xl font-medium min-w-[140px] flex items-center gap-2">
                      Variable {variable}:
                      {submitted && (
                        <span className={isCorrect ? 'text-green-600' : 'text-red-600'}>
                          {isCorrect ? <Check className="w-6 h-6" /> : <X className="w-6 h-6" />}
                        </span>
                      )}
                    </label>
                    <RadioGroup 
                      value={answers[variable] || ''} 
                      onValueChange={(val) => setAnswers(prev => ({ ...prev, [variable]: val }))}
                      className="flex gap-8"
                      disabled={submitted}
                    >
                      <div className="flex items-center gap-2">
                        <RadioGroupItem value="True" id={`${variable}-true`} />
                        <label htmlFor={`${variable}-true`} className="text-lg cursor-pointer">Wahr</label>
                      </div>
                      <div className="flex items-center gap-2">
                        <RadioGroupItem value="False" id={`${variable}-false`} />
                        <label htmlFor={`${variable}-false`} className="text-lg cursor-pointer">Falsch</label>
                      </div>
                      <div className="flex items-center gap-2">
                        <RadioGroupItem value="None" id={`${variable}-none`} />
                        <label htmlFor={`${variable}-none`} className="text-lg cursor-pointer">Kein konkreter Schluss möglich</label>
                      </div>
                    </RadioGroup>
                    
                    {/* Feedback Button */}
                    {submitted && !isCorrect && feedback && (
                      <button
                        onClick={() => setShowFeedback(showFeedback === variable ? null : variable)}
                        className="p-2 text-purple-600 hover:bg-purple-50 rounded-full"
                        title="Feedback anzeigen"
                      >
                        <Info className="w-6 h-6" />
                      </button>
                    )}
                  </div>
                  
                  {/* Feedback Anzeige */}
                  {showFeedback === variable && feedback && (
                    <div className="mt-2 ml-[156px] p-4 bg-purple-50 border border-purple-200 rounded-lg">
                      <div className="flex items-start gap-2">
                        <HelpCircle className="w-5 h-5 text-purple-600 flex-shrink-0 mt-0.5" />
                        <div className="text-gray-700 whitespace-pre-wrap">{feedback}</div>
                      </div>
                    </div>
                  )}
                  
                  {/* Korrekte Antwort anzeigen wenn falsch */}
                  {submitted && !isCorrect && result && (
                    <div className="mt-2 ml-[156px] text-sm text-gray-600">
                      Korrekte Antwort: <span className="font-semibold">
                        {result.correct_answer === 'True' ? 'Wahr' : result.correct_answer === 'False' ? 'Falsch' : 'Kein konkreter Schluss möglich'}
                      </span>
                    </div>
                  )}
                </div>
              );
            })}

            {/* Result Message */}
            {submitted && solveResult && (
              <div className={`mb-6 p-4 rounded-lg ${
                solveResult.is_correct 
                  ? 'bg-green-100 text-green-800 border border-green-300' 
                  : 'bg-red-100 text-red-800 border border-red-300'
              }`}>
                {solveResult.is_correct ? (
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-6 h-6" />
                    <span className="font-semibold">Richtig!</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <X className="w-6 h-6" />
                    <span>Nicht ganz richtig. Klicke auf das Info-Symbol für detailliertes Feedback.</span>
                  </div>
                )}
              </div>
            )}

            {/* Buttons */}
            <div className="flex gap-4">
              {!submitted ? (
                <Button
                  onClick={handleSubmit}
                  disabled={loading || Object.keys(answers).length !== currentTask.variables.length}
                  className="flex-1 bg-red-600 hover:bg-red-700 text-white text-lg py-6 border-none"
                >
                  {loading ? 'Prüfe...' : 'Lösung prüfen'}
                </Button>
              ) : (
                <Button
                  onClick={handleNextTask}
                  disabled={loading}
                  className="flex-1 bg-red-600 hover:bg-red-700 text-white text-lg py-6 border-none"
                >
                  {loading ? 'Lade...' : 'Nächste Aufgabe'}
                </Button>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
