export function LogicSymbolsLogo({ className = "w-72 h-72" }: { className?: string }) {
  return (
    <svg 
      className={className} 
      viewBox="0 0 500 250" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Connections - drawn first so they appear behind nodes */}
      {/* Layer 1 to Layer 2 connections */}
      <line x1="40" y1="50" x2="110" y2="60" stroke="#DC2626" strokeWidth="2.5" />
      <line x1="40" y1="50" x2="110" y2="120" stroke="#9CA3AF" strokeWidth="2" />
      <line x1="40" y1="50" x2="110" y2="180" stroke="#DC2626" strokeWidth="2.5" />
      
      <line x1="40" y1="120" x2="110" y2="60" stroke="#DC2626" strokeWidth="2.5" />
      <line x1="40" y1="120" x2="110" y2="120" stroke="#DC2626" strokeWidth="2.5" />
      <line x1="40" y1="120" x2="110" y2="180" stroke="#9CA3AF" strokeWidth="2" />
      
      <line x1="40" y1="190" x2="110" y2="60" stroke="#9CA3AF" strokeWidth="2" />
      <line x1="40" y1="190" x2="110" y2="120" stroke="#1F2937" strokeWidth="2.5" />
      <line x1="40" y1="190" x2="110" y2="180" stroke="#DC2626" strokeWidth="2.5" />
      
      {/* Layer 2 to Layer 3 connections */}
      <line x1="130" y1="60" x2="200" y2="70" stroke="#DC2626" strokeWidth="2.5" />
      <line x1="130" y1="60" x2="200" y2="130" stroke="#9CA3AF" strokeWidth="2" />
      <line x1="130" y1="60" x2="200" y2="190" stroke="#DC2626" strokeWidth="2.5" />
      
      <line x1="130" y1="120" x2="200" y2="70" stroke="#9CA3AF" strokeWidth="2" />
      <line x1="130" y1="120" x2="200" y2="130" stroke="#DC2626" strokeWidth="2.5" />
      <line x1="130" y1="120" x2="200" y2="190" stroke="#DC2626" strokeWidth="2.5" />
      
      <line x1="130" y1="180" x2="200" y2="70" stroke="#DC2626" strokeWidth="2.5" />
      <line x1="130" y1="180" x2="200" y2="130" stroke="#1F2937" strokeWidth="2.5" />
      <line x1="130" y1="180" x2="200" y2="190" stroke="#9CA3AF" strokeWidth="2" />
      
      {/* Layer 3 to Layer 4 connections */}
      <line x1="220" y1="70" x2="290" y2="60" stroke="#DC2626" strokeWidth="2.5" />
      <line x1="220" y1="70" x2="290" y2="120" stroke="#9CA3AF" strokeWidth="2" />
      <line x1="220" y1="70" x2="290" y2="180" stroke="#DC2626" strokeWidth="2.5" />
      
      <line x1="220" y1="130" x2="290" y2="60" stroke="#9CA3AF" strokeWidth="2" />
      <line x1="220" y1="130" x2="290" y2="120" stroke="#DC2626" strokeWidth="2.5" />
      <line x1="220" y1="130" x2="290" y2="180" stroke="#1F2937" strokeWidth="2.5" />
      
      <line x1="220" y1="190" x2="290" y2="60" stroke="#DC2626" strokeWidth="2.5" />
      <line x1="220" y1="190" x2="290" y2="120" stroke="#DC2626" strokeWidth="2.5" />
      <line x1="220" y1="190" x2="290" y2="180" stroke="#9CA3AF" strokeWidth="2" />
      
      {/* Layer 4 to Layer 5 connections */}
      <line x1="310" y1="60" x2="380" y2="90" stroke="#DC2626" strokeWidth="2.5" />
      <line x1="310" y1="60" x2="380" y2="150" stroke="#1F2937" strokeWidth="2.5" />
      
      <line x1="310" y1="120" x2="380" y2="90" stroke="#9CA3AF" strokeWidth="2" />
      <line x1="310" y1="120" x2="380" y2="150" stroke="#DC2626" strokeWidth="2.5" />
      
      <line x1="310" y1="180" x2="380" y2="90" stroke="#9CA3AF" strokeWidth="2" />
      <line x1="310" y1="180" x2="380" y2="150" stroke="#DC2626" strokeWidth="2.5" />
      
      {/* Layer 5 to Layer 6 connections */}
      <line x1="400" y1="90" x2="460" y2="120" stroke="#DC2626" strokeWidth="2.5" />
      <line x1="400" y1="150" x2="460" y2="120" stroke="#9CA3AF" strokeWidth="2" />
      
      {/* Layer 1 - leftmost (3 nodes) */}
      <circle cx="40" cy="50" r="16" fill="#1F2937" />
      <text 
        x="40" 
        y="50" 
        textAnchor="middle" 
        dominantBaseline="central" 
        fill="white" 
        fontSize="20"
        fontFamily="serif"
        fontWeight="bold"
      >
        ¬
      </text>
      
      <circle cx="40" cy="120" r="16" fill="#DC2626" />
      <text 
        x="40" 
        y="120" 
        textAnchor="middle" 
        dominantBaseline="central" 
        fill="white" 
        fontSize="20"
        fontFamily="serif"
        fontWeight="bold"
      >
        ∧
      </text>
      
      <circle cx="40" cy="190" r="16" fill="#DC2626" />
      <text 
        x="40" 
        y="190" 
        textAnchor="middle" 
        dominantBaseline="central" 
        fill="white" 
        fontSize="20"
        fontFamily="serif"
        fontWeight="bold"
      >
        ∨
      </text>
      
      {/* Layer 2 (3 nodes) */}
      <circle cx="110" cy="60" r="16" fill="#DC2626" />
      <text 
        x="110" 
        y="60" 
        textAnchor="middle" 
        dominantBaseline="central" 
        fill="white" 
        fontSize="20"
        fontFamily="serif"
        fontWeight="bold"
      >
        ∧
      </text>
      
      <circle cx="110" cy="120" r="16" fill="#DC2626" />
      <text 
        x="110" 
        y="120" 
        textAnchor="middle" 
        dominantBaseline="central" 
        fill="white" 
        fontSize="20"
        fontFamily="serif"
        fontWeight="bold"
      >
        ∨
      </text>
      
      <circle cx="110" cy="180" r="16" fill="#1F2937" />
      <text 
        x="110" 
        y="180" 
        textAnchor="middle" 
        dominantBaseline="central" 
        fill="white" 
        fontSize="20"
        fontFamily="serif"
        fontWeight="bold"
      >
        ¬
      </text>
      
      {/* Layer 3 (3 nodes) */}
      <circle cx="200" cy="70" r="16" fill="#DC2626" />
      <text 
        x="200" 
        y="70" 
        textAnchor="middle" 
        dominantBaseline="central" 
        fill="white" 
        fontSize="20"
        fontFamily="serif"
        fontWeight="bold"
      >
        →
      </text>
      
      <circle cx="200" cy="130" r="16" fill="#9CA3AF" />
      <text 
        x="200" 
        y="130" 
        textAnchor="middle" 
        dominantBaseline="central" 
        fill="white" 
        fontSize="20"
        fontFamily="serif"
        fontWeight="bold"
      >
        ⊕
      </text>
      
      <circle cx="200" cy="190" r="16" fill="#DC2626" />
      <text 
        x="200" 
        y="190" 
        textAnchor="middle" 
        dominantBaseline="central" 
        fill="white" 
        fontSize="20"
        fontFamily="serif"
        fontWeight="bold"
      >
        ∨
      </text>
      
      {/* Layer 4 (3 nodes) */}
      <circle cx="290" cy="60" r="16" fill="#DC2626" />
      <text 
        x="290" 
        y="60" 
        textAnchor="middle" 
        dominantBaseline="central" 
        fill="white" 
        fontSize="20"
        fontFamily="serif"
        fontWeight="bold"
      >
        ∧
      </text>
      
      <circle cx="290" cy="120" r="16" fill="#DC2626" />
      <text 
        x="290" 
        y="120" 
        textAnchor="middle" 
        dominantBaseline="central" 
        fill="white" 
        fontSize="20"
        fontFamily="serif"
        fontWeight="bold"
      >
        ↔
      </text>
      
      <circle cx="290" cy="180" r="16" fill="#1F2937" />
      <text 
        x="290" 
        y="180" 
        textAnchor="middle" 
        dominantBaseline="central" 
        fill="white" 
        fontSize="20"
        fontFamily="serif"
        fontWeight="bold"
      >
        ¬
      </text>
      
      {/* Layer 5 (2 nodes) */}
      <circle cx="380" cy="90" r="16" fill="#9CA3AF" />
      <text 
        x="380" 
        y="90" 
        textAnchor="middle" 
        dominantBaseline="central" 
        fill="white" 
        fontSize="20"
        fontFamily="serif"
        fontWeight="bold"
      >
        →
      </text>
      
      <circle cx="380" cy="150" r="16" fill="#1F2937" />
      <text 
        x="380" 
        y="150" 
        textAnchor="middle" 
        dominantBaseline="central" 
        fill="white" 
        fontSize="20"
        fontFamily="serif"
        fontWeight="bold"
      >
        ¬
      </text>
      
      {/* Layer 6 - rightmost (1 node) */}
      <circle cx="460" cy="120" r="16" fill="#DC2626" />
      <text 
        x="460" 
        y="120" 
        textAnchor="middle" 
        dominantBaseline="central" 
        fill="white" 
        fontSize="20"
        fontFamily="serif"
        fontWeight="bold"
      >
        ∨
      </text>
    </svg>
  );
}
