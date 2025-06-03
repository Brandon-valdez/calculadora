from typing import Self

from flask import Flask, request, jsonify, render_template

from sympy import Add, expand, factor, latex, sqrt, symbols, limit, simplify, Symbol, sympify

from sympy.calculus.util import continuous_domain

from sympy import log, exp, series, Derivative

from sympy import Integer, oo



app = Flask(__name__)



def resolver_indeterminacion(f, var, punto):

  pasos = []

  original_expr = f

  

  try:

    # Evaluar la forma inicial

    forma = limit(f, var, punto)

    pasos.append(f"Forma inicial: {latex(f)}")

    

    # Si no hay indeterminación, retornar directamente

    if forma not in [0/0, oo/oo, oo - oo, 0*oo, oo**0, 0**0, 1**oo]:

      return forma, pasos

    # Identificar tipo de indeterminación

    if forma == 0/0:

        pasos.append("Indeterminación 0/0 detectada. Aplicando métodos:")

        # Factorización

        try:

          f_factor = factor(f)

          if f_factor != f:

            pasos.append(f"Factorización: {latex(f)} = {latex(f_factor)}")

            f = f_factor

        except:

          pass

        # Regla de L'Hôpital

        deriv_num = Derivative(f.as_numer_denom()[0], var)

        deriv_den = Derivative(f.as_numer_denom()[1], var)

        pasos.append(f"Aplicando Regla de L'Hôpital:")

        pasos.append(f"Derivada del numerador: {latex(deriv_num.doit())}")

        pasos.append(f"Derivada del denominador: {latex(deriv_den.doit())}")

        f = deriv_num.doit() / deriv_den.doit()

        try:

          # ... código anterior de detección de indeterminaciones ...

          if forma == 0/0:

            pasos.append("Indeterminación 0/0 detectada. Aplicando métodos:")

            # Intento de racionalización primero

            if Self._tiene_radicales(f):

              pasos.append("Detectado radical en la expresión. Aplicando racionalización:")

              f_rac, paso_rac = Self._racionalizar_expresion(f, var)

              pasos.extend(paso_rac)

              f = f_rac

              pasos.append("Expresión después de racionalizar: " + latex(f))

        except:

          pass

        # Regla de L'Hôpital

        deriv_num = Derivative(f.as_numer_denom()[0], var)

        deriv_den = Derivative(f.as_numer_denom()[1], var)

        pasos.append(f"Aplicando Regla de L'Hôpital:")

        pasos.append(f"Derivada del numerador: {latex(deriv_num.doit())}")

        pasos.append(f"Derivada del denominador: {latex(deriv_den.doit())}")

        f = deriv_num.doit() / deriv_den.doit()

    elif forma == oo/oo:

      pasos.append("Indeterminación ∞/∞ detectada. Aplicando Regla de L'Hôpital:")

    # Similar al caso anterior...

    # ... Implementar para otros tipos de indeterminaciones ...

    # Calcular nuevo límite

    nuevo_limite = limit(f, var, punto)

    pasos.append(f"Nuevo límite después de simplificación: {latex(nuevo_limite)}")

    

    return nuevo_limite, pasos

  except Exception as e:

      return forma, pasos



@app.route('/')

def index():

    return render_template('index.html')



@app.route('/calcular', methods=['POST'])

def calcular():

    data = request.json

    try:

        expr = (data['funcion'].replace(' ', '')

                .replace('√', 'sqrt')

                .replace('÷', '/')

                .replace('×', '*')

                .replace('^', '**'))

        

        f = sympify(expr, evaluate=False)



        variable = data.get('variable', 'x')

        punto = data.get('punto', 'a')

        

        x = symbols(variable)

        f = sympify(data['funcion'].replace('^', '**'))

        punto_sym = sympify(punto)

        

        # Calcular límite y discontinuidad

        lim = limit(f, x, punto_sym)

        disco = analizar_discontinuidad(f, x, punto_sym)

        

        return jsonify({

            'limite': latex(lim),

            'funcion': latex(f),

            'variable': variable,

            'punto': str(punto),

            'discontinuidad': {

                'tipo': disco['tipo'],

                'descripcion': latex(sympify(disco['descripcion'])) if ':' not in disco['descripcion'] else disco['descripcion']

            }

        })

        

    except Exception as e:

        return jsonify({'error': f'Error en el cálculo: {str(e)}'})

def analizar_discontinuidad(f, var, punto):
  """
  Analiza la discontinuidad de una función en un punto dado.
  Determina si la discontinuidad es evitable o inevitable.
  """
  try:
    # Calcular el límite por la izquierda y por la derecha
    limite_izq = limit(f, var, punto, dir='-')
    limite_der = limit(f, var, punto, dir='+')
    limite = limit(f, var, punto)
    # Evaluar la función en el punto
    valor_funcion = f.subs(var, punto)
    # Determinar el tipo de discontinuidad
    if limite_izq == limite_der:
      if limite_izq == valor_funcion:
        return {'tipo': 'ninguna ', 'descripcion': 'La función es continua en el punto.'}
      else:
        return {'tipo': 'evitable ', 'descripcion': f'Discontinuidad evitable. Límite: {limite_izq}, Valor de la función: {valor_funcion}'}
    else:
        return {'tipo': 'inevitable ', 'descripcion': f'Discontinuidad inevitable. Límite por la izquierda: {limite_izq}, Límite por la derecha: {limite_der}'}
  except Exception as e:
    return {'tipo': 'error', 'descripcion ': f'Error al analizar la discontinuidad: {str(e)}'}



def _tiene_radicales(self, expr):

  return any(term.has(sqrt) for term in expr.as_numer_denom())



def _racionalizar_expresion(self, expr, var):

  pasos = []

  num, den = expr.as_numer_denom()

  

  # Determinar qué parte tiene el radical

  if num.has(sqrt):

    conjugado = self._obtener_conjugado(num)

    factor_rac = conjugado

    parte_rac = "numerador"

  else:

    conjugado = self._obtener_conjugado(den)

    factor_rac = conjugado

    parte_rac = "denominador"



    pasos.append(f"Multiplicando por el conjugado del {parte_rac}: {latex(factor_rac)}")

    nueva_expr = (expr * factor_rac).expand()

    pasos.append("Expresión expandida: " + latex(nueva_expr))

    nueva_expr = simplify(nueva_expr)

    pasos.append("Expresión simplificada: " + latex(nueva_expr))  

  return nueva_expr, pasos



def _obtener_conjugado(self, expr):

  if expr.is_Add:

    terms = expr.args

    for term in terms:

      if term.has(sqrt):

        radical = term

        otros_terms = [t for t in terms if t != radical]

        return Add(*otros_terms) - radical

      elif expr.is_Mul:

        return self._obtener_conjugado(expand(expr))

  return expr



if __name__ == '__main__':

    app.run(debug=True)