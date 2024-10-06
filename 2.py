import itertools


class GrammarTransformer:
    def __init__(self, grammar, startSymbol):
        self.grammar = grammar
        self.startSymbol = startSymbol
        self.counter = 0
        self.terminalMap = {}

    def encontrarNullable(self):
        nullable = set()
        changed = True
        print("ENCONTRAR ANULABLES")

        while changed:
            changed = False
            for nonTerminal, productions in self.grammar.items():
                
                for production in productions:            
                    if production == 'ε' or all(symbol in nullable for symbol in production):
                        if nonTerminal not in nullable:
                            print(f"{nonTerminal} es anulable")
                            nullable.add(nonTerminal)
                            changed = True
                       
        return nullable


    def eliminarProduccionesEpsilon(self):
        nullable = self.encontrarNullable()
        print(f"Símbolos anulables: {nullable}")

        newGrammar = {}

        for nonTerminal, productions in self.grammar.items():
            print(f"\nProcesando no terminal '{nonTerminal}': producciones originales {productions}")
            newProductions = set()

            for production in productions:
                if production != 'ε':
                    nullablePositions = [i for i, symbol in enumerate(production) if symbol in nullable]

                    print(f"  Producción '{production}': posiciones anulables {nullablePositions}")

                    combinations = []
                    for r in range(len(nullablePositions) + 1):
                        for positionsToRemove in itertools.combinations(nullablePositions, r):
                            newComb = ''.join([symbol for i, symbol in enumerate(production) if i not in positionsToRemove])
                            combinations.append(newComb)
                    
                    print(f"  Combinaciones generadas para '{production}': {combinations}")

                    newProductions.update(combinations)

            print(f"  Nuevas producciones generadas para '{nonTerminal}': {newProductions}")

            newProductions = {prod for prod in newProductions if prod}
            
            newGrammar[nonTerminal] = newProductions

        for nonTerminal, productions in newGrammar.items():
            if 'ε' in productions:
                print(f"Eliminando producción 'ε' en '{nonTerminal}'")
                productions.remove('ε')

        print(f"\nGramática nueva después de eliminar producciones ε:\n{newGrammar}")

        self.grammar = newGrammar

    def eliminarProduccionesUnarias(self):
        unarias = []
        newGrammar = {}

        for nonTerminal, productions in self.grammar.items():
            newGrammar[nonTerminal] = set()
            for production in productions:
                if len(production) == 1 and production.isupper():
                    unarias.append((nonTerminal, production))
                else:
                    newGrammar[nonTerminal].add(production)

        for A, B in unarias:
            visitados = set()
            cola = [B]
            while cola:
                actual = cola.pop()
                if actual not in visitados:
                    visitados.add(actual)
                    if actual in self.grammar:
                        for production in self.grammar[actual]:
                            if len(production) == 1 and production.isupper():
                                cola.append(production)
                            else:
                                newGrammar[A].add(production)

        self.grammar = newGrammar

    def eliminarSimbolosInutiles(self):
        generadores = set()
        cambiando = True

        while cambiando:
            cambiando = False
            for nonTerminal, productions in self.grammar.items():
                for production in productions:
                    if all(symbol.islower() or symbol.isnumeric() or symbol in generadores for symbol in production):
                        if nonTerminal not in generadores:
                            generadores.add(nonTerminal)
                            cambiando = True

        self.grammar = {nt: [p for p in productions if all(s.islower() or s.isnumeric() or s in generadores for s in p)]
                        for nt, productions in self.grammar.items() if nt in generadores}

        alcanzables = {self.startSymbol}
        cambiando = True

        while cambiando:
            cambiando = False
            for nonTerminal in list(alcanzables):
                if nonTerminal in self.grammar:
                    for production in self.grammar[nonTerminal]:
                        for symbol in production:
                            if symbol.isupper() and symbol not in alcanzables:
                                alcanzables.add(symbol)
                                cambiando = True

        self.grammar = {nt: [p for p in productions if all(s.islower() or s.isnumeric() or s in alcanzables for s in p)]
                        for nt, productions in self.grammar.items() if nt in alcanzables}

    


    def transformarACNF(self):
        newGrammar = {}


        def getNewNonTerminal():
            newNT = f"X{self.counter}"
            self.counter += 1
            return newNT

        def getFilterGramar():
            filterGrama = []

            print(newGrammar)
            
            for rule in list(newGrammar.values()):
                print(f"rule {rule}")
                if len(rule) == 1:
                    filterGrama.append(rule)
                else:
                    should_exclude = False
                    for item in rule:
                        if len(item) > 1:  # Si el elemento es "compuesto", como 'BB', 'AX1', etc.
                            should_exclude = True
                            break
                    
                    # Si no encontramos ningún problema, añadimos el conjunto
                    if not should_exclude:
                        filterGrama.append(rule)
            
            return filterGrama

        def getKeyforValue(value):

            keyFound = None
            for key, valueSet in newGrammar.items():
                if value in valueSet:
                    keyFound = key
                    break 

            return keyFound

            

        for nonTerminal, productions in self.grammar.items():
            newProductions = set()
            print(self.terminalMap)
            for production in productions:
                if len(production) > 2:
                    first, *rest = production

                    print(f"first {first} *rest {rest}")
                    
                    if first.islower() or first.isnumeric():
                        if first in self.terminalMap:
                            first = self.terminalMap[first]
                        else:
                            self.terminalMap[first] = getNewNonTerminal()
                            newGrammar[self.terminalMap[first]] = {first}
                            first = self.terminalMap[first]
                            # first = getNewNonTerminal()
                            # newGrammar

                    # print(list(newGrammar.values()))
                    
                    newNonTerminal = getNewNonTerminal()
                    newProductions.add(first + newNonTerminal)
                    for index, symbol in enumerate(rest[:-1]):
                        if symbol in self.terminalMap:
                            nextNonTerminal = self.terminalMap[symbol]
                        else:
                            nextNonTerminal = ""
                            if index + 1 == len(rest[:-1]):
                                if rest[-1].islower() or rest[-1].isnumeric():
                                    if rest[-1] in self.terminalMap:
                                        nextNonTerminal = self.terminalMap[rest[-1]]
                                    else:
                                        nextNonTerminal = getNewNonTerminal()
                                        newGrammar[nextNonTerminal] = {rest[-1]}
                                else:
                                    nextNonTerminal = rest[-1]
                            else:
                                nextNonTerminal = getNewNonTerminal()

                            print(f"GRAMAr {list(newGrammar.values())}")
                            print(newProductions)
                            # print(f"FILTER {}")

                            if {symbol + nextNonTerminal} in getFilterGramar():

                                matches = [item for item in newProductions if newNonTerminal in item]

                                newProductions.remove(matches[0])

                                newValue = matches[0].replace(newNonTerminal,"")

                                newValue += str(getKeyforValue(symbol+nextNonTerminal))

                                newProductions.add(newValue)

                            else:
                                newGrammar[newNonTerminal] = {symbol + nextNonTerminal}
                                newNonTerminal = nextNonTerminal

                    # newGrammar[newNonTerminal] = {rest[-1]}
                elif len(production) == 2:
                    left, right = production
                    if left.islower() or left.isnumeric():
                        if left not in self.terminalMap:
                            self.terminalMap[left] = getNewNonTerminal()
                            newGrammar[self.terminalMap[left]] = {left}
                        left = self.terminalMap[left]
                    if right.islower() or right.isnumeric():
                        if right not in self.terminalMap:
                            self.terminalMap[right] = getNewNonTerminal()
                            newGrammar[self.terminalMap[right]] = {right}
                        right = self.terminalMap[right]
                    newProductions.add(left + right)
                else:
                    if production.islower() or production.isnumeric():
                        if production not in self.terminalMap:
                            self.terminalMap[production] = getNewNonTerminal()
                            newGrammar[self.terminalMap[production]] = {production}
                        newProductions.add(production)
            newGrammar[nonTerminal] = newProductions

        self.grammar = newGrammar


# grammar = {
#     'S': ['aAa', 'bBb', 'ε'],
#     'A': ['C',"a"],
#     'B': ['C', 'b'],
#     'C': ['CDE', 'ε'],
#     "D": ["A","B","ab"]
# }


# startSymbol = 'S'
# transformer = GrammarTransformer(grammar, startSymbol)

# # Aplicar las transformaciones
# transformer.eliminarProduccionesEpsilon()
# transformer.eliminarProduccionesUnarias()
# transformer.eliminarSimbolosInutiles()
# transformer.transformarACNF()

# # # Imprimir el resultado final
# for nonTerminal, productions in transformer.grammar.items():
#     print(f"{nonTerminal} → {' | '.join(productions)}")

def leer_gramaticas_desde_archivo(nombre_archivo):
    with open(nombre_archivo, 'r', encoding="utf-8") as archivo:
        contenido = archivo.read().strip()
        bloques_gramatica = contenido.split('#')
        
        gramaticas = []
        
        for bloque in bloques_gramatica:
            if bloque.strip():
                gramatica = {}
                lineas = bloque.strip().splitlines()
                for linea in lineas:
                    if '→' in linea:
                        non_terminal, producciones = linea.split('→')
                        non_terminal = non_terminal.strip()
                        producciones = producciones.split('|')
                        gramatica[non_terminal] = [p.strip() for p in producciones]
                gramaticas.append(gramatica)
        
        return gramaticas


nombre_archivo = '2.txt'
gramaticas = leer_gramaticas_desde_archivo(nombre_archivo)

for i, gramatica in enumerate(gramaticas):
    print(f"Gramática {i + 1}:")

    startSymbol = list(gramatica.keys())[0]

    transformer = GrammarTransformer(gramatica, startSymbol)

    transformer.eliminarProduccionesEpsilon()
    transformer.eliminarProduccionesUnarias()
    transformer.eliminarSimbolosInutiles()
    transformer.transformarACNF()

    for nonTerminal, productions in transformer.grammar.items():
        print(f"{nonTerminal} → {' | '.join(productions)}")
