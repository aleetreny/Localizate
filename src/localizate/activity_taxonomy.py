from __future__ import annotations

from dataclasses import dataclass
import re

import pandas as pd


@dataclass(frozen=True)
class TaxonomyDecision:
    web_supercategory: str
    web_category: str
    web_subcategory: str
    display_label: str
    investable: bool
    mapping_rule: str


EXACT_CODE_RULES: dict[str, TaxonomyDecision] = {
    "472101": TaxonomyDecision("Alimentacion", "Alimentacion fresca", "Fruteria", "Fruteria", True, "exact_code"),
    "472102": TaxonomyDecision("Alimentacion", "Alimentacion fresca", "Fruteria", "Fruteria", True, "exact_code"),
    "472201": TaxonomyDecision("Alimentacion", "Alimentacion fresca", "Carniceria", "Carniceria", True, "exact_code"),
    "472202": TaxonomyDecision("Alimentacion", "Alimentacion fresca", "Charcuteria", "Charcuteria", True, "exact_code"),
    "472203": TaxonomyDecision("Alimentacion", "Alimentacion fresca", "Carniceria y charcuteria", "Carniceria y charcuteria", True, "exact_code"),
    "472204": TaxonomyDecision("Alimentacion", "Alimentacion fresca", "Carniceria y charcuteria", "Carniceria y charcuteria", True, "exact_code"),
    "472205": TaxonomyDecision("Alimentacion", "Alimentacion fresca", "Aves y huevos", "Aves y huevos", True, "exact_code"),
    "472206": TaxonomyDecision("Alimentacion", "Alimentacion fresca", "Aves y huevos", "Aves y huevos", True, "exact_code"),
    "472207": TaxonomyDecision("Alimentacion", "Alimentacion fresca", "Casqueria", "Casqueria", True, "exact_code"),
    "472301": TaxonomyDecision("Alimentacion", "Alimentacion fresca", "Pescaderia", "Pescaderia", True, "exact_code"),
    "472302": TaxonomyDecision("Alimentacion", "Alimentacion fresca", "Pescaderia", "Pescaderia", True, "exact_code"),
    "472401": TaxonomyDecision("Alimentacion", "Panaderia y pasteleria", "Panaderia", "Panaderia", True, "exact_code"),
    "472402": TaxonomyDecision("Alimentacion", "Panaderia y pasteleria", "Panaderia", "Panaderia", True, "exact_code"),
    "472403": TaxonomyDecision("Alimentacion", "Panaderia y pasteleria", "Pasteleria y reposteria", "Pasteleria y reposteria", True, "exact_code"),
    "472404": TaxonomyDecision("Alimentacion", "Panaderia y pasteleria", "Pasteleria y reposteria", "Pasteleria y reposteria", True, "exact_code"),
    "472405": TaxonomyDecision("Alimentacion", "Panaderia y pasteleria", "Pasteleria y reposteria", "Pasteleria y reposteria", True, "exact_code"),
    "472406": TaxonomyDecision("Alimentacion", "Comida preparada", "Comida preparada", "Comida preparada", True, "exact_code"),
    "472407": TaxonomyDecision("Alimentacion", "Comida preparada", "Comida preparada", "Comida preparada", True, "exact_code"),
    "472501": TaxonomyDecision("Alimentacion", "Especialistas alimentacion", "Lacteos y bebidas", "Lacteos y bebidas", True, "exact_code"),
    "472502": TaxonomyDecision("Alimentacion", "Especialistas alimentacion", "Bodega", "Bodega", True, "exact_code"),
    "472601": TaxonomyDecision("Retail especializado", "Conveniencia", "Estanco", "Estanco", True, "exact_code"),
    "472901": TaxonomyDecision("Salud y bienestar", "Salud retail", "Herbolario", "Herbolario", True, "exact_code"),
    "472904": TaxonomyDecision("Alimentacion", "Especialistas alimentacion", "Heladeria", "Heladeria", True, "exact_code"),
    "472905": TaxonomyDecision("Alimentacion", "Especialistas alimentacion", "Congelados", "Congelados", True, "exact_code"),
    "472906": TaxonomyDecision("Alimentacion", "Especialistas alimentacion", "Golosinas", "Golosinas", True, "exact_code"),
    "472907": TaxonomyDecision("Alimentacion", "Especialistas alimentacion", "Frutos secos y encurtidos", "Frutos secos y encurtidos", True, "exact_code"),
    "472908": TaxonomyDecision("Hosteleria", "Bar y cafeteria", "Churreria", "Churreria", True, "exact_code"),
    "472910": TaxonomyDecision("Alimentacion", "Especialistas alimentacion", "Cafe e infusiones", "Cafe e infusiones", True, "exact_code"),
    "472911": TaxonomyDecision("Alimentacion", "Supermercado y conveniencia", "Tienda de alimentacion", "Tienda de alimentacion", True, "exact_code"),
    "471101": TaxonomyDecision("Alimentacion", "Supermercado y conveniencia", "Supermercado", "Supermercado", True, "exact_code"),
    "471102": TaxonomyDecision("Alimentacion", "Supermercado y conveniencia", "Gran superficie alimentacion", "Gran superficie alimentacion", True, "exact_code"),
    "471104": TaxonomyDecision("Alimentacion", "Supermercado y conveniencia", "Alimentacion envasada", "Alimentacion envasada", True, "exact_code"),
    "471901": TaxonomyDecision("Retail especializado", "Conveniencia", "Tienda multiproducto", "Tienda multiproducto", True, "exact_code"),
    "471902": TaxonomyDecision("Retail especializado", "Conveniencia", "Bazar y precio unico", "Bazar y precio unico", True, "exact_code"),
    "477301": TaxonomyDecision("Salud y bienestar", "Salud retail", "Farmacia", "Farmacia", True, "exact_code"),
    "960201": TaxonomyDecision("Belleza y cuidado personal", "Peluqueria y estetica", "Peluqueria", "Peluqueria", True, "exact_code"),
    "960202": TaxonomyDecision("Belleza y cuidado personal", "Peluqueria y estetica", "Instituto de belleza", "Instituto de belleza", True, "exact_code"),
    "960203": TaxonomyDecision("Belleza y cuidado personal", "Peluqueria y estetica", "Centro de estetica", "Centro de estetica", True, "exact_code"),
    "960205": TaxonomyDecision("Belleza y cuidado personal", "Peluqueria y estetica", "Bronceado", "Bronceado", True, "exact_code"),
    "960206": TaxonomyDecision("Belleza y cuidado personal", "Peluqueria y estetica", "Fotodepilacion", "Fotodepilacion", True, "exact_code"),
    "960901": TaxonomyDecision("Belleza y cuidado personal", "Servicios personales", "Tattoo y piercing", "Tattoo y piercing", True, "exact_code"),
    "960101": TaxonomyDecision("Servicios", "Servicios personales", "Lavanderia y tintoreria", "Lavanderia y tintoreria", True, "exact_code"),
    "952004": TaxonomyDecision("Servicios", "Servicios personales", "Arreglo de ropa", "Arreglo de ropa", True, "exact_code"),
    "952002": TaxonomyDecision("Servicios", "Servicios personales", "Reparacion de calzado", "Reparacion de calzado", True, "exact_code"),
    "477101": TaxonomyDecision("Retail especializado", "Moda y complementos", "Moda", "Moda", True, "exact_code"),
    "477201": TaxonomyDecision("Retail especializado", "Moda y complementos", "Calzado", "Calzado", True, "exact_code"),
    "477701": TaxonomyDecision("Retail especializado", "Moda y complementos", "Joyeria y relojeria", "Joyeria y relojeria", True, "exact_code"),
    "477501": TaxonomyDecision("Belleza y cuidado personal", "Cosmetica y perfumeria", "Perfumeria y cosmetica", "Perfumeria y cosmetica", True, "exact_code"),
    "477601": TaxonomyDecision("Retail especializado", "Hogar y regalos", "Floristeria", "Floristeria", True, "exact_code"),
    "477602": TaxonomyDecision("Retail especializado", "Mascotas", "Mascotas", "Mascotas", True, "exact_code"),
    "477806": TaxonomyDecision("Salud y bienestar", "Salud retail", "Optica", "Optica", True, "exact_code"),
    "862003": TaxonomyDecision("Salud y bienestar", "Clinicas y consultas", "Clinica dental", "Clinica dental", True, "exact_code"),
    "862001": TaxonomyDecision("Salud y bienestar", "Clinicas y consultas", "Consulta medica", "Consulta medica", True, "exact_code"),
    "862002": TaxonomyDecision("Salud y bienestar", "Clinicas y consultas", "Consulta medica", "Consulta medica", True, "exact_code"),
    "861002": TaxonomyDecision("Salud y bienestar", "Clinicas y consultas", "Clinica medica", "Clinica medica", True, "exact_code"),
    "869007": TaxonomyDecision("Salud y bienestar", "Clinicas y consultas", "Fisioterapia", "Fisioterapia", True, "exact_code"),
    "869008": TaxonomyDecision("Salud y bienestar", "Clinicas y consultas", "Fisioterapia", "Fisioterapia", True, "exact_code"),
    "869003": TaxonomyDecision("Salud y bienestar", "Clinicas y consultas", "Podologia", "Podologia", True, "exact_code"),
    "869005": TaxonomyDecision("Salud y bienestar", "Clinicas y consultas", "Optometria", "Optometria", True, "exact_code"),
    "869009": TaxonomyDecision("Salud y bienestar", "Clinicas y consultas", "Parasanitario", "Parasanitario", True, "exact_code"),
    "750002": TaxonomyDecision("Salud y bienestar", "Clinicas y consultas", "Veterinaria", "Veterinaria", True, "exact_code"),
    "750003": TaxonomyDecision("Salud y bienestar", "Clinicas y consultas", "Veterinaria", "Veterinaria", True, "exact_code"),
    "475201": TaxonomyDecision("Retail especializado", "Hogar y reformas", "Ferreteria", "Ferreteria", True, "exact_code"),
    "475204": TaxonomyDecision("Retail especializado", "Hogar y reformas", "Bricolaje", "Bricolaje", True, "exact_code"),
    "475202": TaxonomyDecision("Retail especializado", "Hogar y reformas", "Materiales de construccion", "Materiales de construccion", True, "exact_code"),
    "475203": TaxonomyDecision("Retail especializado", "Hogar y reformas", "Puertas y ventanas", "Puertas y ventanas", True, "exact_code"),
    "475205": TaxonomyDecision("Retail especializado", "Hogar y reformas", "Saneamientos", "Saneamientos", True, "exact_code"),
    "475206": TaxonomyDecision("Retail especializado", "Hogar y reformas", "Material electrico", "Material electrico", True, "exact_code"),
    "475901": TaxonomyDecision("Retail especializado", "Hogar y decoracion", "Muebles", "Muebles", True, "exact_code"),
    "475903": TaxonomyDecision("Retail especializado", "Hogar y decoracion", "Muebles de cocina", "Muebles de cocina", True, "exact_code"),
    "475905": TaxonomyDecision("Retail especializado", "Hogar y decoracion", "Colchoneria", "Colchoneria", True, "exact_code"),
    "475906": TaxonomyDecision("Retail especializado", "Hogar y decoracion", "Iluminacion", "Iluminacion", True, "exact_code"),
    "475907": TaxonomyDecision("Retail especializado", "Hogar y decoracion", "Hogar y menaje", "Hogar y menaje", True, "exact_code"),
    "475902": TaxonomyDecision("Retail especializado", "Hogar y decoracion", "Menaje del hogar", "Menaje del hogar", True, "exact_code"),
    "475101": TaxonomyDecision("Retail especializado", "Hogar y decoracion", "Textil hogar", "Textil hogar", True, "exact_code"),
    "475401": TaxonomyDecision("Retail especializado", "Electronica y telecom", "Electrodomesticos", "Electrodomesticos", True, "exact_code"),
    "474201": TaxonomyDecision("Retail especializado", "Electronica y telecom", "Telefonia", "Telefonia", True, "exact_code"),
    "474302": TaxonomyDecision("Retail especializado", "Electronica y telecom", "Electronica", "Electronica", True, "exact_code"),
    "474102": TaxonomyDecision("Retail especializado", "Electronica y telecom", "Informatica", "Informatica", True, "exact_code"),
    "476201": TaxonomyDecision("Retail especializado", "Cultura y ocio", "Papeleria y prensa", "Papeleria y prensa", True, "exact_code"),
    "476101": TaxonomyDecision("Retail especializado", "Cultura y ocio", "Libreria", "Libreria", True, "exact_code"),
    "476403": TaxonomyDecision("Retail especializado", "Cultura y ocio", "Deporte", "Deporte", True, "exact_code"),
    "476401": TaxonomyDecision("Retail especializado", "Cultura y ocio", "Bicicletas", "Bicicletas", True, "exact_code"),
    "476501": TaxonomyDecision("Retail especializado", "Cultura y ocio", "Jugueteria", "Jugueteria", True, "exact_code"),
    "452001": TaxonomyDecision("Automocion", "Taller y reparacion", "Taller chapa y pintura", "Taller chapa y pintura", True, "exact_code"),
    "452002": TaxonomyDecision("Automocion", "Taller y reparacion", "Taller mecanica", "Taller mecanica", True, "exact_code"),
    "452003": TaxonomyDecision("Automocion", "Taller y reparacion", "Accesorios automovil", "Accesorios automovil", True, "exact_code"),
    "452004": TaxonomyDecision("Automocion", "Taller y reparacion", "Taller automovil", "Taller automovil", True, "exact_code"),
    "453001": TaxonomyDecision("Automocion", "Venta y recambios", "Recambios automovil", "Recambios automovil", True, "exact_code"),
    "451001": TaxonomyDecision("Automocion", "Venta y recambios", "Venta de coches nuevos", "Venta de coches nuevos", True, "exact_code"),
    "451002": TaxonomyDecision("Automocion", "Venta y recambios", "Venta de coches usados", "Venta de coches usados", True, "exact_code"),
    "454001": TaxonomyDecision("Automocion", "Venta y recambios", "Motos y reparacion", "Motos y reparacion", True, "exact_code"),
    "454002": TaxonomyDecision("Automocion", "Venta y recambios", "Venta de motos", "Venta de motos", True, "exact_code"),
    "473001": TaxonomyDecision("Automocion", "Servicios automocion", "Gasolinera", "Gasolinera", True, "exact_code"),
    "821001": TaxonomyDecision("Servicios", "Servicios profesionales", "Oficina y administracion", "Oficina y administracion", True, "exact_code"),
    "683001": TaxonomyDecision("Servicios", "Servicios profesionales", "Inmobiliaria", "Inmobiliaria", True, "exact_code"),
    "692001": TaxonomyDecision("Servicios", "Servicios profesionales", "Asesoria y contabilidad", "Asesoria y contabilidad", True, "exact_code"),
    "691001": TaxonomyDecision("Servicios", "Servicios profesionales", "Despacho juridico", "Despacho juridico", True, "exact_code"),
    "691002": TaxonomyDecision("Servicios", "Servicios profesionales", "Despacho juridico", "Despacho juridico", True, "exact_code"),
    "702001": TaxonomyDecision("Servicios", "Servicios profesionales", "Consultoria empresarial", "Consultoria empresarial", True, "exact_code"),
    "710001": TaxonomyDecision("Servicios", "Servicios profesionales", "Arquitectura e ingenieria", "Arquitectura e ingenieria", True, "exact_code"),
    "710002": TaxonomyDecision("Servicios", "Servicios profesionales", "Arquitectura e ingenieria", "Arquitectura e ingenieria", True, "exact_code"),
    "730001": TaxonomyDecision("Servicios", "Servicios profesionales", "Publicidad y marketing", "Publicidad y marketing", True, "exact_code"),
    "741001": TaxonomyDecision("Servicios", "Servicios profesionales", "Diseno", "Diseno", True, "exact_code"),
    "742001": TaxonomyDecision("Servicios", "Servicios profesionales", "Fotografia", "Fotografia", True, "exact_code"),
    "620001": TaxonomyDecision("Servicios", "Servicios profesionales", "Tecnologia y software", "Tecnologia y software", True, "exact_code"),
    "631001": TaxonomyDecision("Servicios", "Servicios profesionales", "Servicios digitales", "Servicios digitales", True, "exact_code"),
    "641001": TaxonomyDecision("Finanzas", "Finanzas y seguros", "Banco y caja", "Banco y caja", True, "exact_code"),
    "651001": TaxonomyDecision("Finanzas", "Finanzas y seguros", "Seguros", "Seguros", True, "exact_code"),
    "661002": TaxonomyDecision("Finanzas", "Finanzas y seguros", "Cambio y envio de moneda", "Cambio y envio de moneda", True, "exact_code"),
    "662001": TaxonomyDecision("Finanzas", "Finanzas y seguros", "Servicios auxiliares seguros", "Servicios auxiliares seguros", True, "exact_code"),
    "790001": TaxonomyDecision("Servicios", "Servicios al consumidor", "Agencia de viajes", "Agencia de viajes", True, "exact_code"),
    "610002": TaxonomyDecision("Servicios", "Servicios al consumidor", "Locutorio", "Locutorio", True, "exact_code"),
    "610001": TaxonomyDecision("Servicios", "Servicios profesionales", "Telecomunicaciones", "Telecomunicaciones", True, "exact_code"),
    "931008": TaxonomyDecision("Deporte y ocio", "Fitness y deporte", "Gimnasio", "Gimnasio", True, "exact_code"),
    "931001": TaxonomyDecision("Deporte y ocio", "Fitness y deporte", "Instalacion deportiva", "Instalacion deportiva", True, "exact_code"),
    "931009": TaxonomyDecision("Deporte y ocio", "Fitness y deporte", "Club deportivo", "Club deportivo", True, "exact_code"),
    "932006": TaxonomyDecision("Hosteleria", "Ocio nocturno", "Discoteca", "Discoteca", True, "exact_code"),
    "932007": TaxonomyDecision("Deporte y ocio", "Ocio y entretenimiento", "Salon recreativo", "Salon recreativo", True, "exact_code"),
    "932002": TaxonomyDecision("Deporte y ocio", "Ocio y entretenimiento", "Celebraciones infantiles", "Celebraciones infantiles", True, "exact_code"),
    "561001": TaxonomyDecision("Hosteleria", "Restauracion", "Restaurante", "Restaurante", True, "exact_code"),
    "561002": TaxonomyDecision("Hosteleria", "Restauracion", "Comida rapida", "Comida rapida", True, "exact_code"),
    "561004": TaxonomyDecision("Hosteleria", "Bar y cafeteria", "Bar restaurante", "Bar restaurante", True, "exact_code"),
    "561005": TaxonomyDecision("Hosteleria", "Bar y cafeteria", "Bar con cocina", "Bar con cocina", True, "exact_code"),
    "561006": TaxonomyDecision("Hosteleria", "Bar y cafeteria", "Cafeteria", "Cafeteria", True, "exact_code"),
    "561007": TaxonomyDecision("Hosteleria", "Bar y cafeteria", "Heladeria y salon de te", "Heladeria y salon de te", True, "exact_code"),
    "562101": TaxonomyDecision("Hosteleria", "Catering y colectividades", "Eventos y banquetes", "Eventos y banquetes", True, "exact_code"),
    "562901": TaxonomyDecision("Hosteleria", "Catering y colectividades", "Comedor colectivo", "Comedor colectivo", True, "exact_code"),
    "562902": TaxonomyDecision("Hosteleria", "Catering y colectividades", "Comedor colectivo", "Comedor colectivo", True, "exact_code"),
    "562903": TaxonomyDecision("Hosteleria", "Catering y colectividades", "Comedor colectivo", "Comedor colectivo", True, "exact_code"),
    "563001": TaxonomyDecision("Hosteleria", "Bar y cafeteria", "Bodega con consumo", "Bodega con consumo", True, "exact_code"),
    "563002": TaxonomyDecision("Hosteleria", "Bar y cafeteria", "Bar especial", "Bar especial", True, "exact_code"),
    "563003": TaxonomyDecision("Hosteleria", "Bar y cafeteria", "Bar especial con actuaciones", "Bar especial con actuaciones", True, "exact_code"),
    "563004": TaxonomyDecision("Hosteleria", "Bar y cafeteria", "Taberna", "Taberna", True, "exact_code"),
    "563005": TaxonomyDecision("Hosteleria", "Bar y cafeteria", "Bar sin cocina", "Bar sin cocina", True, "exact_code"),
    "563007": TaxonomyDecision("Hosteleria", "Ocio nocturno", "Cafe espectaculo", "Cafe espectaculo", True, "exact_code"),
    "551001": TaxonomyDecision("Alojamiento", "Alojamiento turistico", "Hotel", "Hotel", True, "exact_code"),
    "551003": TaxonomyDecision("Alojamiento", "Alojamiento turistico", "Hostal", "Hostal", True, "exact_code"),
    "551005": TaxonomyDecision("Alojamiento", "Alojamiento turistico", "Vivienda turistica", "Vivienda turistica", True, "exact_code"),
    "552001": TaxonomyDecision("Alojamiento", "Alojamiento turistico", "Albergue", "Albergue", True, "exact_code"),
    "855001": TaxonomyDecision("Educacion", "Formacion", "Autoescuela", "Autoescuela", True, "exact_code"),
    "855002": TaxonomyDecision("Educacion", "Formacion", "Formacion no reglada", "Formacion no reglada", True, "exact_code"),
    "855003": TaxonomyDecision("Educacion", "Formacion", "Idiomas", "Idiomas", True, "exact_code"),
    "851001": TaxonomyDecision("Educacion", "Educacion infantil", "Escuela infantil", "Escuela infantil", True, "exact_code"),
    "851002": TaxonomyDecision("Educacion", "Educacion infantil", "Escuela infantil", "Escuela infantil", True, "exact_code"),
    "851003": TaxonomyDecision("Educacion", "Educacion infantil", "Centro de cuidado infantil", "Centro de cuidado infantil", True, "exact_code"),
}


NON_INVESTABLE_PREFIXES = (
    "01", "02", "03", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "35", "36", "37", "38", "39", "41", "42", "43", "46", "49", "50", "51", "52", "53", "58", "59", "60", "64", "65", "66", "68", "69", "70", "71", "72", "73", "74", "77", "78", "79", "80", "81", "82", "84", "85", "87", "88", "89", "90", "91", "94", "95", "97", "98", "99",
)


def build_web_taxonomy(audit_frame: pd.DataFrame) -> pd.DataFrame:
    frame = audit_frame.copy()
    frame = frame[(frame["taxonomy"] == "epigrafe") & (frame["code_valid"].astype(str).str.lower() == "true")].copy()
    frame["n"] = pd.to_numeric(frame["n"], errors="coerce").fillna(0)
    frame = (
        frame.sort_values(["clean_code", "n"], ascending=[True, False])
        .drop_duplicates(subset=["clean_code"], keep="first")
        .reset_index(drop=True)
    )

    rows: list[dict[str, object]] = []
    for row in frame.itertuples(index=False):
        clean_code = str(row.clean_code)
        clean_desc = str(row.clean_desc)
        decision = classify_epigrafe(clean_code, clean_desc)
        rows.append(
            {
                "epigrafe_code": clean_code,
                "epigrafe_desc": clean_desc,
                "web_supercategory": decision.web_supercategory,
                "web_category": decision.web_category,
                "web_subcategory": decision.web_subcategory,
                "display_label": decision.display_label,
                "investable": decision.investable,
                "mapping_rule": decision.mapping_rule,
                "source_rows": int(row.n),
            }
        )

    mapped = pd.DataFrame(rows)
    mapped["needs_manual_review"] = mapped["mapping_rule"].eq("fallback_other")
    return mapped.sort_values(["investable", "web_supercategory", "web_category", "display_label", "epigrafe_code"], ascending=[False, True, True, True, True]).reset_index(drop=True)


def classify_epigrafe(clean_code: str, clean_desc: str) -> TaxonomyDecision:
    code = str(clean_code or "").strip()
    desc = _normalize_text(clean_desc)

    if code in EXACT_CODE_RULES:
        return EXACT_CODE_RULES[code]

    if code.startswith("56"):
        return TaxonomyDecision("Hosteleria", "Restauracion", "Hosteleria especializada", "Hosteleria especializada", True, "prefix_56")
    if code.startswith("47"):
        return _classify_retail_epigrafe(code, desc)
    if code.startswith("96") or "PELUQUER" in desc or "BELLEZA" in desc or "ESTETIC" in desc:
        return TaxonomyDecision("Belleza y cuidado personal", "Servicios personales", "Belleza y cuidado personal", "Belleza y cuidado personal", True, "prefix_96")
    if code.startswith("86") or code.startswith("87") or code.startswith("75") or "CONSULTA" in desc or "CLINICA" in desc or "FISIOTER" in desc:
        return TaxonomyDecision("Salud y bienestar", "Clinicas y consultas", "Clinicas y consultas", "Clinicas y consultas", True, "prefix_health")
    if code.startswith("45") or code.startswith("47") and "VEHICUL" in desc:
        return TaxonomyDecision("Automocion", "Venta y recambios", "Automocion", "Automocion", True, "prefix_auto")
    if code.startswith("55"):
        return TaxonomyDecision("Alojamiento", "Alojamiento turistico", "Alojamiento turistico", "Alojamiento turistico", True, "prefix_55")
    if code.startswith("85"):
        return TaxonomyDecision("Educacion", "Formacion", "Educacion y formacion", "Educacion y formacion", True, "prefix_85")
    if code.startswith("93") or code.startswith("92"):
        return TaxonomyDecision("Deporte y ocio", "Ocio y entretenimiento", "Ocio y entretenimiento", "Ocio y entretenimiento", True, "prefix_92_93")
    if code.startswith("61") or code.startswith("62") or code.startswith("63") or code.startswith("69") or code.startswith("70") or code.startswith("71") or code.startswith("73") or code.startswith("74") or code.startswith("79") or code.startswith("82"):
        return TaxonomyDecision("Servicios", "Servicios profesionales", "Servicios profesionales", "Servicios profesionales", True, "prefix_services")
    if code.startswith("64") or code.startswith("65") or code.startswith("66"):
        return TaxonomyDecision("Finanzas", "Finanzas y seguros", "Finanzas y seguros", "Finanzas y seguros", True, "prefix_finance")
    if code.startswith("52") or code.startswith("53") or code.startswith("49"):
        return TaxonomyDecision("Servicios", "Logistica y movilidad", "Logistica y movilidad", "Logistica y movilidad", True, "prefix_logistics")
    if code.startswith("95"):
        return TaxonomyDecision("Servicios", "Servicios personales", "Reparacion especializada", "Reparacion especializada", True, "prefix_95")
    if any(code.startswith(prefix) for prefix in NON_INVESTABLE_PREFIXES):
        return TaxonomyDecision("No priorizable", "Industrial o institucional", "Industrial o institucional", "Industrial o institucional", False, "non_investable_prefix")
    return TaxonomyDecision("No priorizable", "Otros", "Otros", "Otros", False, "fallback_other")


def _classify_retail_epigrafe(code: str, desc: str) -> TaxonomyDecision:
    if any(term in desc for term in ("FRUTAS", "HORTALIZAS")):
        return TaxonomyDecision("Alimentacion", "Alimentacion fresca", "Fruteria", "Fruteria", True, "keyword_fruit")
    if any(term in desc for term in ("CARNICER", "CHARCUTER", "SALCHICHER")):
        return TaxonomyDecision("Alimentacion", "Alimentacion fresca", "Carniceria y charcuteria", "Carniceria y charcuteria", True, "keyword_butcher")
    if any(term in desc for term in ("PESCADOS", "MARISCOS", "PESCA")):
        return TaxonomyDecision("Alimentacion", "Alimentacion fresca", "Pescaderia", "Pescaderia", True, "keyword_fish")
    if any(term in desc for term in ("PANADERIA", "BOLLERIA", "PASTELERIA", "CONFITERIA", "REPOSTERIA")):
        return TaxonomyDecision("Alimentacion", "Panaderia y pasteleria", "Panaderia y pasteleria", "Panaderia y pasteleria", True, "keyword_bakery")
    if any(term in desc for term in ("HELADOS", "HELADERIA")):
        return TaxonomyDecision("Hosteleria", "Bar y cafeteria", "Heladeria", "Heladeria", True, "keyword_icecream")
    if any(term in desc for term in ("PLATOS PREPARADOS", "COMIDA RAPIDA", "COMIDAS")):
        return TaxonomyDecision("Alimentacion", "Comida preparada", "Comida preparada", "Comida preparada", True, "keyword_prepared_food")
    if any(term in desc for term in ("AUTOSERVICIO", "SUPERMERC", "ESTABLECIMIENTOS NO ESPECIALIZADOS", "ALIMENTICIOS NO PERECEDEROS", "BAZARES", "PRECIO UNICO")):
        label = "Supermercado y conveniencia" if "ALIMENT" in desc or "AUTOSERVICIO" in desc else "Bazar y conveniencia"
        return TaxonomyDecision("Alimentacion" if "Supermercado" in label else "Retail especializado", label, label, label, True, "keyword_general_retail")
    if any(term in desc for term in ("FARMACIA", "OPTICA", "ORTOPED", "DROGUERIA", "PERFUMERIA", "COSMETICA")):
        return TaxonomyDecision("Salud y bienestar", "Salud retail", "Salud retail", "Salud retail", True, "keyword_health_retail")
    if any(term in desc for term in ("PRENDAS DE VESTIR", "CALZADO", "BISUTERIA", "JOYAS", "RELOJERIA")):
        return TaxonomyDecision("Retail especializado", "Moda y complementos", "Moda y complementos", "Moda y complementos", True, "keyword_fashion")
    if any(term in desc for term in ("FERRETERIA", "BRICOLAJE", "MUEBLES", "ELECTRODOMESTICOS", "MENAJE", "ILUMINACION", "MATERIAL ELECTRICO", "MATERIALES DE CONSTRUCCION", "TEXTILES PARA EL HOGAR")):
        return TaxonomyDecision("Retail especializado", "Hogar y reformas", "Hogar y reformas", "Hogar y reformas", True, "keyword_home")
    if any(term in desc for term in ("PAPELERIA", "LIBROS", "JUGUETES", "DEPORTIVOS", "BICICLETAS")):
        return TaxonomyDecision("Retail especializado", "Cultura y ocio", "Cultura y ocio", "Cultura y ocio", True, "keyword_leisure_retail")
    if any(term in desc for term in ("TELEFONIA", "TELECOMUNICACIONES", "INFORMATICOS", "ELECTRONICO", "FOTOGRAFICO")):
        return TaxonomyDecision("Retail especializado", "Electronica y telecom", "Electronica y telecom", "Electronica y telecom", True, "keyword_tech_retail")
    if any(term in desc for term in ("SEGUNDA MANO", "ARTICULOS NUEVOS", "N.C.O.P", "SEMILLAS", "PLANTAS", "ANIMALES DE COMPANIA")):
        return TaxonomyDecision("Retail especializado", "Otros comercios", "Otros comercios", "Otros comercios", True, "keyword_other_retail")
    return TaxonomyDecision("Retail especializado", "Otros comercios", "Otros comercios", "Otros comercios", True, "fallback_retail")


def render_taxonomy_report(taxonomy: pd.DataFrame) -> str:
    lines: list[str] = []
    lines.append("# Taxonomia Comercial Web")
    lines.append("")
    lines.append("Taxonomia de producto derivada desde epigrafes normalizados para exponer categorias comprensibles en la web.")
    lines.append("")
    lines.append("## Resumen")
    lines.append("")
    lines.append(f"- Epigrafes validos unicos: {len(taxonomy):,}")
    lines.append(f"- Categorias web: {taxonomy['display_label'].nunique(dropna=True):,}")
    lines.append(f"- Supercategorias web: {taxonomy['web_supercategory'].nunique(dropna=True):,}")
    lines.append(f"- Epigrafes priorizables para inversor: {int(taxonomy['investable'].sum()):,}")
    lines.append(f"- Filas pendientes de revision manual: {int(taxonomy['needs_manual_review'].sum()):,}")
    lines.append("")
    lines.append("## Cobertura por categoria")
    lines.append("")
    summary = (
        taxonomy.groupby(["web_supercategory", "web_category", "display_label", "investable"], dropna=False)
        .agg(epigrafes=("epigrafe_code", "nunique"), source_rows=("source_rows", "sum"))
        .reset_index()
        .sort_values(["investable", "source_rows"], ascending=[False, False])
    )
    for row in summary.head(80).itertuples(index=False):
        lines.append(
            f"- {row.display_label} [{row.web_supercategory} / {row.web_category}] -> epigrafes={row.epigrafes}, source_rows={int(row.source_rows):,}, investable={row.investable}"
        )
    if int(taxonomy["needs_manual_review"].sum()) > 0:
        lines.append("")
        lines.append("## Pendientes de revision")
        lines.append("")
        for row in taxonomy[taxonomy["needs_manual_review"]].sort_values("source_rows", ascending=False).head(40).itertuples(index=False):
            lines.append(f"- {row.epigrafe_code}: {row.epigrafe_desc}")
    lines.append("")
    return "\n".join(lines) + "\n"


def _normalize_text(value: object) -> str:
    text = str(value or "").upper()
    text = re.sub(r"[^A-Z0-9ÑÁÉÍÓÚÜ ]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text