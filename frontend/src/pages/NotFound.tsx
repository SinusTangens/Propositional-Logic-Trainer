import { Home, ArrowLeft } from 'lucide-react';
import { Button } from '../components/ui/button';
import { hkaLogo } from '../assets';
import { useNavigate } from 'react-router-dom';

export default function NotFound() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Header */}
      <header className="container mx-auto px-4 py-6 flex justify-between items-center">
        <div className="flex items-center cursor-pointer" onClick={() => navigate('/')}>
          <img src={hkaLogo} alt="Hochschule Karlsruhe - University of Applied Sciences" className="h-48 w-auto object-contain" />
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center px-4">
        <div className="text-center max-w-lg">
          {/* 404 Große Zahl */}
          <h1 className="text-9xl font-bold text-red-600 mb-4">404</h1>
          
          {/* Untertitel */}
          <h2 className="text-3xl font-semibold text-gray-800 mb-4">
            Seite nicht gefunden
          </h2>
          
          {/* Beschreibung */}
          <p className="text-lg text-gray-600 mb-8">
            Die angeforderte Seite existiert leider nicht. 
            Möglicherweise wurde sie verschoben oder der Link ist fehlerhaft.
          </p>

          {/* Logik-Witz */}
          <div className="bg-gray-100 rounded-lg p-4 mb-8">
            <p className="text-gray-700 italic">
              "Wenn diese Seite existiert, dann ist 0 = 1."
            </p>
            <p className="text-sm text-gray-500 mt-2">
              — Ein klassisches Beispiel für eine wahre Implikation mit falscher Prämisse
            </p>
          </div>

          {/* Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              onClick={() => navigate(-1)}
              className="flex items-center justify-center gap-2 bg-gray-200 hover:bg-gray-300 text-black border-none px-6 py-3"
            >
              <ArrowLeft className="w-5 h-5" />
              Zurück
            </Button>
            
            <Button
              onClick={() => navigate('/')}
              className="flex items-center justify-center gap-2 bg-red-600 hover:bg-red-700 text-white border-none px-6 py-3"
            >
              <Home className="w-5 h-5" />
              Zur Startseite
            </Button>
          </div>
        </div>
      </main>
    </div>
  );
}
