import { User, ArrowLeft } from 'lucide-react';
import { Button } from '../components/ui/button';
import { useNavigate } from 'react-router-dom';

export default function FreiesUeben() {
  const navigate = useNavigate();

  const handleAccountClick = () => {
    navigate('/account');
  };

  return (
    <div className="min-h-screen bg-white">
      <header className="container mx-auto px-4 py-6 flex justify-between items-center">
        <div className="flex items-center cursor-pointer" onClick={() => navigate('/')}>
          <img src="/hka-logo.jpg" alt="Hochschule Karlsruhe - University of Applied Sciences" className="h-48 w-auto object-contain" />
        </div>
        
          <Button 
            onClick={handleAccountClick}
            className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white border-none px-5 py-3 text-base"
          >
          <User className="w-4 h-4" />
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
        
        <h1 className="text-5xl mb-12">Freies Üben</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white border border-gray-200 rounded-2xl shadow-lg p-8">
            <h2 className="text-3xl font-semibold mb-4">Unit Propagation</h2>
            <p className="text-lg text-gray-700 mb-6">
              Üben Sie Unit Propagation mit verschiedenen Schwierigkeitsgraden
            </p>
            <Button
              onClick={() => navigate('/unit-propagation')}
              className="w-full bg-red-600 hover:bg-red-700 text-white"
            >
              Starten
            </Button>
          </div>

          <div className="bg-white border border-gray-200 rounded-2xl shadow-lg p-8">
            <h2 className="text-3xl font-semibold mb-4">Case Split</h2>
            <p className="text-lg text-gray-700 mb-6">
              Üben Sie Case Split mit verschiedenen Schwierigkeitsgraden
            </p>
            <Button
              onClick={() => navigate('/case-split')}
              className="w-full bg-red-600 hover:bg-red-700 text-white"
            >
              Starten
            </Button>
          </div>
        </div>
      </main>
    </div>
  );
}
