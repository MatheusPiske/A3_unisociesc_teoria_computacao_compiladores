import re
from flask import Flask, render_template, request

app = Flask(__name__)

def lexical_analysis(code):
    patterns = [
        (r'\bint\b|\bfloat\b|\bchar\b', 'TIPO'),
        (r'\bif\b|\belse\b|\bwhile\b', 'ESTRUTURA'),
        (r'\b\d+\b', 'NUMERO'),
        (r'\b\d+\.\d+\b', 'NUMERO_FLUTUANTE'),
        (r'\bprint\b', 'PRINT'),
        (r'\b[a-zA-Z_]\w*(?=\s*=)', 'IDENTIFICADOR'),
        (r'[\+\-\*/\{\}\[\]=;]', 'OPERADOR'),
        (r'==|!=|<=|>=|<|>', 'COMPARACAO'),
        (r'[\(\)\{\}]', 'DELIMITADOR'),  # Added curly braces
        (r'"([^"]*)"', 'RETORNO'),
    ]

    tokens = []

    for pattern, token_type in patterns:
        matches = re.findall(pattern, code)
        tokens.extend([(match, token_type) for match in matches])

    return tokens

def check_parentheses_balance(tokens):
    stack = []

    for token, token_type in tokens:
        if token_type == 'DELIMITADOR':
            if token in '({':
                stack.append(token)
            elif token in ')}':
                if not stack:
                    return False, f"Erro sintático: Parênteses desbalanceados."
                elif token == ')' and stack[-1] != '(':
                    return False, f"Erro sintático: Parênteses desbalanceados."
                elif token == '}' and stack[-1] != '{':
                    return False, f"Erro sintático: Chaves desbalanceadas."
                stack.pop()

    if stack:
        return False, f"Erro sintático: Parênteses desbalanceados."

    return True, None

def semantic_analysis(tokens):
    errors = []

    for i in range(len(tokens) - 1):
        current_token, current_type = tokens[i]
        next_token, next_type = tokens[i + 1]

        if current_type == 'OPERADOR' and current_token == '=':
            if next_type == 'OPERADOR' and next_token == '=':
                errors.append("Aviso semântico: Utilizando '==' para comparação, use apenas '=' para atribuição.")

    return errors

        # Adicionar mais regras semânticas conforme necessário

def display_symbol_table(symbol_table):
    print("\nTabela de Símbolos:")
    print("{:<15} {:<15}".format("Token", "Tipo"))
    print("-" * 30)
    for token, token_type in symbol_table:
        print("{:<15} {:<15}".format(token, token_type))

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        code = request.form["code"]
        result = lexical_analysis(code)

        balanced, error_message = check_parentheses_balance(result)

        if not balanced:
            return render_template("index.html", error_message=error_message)

        semantic_errors = semantic_analysis(result)

        if semantic_errors:
            return render_template("index.html", error_message=semantic_errors[0])

        display_symbol_table(result)
        symbol_table = result

        return render_template("index.html", symbol_table=symbol_table)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)