import { LucideIcon } from 'lucide-react';
import { ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface SelectionCardProps {
  title: string;
  icon: LucideIcon;
  link: string;
  color: string;
}

export function SelectionCard({ title, icon: Icon, link, color }: SelectionCardProps) {
  const navigate = useNavigate();

  const handleClick = () => {
    if (link.startsWith('http')) {
      window.location.href = link;
    } else {
      navigate(link);
    }
  };

  return (
    <button
      onClick={handleClick}
      className="group relative bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 p-8 text-left overflow-hidden transform hover:-translate-y-1 border-2 border-gray-200 hover:border-red-600"
    >
      {/* Gradient background */}
      <div className={`absolute top-0 left-0 w-full h-2 bg-gradient-to-r ${color}`} />
      
      <div className="relative z-10">
        <div className={`inline-flex p-4 rounded-xl bg-gradient-to-r ${color} mb-4 group-hover:scale-110 transition-transform duration-300`}>
          <Icon className="w-8 h-8 text-white" />
        </div>
        
        <h3 className="text-2xl font-semibold text-black mb-6">
          {title}
        </h3>
        
        <div className="flex items-center text-red-600 font-medium group-hover:gap-3 gap-2 transition-all">
          <span>Öffnen</span>
          <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
        </div>
      </div>
      
      {/* Hover effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-red-600/5 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700" />
    </button>
  );
}
