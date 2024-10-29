import json
from collections import defaultdict
from itertools import product

class RedBayesiana:
    def __init__(self):
        self.nodos = {}
        self.aristas = defaultdict(list)
        self.probabilidades = {}
        self.estados = {}

    def agregar_nodo(self, nodo):
        self.nodos[nodo] = True

    def agregar_arista(self, padre, hijo):
        self.aristas[padre].append(hijo)

    def establecer_probabilidad(self, nodo, probabilidad):
        self.probabilidades[nodo] = probabilidad

    def cargar_desde_json(self, archivo):
        with open(archivo, 'r') as file:
            data = json.load(file)

            for nodo in data["NODOS"]:
                self.agregar_nodo(nodo)

            for arista in data["ARISTAS"]:
                padre, hijo = arista.split('->')
                self.agregar_arista(padre.strip(), hijo.strip())
            
            self.estados = data["ESTADOS"]

            self.probabilidades = data["PROBABILIDADES"]

    def cargar_evidencia(self, archivo):
        evidencia = {}
        with open(archivo, 'r') as file:
            lineas = file.readlines()
            for linea in lineas:
                linea = linea.strip()
                if '=' in linea:
                    nodo, valor = linea.split('=')
                    evidencia[nodo.strip()] = valor.strip()
        return evidencia
    
    def dependencias(self, nodo, dependen):
        for arista in self.aristas:
            if nodo in self.aristas[arista]:
                if arista not in dependen:
                    dependen.append(arista)
                    self.dependencias(arista, dependen)
        return dependen
    
    def generar_combinaciones(self, consulta):
        combinaciones = list(product(*consulta.values()))
        
        etiquetas = list(consulta.keys())
        lista_combinaciones = []
        for combinacion in combinaciones:
            tupla_combinacion = list(f"{etiquetas[i]}: {combinacion[i]}" for i in range(len(combinacion)))
            lista_combinaciones.append(tupla_combinacion)
        
        return lista_combinaciones
    
    def convertir_a_diccionario(self,lista):
        diccionario = {}
        for elemento in lista:
            clave, valor = elemento.split(": ")
            diccionario[clave.strip()] = valor.strip()  
        return diccionario

    def recorrer_diccionario_prob(self, dic, evidencia, mensaje):
        for key, value in dic.items():
            if key in evidencia:
                if isinstance(value, dict):
                    mensaje.add(key)
                    resultado = self.recorrer_diccionario_prob(value, evidencia, mensaje)
                    if resultado is not None:
                        return resultado  
                else:
                    print(f"--Valor Dado--")
                    resultado = ""
                    for i, elemento in enumerate(mensaje):
                        resultado += elemento
                        if i < len(mensaje) - 1:
                            resultado += " ∧ "
                    formateado = f"{float(value):.4f}"
                    print(f"P({key}|{resultado}) = {formateado}")

                    return value, f"P({key}|{resultado})" 
        return None

    def calcular_probabilidad(self, objetivo, evidencia):
        resultados = []
        consultas = {}
        pregunta = self.estados[objetivo]
        print(evidencia.keys())
        for nodo in self.nodos:
            if nodo not in evidencia.keys() and nodo != objetivo:
                consultas[nodo] = self.estados[nodo]
        
        dependen = [objetivo]
        dependen = self.dependencias(objetivo, dependen)

        print(f"Dependen : {dependen}")
        print(f"Evidencia : {evidencia}")
        print(f"Consulta : {consultas}")
        print(f"Pregunta : {pregunta}")

        combinaciones_consultas = self.generar_combinaciones(consultas)

        for Q in pregunta: # Separacion
            suma = 0
            for C in combinaciones_consultas: # Suma
                evidencia_aux = evidencia
                evidencia_aux[objetivo] = Q
                evidencia_aux.update(self.convertir_a_diccionario(C))
                
                evidencias = evidencia_aux.values()
                resultado = 1
                mensaje = set()
                mensajes = ""                
                for P in self.probabilidades: # Multiplicacion
                    if P in dependen:
                       valor, aux = self.recorrer_diccionario_prob(self.probabilidades[P], evidencias, mensaje)
                       mensajes += aux
                       resultado *= float(valor)
                       formateado = f"{resultado:.4f}"
                print(f"{mensajes} = {formateado}")
                suma += resultado
            formateado = f"{suma:.4f}"
            print(f"Suma = {formateado}")
            print(f"Siguiente con {C} Variables y Pregunta {pregunta}: {Q} Estable")
            resultados.append([Q, formateado])
            print("-------------------------------")

        self.normalizar_probabilidades(resultados)
            

    def normalizar_probabilidades(self, resultados):
        resultados_float = [(evento, float(probabilidad)) for evento, probabilidad in resultados]
        suma_probabilidades = sum(probabilidad for _, probabilidad in resultados_float)
        resultados_normalizados = [(evento, probabilidad / suma_probabilidades) for evento, probabilidad in resultados_float]

        print("Resultados normalizados:")
        for evento, probabilidad in resultados_normalizados:
            print(f"{evento}: {probabilidad:.4f}")

        evento_maximo = max(resultados_normalizados, key=lambda x: x[1])
        evento, probabilidad_maxima = evento_maximo

        print(f"\n'{evento}' es más probable con una posibilidad de: {probabilidad_maxima:.4f}")


if __name__ == "__main__":
    archivo_red = 'felicidad.json'
    rb = RedBayesiana()
    rb.cargar_desde_json(archivo_red)

    archivo_evidencia = 'distribucion.txt'
    evidencia = rb.cargar_evidencia(archivo_evidencia)

    rb.calcular_probabilidad("happy", evidencia)