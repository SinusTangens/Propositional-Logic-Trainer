import { User, ArrowLeft } from 'lucide-react';
import { Button } from '../components/ui/button';
import { hkaLogo } from '../assets';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function Referenzen() {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();

  const handleAccountClick = () => {
    navigate('/account');
  };

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

      <main className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="flex items-center gap-4 mb-8">
          <Button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 bg-gray-200 hover:bg-gray-300 text-black border-none"
          >
            <ArrowLeft className="w-4 h-4" />
            Zurück
          </Button>
        </div>
        
        <h1 className="text-5xl mb-12">Referenzen</h1>

        <section className="space-y-8">
          <div className="bg-white border border-gray-200 rounded-lg p-6 shadow">
            <h2 className="text-2xl font-semibold mb-4 text-red-600">Vorlesungsmaterialien</h2>
            <ul className="space-y-3 text-gray-700">
              <li className="pl-4 border-l-4 border-red-600">
                <a href="https://ilias.h-ka.de/goto.php?target=crs_1052080&client_id=HSKA" target="_blank" rel="noopener noreferrer" className="text-red-600 hover:underline">
                  ILIAS-Kurs: Mathe 1
                </a>
              </li>
            </ul>
          </div>
        </section>
      </main>
    </div>
  );
}
