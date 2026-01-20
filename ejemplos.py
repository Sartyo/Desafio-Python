from operaciones import RecordContextManager, NormalizeAmountOperation, ContextualFieldValidation

# Configuración del Gestor
manager = RecordContextManager()

# Registro de Contextos basado en tus imágenes
manager.register_context("order_event", [
    NormalizeAmountOperation(field_name="amount"),
    ContextualFieldValidation(field_name="order_id", mandatory_for=["order_event"]),
    ContextualFieldValidation(field_name="customer_name", mandatory_for=["order_event"])
])

manager.register_context("product_update", [
    NormalizeAmountOperation(field_name="price"),
    ContextualFieldValidation(field_name="product_sku", mandatory_for=["product_update"])
])

# Procesamiento de Listing 1
records_input = [
    {"__type__": "order_event", "order_id": "ORD789", "customer_name": "Luis Vargas","amount": "123,45 EUR"},
    {"__type__": "order_event", "order_id": "ORD100", "customer_name": "Bob el Constructor", "amount": "no_es_un_numero"},
    {"__type__": "product_update", "product_sku": "SKU_P002", "price": None},
    {"__type__": "product_update", "product_sku": "SKU_P003", "price": "25,00 USD"},
    {} # Registro vacío
]

print(f"{'#':<3} | {'TIPO':<16} | {'ID/SKU':<12} | {'ESTADO':<10}")
print("-" * 55)

for i, (processed_record, error_list) in enumerate(manager.process_stream(records_input), 1):
    # Intentamos obtener un identificador (ID de orden, SKU o 'N/A')
    record_id = (processed_record.get("order_id") or 
                 processed_record.get("product_sku") or 
                 "N/A")
    
    record_type = processed_record.get("__type__", "Desconocido")
    status = processed_record.get("__status__")

    # Impresión de la línea principal
    print(f"{i:<3} | {record_type:<16} | {record_id:<12} | {status:<10}")

    # Si hay errores o advertencias, los mostramos justo debajo con sangría
    if error_list:
        for error in error_list:
            print(f"    └── ⚠️  {error}")