# Definición de los tipos y subtipos de entidades

def get_entity_types():
    """
    Devuelve un diccionario con los tipos y subtipos de entidades.

    Returns:
        dict: Diccionario con los tipos y subtipos de entidades.
    """
    return {
        "Tiempo": [
            "Fecha"
        ],
        "Concepto": [
            "Saldo vivo", "Tipo de interés", "Tipo de interés medio", "Vigencia", "Contrato vivo",
            "Importe Concedido", "Plazo Concesión", "Plazo medio de Concesión", "Importe de Nueva formalización",
            "Indicativo de Nueva formalización", "Saldo impagado", "Importe dudoso", "Impago 30+", "Impago 90+",
            "Mora temprana", "Número de días de impago", "Ratio de dudoso", "Ratio de impago", "Cartera mercado",
            "Producto", "Finalidad", "Tipo de garantía", "Marca Subrogación", "Situación morosidad",
            "Tipo de dudoso", "Seg. comercial HolaBank", "Seg. comercial ImaginBank", "Seg. comercial AgroBank",
            "Seg. comercial_feel good", "Seg. comercial_food and drinks", "Seg. comercial_pharma",
            "Seg. comercial_Real Estate", "Seg. comercial_Banca Privada", "Tipología de tipo de interés",
            "Marca Cuota Creciente", "Marca Ayuda Covid", "Indicativo de impago 30+", "Indicativo de impago 90+",
            "Contrato en impago", "saldo actual, saldo vivo Mercado, riesgo vivo, riesgo total, importe vivo",
            "Tipo interés actual, tipo", "Tipo interés actual medio, interés actual, tipo de interés promedio",
            "Operación viva, producto vivo", "Capital inicial, importe de concesión, saldo inicial, riesgo inicial",
            "Plazo inicial, plazo de concesión", "Plazo inicial medio, plazo de concesión medio, plazo medio de los contratos, plazo medio de cartera",
            "Importe de producción, nuevo importe concedido, riesgo formalizado, nuevo negocio",
            "Nuevo producto, concedido en el mes, nuevo riesgo formalizado, nuevo formalizado",
            "Importe impagado, volumen impagado, saldo de impago, impagado",
            "Importe de mora, Mora contable, NPL, Morosidad contable, stage 3, saldo dudoso",
            "Importe impagado de +30", "Importe impagado de +90", "Impagados no dudosos, impagados no morosos",
            "Ratio de mora, porcentaje de mora, ratio NPL", "porcentaje de impago, porcentajes impagados",
            "Segmentación, cartera", "Tipo de activo, tipo de contrato", "Motivo de la financiación",
            "Colateral", "Situación morosidad, Stage", "Cliente de HolaBank", "Cliente de Imagin",
            "Cliente de Agro", "Cliente feed good", "Cliente alimentación y bebidas", "Cliente Farma",
            "Cliente de Rela Estate, mercado inmobiliario", "Cliente de Banca Privada", "Amortización creciente",
            "Contrato impagado"
        ],
        "Localización": [
            "DT del contrato", "DG del contrato", "DAN del contrato", "Oficina del contrato", "Provincia del contrato",
            "Comunidad autónoma", "Población del contrato", "Empresa origen", "Dirección Territorial",
            "Dirección Comercial", "Dirección Área de Negocio, Dirección de Zona", "Centro de empresa, Store",
            "Prov.", "CA, Com.Aut. CCAA", "Ciudad, pueblo, localidad", "Entidad de origen"
        ]
    }