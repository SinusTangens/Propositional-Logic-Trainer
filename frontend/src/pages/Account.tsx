import { useState } from 'react';
import { User, ArrowLeft, LogOut, Lock, Trophy, Target, TrendingUp, Flame, Mail, KeyRound, RotateCcw, Pencil, Eye, EyeOff } from 'lucide-react';
import { hkaLogo } from '../assets';
import { Button } from '../components/ui/button';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { changePassword, resetProgress as apiResetProgress, AvatarSettings } from '../services/api';
import AvatarEditor from '../components/AvatarEditor';

export default function Account() {
  const navigate = useNavigate();
  const { user, logout, refreshUser, isAuthenticated } = useAuth();
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [showAvatarEditor, setShowAvatarEditor] = useState(false);
  const [passwordForm, setPasswordForm] = useState({
    oldPassword: '',
    newPassword: '',
    newPassword2: '',
  });
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [passwordSuccess, setPasswordSuccess] = useState(false);
  const [showPassword, setShowPassword] = useState({
    old: false,
    new: false,
    confirm: false,
  });
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);

  if (!isAuthenticated || !user) {
    navigate('/login');
    return null;
  }

  const progress = user.progress || [];
  const stats = user.stats || { totalSolved: 0, correctSolved: 0, currentStreak: 0, highscoreStreak: 0 };

  // Finde Unit Propagation und Case Split Progress
  const unitPropProgress = progress.find(p => p.task_type === 'DIRECT_INFERENCE') || {
    type: 'Unit Propagation',
    currentLevel: 1,
    totalLevels: 4,
    correctInRow: 0,
    requiredCorrect: 5,
    isUnlocked: true,
    isCompleted: false,
  };

  const caseSplitProgress = progress.find(p => p.task_type === 'CASE_SPLIT') || {
    type: 'Case Split',
    currentLevel: 1,
    totalLevels: 3,
    correctInRow: 0,
    requiredCorrect: 5,
    isUnlocked: false,
    isCompleted: false,
  };

  const calculateOverallProgress = () => {
    // Gesamtzahl der Levels dynamisch aus den Progress-Daten berechnen
    const totalLevels = unitPropProgress.totalLevels + caseSplitProgress.totalLevels;
    let completedLevels = 0;

    // Count completed Unit Propagation levels
    if (unitPropProgress.currentLevel > 1) {
      completedLevels += unitPropProgress.currentLevel - 1;
    }
    
    // Add current level progress
    const currentLevelProgress = unitPropProgress.correctInRow / unitPropProgress.requiredCorrect;
    completedLevels += currentLevelProgress;
    
    // If Case Split is unlocked
    if (caseSplitProgress.isUnlocked) {
      completedLevels = unitPropProgress.totalLevels; // All Unit Propagation levels completed
      if (caseSplitProgress.currentLevel > 1) {
        completedLevels += caseSplitProgress.currentLevel - 1;
      }
      const caseSplitLevelProgress = caseSplitProgress.correctInRow / caseSplitProgress.requiredCorrect;
      completedLevels += caseSplitLevelProgress;
    }

    return (completedLevels / totalLevels) * 100;
  };

  const handlePasswordChange = async () => {
    setPasswordError(null);
    setPasswordSuccess(false);

    if (passwordForm.newPassword !== passwordForm.newPassword2) {
      setPasswordError('Die Passwörter stimmen nicht überein');
      return;
    }

    if (passwordForm.oldPassword === passwordForm.newPassword) {
      setPasswordError('Das neue Passwort muss sich vom alten unterscheiden');
      return;
    }

    const result = await changePassword(
      passwordForm.oldPassword,
      passwordForm.newPassword,
      passwordForm.newPassword2
    );

    if (result.data) {
      setPasswordSuccess(true);
      setPasswordForm({ oldPassword: '', newPassword: '', newPassword2: '' });
      setShowPassword({ old: false, new: false, confirm: false });
      setTimeout(() => {
        setShowPasswordModal(false);
        setPasswordSuccess(false);
      }, 2000);
    } else {
      setPasswordError(result.error || 'Fehler beim Ändern des Passworts');
    }
  };

  const handleResetProgress = async () => {
    if (window.confirm('Möchten Sie wirklich Ihren gesamten Fortschritt zurücksetzen? Diese Aktion kann nicht rückgängig gemacht werden.')) {
      const result = await apiResetProgress();
      if (result.data) {
        await refreshUser();
        alert('Fortschritt wurde zurückgesetzt');
      } else {
        alert('Fehler beim Zurücksetzen: ' + result.error);
      }
    }
  };

  const handleLogout = async () => {
    if (window.confirm('Möchten Sie sich wirklich ausloggen?')) {
      await logout();
      navigate('/');
    }
  };

  const handleAvatarUpdate = (avatar: AvatarSettings) => {
    setAvatarUrl(avatar.url);
    refreshUser();
  };

  // Avatar URL bestimmen: Entweder die aktualisierte oder die vom Server
  const currentAvatarUrl = avatarUrl || user.avatar?.url || `https://api.dicebear.com/9.x/avataaars/svg?seed=${user.username}`;

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="container mx-auto px-4 py-6 flex justify-between items-center">
        <div className="flex items-center cursor-pointer" onClick={() => navigate('/')}>
          <img src={hkaLogo} alt="Hochschule Karlsruhe - University of Applied Sciences" className="h-48 w-auto object-contain" />
        </div>
        
<Button 
          onClick={() => navigate('/account')}
          className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white border-none px-5 py-3 text-base"
        >
          {currentAvatarUrl ? (
            <img src={currentAvatarUrl} alt="Avatar" className="w-6 h-6 rounded-full" />
          ) : (
            <User className="w-4 h-4" />
          )}
          Account
        </Button>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-5xl">
        <div className="flex items-center gap-4 mb-8">
          <Button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 bg-gray-200 hover:bg-gray-300 text-black border-none"
          >
            <ArrowLeft className="w-4 h-4" />
            Zurück
          </Button>
        </div>
        
        <h1 className="text-5xl mb-12">Mein Account</h1>

        {/* User Profile Section */}
        <section className="bg-white border border-gray-300 rounded-lg shadow-lg p-8 mb-8">
          <h2 className="text-3xl mb-6">Profil</h2>
          
          <div className="flex items-center gap-8">
            <div className="relative group">
              <div className="w-32 h-32 rounded-full overflow-hidden bg-gray-200 border-4 border-red-600">
                <img 
                  src={currentAvatarUrl} 
                  alt="Avatar" 
                  className="w-full h-full" 
                />
              </div>
              <button
                onClick={() => setShowAvatarEditor(true)}
                className="absolute bottom-0 right-0 w-10 h-10 bg-red-600 hover:bg-red-700 rounded-full flex items-center justify-center shadow-lg transition-colors"
                title="Avatar bearbeiten"
              >
                <Pencil className="w-5 h-5 text-white" />
              </button>
            </div>
            
            <div className="flex-1">
              <div className="mb-4">
                <label className="text-lg font-semibold text-gray-700">Benutzername</label>
                <div className="flex items-center gap-2 mt-1">
                  <User className="w-5 h-5 text-gray-600" />
                  <p className="text-xl">{user.username}</p>
                </div>
              </div>
              
              <div>
                <label className="text-lg font-semibold text-gray-700">E-Mail</label>
                <div className="flex items-center gap-2 mt-1">
                  <Mail className="w-5 h-5 text-gray-600" />
                  <p className="text-xl">{user.email}</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Learning Path Progress Section */}
        <section className="bg-white border border-gray-300 rounded-lg shadow-lg p-8 mb-8">
          <h2 className="text-3xl mb-6">Lernpfad-Fortschritt</h2>
          
          {/* Overall Progress */}
          <div className="mb-8 bg-gray-50 p-6 rounded-lg">
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-xl font-semibold">Gesamtfortschritt</h3>
              <span className="text-2xl font-bold text-red-600">
                {Math.round(calculateOverallProgress())}%
              </span>
            </div>
            <div className="h-6 bg-gray-300 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-red-600 to-red-700 transition-all duration-500"
                style={{ width: `${calculateOverallProgress()}%` }}
              />
            </div>
          </div>

          {/* Unit Propagation Progress */}
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-4">
              <h3 className="text-2xl">Unit Propagation</h3>
              {unitPropProgress.isCompleted ? (
                <span className="px-3 py-1 bg-green-600 text-white rounded-full text-sm font-semibold">
                  Abgeschlossen
                </span>
              ) : unitPropProgress.isUnlocked && (
                <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-semibold">
                  Freigeschaltet
                </span>
              )}
            </div>
            
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              {unitPropProgress.isCompleted ? (
                <>
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-sm text-gray-600">Abgeschlossene Level</p>
                      <p className="text-2xl font-bold text-blue-600">
                        {unitPropProgress.totalLevels} / {unitPropProgress.totalLevels}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Gesamtfortschritt</p>
                      <p className="text-2xl font-bold text-blue-600">
                        100%
                      </p>
                    </div>
                  </div>
                  
                  <div className="h-4 bg-gray-300 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-green-500 transition-all duration-500"
                      style={{ width: '100%' }}
                    />
                  </div>
                </>
              ) : (
                <>
                  <div className="grid grid-cols-3 gap-4 mb-4">
                    <div>
                      <p className="text-sm text-gray-600">Aktuelles Level</p>
                      <p className="text-2xl font-bold text-blue-600">
                        {unitPropProgress.currentLevel} / {unitPropProgress.totalLevels}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Richtig in Folge</p>
                      <p className="text-2xl font-bold text-blue-600">
                        {unitPropProgress.correctInRow} / {unitPropProgress.requiredCorrect}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Gesamtfortschritt</p>
                      <p className="text-2xl font-bold text-blue-600">
                        {Math.round(((unitPropProgress.currentLevel - 1 + unitPropProgress.correctInRow / unitPropProgress.requiredCorrect) / unitPropProgress.totalLevels) * 100)}%
                      </p>
                    </div>
                  </div>
                  
                  <div className="h-4 bg-gray-300 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-blue-600 transition-all duration-500"
                      style={{ width: `${((unitPropProgress.currentLevel - 1 + unitPropProgress.correctInRow / unitPropProgress.requiredCorrect) / unitPropProgress.totalLevels) * 100}%` }}
                    />
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Case Split Progress */}
          <div>
            <div className="flex items-center gap-3 mb-4">
              <h3 className="text-2xl">Case Split</h3>
              {!caseSplitProgress.isUnlocked && (
                <div className="flex items-center gap-2 px-3 py-1 bg-gray-200 text-gray-700 rounded-full text-sm font-semibold">
                  <Lock className="w-4 h-4" />
                  Gesperrt
                </div>
              )}
              {caseSplitProgress.isCompleted ? (
                <span className="px-3 py-1 bg-green-600 text-white rounded-full text-sm font-semibold">
                  Abgeschlossen
                </span>
              ) : caseSplitProgress.isUnlocked && (
                <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-semibold">
                  Freigeschaltet
                </span>
              )}
            </div>
            
            <div className={`border rounded-lg p-6 ${
              caseSplitProgress.isUnlocked 
                ? 'bg-purple-50 border-purple-200' 
                : 'bg-gray-100 border-gray-300 opacity-60'
            }`}>
              {caseSplitProgress.isUnlocked ? (
                caseSplitProgress.isCompleted ? (
                  <>
                    <div className="grid grid-cols-2 gap-4 mb-4">
                      <div>
                        <p className="text-sm text-gray-600">Abgeschlossene Level</p>
                        <p className="text-2xl font-bold text-purple-600">
                          {caseSplitProgress.totalLevels} / {caseSplitProgress.totalLevels}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Gesamtfortschritt</p>
                        <p className="text-2xl font-bold text-purple-600">
                          100%
                        </p>
                      </div>
                    </div>
                    
                    <div className="h-4 bg-gray-300 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-green-500 transition-all duration-500"
                        style={{ width: '100%' }}
                      />
                    </div>
                  </>
                ) : (
                  <>
                    <div className="grid grid-cols-3 gap-4 mb-4">
                      <div>
                        <p className="text-sm text-gray-600">Aktuelles Level</p>
                        <p className="text-2xl font-bold text-purple-600">
                          {caseSplitProgress.currentLevel} / {caseSplitProgress.totalLevels}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Richtig in Folge</p>
                        <p className="text-2xl font-bold text-purple-600">
                          {caseSplitProgress.correctInRow} / {caseSplitProgress.requiredCorrect}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Gesamtfortschritt</p>
                        <p className="text-2xl font-bold text-purple-600">
                          {Math.round(((caseSplitProgress.currentLevel - 1 + caseSplitProgress.correctInRow / caseSplitProgress.requiredCorrect) / caseSplitProgress.totalLevels) * 100)}%
                        </p>
                      </div>
                    </div>
                    
                    <div className="h-4 bg-gray-300 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-purple-600 transition-all duration-500"
                        style={{ width: `${((caseSplitProgress.currentLevel - 1 + caseSplitProgress.correctInRow / caseSplitProgress.requiredCorrect) / caseSplitProgress.totalLevels) * 100}%` }}
                      />
                    </div>
                  </>
                )
              ) : (
                <div className="flex items-center justify-center gap-3 py-4">
                  <Lock className="w-8 h-8 text-gray-500" />
                  <p className="text-lg text-gray-600">
                    Schließe alle Unit Propagation Level ab, um diesen Bereich freizuschalten
                  </p>
                </div>
              )}
            </div>
          </div>
        </section>

        {/* Statistics Section */}
        <section className="bg-white border border-gray-300 rounded-lg shadow-lg p-8 mb-8">
          <h2 className="text-3xl mb-6">Statistiken</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-gradient-to-br from-green-50 to-green-100 border border-green-300 rounded-lg p-6 text-center">
              <div className="flex justify-center mb-3">
                <Target className="w-12 h-12 text-green-600" />
              </div>
              <p className="text-sm text-gray-600 mb-2">Korrekt gelöste Aufgaben</p>
              <p className="text-4xl font-bold text-green-700">{stats.correctSolved}</p>
            </div>
            
            <div className="bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-300 rounded-lg p-6 text-center">
              <div className="flex justify-center mb-3">
                <Flame className="w-12 h-12 text-orange-600" />
              </div>
              <p className="text-sm text-gray-600 mb-2">Aktuelle Streak</p>
              <p className="text-4xl font-bold text-orange-700">{stats.currentStreak}</p>
            </div>
            
            <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-300 rounded-lg p-6 text-center">
              <div className="flex justify-center mb-3">
                <Trophy className="w-12 h-12 text-yellow-600" />
              </div>
              <p className="text-sm text-gray-600 mb-2">Highscore Streak</p>
              <p className="text-4xl font-bold text-yellow-700">{stats.highscoreStreak}</p>
            </div>
            
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-300 rounded-lg p-6 text-center">
              <div className="flex justify-center mb-3">
                <TrendingUp className="w-12 h-12 text-blue-600" />
              </div>
              <p className="text-sm text-gray-600 mb-2">Gelöste Aufgaben Gesamt</p>
              <p className="text-4xl font-bold text-blue-700">{stats.totalSolved}</p>
            </div>
          </div>
        </section>

        {/* Account Management Section */}
        <section className="bg-gray-50 border border-gray-300 rounded-lg shadow-lg p-8">
          <h2 className="text-3xl mb-6">Account-Verwaltung</h2>
          
          <div className="space-y-4">
            <Button
              onClick={() => setShowPasswordModal(true)}
              className="w-full flex items-center justify-center gap-3 bg-blue-600 hover:bg-blue-700 text-white text-lg py-6 border-none"
            >
              <KeyRound className="w-5 h-5" />
              Passwort ändern
            </Button>
            
            <Button
              onClick={handleResetProgress}
              className="w-full flex items-center justify-center gap-3 bg-orange-600 hover:bg-orange-700 text-white text-lg py-6 border-none"
            >
              <RotateCcw className="w-5 h-5" />
              Fortschritt zurücksetzen
            </Button>
            
            <Button
              onClick={handleLogout}
              className="w-full flex items-center justify-center gap-3 bg-red-600 hover:bg-red-700 text-white text-lg py-6 border-none"
            >
              <LogOut className="w-5 h-5" />
              Ausloggen
            </Button>
          </div>
        </section>
      </main>

      {/* Password Change Modal */}
      {showPasswordModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
            <h3 className="text-2xl font-bold mb-6">Passwort ändern</h3>
            
            {passwordError && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                {passwordError}
              </div>
            )}
            
            {passwordSuccess && (
              <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
                Passwort erfolgreich geändert!
              </div>
            )}
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Aktuelles Passwort
                </label>
                <div className="relative">
                  <input
                    type={showPassword.old ? "text" : "password"}
                    value={passwordForm.oldPassword}
                    onChange={(e) => setPasswordForm(prev => ({ ...prev, oldPassword: e.target.value }))}
                    className="w-full px-4 py-2 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(prev => ({ ...prev, old: !prev.old }))}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                  >
                    {showPassword.old ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Neues Passwort
                </label>
                <div className="relative">
                  <input
                    type={showPassword.new ? "text" : "password"}
                    value={passwordForm.newPassword}
                    onChange={(e) => setPasswordForm(prev => ({ ...prev, newPassword: e.target.value }))}
                    className="w-full px-4 py-2 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(prev => ({ ...prev, new: !prev.new }))}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                  >
                    {showPassword.new ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Neues Passwort bestätigen
                </label>
                <div className="relative">
                  <input
                    type={showPassword.confirm ? "text" : "password"}
                    value={passwordForm.newPassword2}
                    onChange={(e) => setPasswordForm(prev => ({ ...prev, newPassword2: e.target.value }))}
                    className="w-full px-4 py-2 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(prev => ({ ...prev, confirm: !prev.confirm }))}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                  >
                    {showPassword.confirm ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
              </div>
            </div>
            
            <div className="flex gap-4 mt-6">
              <Button
                onClick={() => {
                  setShowPasswordModal(false);
                  setPasswordError(null);
                  setPasswordForm({ oldPassword: '', newPassword: '', newPassword2: '' });
                  setShowPassword({ old: false, new: false, confirm: false });
                }}
                className="flex-1 bg-gray-200 hover:bg-gray-300 text-black border-none"
              >
                Abbrechen
              </Button>
              <Button
                onClick={handlePasswordChange}
                className="flex-1 bg-red-600 hover:bg-red-700 text-white border-none"
              >
                Speichern
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Avatar Editor Modal */}
      {user.avatar && (
        <AvatarEditor
          isOpen={showAvatarEditor}
          onClose={() => setShowAvatarEditor(false)}
          currentAvatar={user.avatar}
          onAvatarUpdate={handleAvatarUpdate}
        />
      )}
    </div>
  );
}
