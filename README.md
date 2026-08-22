# Motor de Conversión de Bases y ALU

## Cómo desplegar en Vercel (3 pasos)

1. Sube esta carpeta a un repositorio nuevo en GitHub.
2. Entra a https://vercel.com → **Add New Project** → importa ese repositorio.
3. Deja todo por defecto (no hay que configurar nada) y dale **Deploy**.

Vercel detecta automáticamente:
- `index.html` → lo sirve como sitio estático.
- `api/convert.py` → lo convierte en función serverless, disponible en `/api/convert`.

No hay dependencias externas (`requirements.txt` no es necesario porque solo se usa
la librería estándar de Python: `http.server` y `json`).

## Cómo probarlo en local (opcional)

```bash
python3 -c "
import sys; sys.path.insert(0,'api')
from convert import validate_and_convert, alu_operation
print(validate_and_convert('FF', 16, 8))
print(alu_operation('1010','1100','XOR',4))
"
```

## Estructura

```
conversor-bases/
├── index.html          # Frontend (HTML/CSS/JS vanilla, sin frameworks)
├── api/
│   └── convert.py       # Toda la lógica: conversión de bases + ALU
├── vercel.json           # Config mínima
└── README.md
```

## Qué hace cada algoritmo (para sustentar)

- **`to_decimal`**: cualquier base → decimal, usando el teorema fundamental de la
  numeración (dígito × base^posición), recorriendo el número de derecha a izquierda.
- **`to_base`**: decimal → cualquier base, con divisiones sucesivas (`% ` y `//`),
  guardando los residuos y revirtiéndolos al final.
- **`CHAR_TO_VALUE` / `VALUE_TO_CHAR`**: mapeo manual para hexadecimal (A-F ↔ 10-15).
- **`validate_and_convert`**: valida overflow (`2^n - 1`) y aplica padding para
  completar el registro binario/octal/hexadecimal.
- **`alu_operation`**: recorre bit a bit dos cadenas binarias y aplica la tabla de
  verdad de AND/OR/XOR manualmente.
