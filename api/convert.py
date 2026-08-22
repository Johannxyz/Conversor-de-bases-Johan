"""
Motor de Conversión de Bases y ALU - Backend
Toda la lógica está hecha a mano (sin int(x, base), bin(), oct(), hex(), format()).
Solo se usan operadores aritméticos básicos (%, //, **) y estructuras de datos.
"""

from http.server import BaseHTTPRequestHandler
import json

# ---------------------------------------------------------------------------
# 1. MAPEO MANUAL DE DÍGITOS (requisito: mapeo hexadecimal 10-15 -> A-F)
# ---------------------------------------------------------------------------

CHAR_TO_VALUE = {
    '0': 0, '1': 1, '2': 2, '3': 3, '4': 4,
    '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
    'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15,
}

VALUE_TO_CHAR = "0123456789ABCDEF"


def char_to_value(c):
    c = c.upper()
    if c not in CHAR_TO_VALUE:
        raise ValueError(f"Carácter inválido: '{c}'")
    return CHAR_TO_VALUE[c]


def value_to_char(v):
    return VALUE_TO_CHAR[v]


# ---------------------------------------------------------------------------
# 2. CUALQUIER BASE -> DECIMAL (teorema fundamental de la numeración)
#    valor = suma( digito_i * base ^ posicion_i )
# ---------------------------------------------------------------------------

def to_decimal(number_str, base):
    number_str = number_str.strip().upper()
    if number_str == "":
        raise ValueError("El número no puede estar vacío.")

    result = 0
    power = 0
    for char in reversed(number_str):
        digit = char_to_value(char)
        if digit >= base:
            raise ValueError(
                f"El dígito '{char}' no es válido para base {base}."
            )
        result += digit * (base ** power)
        power += 1
    return result


# ---------------------------------------------------------------------------
# 3. DECIMAL -> CUALQUIER BASE (divisiones sucesivas)
# ---------------------------------------------------------------------------

def to_base(decimal_value, base, min_digits=1):
    if decimal_value == 0:
        digits = ['0']
    else:
        digits = []
        n = decimal_value
        while n > 0:
            remainder = n % base
            digits.append(value_to_char(remainder))
            n = n // base
        digits.reverse()

    # Padding / relleno para completar el registro
    while len(digits) < min_digits:
        digits.insert(0, '0')

    return ''.join(digits)


# ---------------------------------------------------------------------------
# 4. VALIDACIÓN DE ARQUITECTURA (overflow) + cantidad de dígitos por registro
# ---------------------------------------------------------------------------

def digits_needed(word_size, base):
    # cuántos dígitos de "base" hacen falta para representar word_size bits
    count = 0
    max_value = (2 ** word_size) - 1
    if max_value == 0:
        return 1
    n = max_value
    while n > 0:
        count += 1
        n = n // base
    return count


def validate_and_convert(number_str, source_base, word_size):
    decimal_value = to_decimal(number_str, source_base)
    max_value = (2 ** word_size) - 1

    if decimal_value > max_value:
        raise ValueError(
            f"Overflow / Desbordamiento de Registro: el valor {decimal_value} "
            f"no cabe en {word_size} bits (máximo permitido = {max_value})."
        )
    if decimal_value < 0:
        raise ValueError("Solo se admiten números enteros no negativos.")

    return {
        "decimal": to_base(decimal_value, 10, 1),
        "binary": to_base(decimal_value, 2, word_size),
        "octal": to_base(decimal_value, 8, digits_needed(word_size, 8)),
        "hexadecimal": to_base(decimal_value, 16, digits_needed(word_size, 16)),
    }


# ---------------------------------------------------------------------------
# 5. ALU - operaciones lógicas bit a bit (tabla de verdad manual)
# ---------------------------------------------------------------------------

def alu_operation(bin1, bin2, operation, word_size):
    bin1 = bin1.strip().zfill(word_size)
    bin2 = bin2.strip().zfill(word_size)

    for c in bin1 + bin2:
        if c not in ('0', '1'):
            raise ValueError("Las entradas de la ALU deben ser binarias (0/1).")

    if len(bin1) > word_size or len(bin2) > word_size:
        raise ValueError(f"Las entradas superan el tamaño de palabra ({word_size} bits).")

    result = []
    for i in range(word_size):
        b1 = bin1[i]
        b2 = bin2[i]
        if operation == "AND":
            r = '1' if (b1 == '1' and b2 == '1') else '0'
        elif operation == "OR":
            r = '1' if (b1 == '1' or b2 == '1') else '0'
        elif operation == "XOR":
            r = '1' if (b1 != b2) else '0'
        else:
            raise ValueError("Operación no soportada.")
        result.append(r)

    return ''.join(result)


# ---------------------------------------------------------------------------
# 6. HANDLER HTTP (Vercel Python serverless function)
# ---------------------------------------------------------------------------

class handler(BaseHTTPRequestHandler):
    def _send_json(self, status, payload):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode())

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            data = json.loads(body) if body else {}
            action = data.get("action")

            if action == "convert":
                number = str(data.get("number", ""))
                source_base = int(data.get("source_base"))
                word_size = int(data.get("word_size"))
                result = validate_and_convert(number, source_base, word_size)
                self._send_json(200, result)

            elif action == "alu":
                bin1 = str(data.get("bin1", ""))
                bin2 = str(data.get("bin2", ""))
                operation = str(data.get("operation", "")).upper()
                word_size = int(data.get("word_size"))
                result = alu_operation(bin1, bin2, operation, word_size)
                self._send_json(200, {"result": result})

            else:
                self._send_json(400, {"error": "Acción no reconocida."})

        except ValueError as e:
            self._send_json(400, {"error": str(e)})
        except Exception as e:
            self._send_json(500, {"error": f"Error interno: {str(e)}"})
