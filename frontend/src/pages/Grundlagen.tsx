import { User, ArrowLeft } from 'lucide-react';
import { Button } from '../components/ui/button';
import { useNavigate } from 'react-router-dom';

export default function Grundlagen() {
  const navigate = useNavigate();

  const handleAccountClick = () => {
    navigate('/account');
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
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
        
        <h1 className="text-5xl mb-12">Grundlagen der Aussagenlogik</h1>

        {/* Wahrheitstabelle Section */}
        <section className="mb-16">
          <h2 className="text-3xl mb-6 text-red-600">Wahrheitstabelle der logischen Operationen</h2>
          
          <div className="bg-white border border-gray-300 rounded-lg overflow-hidden shadow-lg">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-100">
                  <th className="border border-gray-300 px-6 py-4 text-xl">A</th>
                  <th className="border border-gray-300 px-6 py-4 text-xl">B</th>
                  <th className="border border-gray-300 px-6 py-4 text-xl">A ∧ B<br/>(AND)</th>
                  <th className="border border-gray-300 px-6 py-4 text-xl">A ∨ B<br/>(OR)</th>
                  <th className="border border-gray-300 px-6 py-4 text-xl">A ⊕ B<br/>(XOR)</th>
                  <th className="border border-gray-300 px-6 py-4 text-xl">A ↔ B<br/>(EQUIV)</th>
                  <th className="border border-gray-300 px-6 py-4 text-xl">A → B<br/>(IMP)</th>
                  <th className="border border-gray-300 px-6 py-4 text-xl">¬A<br/>(NOT)</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="border border-gray-300 px-6 py-3 text-center text-lg">W</td>
                  <td className="border border-gray-300 px-6 py-3 text-center text-lg">W</td>
                  <td className="border border-gray-300 px-6 py-3 text-center text-lg font-semibold">W</td>
                  <td className="border border-gray-300 px-6 py-3 text-center text-lg font-semibold">W</td>
                  <td className="border border-gray-300 px-6 py-3 text-center text-lg font-semibold">F</td>
                  <td className="border border-gray-300 px-6 py-3 text-center text-lg font-semibold">W</td>
                  <td className="border border-gray-300 px-6 py-3 text-center text-lg font-semibold">W</td>
                  <td className="border border-gray-300 px-6 py-3 text-center text-lg font-semibold">F</td>
                </tr>
                <tr className="bg-gray-50">
                  <td className="border border-gray-300 px-6 py-3 text-center text-lg">W</td>
                  <td className="border border-gray-300 px-6 py-3 text-center text-lg">F</td>
                  <td className="border border-gray-300 px-6 py-3 text-center text-lg font-semibold">F</td>
                  <td className="border border-gray-300 px-6 py-3 text-center text-lg font-semibold">W</td>
                  <td className="border border-gray-300 px-6 py-3 text-center text-lg font-semibold">W</td>
                  <td className="border border-gray-300 px-6 py-3 text-center text-lg font-semibold">F</td>
                  <td className="border border-gray-300 px-6 py-3 text-center text-lg font-semibold">F</td>
                  <td className="border border-gray-300 px-6 py-3 text-center text-lg font-semibold">F</td>
                </tr>
                <tr>
                  <td className="border border-gray-300 px-6 py-3 text-center text-lg">F</td>
                  <td className="border border-gray-300 px-6 py-3 text-center text-lg">W</td>
                  <td className="border border-gray-300 px-6 py-3 text-center text-lg font-semibold">F</td>
                  <td className="border border-gray-300 px-6 py-3 text-center text-lg font-semibold">W</td>
                  <td className="border border-gray-300 px-6 py-3 text-center text-lg font-semibold">W</td>
                  <td className="border border-gray-300 px-6 py-3 text-center text-lg font-semibold">F</td>
                  <td className="border border-gray-300 px-6 py-3 text-center text-lg font-semibold">W</td>
                  <td className="border border-gray-300 px-6 py-3 text-center text-lg font-semibold">W</td>
                </tr>
                <tr className="bg-gray-50">
                  <td className="border border-gray-300 px-6 py-3 text-center text-lg">F</td>
                  <td className="border border-gray-300 px-6 py-3 text-center text-lg">F</td>
                  <td className="border border-gray-300 px-6 py-3 text-center text-lg font-semibold">F</td>
                  <td className="border border-gray-300 px-6 py-3 text-center text-lg font-semibold">F</td>
                  <td className="border border-gray-300 px-6 py-3 text-center text-lg font-semibold">F</td>
                  <td className="border border-gray-300 px-6 py-3 text-center text-lg font-semibold">W</td>
                  <td className="border border-gray-300 px-6 py-3 text-center text-lg font-semibold">W</td>
                  <td className="border border-gray-300 px-6 py-3 text-center text-lg font-semibold">W</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        {/* Unit Propagation Section */}
        <section className="mb-16">
          <h2 className="text-3xl mb-6 text-red-600">Aufgabentyp: Unit Propagation</h2>
          
          <div className="bg-gray-50 border border-gray-300 rounded-lg p-8 mb-8">
            <h3 className="text-2xl mb-4 font-semibold">Erklärung</h3>
            <p className="text-lg leading-relaxed">
              Bei diesem Aufgabentyp sollen aus einer kleinen Menge von Prämissen direkte logische
              Folgerungen abgeleitet werden. Die Bearbeitung erfolgt, indem die gegebenen Aussagenmodelle betrachtet und jene Variablenbelegungen identifiziert werden, die alle Prämissen
              gleichzeitig erfüllen. Aus diesen gültigen Belegungen lässt sich anschließend bestimmen,
              welche Schlüsse logisch folgen.
            </p>
          </div>

          <div className="bg-white border border-gray-300 rounded-lg p-8">
            <h3 className="text-2xl mb-6 font-semibold">Beispiel</h3>
            
            <div className="mb-8 flex justify-center">
              <img src="/unit-prop-example.png" alt="Unit Propagation Beispiel" className="max-w-md" />
            </div>

            <div className="bg-blue-50 border-l-4 border-blue-500 p-6 mb-6">
              <h4 className="text-xl font-semibold mb-4">Gegeben:</h4>
              <div className="text-lg space-y-2">
                <p>Y → ¬V ∨ ¬X</p>
                <p>X</p>
              </div>
            </div>

            <div className="bg-green-50 border-l-4 border-green-500 p-6">
              <h4 className="text-xl font-semibold mb-4">Lösung:</h4>
              <div className="text-lg space-y-3">
                <p><strong>Schritt 1:</strong> Aus der zweiten Prämisse wissen wir direkt, dass X = wahr.</p>
                <p><strong>Schritt 2:</strong> Wir setzen X = wahr in die erste Prämisse ein:</p>
                <p className="ml-8">Y → ¬V ∨ ¬(wahr)</p>
                <p className="ml-8">Y → ¬V ∨ falsch</p>
                <p className="ml-8">Y → ¬V</p>
                <p><strong>Schritt 3:</strong> Damit diese Implikation wahr ist, gibt es zwei Möglichkeiten:</p>
                <ul className="ml-8 list-disc space-y-2">
                  <li>Fall 1: Y = falsch (dann ist die Implikation automatisch wahr)</li>
                  <li>Fall 2: Y = wahr und V = falsch (dann ist ¬V wahr, also die Implikation erfüllt)</li>
                </ul>
                <p className="mt-4"><strong>Ergebnis:</strong></p>
                <ul className="ml-8 list-disc space-y-2">
                  <li><strong>X = wahr</strong> (direkte Folgerung aus P2)</li>
                  <li><strong>Y:</strong> Kein konkreter Schluss möglich (kann wahr oder falsch sein)</li>
                  <li><strong>V:</strong> Kein konkreter Schluss möglich (hängt von Y ab)</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* Case Split Section */}
        <section className="mb-16">
          <h2 className="text-3xl mb-6 text-red-600">Aufgabentyp: Case Split</h2>
          
          <div className="bg-gray-50 border border-gray-300 rounded-lg p-8 mb-8">
            <h3 className="text-2xl mb-4 font-semibold">Erklärung</h3>
            <p className="text-lg leading-relaxed">
              Dieser Aufgabentyp erfordert das Bilden mehrstufiger Schlussketten aus einer größeren
              Menge an Prämissen. Um komplexe logische Zusammenhänge übersichtlich ableiten zu
              können, wird hierbei eine gezielte Fallunterscheidung getroffen, beispielsweise durch die
              Annahme einer Belegung für eine Variable wie A (wahr oder falsch). Auf Basis dieser
              Annahme werden die Prämissen nacheinander angewendet, um neue Aussagen abzuleiten
              und die Konsistenz des angenommenen Falls zu prüfen.
            </p>
          </div>

          <div className="bg-white border border-gray-300 rounded-lg p-8">
            <h3 className="text-2xl mb-6 font-semibold">Beispiel</h3>
            
            <div className="mb-8 flex justify-center">
              <img src="/case-split-example.png" alt="Case Split Beispiel" className="max-w-2xl" />
            </div>

            <div className="bg-blue-50 border-l-4 border-blue-500 p-6 mb-6">
              <h4 className="text-xl font-semibold mb-4">Gegeben:</h4>
              <div className="text-lg space-y-2">
                <p>(P1) ¬E → D</p>
                <p>(P2) ¬E ∨ ¬(D ∨ A)</p>
                <p>(P3) ¬D ∨ A</p>
                <p>(P4) E ∧ ¬D → A</p>
                <p>(P5) ¬B ∨ ¬A → E ∧ C</p>
                <p>(P6) ¬C ∧ B → ¬A ∧ B</p>
              </div>
            </div>

            <div className="bg-green-50 border-l-4 border-green-500 p-6">
              <h4 className="text-xl font-semibold mb-4">Lösung durch Fallunterscheidung:</h4>
              <div className="text-lg space-y-4">
                <div>
                  <p className="font-semibold mb-2">Fall 1: Angenommen E = wahr</p>
                  <ul className="ml-8 list-disc space-y-2">
                    <li>Aus P2: ¬E ∨ ¬(D ∨ A) wird zu: falsch ∨ ¬(D ∨ A), also muss ¬(D ∨ A) wahr sein</li>
                    <li>Das bedeutet: D = falsch UND A = falsch</li>
                    <li>Aus P4: E ∧ ¬D → A wird zu: wahr ∧ wahr → falsch, also: wahr → falsch</li>
                    <li><strong className="text-red-600">Dies ist ein Widerspruch!</strong></li>
                  </ul>
                </div>

                <div>
                  <p className="font-semibold mb-2">Fall 2: Angenommen E = falsch</p>
                  <ul className="ml-8 list-disc space-y-2">
                    <li>Aus P1: ¬E → D wird zu: wahr → D, also muss <strong>D = wahr</strong></li>
                    <li>Aus P3: ¬D ∨ A wird zu: falsch ∨ A, also muss <strong>A = wahr</strong></li>
                    <li>Aus P5: ¬B ∨ ¬A → E ∧ C wird zu: ¬B ∨ falsch → falsch ∧ C</li>
                    <li>Das heißt: ¬B → falsch, also muss <strong>B = wahr</strong></li>
                    <li>Aus P6: ¬C ∧ B → ¬A ∧ B wird zu: ¬C ∧ wahr → falsch ∧ wahr</li>
                    <li>Das heißt: ¬C → falsch, also muss <strong>C = wahr</strong></li>
                  </ul>
                </div>

                <div className="mt-6 p-4 bg-white rounded border-2 border-green-600">
                  <p className="font-semibold text-xl mb-3">Endgültige Lösung:</p>
                  <ul className="ml-8 list-disc space-y-1">
                    <li><strong>E = falsch</strong></li>
                    <li><strong>D = wahr</strong></li>
                    <li><strong>A = wahr</strong></li>
                    <li><strong>B = wahr</strong></li>
                    <li><strong>C = wahr</strong></li>
                  </ul>
                  <p className="mt-4">Alle Variablen haben eindeutige Werte, die alle Prämissen gleichzeitig erfüllen.</p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
