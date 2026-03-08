import { useEffect, useState } from 'react';
import { Trophy, Star, Sparkles, ArrowRight, PartyPopper } from 'lucide-react';
import { Button } from './ui/button';

interface CelebrationModalProps {
  isOpen: boolean;
  onClose: () => void;
  avatarUrl?: string;
  title: string;
  message: string;
  showFreiesUebenHint?: boolean;
  onNavigateToFreiesUeben?: () => void;
}

export default function CelebrationModal({
  isOpen,
  onClose,
  avatarUrl,
  title,
  message,
  showFreiesUebenHint = false,
  onNavigateToFreiesUeben
}: CelebrationModalProps) {
  const [confetti, setConfetti] = useState<Array<{ id: number; left: number; delay: number; color: string }>>([]);
  
  useEffect(() => {
    if (isOpen) {
      // Konfetti erzeugen
      const colors = ['#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899'];
      const newConfetti = Array.from({ length: 50 }, (_, i) => ({
        id: i,
        left: Math.random() * 100,
        delay: Math.random() * 2,
        color: colors[Math.floor(Math.random() * colors.length)]
      }));
      setConfetti(newConfetti);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" />
      
      {/* Konfetti Animation */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {confetti.map((piece) => (
          <div
            key={piece.id}
            className="absolute w-3 h-3 animate-confetti"
            style={{
              left: `${piece.left}%`,
              top: '-20px',
              backgroundColor: piece.color,
              animationDelay: `${piece.delay}s`,
              borderRadius: Math.random() > 0.5 ? '50%' : '0%',
              transform: `rotate(${Math.random() * 360}deg)`
            }}
          />
        ))}
      </div>
      
      {/* Modal Content */}
      <div className="relative bg-white rounded-3xl shadow-2xl p-8 max-w-lg w-full mx-4 transform animate-modal-pop">
        {/* Star Decorations */}
        <div className="absolute -top-4 -left-4">
          <Star className="w-8 h-8 text-yellow-400 fill-yellow-400 animate-pulse" />
        </div>
        <div className="absolute -top-4 -right-4">
          <Sparkles className="w-8 h-8 text-yellow-400 animate-pulse" style={{ animationDelay: '0.5s' }} />
        </div>
        
        {/* Trophy Icon */}
        <div className="flex justify-center mb-6">
          <div className="relative">
            <div className="w-20 h-20 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center animate-bounce-slow">
              {showFreiesUebenHint ? (
                <PartyPopper className="w-10 h-10 text-white" />
              ) : (
                <Trophy className="w-10 h-10 text-white" />
              )}
            </div>
            <div className="absolute -inset-2 bg-yellow-400/30 rounded-full animate-ping" style={{ animationDuration: '1.5s' }} />
          </div>
        </div>
        
        {/* Title */}
        <h2 className="text-3xl font-bold text-center text-gray-800 mb-4">
          {title}
        </h2>
        
        {/* Avatar mit Hüpf-Animation */}
        {avatarUrl && (
          <div className="flex justify-center mb-6">
            <div className="relative">
              {/* Schatten unter dem Avatar */}
              <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-24 h-4 bg-black/20 rounded-full animate-shadow-pulse" />
              
              {/* Avatar Container mit Hüpf-Animation */}
              <div className="animate-avatar-jump">
                <img 
                  src={avatarUrl} 
                  alt="Dein Avatar" 
                  className="w-32 h-32 rounded-full border-4 border-yellow-400 shadow-lg"
                />
              </div>
              
              {/* Sterne um den Avatar */}
              <Star className="absolute -top-2 -right-2 w-6 h-6 text-yellow-400 fill-yellow-400 animate-spin-slow" />
              <Star className="absolute -bottom-2 -left-2 w-5 h-5 text-yellow-400 fill-yellow-400 animate-spin-slow" style={{ animationDirection: 'reverse' }} />
            </div>
          </div>
        )}
        
        {/* Message */}
        <p className="text-lg text-center text-gray-600 mb-6">
          {message}
        </p>
        
        {/* Freies Üben Hint */}
        {showFreiesUebenHint && (
          <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-4 mb-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="font-semibold text-green-800">Neues Feature freigeschaltet!</p>
                <p className="text-sm text-green-700">
                  Du kannst jetzt im &quot;Freien Üben&quot; alle Aufgabentypen ohne Einschränkungen trainieren.
                </p>
              </div>
            </div>
          </div>
        )}
        
        {/* Buttons */}
        <div className="flex flex-col gap-3">
          {showFreiesUebenHint && onNavigateToFreiesUeben && (
            <Button
              onClick={onNavigateToFreiesUeben}
              className="w-full bg-green-600 hover:bg-green-700 text-white py-4 text-lg flex items-center justify-center gap-2 border-none"
            >
              Zum Freien Üben
              <ArrowRight className="w-5 h-5" />
            </Button>
          )}
          <Button
            onClick={onClose}
            className={`w-full py-4 text-lg border-none ${
              showFreiesUebenHint 
                ? 'bg-gray-200 hover:bg-gray-300 text-gray-700' 
                : 'bg-red-600 hover:bg-red-700 text-white'
            }`}
          >
            {showFreiesUebenHint ? 'Zum Lernpfad' : 'Weiter'}
          </Button>
        </div>
      </div>
      
      {/* CSS for custom animations */}
      <style>{`
        @keyframes confetti-fall {
          0% {
            transform: translateY(0) rotate(0deg);
            opacity: 1;
          }
          100% {
            transform: translateY(100vh) rotate(720deg);
            opacity: 0;
          }
        }
        
        @keyframes modal-pop {
          0% {
            transform: scale(0.5);
            opacity: 0;
          }
          50% {
            transform: scale(1.05);
          }
          100% {
            transform: scale(1);
            opacity: 1;
          }
        }
        
        @keyframes avatar-jump {
          0%, 100% {
            transform: translateY(0);
          }
          25% {
            transform: translateY(-20px) rotate(-5deg);
          }
          50% {
            transform: translateY(0);
          }
          75% {
            transform: translateY(-15px) rotate(5deg);
          }
        }
        
        @keyframes shadow-pulse {
          0%, 100% {
            transform: translateX(-50%) scaleX(1);
            opacity: 0.2;
          }
          25% {
            transform: translateX(-50%) scaleX(0.7);
            opacity: 0.1;
          }
          50% {
            transform: translateX(-50%) scaleX(1);
            opacity: 0.2;
          }
          75% {
            transform: translateX(-50%) scaleX(0.8);
            opacity: 0.15;
          }
        }
        
        @keyframes bounce-slow {
          0%, 100% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-10px);
          }
        }
        
        @keyframes spin-slow {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }
        
        .animate-confetti {
          animation: confetti-fall 3s ease-in-out forwards;
        }
        
        .animate-modal-pop {
          animation: modal-pop 0.5s ease-out forwards;
        }
        
        .animate-avatar-jump {
          animation: avatar-jump 1.5s ease-in-out infinite;
        }
        
        .animate-shadow-pulse {
          animation: shadow-pulse 1.5s ease-in-out infinite;
        }
        
        .animate-bounce-slow {
          animation: bounce-slow 2s ease-in-out infinite;
        }
        
        .animate-spin-slow {
          animation: spin-slow 4s linear infinite;
        }
      `}</style>
    </div>
  );
}
