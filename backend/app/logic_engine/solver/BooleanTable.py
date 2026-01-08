import numpy as np
from typing import List, Set, Optional
from sympy import Symbol

class BooleanTable:
    """
    Repräsentiert eine boolesche Tabelle (Boolean Array) gemäß dem Shenoy-Shafer Framework.
    Kapselt ein NumPy Array und die zugehörigen SymPy-Variablen.
    """


    def __init__(self, variables: List[Symbol], data: np.ndarray, source_indices: Optional[Set[int]] = None):

        self.variables = variables
        self.data = data.astype(bool) 
        self.source_indices = source_indices if source_indices is not None else set()         # source_indices merkt sich, aus welchen ursprünglichen Prämissen (P1, P2...) diese Tabelle stammt



    @property
    def rank(self):
        return len(self.variables)



    def extend_to(self, new_vars: List[Symbol]) -> 'BooleanTable':
        """
        Erweitert die Tabelle auf eine größere Menge von Variablen (Broadcasting).
        Richtet die Achsen so aus, dass sie der Reihenfolge in 'new_vars' entsprechen.
        
        Beispiel:
        Self: [B, A] (Shape 2x2)
        Target: [A, C, B] (Shape 2x2x2)
        Ergebnis: Die Daten werden transponiert und entlang C wiederholt.
        """
        if self.variables == new_vars:
            return self

        # Prüfung, ob new_vars wirklich eine Obermenge von self.variables ist
        current_set = set(self.variables)
        new_set = set(new_vars)
        if not current_set.issubset(new_set):
            raise ValueError("Neue Variablen müssen eine Obermenge der aktuellen sein.")

        # Aktuelle Daten
        new_data = self.data
        current_vars_list = list(self.variables)

        
        
        for i, target_var in enumerate(new_vars):

            if target_var in current_vars_list:             #Falls die Variable in current_vars_list schon existiert, muss sie permutiert werden (man will bspw. [A, B] statt [B, A])
                
                #Momentanen Index der Variable ermitteln und anhand dessen die Achse verschieben
                current_idx = current_vars_list.index(target_var)
                new_data = np.moveaxis(new_data, current_idx, i)
                
                # Aktualisiere unsere interne Liste, um den Move widerzuspiegeln
                moved_var = current_vars_list.pop(current_idx)
                current_vars_list.insert(i, moved_var)
                
            else:           #Falls die Variable noch nicht existiert wird eine neue Achse/Dimension eingefügt
                
                # Fügt neue Dimension der Größe 1 hinzu
                new_data = np.expand_dims(new_data, axis=i)         
                current_vars_list.insert(i, target_var)


        return BooleanTable(new_vars, new_data, self.source_indices)



    @staticmethod
    def combine(t1: 'BooleanTable', t2: 'BooleanTable') -> 'BooleanTable':
        """
        Implementiert die Kombination (Otimes): T1 AND T2.
        Nimmt das Minimum (logisches UND) der Einträge.
        """

        # Vereinigungsmenge der Variablen beider Tabllen bilden und alphabetisch sortieren
        all_vars_set = set(t1.variables + t2.variables)
        all_vars = sorted(list(all_vars_set), key=lambda s: s.name)
        

        # Beide Tabellen auf den gemeinsamen Raum erweitern
        t1_ext = t1.extend_to(all_vars)
        t2_ext = t2.extend_to(all_vars)
        
        # Beide Tabellen durch logisches UND kombinieren
        combined_data = np.logical_and(t1_ext.data, t2_ext.data)
        
        # Quellenindizes in einer Menge zusammenführen
        combined_sources = t1.source_indices.union(t2.source_indices)
        
        return BooleanTable(all_vars, combined_data, combined_sources)



    def marginalize(self, var_to_remove: Symbol) -> 'BooleanTable':
        """
        Löscht eine Variable durch Marginalisierung (Maximum / Logisches ODER).
        Entspricht T^{-v}.
        """
        if var_to_remove not in self.variables:
            return self
        
        # Filtert Index der zu löschenden Variable heraus 
        axis = self.variables.index(var_to_remove)
        
        # Logisches ODER entlang der Achse (Projektion)
        new_data = np.any(self.data, axis=axis)
        
        new_vars = list(self.variables)
        new_vars.pop(axis)
        
        return BooleanTable(new_vars, new_data, self.source_indices)



    def condition(self, variable: Symbol, value: bool) -> 'BooleanTable':
        """
        Schränkt die Tabelle ein: U(T, variable=value).
        Entspricht dem 'Slicing' des Arrays.
        """

        if variable not in self.variables:
            return self
            
        axis = self.variables.index(variable)
        idx = 1 if value else 0
        
        # Extrahiert die Daten für den festen Wert (True/False) und entfernt die Dimension dieser Variable komplett (Rank -1)
        new_data = np.take(self.data, idx, axis=axis)
        
        new_vars = list(self.variables)
        new_vars.pop(axis)
        
        return BooleanTable(new_vars, new_data, self.source_indices)



    def is_consistent(self) -> bool:
        """Prüft, ob die Tabelle mindestens eine 1 enthält (nicht widersprüchlich ist)."""

        return self.data.any().item()