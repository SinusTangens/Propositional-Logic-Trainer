import { useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { User, ArrowLeft, Flag, BookOpen, CheckCircle2, Lock, LogIn, Play, HelpCircle, X, Check, Info } from 'lucide-react';
import { hkaLogo } from '../assets';
import { Button } from '../components/ui/button';
import { RadioGroup, RadioGroupItem } from '../components/ui/radio-group';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import CelebrationModal from '../components/CelebrationModal';
import { 
  generateTask, 
  solveTask, 
  getFeedback,
  Task, 
  SolveResponse
} from '../services/api';

type ViewState = 'path' | 'task';
type TaskType = 'DIRECT_INFERENCE' | 'CASE_SPLIT';

// Checkpoint-Komponente mit hüpfender Animation und Portal-Tooltip
function Checkpoint({ 
  level, 
  isActive, 
  isCompleted, 
  isLocked, 
  type,
  onClick,
  description
}: { 
  level: number;
  isActive: boolean;
  isCompleted: boolean;
  isLocked: boolean;
  type: TaskType;
  onClick: () => void;
  description: string;
}) {
  const baseColor = type === 'DIRECT_INFERENCE' ? 'blue' : 'purple';
  const [showTooltip, setShowTooltip] = useState(false);
  const [tooltipPos, setTooltipPos] = useState({ top: 0, left: 0 });
  const buttonRef = useRef<HTMLButtonElement>(null);
  
  useEffect(() => {
    if (showTooltip && buttonRef.current) {
      const rect = buttonRef.current.getBoundingClientRect();
      setTooltipPos({
        top: rect.top - 8,
        left: rect.left + rect.width / 2
      });
    }
  }, [showTooltip]);
  
  return (
    <div 
      className="relative"
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      <button
        ref={buttonRef}
        onClick={onClick}
        disabled={isLocked || isCompleted}
        className={`
          relative w-20 h-20 rounded-full flex items-center justify-center
          transition-all duration-300 transform
          ${isLocked ? 'bg-gray-300 cursor-not-allowed' : ''}
          ${isActive && !isLocked ? `bg-${baseColor}-600 animate-bounce cursor-pointer hover:scale-110` : ''}
          ${isCompleted ? 'bg-green-500 cursor-default' : ''}
          ${!isActive && !isCompleted && !isLocked ? `bg-${baseColor}-200 cursor-pointer hover:scale-105` : ''}
        `}
        style={{
          animationDuration: isActive && !isLocked ? '1.5s' : undefined
        }}
      >
        {isLocked && <Lock className="w-8 h-8 text-gray-500" />}
        {isCompleted && <CheckCircle2 className="w-10 h-10 text-white" />}
        {!isLocked && !isCompleted && (
          <span className="text-2xl font-bold text-white">{level}</span>
        )}
      </button>
      
      {/* Tooltip via Portal - wird außerhalb des overflow-Containers gerendert */}
      {showTooltip && createPortal(
        <div 
          className="fixed px-3 py-2 bg-gray-900 text-white text-sm rounded-lg whitespace-nowrap pointer-events-none"
          style={{
            top: tooltipPos.top,
            left: tooltipPos.left,
            transform: 'translate(-50%, -100%)',
            zIndex: 9999
          }}
        >
          {description}
          <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-gray-900" />
        </div>,
        document.body
      )}
    </div>
  );
}

// Pfadlinie zwischen Checkpoints
function PathLine({ isCompleted }: { isCompleted: boolean }) {
  return (
    <div className={`w-16 h-1 ${isCompleted ? 'bg-green-500' : 'bg-gray-300'} -mx-2`} />
  );
}

export default function Lernpfad() {
  const navigate = useNavigate();
  const { user, isAuthenticated, refreshUser } = useAuth();
  
  // Zustände
  const [viewState, setViewState] = useState<ViewState>('path');
  const [currentTask, setCurrentTask] = useState<Task | null>(null);
  const [currentTaskType, setCurrentTaskType] = useState<TaskType>('DIRECT_INFERENCE');
  const [currentLevel, setCurrentLevel] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Aufgaben-Zustand
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [solveResult, setSolveResult] = useState<SolveResponse | null>(null);
  const [feedbackTexts, setFeedbackTexts] = useState<Record<string, string>>({});
  const [showFeedback, setShowFeedback] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);
  
  // Celebration-Modal Zustände
  const [showCelebration, setShowCelebration] = useState(false);
  const [celebrationType, setCelebrationType] = useState<'type' | 'all'>('type');
  const [completedTaskTypeName, setCompletedTaskTypeName] = useState<string>('');
  
  // Progress aus User-Daten
  const progress = user?.progress || [];
  const unitPropProgress = progress.find(p => p.task_type === 'DIRECT_INFERENCE') || {
    currentLevel: 1, totalLevels: 4, correctInRow: 0, requiredCorrect: 5, isUnlocked: true, isCompleted: false
  };
  const caseSplitProgress = progress.find(p => p.task_type === 'CASE_SPLIT') || {
    currentLevel: 1, totalLevels: 3, correctInRow: 0, requiredCorrect: 5, isUnlocked: false, isCompleted: false
  };

  const handleAuthClick = () => {
    if (isAuthenticated) {
      navigate('/account');
    } else {
      navigate('/login');
    }
  };

  // Starte Aufgabe für bestimmtes Level
  const startTask = async (type: TaskType, level: number) => {
    setLoading(true);
    setError(null);
    setCurrentTaskType(type);
    setCurrentLevel(level);
    
    const response = await generateTask({ task_type: type, level });
    
    if (response.data) {
      setCurrentTask(response.data);
      setAnswers({});
      setSolveResult(null);
      setFeedbackTexts({});
      setSubmitted(false);
      setViewState('task');
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
      
      // User-Daten aktualisieren
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
    if (solveResult?.progress?.type_completed) {
      // Typ abgeschlossen - prüfe ob gesamter Lernpfad fertig
      const typeName = currentTaskType === 'DIRECT_INFERENCE' ? 'Unit Propagation' : 'Case Split';
      setCompletedTaskTypeName(typeName);
      
      // Prüfe ob der gesamte Lernpfad jetzt abgeschlossen ist
      // Nach Case Split Abschluss UND Unit Prop war schon fertig
      const updatedProgress = solveResult.user_progress || [];
      const updatedUnitProp = updatedProgress.find(p => p.task_type === 'DIRECT_INFERENCE');
      const updatedCaseSplit = updatedProgress.find(p => p.task_type === 'CASE_SPLIT');
      
      const allCompleted = updatedUnitProp?.isCompleted && updatedCaseSplit?.isCompleted;
      
      if (allCompleted) {
        setCelebrationType('all');
      } else {
        setCelebrationType('type');
      }
      
      setShowCelebration(true);
      setViewState('path');
    } else if (solveResult?.progress?.level_up) {
      // Level Up - zurück zur Pfad-Ansicht
      setViewState('path');
    } else {
      // Nächste Aufgabe im selben Level
      startTask(currentTaskType, currentLevel);
    }
  };

  // Zurück zur Pfad-Ansicht
  const handleBackToPath = () => {
    setViewState('path');
    setCurrentTask(null);
    setSolveResult(null);
    setAnswers({});
    setSubmitted(false);
  };

  // ================================
  // PFAD-ANSICHT
  // ================================
  if (viewState === 'path') {
    return (
      <div className="min-h-screen bg-white">
        {/* Header */}
        <header className="container mx-auto px-4 py-6 flex justify-between items-center">
          <div className="flex items-center cursor-pointer" onClick={() => navigate('/')}>
            <img src={hkaLogo} alt="Hochschule Karlsruhe" className="h-48 w-auto object-contain" />
          </div>
          
<Button 
            onClick={handleAuthClick}
            className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white border-none px-5 py-3 text-base"
          >
            {isAuthenticated ? (
              <>
                {user?.avatar?.url ? (
                  <img src={user.avatar.url} alt="Avatar" className="w-6 h-6 rounded-full" />
                ) : (
                  <User className="w-4 h-4" />
                )}
                Account
              </>
            ) : (
              <>
                <LogIn className="w-4 h-4" />
                Einloggen
              </>
            )}
          </Button>
        </header>

        <main className="container mx-auto px-4 py-8">
          <div className="flex items-center gap-4 mb-8">
            <Button
              onClick={() => navigate('/')}
              className="flex items-center gap-2 bg-gray-200 hover:bg-gray-300 text-black border-none"
            >
              <ArrowLeft className="w-4 h-4" />
              Zurück
            </Button>
            <h1 className="text-4xl font-bold">Lernpfad</h1>
          </div>

          {/* Intro Text */}
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 mb-8">
            <div className="flex items-start gap-4">
              <BookOpen className="w-8 h-8 text-red-600 flex-shrink-0 mt-1" />
              <div>
                <h2 className="text-xl font-semibold mb-2">Willkommen im Lernpfad!</h2>
                <p className="text-gray-700 mb-2">
                  Hier lernst du Schritt für Schritt logische Schlussfolgerungen. 
                  Klicke auf einen <strong>hüpfenden Checkpoint</strong>, um zu beginnen.
                </p>
                <p className="text-gray-600 text-sm">
                  <strong>Tipp:</strong> Du musst  mehrere Aufgaben in Folge richtig lösen, um das nächste Level freizuschalten.
                  Besuche die <a href="/grundlagen" className="text-red-600 hover:underline">Grundlagen</a>-Seite für eine Einführung
                  oder die <a href="/referenzen" className="text-red-600 hover:underline">Referenzen</a> für Vorlesungsmaterial.
                </p>
              </div>
            </div>
          </div>

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
              {error}
            </div>
          )}

          {/* Unit Propagation Pfad */}
          <section className="mb-12">
            <h2 className="text-2xl font-semibold mb-6 flex items-center gap-3">
              <div className="w-4 h-4 rounded-full bg-blue-600" />
              Unit Propagation
              <span className="text-sm font-normal text-gray-500">
                (Direktes Schließen)
              </span>
            </h2>
            
            <div className="bg-white border border-gray-200 rounded-lg p-8 overflow-x-auto">
              <div className="flex items-center justify-start gap-0 min-w-max">
                {[1, 2, 3, 4].map((level, idx) => {
                  const isCompleted = level < unitPropProgress.currentLevel || (unitPropProgress.isCompleted && level === unitPropProgress.totalLevels);
                  const isActive = level === unitPropProgress.currentLevel && !unitPropProgress.isCompleted;
                  const isLocked = false; // Unit Prop ist nie gesperrt
                  
                  return (
                    <div key={level} className="flex items-center">
                      <Checkpoint
                        level={level}
                        isActive={isActive}
                        isCompleted={isCompleted}
                        isLocked={isLocked}
                        type="DIRECT_INFERENCE"
                        onClick={() => !isLocked && !isCompleted && startTask('DIRECT_INFERENCE', level)}
                        description={`Level ${level}: ${level === 1 ? 'Einfache Schlüsse' : level === 2 ? 'Mittlere Komplexität' : level === 3 ? 'Fortgeschritten' : 'Experte'}`}
                      />
                      {idx < 3 && <PathLine isCompleted={isCompleted || (isActive && idx < unitPropProgress.currentLevel - 1)} />}
                    </div>
                  );
                })}
                
                {/* Ziel */}
                <PathLine isCompleted={unitPropProgress.isCompleted} />
                <div className="w-20 h-20 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center">
                  <Flag className={`w-10 h-10 ${unitPropProgress.isCompleted ? 'text-green-400' : 'text-white'}`} />
                </div>
              </div>
              
              {/* Progress-Anzeige */}
              <div className="mt-6 pt-4 border-t border-gray-200">
                {unitPropProgress.isCompleted ? (
                  <div className="flex items-center gap-2 text-green-600 font-semibold">
                    <CheckCircle2 className="w-5 h-5" />
                    <span>Alle {unitPropProgress.totalLevels} Level erfolgreich abgeschlossen!</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-4 text-sm text-gray-600">
                    <span>Level {unitPropProgress.currentLevel}/{unitPropProgress.totalLevels}</span>
                    <span>•</span>
                    <span>{unitPropProgress.correctInRow}/{unitPropProgress.requiredCorrect} richtig in Folge</span>
                  </div>
                )}
              </div>
            </div>
          </section>

          {/* Case Split Pfad */}
          <section>
            <h2 className="text-2xl font-semibold mb-6 flex items-center gap-3">
              <div className="w-4 h-4 rounded-full bg-purple-600" />
              Case Split
              <span className="text-sm font-normal text-gray-500">
                (Mit Fallunterscheidung)
              </span>
              {!caseSplitProgress.isUnlocked && (
                <span className="flex items-center gap-1 px-3 py-1 bg-gray-200 text-gray-600 rounded-full text-sm">
                  <Lock className="w-4 h-4" />
                  Gesperrt
                </span>
              )}
            </h2>
            
            <div className={`bg-white border border-gray-200 rounded-lg p-8 overflow-x-auto ${!caseSplitProgress.isUnlocked ? 'opacity-60' : ''}`}>
              <div className="flex items-center justify-start gap-0 min-w-max">
                {[1, 2, 3].map((level, idx) => {
                  const isCompleted = caseSplitProgress.isUnlocked && (level < caseSplitProgress.currentLevel || (caseSplitProgress.isCompleted && level === caseSplitProgress.totalLevels));
                  const isActive = caseSplitProgress.isUnlocked && level === caseSplitProgress.currentLevel && !caseSplitProgress.isCompleted;
                  const isLocked = !caseSplitProgress.isUnlocked;
                  
                  return (
                    <div key={level} className="flex items-center">
                      <Checkpoint
                        level={level}
                        isActive={isActive}
                        isCompleted={isCompleted}
                        isLocked={isLocked}
                        type="CASE_SPLIT"
                        onClick={() => !isLocked && !isCompleted && startTask('CASE_SPLIT', level)}
                        description={isLocked ? 'Schließe zuerst Unit Propagation ab' : `Level ${level}: ${level === 1 ? 'Einfache Fälle' : level === 2 ? 'Mehrere Fälle' : 'Komplexe Szenarien'}`}
                      />
                      {idx < 2 && <PathLine isCompleted={isCompleted || (isActive && idx < caseSplitProgress.currentLevel - 1)} />}
                    </div>
                  );
                })}
                
                {/* Ziel */}
                <PathLine isCompleted={caseSplitProgress.isCompleted} />
                <div className={`w-20 h-20 rounded-full flex items-center justify-center ${caseSplitProgress.isUnlocked ? 'bg-gradient-to-r from-purple-500 to-pink-500' : 'bg-gray-300'}`}>
                  <Flag className={`w-10 h-10 ${caseSplitProgress.isCompleted ? 'text-green-400' : caseSplitProgress.isUnlocked ? 'text-white' : 'text-gray-500'}`} />
                </div>
              </div>
              
              {/* Progress-Anzeige */}
              {caseSplitProgress.isUnlocked && (
                <div className="mt-6 pt-4 border-t border-gray-200">
                  {caseSplitProgress.isCompleted ? (
                    <div className="flex items-center gap-2 text-green-600 font-semibold">
                      <CheckCircle2 className="w-5 h-5" />
                      <span>Alle {caseSplitProgress.totalLevels} Level erfolgreich abgeschlossen!</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <span>Level {caseSplitProgress.currentLevel}/{caseSplitProgress.totalLevels}</span>
                      <span>•</span>
                      <span>{caseSplitProgress.correctInRow}/{caseSplitProgress.requiredCorrect} richtig in Folge</span>
                    </div>
                  )}
                </div>
              )}
              
              {!caseSplitProgress.isUnlocked && (
                <div className="mt-6 pt-4 border-t border-gray-200 text-center text-gray-500">
                  Schließe alle Unit Propagation Level ab, um Case Split freizuschalten.
                </div>
              )}
            </div>
          </section>

          {/* Quick Start Button */}
          <div className="mt-12 text-center">
            <Button
              onClick={() => {
                if (caseSplitProgress.isUnlocked && !caseSplitProgress.isCompleted) {
                  startTask('CASE_SPLIT', caseSplitProgress.currentLevel);
                } else if (!unitPropProgress.isCompleted) {
                  startTask('DIRECT_INFERENCE', unitPropProgress.currentLevel);
                }
              }}
              disabled={loading || (unitPropProgress.isCompleted && caseSplitProgress.isCompleted)}
              className="bg-red-600 hover:bg-red-700 text-white text-xl px-12 py-6 border-none flex items-center gap-3 mx-auto"
            >
              <Play className="w-6 h-6" />
              {loading ? 'Lade...' : unitPropProgress.isCompleted && caseSplitProgress.isCompleted ? 'Alle Level abgeschlossen!' : 'Fortfahren'}
            </Button>
          </div>
        </main>
        
        {/* Celebration Modal */}
        <CelebrationModal
          isOpen={showCelebration}
          onClose={() => setShowCelebration(false)}
          avatarUrl={user?.avatar?.url}
          title={celebrationType === 'all' 
            ? '🎉 Lernpfad abgeschlossen!' 
            : `🏆 ${completedTaskTypeName} gemeistert!`
          }
          message={celebrationType === 'all'
            ? 'Fantastisch! Du hast den gesamten Lernpfad erfolgreich abgeschlossen und bist jetzt bereit für das Freie Üben!'
            : `Großartig! Du hast alle Level von ${completedTaskTypeName} erfolgreich abgeschlossen. Mach weiter so!`
          }
          showFreiesUebenHint={celebrationType === 'all'}
          onNavigateToFreiesUeben={() => navigate('/freies-ueben')}
        />
      </div>
    );
  }

  // ================================
  // AUFGABEN-ANSICHT
  // ================================
  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="container mx-auto px-4 py-6 flex justify-between items-center">
        <div className="flex items-center cursor-pointer" onClick={() => navigate('/')}>
          <img src={hkaLogo} alt="Hochschule Karlsruhe" className="h-48 w-auto object-contain" />
        </div>
        
<Button 
          onClick={handleAuthClick}
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
            onClick={handleBackToPath}
            className="flex items-center gap-2 bg-gray-200 hover:bg-gray-300 text-black border-none"
          >
            <ArrowLeft className="w-4 h-4" />
            Zurück zum Pfad
          </Button>
          <h1 className="text-4xl font-bold">
            {currentTaskType === 'DIRECT_INFERENCE' ? 'Unit Propagation' : 'Case Split'}
          </h1>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {/* Level Badge and Progress */}
        <div className="flex items-center gap-6 mb-8">
          <div className={`flex items-center justify-center w-24 h-24 rounded-full text-white ${currentTaskType === 'DIRECT_INFERENCE' ? 'bg-blue-600' : 'bg-purple-600'}`}>
            <div className="text-center">
              <div className="text-sm">Level</div>
              <div className="text-3xl font-bold">{currentLevel}</div>
            </div>
          </div>
          
          <div className="flex-1">
            <div className="h-3 bg-gray-300 rounded-full overflow-hidden">
              <div 
                className={`h-full transition-all duration-300 ${currentTaskType === 'DIRECT_INFERENCE' ? 'bg-blue-600' : 'bg-purple-600'}`}
                style={{ width: `${((currentTaskType === 'DIRECT_INFERENCE' ? unitPropProgress.correctInRow : caseSplitProgress.correctInRow) / (currentTaskType === 'DIRECT_INFERENCE' ? unitPropProgress.requiredCorrect : caseSplitProgress.requiredCorrect)) * 100}%` }}
              />
            </div>
            <p className="mt-2 text-gray-700">
              {currentTaskType === 'DIRECT_INFERENCE' ? unitPropProgress.correctInRow : caseSplitProgress.correctInRow}/{currentTaskType === 'DIRECT_INFERENCE' ? unitPropProgress.requiredCorrect : caseSplitProgress.requiredCorrect} richtige Antworten in Folge
            </p>
          </div>
        </div>

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
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded-full"
                        title="Feedback anzeigen"
                      >
                        <Info className="w-6 h-6" />
                      </button>
                    )}
                  </div>
                  
                  {/* Feedback Anzeige */}
                  {showFeedback === variable && feedback && (
                    <div className="mt-2 ml-[156px] p-4 bg-blue-50 border border-blue-200 rounded-lg">
                      <div className="flex items-start gap-2">
                        <HelpCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
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
                    <span className="font-semibold">
                      Richtig! 
                      {solveResult.progress?.level_up && ' Level Up!'}
                      {solveResult.progress?.type_completed && ' Herzlichen Glückwunsch, du hast diesen Bereich abgeschlossen!'}
                    </span>
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
                  className="flex-1 bg-red-600 hover:bg-red-700 text-white text-lg py-6 border-none"
                >
                  {solveResult?.progress?.level_up || solveResult?.progress?.type_completed 
                    ? 'Weiter zum Pfad' 
                    : 'Nächste Aufgabe'}
                </Button>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
