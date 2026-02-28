import { ArrowLeft } from 'lucide-react';
import { Button } from '../components/ui/button';
import { hkaLogo } from '../assets';
import { useNavigate } from 'react-router-dom';

export default function Datenschutz() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="container mx-auto px-4 py-6 flex justify-between items-center">
        <div className="flex items-center cursor-pointer" onClick={() => navigate('/')}>
          <img src={hkaLogo} alt="Hochschule Karlsruhe - University of Applied Sciences" className="h-48 w-auto object-contain" />
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="flex items-center gap-4 mb-8">
          <Button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 bg-gray-200 hover:bg-gray-300 text-black border-none"
          >
            <ArrowLeft className="w-4 h-4" />
            Zurück
          </Button>
        </div>

        <h1 className="text-4xl font-bold mb-8">Datenschutzerklärung</h1>

        <div className="prose prose-lg max-w-none space-y-8">
          {/* Einleitung */}
          <section>
            <h2 className="text-2xl font-semibold text-red-600 mb-4">1. Allgemeine Hinweise</h2>
            <p className="text-gray-700 leading-relaxed">
              Diese Webanwendung wurde im Rahmen einer Bachelorarbeit an der Hochschule Karlsruhe – 
              Technik und Wirtschaft entwickelt. Der Schutz Ihrer persönlichen Daten ist uns wichtig. 
              Diese Datenschutzerklärung informiert Sie darüber, welche Daten erhoben werden und wie 
              diese verwendet werden.
            </p>
          </section>

          {/* Verantwortlicher */}
          <section>
            <h2 className="text-2xl font-semibold text-red-600 mb-4">2. Verantwortlicher</h2>
            <div className="text-gray-700 leading-relaxed">
              <p><strong>Verantwortlich für diese Webanwendung:</strong></p>
              <p>Reimar Hofmann</p>
              <p>Hochschule Karlsruhe – Technik und Wirtschaft</p>
              <p>Moltkestraße 30</p>
              <p>76133 Karlsruhe</p>
              <p className="mt-2"><strong>E-Mail:</strong> hore0001@h-ka.de</p>
            </div>
          </section>

          {/* Erhobene Daten */}
          <section>
            <h2 className="text-2xl font-semibold text-red-600 mb-4">3. Welche Daten werden erhoben?</h2>
            <div className="text-gray-700 leading-relaxed">
              <p className="mb-4">Bei der Nutzung dieser Anwendung werden folgende Daten erhoben:</p>
              
              <h3 className="text-xl font-medium mb-2">3.1 Registrierungsdaten</h3>
              <ul className="list-disc pl-6 mb-4">
                <li>Benutzername</li>
                <li>E-Mail-Adresse</li>
                <li>Passwort (verschlüsselt gespeichert)</li>
              </ul>

              <h3 className="text-xl font-medium mb-2">3.2 Nutzungsdaten</h3>
              <ul className="list-disc pl-6 mb-4">
                <li>Lernfortschritt (gelöste Aufgaben, erreichte Punkte)</li>
                <li>Avatar-Einstellungen</li>
                <li>Zeitpunkt der Registrierung und letzten Anmeldung</li>
              </ul>

              <h3 className="text-xl font-medium mb-2">3.3 Technische Daten</h3>
              <ul className="list-disc pl-6">
                <li>IP-Adresse (für die Dauer der Sitzung)</li>
                <li>Session-Cookies für die Authentifizierung</li>
              </ul>
            </div>
          </section>

          {/* Zweck der Datenverarbeitung */}
          <section>
            <h2 className="text-2xl font-semibold text-red-600 mb-4">4. Zweck der Datenverarbeitung</h2>
            <div className="text-gray-700 leading-relaxed">
              <p className="mb-4">Die erhobenen Daten werden ausschließlich für folgende Zwecke verwendet:</p>
              <ul className="list-disc pl-6">
                <li>Bereitstellung und Verwaltung Ihres Benutzerkontos</li>
                <li>Speicherung Ihres Lernfortschritts</li>
                <li>Personalisierung der Lernerfahrung (Avatar)</li>
                <li>Technische Bereitstellung der Anwendung</li>
              </ul>
            </div>
          </section>

          {/* Speicherung */}
          <section>
            <h2 className="text-2xl font-semibold text-red-600 mb-4">5. Datenspeicherung</h2>
            <p className="text-gray-700 leading-relaxed">
              Ihre Daten werden auf Servern gespeichert, die im Rahmen dieses Hochschulprojekts 
              betrieben werden. Die Daten werden so lange gespeichert, wie Ihr Benutzerkonto 
              besteht oder bis Sie die Löschung beantragen.
            </p>
          </section>

          {/* Cookies */}
          <section>
            <h2 className="text-2xl font-semibold text-red-600 mb-4">6. Cookies</h2>
            <div className="text-gray-700 leading-relaxed">
              <p className="mb-4">Diese Anwendung verwendet ausschließlich technisch notwendige Cookies:</p>
              <ul className="list-disc pl-6">
                <li><strong>Session-Cookie:</strong> Speichert Ihre Anmeldeinformationen während der Sitzung</li>
                <li><strong>CSRF-Token:</strong> Schutz vor Cross-Site-Request-Forgery-Angriffen</li>
              </ul>
              <p className="mt-4">
                Es werden keine Tracking-Cookies oder Cookies von Drittanbietern verwendet.
              </p>
            </div>
          </section>

          {/* Ihre Rechte */}
          <section>
            <h2 className="text-2xl font-semibold text-red-600 mb-4">7. Ihre Rechte</h2>
            <div className="text-gray-700 leading-relaxed">
              <p className="mb-4">Sie haben gemäß DSGVO folgende Rechte:</p>
              <ul className="list-disc pl-6">
                <li><strong>Auskunftsrecht:</strong> Sie können Auskunft über Ihre gespeicherten Daten verlangen</li>
                <li><strong>Berichtigungsrecht:</strong> Sie können die Berichtigung falscher Daten verlangen</li>
                <li><strong>Löschungsrecht:</strong> Sie können die Löschung Ihrer Daten verlangen</li>
                <li><strong>Datenübertragbarkeit:</strong> Sie können Ihre Daten in einem gängigen Format anfordern</li>
              </ul>
              <p className="mt-4">
                Zur Ausübung Ihrer Rechte wenden Sie sich bitte an die oben genannte E-Mail-Adresse.
              </p>
            </div>
          </section>

          {/* Kontakt */}
          <section>
            <h2 className="text-2xl font-semibold text-red-600 mb-4">8. Kontakt bei Datenschutzfragen</h2>
            <p className="text-gray-700 leading-relaxed">
              Bei Fragen zum Datenschutz können Sie sich jederzeit an den Verantwortlichen wenden.
              Zusätzlich haben Sie das Recht, sich bei einer Datenschutz-Aufsichtsbehörde zu beschweren.
            </p>
          </section>

          {/* Änderungen */}
          <section>
            <h2 className="text-2xl font-semibold text-red-600 mb-4">9. Änderungen dieser Datenschutzerklärung</h2>
            <p className="text-gray-700 leading-relaxed">
              Diese Datenschutzerklärung kann bei Bedarf aktualisiert werden. Die aktuelle Version 
              ist stets auf dieser Seite verfügbar.
            </p>
            <p className="text-gray-500 mt-4 text-sm">
              Stand: Februar 2026
            </p>
          </section>
        </div>
      </main>
    </div>
  );
}
