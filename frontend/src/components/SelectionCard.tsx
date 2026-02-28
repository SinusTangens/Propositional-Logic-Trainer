import { LucideIcon } from 'lucide-react';
import { ArrowRight, Lock } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface SelectionCardProps {
  title: string;
  icon: LucideIcon;
  link: string;
  color: string;
  locked?: boolean;
  lockedMessage?: string;
}

export function SelectionCard({ title, icon: Icon, link, color, locked = false, lockedMessage }: SelectionCardProps) {
  const navigate = useNavigate();

  const handleClick = () => {
    if (locked) {
      // Bei gesperrten Karten trotzdem navigieren - die Zielseite zeigt die Sperrung
      navigate(link);
      return;
    }
    
    if (link.startsWith('http')) {
      window.location.href = link;
    } else {
      navigate(link);
    }
  };

  return (
    <button
      onClick={handleClick}
      className={`group relative bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 p-8 text-left overflow-hidden transform hover:-translate-y-1 border-2 ${
        locked 
          ? 'border-gray-200 hover:border-gray-400 opacity-75' 
          : 'border-gray-200 hover:border-red-600'
      }`}
    >
      {/* Gradient background */}
      <div className={`absolute top-0 left-0 w-full h-2 bg-gradient-to-r ${locked ? 'from-gray-400 to-gray-500' : color}`} />
      
      {/* Lock badge */}
      {locked && (
        <div className="absolute top-4 right-4 flex items-center gap-1 bg-gray-100 text-gray-600 px-3 py-1 rounded-full text-sm">
          <Lock className="w-4 h-4" />
          <span>Gesperrt</span>
        </div>
      )}
      
      <div className="relative z-10">
        <div className={`inline-flex p-4 rounded-xl bg-gradient-to-r ${locked ? 'from-gray-400 to-gray-500' : color} mb-4 group-hover:scale-110 transition-transform duration-300`}>
          <Icon className="w-8 h-8 text-white" />
        </div>
        
        <h3 className="text-2xl font-semibold text-black mb-2">
          {title}
        </h3>
        
        {locked && lockedMessage && (
          <p className="text-sm text-gray-500 mb-4">{lockedMessage}</p>
        )}
        
        <div className={`flex items-center font-medium group-hover:gap-3 gap-2 transition-all ${
          locked ? 'text-gray-400' : 'text-red-600'
        }`} style={{ marginTop: locked && lockedMessage ? 0 : '1.5rem' }}>
          <span>{locked ? 'Details ansehen' : 'Öffnen'}</span>
          <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
        </div>
      </div>
      
      {/* Hover effect */}
      <div className={`absolute inset-0 bg-gradient-to-r from-transparent ${locked ? 'via-gray-600/5' : 'via-red-600/5'} to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700`} />
    </button>
  );
}
