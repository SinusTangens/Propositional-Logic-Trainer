import { User, ArrowLeft } from 'lucide-react';
import { Button } from '../components/ui/button';
import { useNavigate } from 'react-router-dom';

export default function CaseSplit() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-white">
      <header className="container mx-auto px-4 py-6 flex justify-between items-center">
        <div className="flex items-center cursor-pointer" onClick={() => navigate('/')}>
          <img src="/hka-logo.jpg" alt="Hochschule Karlsruhe - University of Applied Sciences" className="h-48 w-auto object-contain" />
        </div>
        
          <Button 
            onClick={() => navigate('/account')}
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
        
        <h1 className="text-5xl mb-12">Case Split</h1>

        <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-12 max-w-4xl">
          <p className="text-xl text-gray-700">
            Case Split Übungen werden hier implementiert...
          </p>
        </div>
      </main>
    </div>
  );
}
