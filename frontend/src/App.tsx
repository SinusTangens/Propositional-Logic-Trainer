import { BrowserRouter as Router, Routes, Route, useNavigate, Navigate } from 'react-router-dom';
import { SelectionCard } from './components/SelectionCard';
import { Route as RouteIcon, BookOpen, Library, FileText, LogIn } from 'lucide-react';
import { hkaLogo } from './assets';
import { User } from 'lucide-react';
import { Button } from './components/ui/button';
import { LogicSymbolsLogo } from './components/LogicSymbolsLogo';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Lernpfad from './pages/Lernpfad';
import FreiesUeben from './pages/FreiesUeben';
import UnitPropagation from './pages/UnitPropagation';
import CaseSplit from './pages/CaseSplit';
import Grundlagen from './pages/Grundlagen';
import Referenzen from './pages/Referenzen';
import Account from './pages/Account';
import Login from './pages/Login';
import Datenschutz from './pages/Datenschutz';
import NotFound from './pages/NotFound';
import ScrollToTop from './components/ScrollToTop';

// Protected Route Wrapper - leitet zu Login um wenn nicht eingeloggt
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-gray-600">Laden...</div>
      </div>
    );
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
}

function HomePage() {
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuth();

  // Progress prüfen für Freies Üben Sperrung
  const progress = user?.progress || [];
  const unitPropProgress = progress.find(p => p.task_type === 'DIRECT_INFERENCE');
  const caseSplitProgress = progress.find(p => p.task_type === 'CASE_SPLIT');
  const isLernpfadCompleted = unitPropProgress?.isCompleted && caseSplitProgress?.isCompleted;

  const cards = [
    {
      id: 1,
      title: 'Lernpfad',
      icon: RouteIcon,
      link: '/lernpfad',
      color: 'from-red-600 to-red-700'
    },
    {
      id: 2,
      title: 'Freies Üben',
      icon: BookOpen,
      link: '/freies-ueben',
      color: 'from-red-600 to-red-700',
      locked: !isLernpfadCompleted,
      lockedMessage: 'Schließe zuerst den Lernpfad ab'
    },
    {
      id: 3,
      title: 'Grundlagen',
      icon: Library,
      link: '/grundlagen',
      color: 'from-gray-800 to-black'
    },
    {
      id: 4,
      title: 'Referenzen',
      icon: FileText,
      link: '/referenzen',
      color: 'from-gray-800 to-black'
    }
  ];

  const handleAuthClick = () => {
    if (isAuthenticated) {
      navigate('/account');
    } else {
      navigate('/login');
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header with Logo and Account Button */}
      <header className="container mx-auto px-4 py-6 flex justify-between items-center">
        <div className="flex items-center">
          <img src={hkaLogo} alt="Hochschule Karlsruhe - University of Applied Sciences" className="h-48 w-auto object-contain" />
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
      
      <main className="container mx-auto px-4 py-12">
        <div className="flex items-center justify-center gap-16 mb-12 bg-gradient-to-r from-red-50 via-white to-red-50 py-8 px-6 rounded-2xl">
          <h1 className="text-4xl font-bold text-black">Logik-Trainer</h1>
          <LogicSymbolsLogo className="w-72 h-72" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-5xl mx-auto">
          {cards.map((card) => (
            <SelectionCard
              key={card.id}
              title={card.title}
              icon={card.icon}
              link={card.link}
              color={card.color}
              locked={card.locked}
              lockedMessage={card.lockedMessage}
            />
          ))}
        </div>
      </main>

      {/* Footer with Impressum */}
      <footer className="container mx-auto px-4 py-8 mt-12 border-t border-gray-300">
        <div className="max-w-5xl mx-auto text-center">
          <h2 className="text-xl font-semibold mb-4">Impressum</h2>
          <div className="text-sm text-gray-700 space-y-2">
            <p className="font-semibold">Bachelorarbeit an der Hochschule Karlsruhe – Technik und Wirtschaft</p>
            
            <div className="mt-4">
              <p><strong>Autor:</strong> Sinan Kammerer</p>
              <p><strong>Studiengang:</strong> Data Science</p>
              <p><strong>Betreuender Professor:</strong> Prof. Dr. Reimar Hofmann</p>
            </div>
            
            <div className="mt-4">
              <p className="font-semibold">Hochschuladresse:</p>
              <p>Moltkestraße 30</p>
              <p>76133 Karlsruhe</p>
            </div>
            
            <p className="mt-4">
              <strong>Kontakt:</strong> sinan.kammerer@gmail.com
            </p>
            
            <p className="mt-4 text-xs text-gray-500">
              Diese Webanwendung wurde im Rahmen einer Bachelorarbeit entwickelt.
            </p>
            
            <a 
              href="/datenschutz" 
              className="mt-4 block text-red-600 hover:text-red-800 underline"
            >
              Datenschutzerklärung
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <ScrollToTop />
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/grundlagen" element={<Grundlagen />} />
          <Route path="/referenzen" element={<Referenzen />} />
          <Route path="/datenschutz" element={<Datenschutz />} />
          
          {/* Protected Routes - erfordern Login */}
          <Route path="/lernpfad" element={<ProtectedRoute><Lernpfad /></ProtectedRoute>} />
          <Route path="/freies-ueben" element={<ProtectedRoute><FreiesUeben /></ProtectedRoute>} />
          <Route path="/unit-propagation" element={<ProtectedRoute><UnitPropagation /></ProtectedRoute>} />
          <Route path="/case-split" element={<ProtectedRoute><CaseSplit /></ProtectedRoute>} />
          <Route path="/account" element={<ProtectedRoute><Account /></ProtectedRoute>} />
          
          {/* 404 Fallback */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}
