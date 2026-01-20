import abc, re, logging

class Operation:

    def __init__(self, **params):
        """
        Almacena parámetros de configuración como field_name, target_type, etc.
        """
        self.params = params

    @abc.abstractmethod
    def execute(self, record: dict) -> tuple[dict, list[str]]:
        """
        Cada operación debe implementar este método para transformar o validar el registro.
        """
        pass

class NormalizeAmountOperation(Operation):
    def execute(self, record: dict) -> tuple[dict, list[str]]:
        field_name = self.params.get('field_name')
        value = record.get(field_name)
        errors = []

        if value is None:
            errors.append(f"Advertencia: Campo '{field_name}' no encontrado.")
            record[field_name] = None
            return record, errors

        try:
            # Lógica de limpieza (resumida para brevedad)
            val_clean = str(value).replace('$', '').replace(' EUR', '').replace(',', '.').replace(' USD', '')
            record[field_name] = float(val_clean)
        except Exception as e:
            errors.append(f"Error: No se pudo convertir '{value}' a float.")
            record[field_name] = None
            
        return record, errors

class ContextualFieldValidation(Operation):
    def execute(self, record: dict) -> tuple[dict, list[str]]:
        field_name = self.params.get('field_name')
        mandatory_for = self.params.get('mandatory_for', [])
        record_type = record.get('__type__')
        regex_pattern = self.params.get('regex')
        errors = []

        if record_type in mandatory_for:
            value = record.get(field_name)
            # Validar existencia
            if value is None or value == "":
                errors.append(f"Error: El campo '{field_name}' es obligatorio para el tipo '{record_type}'.")
            # Validar formato regex
            elif regex_pattern and not re.match(regex_pattern, str(value)):
                errors.append(f"Error: El campo '{field_name}' con valor '{value}' no cumple el formato requerido.")
        
        return record, errors
    
class RecordContextManager:
    def __init__(self):
        # Almacena las secuencias de operaciones por tipo
        self.contexts = {}

    def register_context(self, record_type: str, operations: list[Operation]):
        """Configura qué operaciones aplicar a cada __type__"""
        self.contexts[record_type] = operations

    def process_stream(self, record_iterator):
        """Procesa un iterable de registros y genera tuplas (registro, errores)"""
        for record in record_iterator:
            all_errors = []
            record_type = record.get("__type__")
            
            # Validación de contexto
            if not record_type:
                all_errors.append("Error: El registro no contiene el campo obligatorio '__type__'.")
            elif record_type not in self.contexts:
                all_errors.append(f"Error: El tipo '{record_type}' no tiene un contexto registrado.")
            else:
                # Si el tipo existe, ejecutamos sus operaciones
                for op in self.contexts[record_type]:
                    record, errors = op.execute(record)
                    all_errors.extend(errors)

            # Marcamos el estado basado en si hubo errores (incluyendo el de tipo faltante)
            record["__status__"] = "no válido" if all_errors else "válido"
            record["__details__"] = all_errors

            yield record, all_errors