**DynamoFlow: Sistema de Procesamiento de Registros Contextual**

Este proyecto implementa una arquitectura robusta y extensible para la transformación y validación de datos en flujos de registros heterogéneos. El sistema utiliza un enfoque basado en objetos para aplicar reglas específicas de procesamiento dependiendo del tipo de registro (__type__).

🚀 **Arquitectura del Sistema**
La arquitectura se divide en dos componentes principales:

Operations (Operaciones): Clases especializadas en una única tarea de transformación o validación.

NormalizeAmountOperation: Estandariza campos numéricos a float, eliminando símbolos de moneda y manejando separadores decimales.

ContextualFieldValidation: Valida la existencia y el formato (vía regex) de campos obligatorios según el contexto del registro.

RecordContextManager (Gestor): El orquestador que registra las secuencias de operaciones y procesa los flujos de datos de manera eficiente mediante generadores (yield).

📝 **Justificación Técnica**
1. Diseño del Sistema de Reglas y "Magic"
Ventajas y desventajas del enfoque de clases (Operation) frente a funciones puras:

* Ventajas: El uso de clases permite el encapsulamiento de la configuración. Cada operación almacena sus propios parámetros (como el nombre del campo o patrones regex), lo que evita pasar múltiples argumentos en cada llamada. Además, facilita el polimorfismo, permitiendo que el gestor ejecute cualquier operación mediante una interfaz común (execute) sin conocer su lógica interna.

* Desventajas: Introducir clases genera una mayor cantidad de código inicial (boilerplate) comparado con una lista de funciones simples.

Frente al uso de eval() o manipulación de cadenas:

* Seguridad: El enfoque de clases evita vulnerabilidades de inyección de código que son inherentes al uso de eval() con datos externos.

* Depuración: Es mucho más sencillo rastrear errores en código Python estructurado que en reglas dinámicas evaluadas como cadenas de texto, las cuales no ofrecen soporte de herramientas de desarrollo o linters.

2. Flexibilidad en NormalizeAmountOperation
Para asegurar que esta operación sea flexible, no se "hardcodean" nombres de campos como amount o price. En su lugar:

* Parámetros: Se configura mediante un field_name dinámico al ser instanciada.

* Manejo de Errores: Si el campo no existe o la conversión falla, el sistema establece el valor como None y registra una advertencia en los detalles del registro, pero nunca detiene el procesamiento del flujo completo.

* Estado: Existe una separación clara entre el estado de la operación (configuración inmutable como el nombre del campo a procesar) y el estado del registro (los datos mutables que se transforman a lo largo de la tubería).
