import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

/**
 * Scrollt die Seite bei jeder Navigation automatisch nach oben.
 * Muss innerhalb des Router-Kontexts verwendet werden.
 */
export default function ScrollToTop() {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  return null;
}
