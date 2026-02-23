import { BrowserRouter as Router, Routes, Route, useNavigate, Navigate } from 'react-router-dom';
import { SelectionCard } from './components/SelectionCard';
import { Route as RouteIcon, BookOpen, Library, FileText, LogIn } from 'lucide-react';
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
  const { isAuthenticated } = useAuth();

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
      color: 'from-red-600 to-red-700'
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
          <img src="/hka-logo.jpg" alt="Hochschule Karlsruhe - University of Applied Sciences" className="h-48 w-auto object-contain" />
        </div>
        
        <Button 
          onClick={handleAuthClick}
          className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white border-none px-5 py-3 text-base"
        >
          {isAuthenticated ? (
            <>
              <User className="w-4 h-4" />
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
            />
          ))}
        </div>
      </main>

      {/* Footer with Impressum */}
      <footer className="container mx-auto px-4 py-8 mt-12 border-t border-gray-300">
        <div className="max-w-5xl mx-auto text-center">
          <h2 className="text-xl font-semibold mb-4">Impressum</h2>
          <div className="text-sm text-gray-700 space-y-2">
            <p className="font-semibold">Hochschule Karlsruhe – Technik und Wirtschaft</p>
            <p>Moltkestraße 30</p>
            <p>76133 Karlsruhe</p>
            <p className="mt-4">
              <strong>Telefon:</strong> +49 721 925-0<br />
              <strong>E-Mail:</strong> info@h-ka.de
            </p>
            <p className="mt-4">
              <strong>Vertreten durch:</strong> Prof. Dr. rer. nat. Frank Artinger (Rektor)
            </p>
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
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/grundlagen" element={<Grundlagen />} />
          <Route path="/referenzen" element={<Referenzen />} />
          
          {/* Protected Routes - erfordern Login */}
          <Route path="/lernpfad" element={<ProtectedRoute><Lernpfad /></ProtectedRoute>} />
          <Route path="/freies-ueben" element={<ProtectedRoute><FreiesUeben /></ProtectedRoute>} />
          <Route path="/unit-propagation" element={<ProtectedRoute><UnitPropagation /></ProtectedRoute>} />
          <Route path="/case-split" element={<ProtectedRoute><CaseSplit /></ProtectedRoute>} />
          <Route path="/account" element={<ProtectedRoute><Account /></ProtectedRoute>} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}
