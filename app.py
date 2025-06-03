from typing import Self
from flask import Flask, request, jsonify, render_template
from sympy import Add, Ne, Piecewise, degree, expand, factor, latex, sqrt, symbols, limit, simplify, Symbol, sympify
from sympy.calculus.util import continuous_domain
from sympy import log, exp, series, Derivative
from sympy import Integer, oo
from sympy import Mul, Pow, Function, zoo, Eq
from sympy.calculus.util import AccumBounds

app = Flask(__name__)

def resolver_indeterminacion(f, var, punto):
    pasos = []
    original_expr = f
    
    try:
        # Evaluar forma inicial
        forma_eval = f.subs(var, punto)
        if forma_eval not in [zoo, AccumBounds(-oo, oo), Mul(0, zoo), Pow(0, 0)]:
            try:
                lim_directo = limit(f, var, punto)
                if lim_directo.is_finite:
                    return lim_directo, ["El límite es determinado y se resuelve directamente."]
            except:
                pass

        # Determinar tipo de indeterminación
        forma = limit(f, var, punto, dir='-')
        pasos.append(f"Forma inicial: {latex(original_expr)}")
        indeterminaciones = {
            '0/0': [0, 0],
            'oo/oo': [oo, oo],
            '0*oo': [0, oo],
            'oo - oo': [oo, -oo],
            '1^oo': [1, oo],
            '0^0': [0, 0],
            'oo^0': [oo, 0]
        }

        tipo_indet = None
        for key, val in indeterminaciones.items():
            try:
                if (limit(f.as_numer_denom()[0], var, punto) == val[0] and 
                    limit(f.as_numer_denom()[1], var, punto) == val[1]):
                    tipo_indet = key
                    break
            except:
                continue

        if not tipo_indet:
            return forma, pasos

        pasos.append(f"Indeterminación {tipo_indet} detectada.")
        
        # Manejar diferentes tipos de indeterminación
        if tipo_indet == '0/0':
            # Factorización
            f_factor = factor(f)
            if f_factor != f:
                pasos.append(f"Factorización: {latex(f)} ⇒ {latex(f_factor)}")
                f = f_factor
                nuevo_lim = limit(f, var, punto)
                if not nuevo_lim.has(oo, -oo, zoo, None):
                    return nuevo_lim, pasos
            
            # Racionalización
            if any(term.has(sqrt) for term in f.as_numer_denom()):
                pasos.append("Aplicando racionalización:")
                num, den = f.as_numer_denom()
                if num.has(sqrt):
                    conjugado = num.conjugate()
                    f = (f * conjugado).expand()
                    pasos.append(f"Multiplicar por conjugado: {latex(conjugado)}")
                elif den.has(sqrt):
                    conjugado = den.conjugate()
                    f = (f * conjugado).expand()
                    pasos.append(f"Multiplicar por conjugado: {latex(conjugado)}")
                f = simplify(f)
                pasos.append(f"Expresión racionalizada: {latex(f)}")

            # Regla de L'Hôpital
            pasos.append("Aplicando Regla de L'Hôpital:")
            for _ in range(2):  # Máximo 2 aplicaciones
                deriv_num = f.as_numer_denom()[0].diff(var)
                deriv_den = f.as_numer_denom()[1].diff(var)
                f = deriv_num / deriv_den
                pasos.append(f"Derivada numerador: {latex(deriv_num)}")
                pasos.append(f"Derivada denominador: {latex(deriv_den)}")
                nuevo_lim = limit(f, var, punto)
                if not nuevo_lim.has(oo, -oo, zoo, None):
                    return nuevo_lim, pasos

        elif tipo_indet == 'oo/oo':
            # Comparar grados para funciones racionales
            num, den = f.as_numer_denom()
            grado_num = degree(num, var)
            grado_den = degree(den, var)
            if grado_num > grado_den:
                return oo, pasos + ["El grado del numerador es mayor"]
            elif grado_num < grado_den:
                return 0, pasos + ["El grado del denominador es mayor"]
            else:
                return limit(num.LC() / den.LC(), var, punto), pasos + ["Mismo grado: usar coeficientes principales"]
        
        # Manejar otros tipos de indeterminación...
        
        nuevo_lim = limit(f, var, punto)
        pasos.append(f"Resultado final: {latex(nuevo_lim)}")
        return nuevo_lim, pasos
        
    except Exception as e:
        return None, [f"Error: {str(e)}"]

def analizar_discontinuidad(f, var, punto):
    try:
        # Calcular límites y valor de la función con manejo de errores
        lim_izq, lim_der, f_val = None, None, None       
        try:
            lim_izq = limit(f, var, punto, dir='-')
        except:
            lim_izq = None 
        try:
            lim_der = limit(f, var, punto, dir='+')
        except:
            lim_der = None
        try:
            lim = limit(f, var, punto)
        except:
            lim = None
        try:
            f_val = f.subs(var, punto)
        except:
            f_val = zoo  # Asumir discontinuidad si no se puede evaluar
        # Caso 1: Límites laterales existen pero son diferentes
        if lim_izq is not None and lim_der is not None and lim_izq != lim_der:
            return {
                'tipo': 'inevitable',
                'descripcion': f'Discontinuidad de salto: lim⁻={latex(lim_izq)}, lim⁺={latex(lim_der)}',
                'texto': 'Discontinuidad de tipo inevitable'
            }
        # Caso 2: Límite existe pero difiere del valor de la función
        if lim is not None and lim != f_val and not isinstance(lim, AccumBounds):
            f_redefinida = Piecewise(
                (f, Ne(var, punto)),  # Para x ≠ punto
                (lim, Eq(var, punto))  # Para x = punto
            )
            funcion_redefinida_latex = (
                f"\\begin{{cases}} {latex(f)} & \\text{{for }} {latex(var)} \\neq {latex(punto)} \\\\ "
                f"{latex(lim)} & \\text{{for }} {latex(var)} = {latex(punto)} \\end{{cases}}"
            )
            return {
                'tipo': 'evitable',
                'descripcion': f'Redefinir f({latex(punto)}) = {latex(lim)}',
                'funcion_redefinida': funcion_redefinida_latex,
                'texto': 'Discontinuidad de tipo evitable'
            }
        # Caso 3: Comportamiento asintótico (ej: 1/x en x=0)
        if lim in [zoo, -oo, oo] or f_val == zoo:
            return {
                'tipo': 'asintótica',
                'descripcion': f'Discontinuidad infinita en {latex(punto)}',
                'texto': 'Discontinuidad de tipo asintótica'
            }
        # Caso 4: Límites oscilantes (ej: sin(1/x))
        if isinstance(lim, AccumBounds):
            return {
                'tipo': 'oscilante',
                'descripcion': f'Límite oscilante entre {latex(lim)}',
                'texto': 'Discontinuidad de tipo oscilante'
            }
        # Si pasa todas las comprobaciones anteriores
        return {'tipo': 'continua', 'descripcion': 'Función continua en el punto', 'texto': 'Función continua'}
    except Exception as e:
        return {'tipo': 'desconocida', 'descripcion': f'Error: {str(e)}', 'texto': 'Error desconocido'}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calcular', methods=['POST'])
def calcular():
    try:
        data = request.get_json()
        if not data or 'funcion' not in data or 'variable' not in data or 'punto' not in data:
            return jsonify({'error': 'Datos incompletos en la solicitud'}), 400

        # Validar variable
        variable = data.get('variable', 'x').strip()
        if len(variable) != 1 or not variable.isalpha():
            return jsonify({'error': 'La variable debe ser un solo carácter alfabético'}), 400

        # Validar punto
        punto_str = data.get('punto', '0').strip().lower()
        if punto_str in ['oo', 'inf', 'infinity']:
            punto = oo
        elif punto_str in ['-oo', '-inf', '-infinity']:
            punto = -oo
        else:
            try:
                punto = sympify(punto_str)
                if not punto.is_number:
                    return jsonify({'error': 'El punto debe ser un número válido'}), 400
            except:
                return jsonify({'error': 'El punto debe ser un número, oo (infinito) o -oo (menos infinito)'}), 400

        # Validar y parsear función
        try:
            expr_str = data['funcion'].replace('^', '**')
            expr = sympify(expr_str)
        except Exception as e:
            return jsonify({'error': f'Error al parsear la función: {str(e)}'}), 400

        x = symbols(variable)
        
        # Verificar que la variable esté en la expresión
        if x not in expr.free_symbols:
            return jsonify({'error': f'La variable {variable} no aparece en la función'}), 400

        # Resolver indeterminación primero
        lim, pasos = resolver_indeterminacion(expr, x, punto)
        if lim is None:
            return jsonify({'error': 'No se pudo calcular el límite'}), 400
            
        disco = analizar_discontinuidad(expr, x, punto)
        
        return jsonify({
            'limite': latex(lim),
            'discontinuidad': disco,
            'funcion_original': latex(expr),
            'funcion_redefinida': disco.get('funcion_redefinida', '')
        })
        
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)