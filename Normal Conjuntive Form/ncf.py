import sys
import re
from termcolor import colored

# Pattern for different inputs
pattern_rule = r'^[0-9]+\.\s*(~?\w+)\(([\w,?]+)\) *$'
pattern_knowledge = r'[0-9]+\. *(~?\w+\([\w,?]+\))( *[∨|or] *(~?\w+\([\w,?]+\)))*'
pattern_question = r'^Q: *(~?\w+)\(([\w,?]+)\)$'

KB = list()  # List of rules
questions = list()

class Rule:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

    def __str__(self):
        args_str = ", ".join(map(str, self.arguments))
        return f"{self.name}({args_str})"


class Knowledge:
    def __init__(self, rules):
        if isinstance(rules, Rule):
            self.rules = [rules]  
        else:
            self.rules = rules if isinstance(rules, list) else [rules]
        self.size = len(self.rules) 
    
    def __str__(self):
        if isinstance(self.rules, Rule):
            r = self.rules
            args_str = ", ".join(map(str, self.arguments))
            return f"{self.name}({args_str})" 
        else:
            return " ∨ ".join(str(rule) for rule in self.rules)
            
    
    def __repr__(self):
        return self.__str__()
    
    def __iter__(self):
        return iter(self.rules)

    def size(self):
        return int(len(self.rules))

class Question:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

    def __str__(self):
        return f"{self.name}({', '.join(map(str, self.arguments))})"

    def to_rule(self):
        return Rule(self.name, self.arguments)


def main():
    read_file(sys.argv[1])
    for k in KB:
        print(k)
    print("Resolver Preguntas:")
    for q in questions:
        print(f"Resolviendo pregunta: {q}\n")
        result = resolution(q)
        print(colored(f"Resultado: Verdadero", 'green') if result else colored("Falso", 'red'))

def read_file(file_name):
    try:
        with open(file_name, "r") as file:
            for line in file:
                line = line.strip()  # strip whitespaces
                print(f"Línea a leer: {line}")
                read_statement(line)
    except FileNotFoundError:
        print(f"Error, el archivo {file_name} no pudo ser abierto")
        sys.exit(1)

def clean_arguments(argument):
    """Limpia los paréntesis y maneja variables con '?'"""
    # Remove parenthesis and ',' in arguments
    cleaned_args = argument.replace('(', '').replace(')', '').split(',')
    return [arg.strip() for arg in cleaned_args]  # Limpiar espacios

def read_statement(statement):
    # Veify if is Rule
    if re.match(pattern_rule, statement):
        #print("Entró por RULE")
        process_rule(statement)
    # Verify if is Knowledge
    elif re.match(pattern_knowledge, statement):
        #print("Entró por KNOWLEDGE")
        process_knowledge(statement)
    # Verify if is Question
    elif re.match(pattern_question, statement):
        #print("Entró por QUESTION")
        process_question(statement)
    else:
        print(f"La línea: {statement} no tiene un formato permitido")

def process_rule(statement):
    # Extraer nombre y argumento de la regla
    match = re.match(pattern_rule, statement)
    if match:
        name = match.group(1)  # Nombre de la regla
        argument = match.group(2)  # Argumento de la regla
        argument = clean_arguments(argument)  # Limpiar paréntesis y espacios

        rule = Rule(name, argument)
        KB.append(rule)
        #print(f"Regla procesada: {rule} \n")

def process_knowledge(statement):
    # Encontrar todas las reglas separadas por ∨
    matches = re.findall(r'(~?\w+)\(([\w,?]+)\)', statement)
    rules = list()

    if matches:
        for name, args in matches:
            args_cleaned = clean_arguments(args)  # Limpiar paréntesis y espacios
            rule = Rule(name, args_cleaned)
            rules.append(rule)

        knowledge = Knowledge(rules)
        KB.append(knowledge)
        #print(f"Conocimiento procesado: {knowledge} \n")

def process_question(statement):
    # Extraer nombre y argumento de la pregunta
    match = re.match(pattern_question, statement)
    if match:
        name = match.group(1)  # Nombre de la pregunta
        argument = match.group(2)  # Argumento de la pregunta
        argument = clean_arguments(argument)  # Limpiar paréntesis y espacios

        question = Question(name, argument)
        questions.append(question)
        #print(f"Pregunta procesada: {question} \n")
    
def add_rule(resolvents, new_clause):
    resolvents.rules.append(new_clause)  

def is_some(question, clause):
    q_rules = ensure_rules_list(question)
    c_rules = ensure_rules_list(clause)
    for q in q_rules:
        negated_q = negate(q)
        negated_q_rules = ensure_rules_list(negated_q)

        for negated_q_rule in negated_q_rules:
            for c in c_rules:
                if negated_q_rule.name == c.name:
                    print(f"{negated_q_rule.name} == {c.name} cumple")
                    return True
    return False


def negate(statement):
    if isinstance(statement, Rule):
        negated_name = f"~{statement.name}" if not statement.name.startswith("~") else statement.name[1:]
        return Rule(negated_name, statement.arguments)
    if isinstance(statement, Knowledge):
        if len(statement.rules) == 1:
            return negate(statement.rules[0])
        else:
            negated_rules = [negate(rule) for rule in statement.rules]
            return Knowledge(negated_rules)
    if isinstance(statement, Question):
        if statement.name.startswith("~"):
            return Question(statement.name[1:], statement.arguments)
        else:
            return Question(f"~{statement.name}", statement.arguments)

    if isinstance(statement, str):
        return f"~{statement}" if not statement.startswith("~") else statement[1:]

    return statement



def resolution(question):
    i = 0
    actual_clause = [negate(question)]
    clauses = KB 
    resolved = False

    while not resolved:
        new_clauses = []
        
        actual_clause = ensure_rules_list(actual_clause)

        for actual in actual_clause:
            for clause1 in clauses:

                i += 1
                if i > 50:
                    return False
                
                print(colored(f"Comparando pregunta negada {negate(actual)} con la cláusula {clause1}\n", 'yellow'))
                
                if is_some(actual, clause1):
                    resolvents = resolve(actual, clause1)
                    if resolvents == []:
                        resolved = True
                        return True
                    if resolvents:
                        new_clauses.append(resolvents)
                        actual_clause.append(resolvents) 
                        break  
        if not new_clauses:
            resolved = True
            return False

        clauses.extend(new_clauses)
def resolve(question, clause2):
    new_clause = None

    if isinstance(question, Question):
        question = question.to_rule()

    c1_rules = ensure_rules_list(question)  # Asegura que siempre sea una lista
    c2_rules = ensure_rules_list(clause2)   # Lo mismo aquí

    print(colored(f"\nResolviendo entre: {question} y {clause2}\n", 'blue'))

    for c1 in c1_rules:
        for c2 in c2_rules:
            print(f"\nComparando {c1} con {c2}\n")

            # Comparamos nombres de las reglas después de negarlas si es necesario
            if c1.name == negate(c2).name:
                print(f"Literal a resolver encontrado: {c1} y {c2}")
                substitution = unify(c1.arguments, c2.arguments)

                if substitution is not None:
                    print(f"Sustitución encontrada: {substitution}")
                    new_clause = Knowledge(apply_substitution(question, clause2, substitution))

                    if isinstance(new_clause, Rule):
                        new_clause = Knowledge([new_clause])  # Convertir a lista de reglas si es una sola

                    if isinstance(new_clause, Knowledge) and len(new_clause.rules) == 0:
                        print("Resuelto, se encontró una contradicción.")
                        return []  # Contradicción, se resuelve con éxito

                else:
                    print(f"No se puede unificar {c1} con {c2}")

    print(colored(f"\n--Resolvents generados: {new_clause}--\n", 'green'))
    return new_clause

def apply_substitution(clause1, clause2, substitution):
    def substitute(argument):
        # Solo reemplaza argumentos que comienzan con '?'
        if is_variable(argument):
            return substitution.get(argument, argument)
        return argument

    new_clause_rules = []

    clause1_rules = clause1.rules if isinstance(clause1, Knowledge) else [clause1]
    clause2_rules = clause2.rules if isinstance(clause2, Knowledge) else [clause2]

    for rule in clause1_rules + clause2_rules:
        new_arguments = [substitute(arg) for arg in rule.arguments]
        new_rule = Rule(rule.name, new_arguments)
        if new_rule.name not in [negate(r.name) for r in clause1_rules + clause2_rules]:
            new_clause_rules.append(new_rule)
    if len(new_clause_rules) == 1:
        return new_clause_rules[0]
    else:
        return new_clause_rules


def unify(args1, args2):
    if len(args1) != len(args2):
        return None  # No pueden unificarse si no tienen el mismo número de argumentos
    substitution = {}
    for a1, a2 in zip(args1, args2):
        if is_variable(a1) and is_variable(a2):
            substitution[a1] = a2  
        elif is_variable(a1):
            substitution[a1] = a2
        elif is_variable(a2):
            substitution[a2] = a1
        elif a1 != a2:
            return None  
    return substitution


def is_variable(arg):
    return arg.startswith('?')

def ensure_rules_list(knowledge_or_rule):
    if isinstance(knowledge_or_rule, Knowledge):
        return knowledge_or_rule.rules 
    elif isinstance(knowledge_or_rule, list):
        return knowledge_or_rule
    else:
        return [knowledge_or_rule] 


if __name__ == "__main__":
    main()
