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


@dataclass(frozen=True)
class MacroCategoryDecision:
    macro_category_code: str
    macro_category_name: str
    macro_category_definition: str
    investable: bool
    mapping_rule: str


EXACT_CODE_RULES: dict[str, TaxonomyDecision] = {
    "472101": TaxonomyDecision("Alimentación", "Alimentación fresca", "Frutería", "Frutería", True, "exact_code"),
    "472102": TaxonomyDecision("Alimentación", "Alimentación fresca", "Frutería", "Frutería", True, "exact_code"),
    "472201": TaxonomyDecision("Alimentación", "Alimentación fresca", "Carnicería", "Carnicería", True, "exact_code"),
    "472202": TaxonomyDecision("Alimentación", "Alimentación fresca", "Charcutería", "Charcutería", True, "exact_code"),
    "472203": TaxonomyDecision("Alimentación", "Alimentación fresca", "Carnicería y charcutería", "Carnicería y charcutería", True, "exact_code"),
    "472204": TaxonomyDecision("Alimentación", "Alimentación fresca", "Carnicería y charcutería", "Carnicería y charcutería", True, "exact_code"),
    "472205": TaxonomyDecision("Alimentación", "Alimentación fresca", "Aves y huevos", "Aves y huevos", True, "exact_code"),
    "472206": TaxonomyDecision("Alimentación", "Alimentación fresca", "Aves y huevos", "Aves y huevos", True, "exact_code"),
    "472207": TaxonomyDecision("Alimentación", "Alimentación fresca", "Casquería", "Casquería", True, "exact_code"),
    "472301": TaxonomyDecision("Alimentación", "Alimentación fresca", "Pescadería", "Pescadería", True, "exact_code"),
    "472302": TaxonomyDecision("Alimentación", "Alimentación fresca", "Pescadería", "Pescadería", True, "exact_code"),
    "472401": TaxonomyDecision("Alimentación", "Panadería y pastelería", "Panadería", "Panadería", True, "exact_code"),
    "472402": TaxonomyDecision("Alimentación", "Panadería y pastelería", "Panadería", "Panadería", True, "exact_code"),
    "472403": TaxonomyDecision("Alimentación", "Panadería y pastelería", "Pastelería y repostería", "Pastelería y repostería", True, "exact_code"),
    "472404": TaxonomyDecision("Alimentación", "Panadería y pastelería", "Pastelería y repostería", "Pastelería y repostería", True, "exact_code"),
    "472405": TaxonomyDecision("Alimentación", "Panadería y pastelería", "Pastelería y repostería", "Pastelería y repostería", True, "exact_code"),
    "472406": TaxonomyDecision("Alimentación", "Comida preparada", "Comida preparada", "Comida preparada", True, "exact_code"),
    "472407": TaxonomyDecision("Alimentación", "Comida preparada", "Comida preparada", "Comida preparada", True, "exact_code"),
    "472501": TaxonomyDecision("Alimentación", "Especialistas de alimentación", "Lácteos y bebidas", "Lácteos y bebidas", True, "exact_code"),
    "472502": TaxonomyDecision("Alimentación", "Especialistas de alimentación", "Bodega", "Bodega", True, "exact_code"),
    "472601": TaxonomyDecision("Retail especializado", "Conveniencia", "Estanco", "Estanco", True, "exact_code"),
    "472901": TaxonomyDecision("Salud y bienestar", "Salud retail", "Herbolario", "Herbolario", True, "exact_code"),
    "472904": TaxonomyDecision("Alimentación", "Especialistas de alimentación", "Heladería", "Heladería", True, "exact_code"),
    "472905": TaxonomyDecision("Alimentación", "Especialistas de alimentación", "Congelados", "Congelados", True, "exact_code"),
    "472906": TaxonomyDecision("Alimentación", "Especialistas de alimentación", "Golosinas", "Golosinas", True, "exact_code"),
    "472907": TaxonomyDecision("Alimentación", "Especialistas de alimentación", "Frutos secos y encurtidos", "Frutos secos y encurtidos", True, "exact_code"),
    "472908": TaxonomyDecision("Hostelería", "Bar y cafetería", "Churrería", "Churrería", True, "exact_code"),
    "472910": TaxonomyDecision("Alimentación", "Especialistas de alimentación", "Café e infusiones", "Café e infusiones", True, "exact_code"),
    "472911": TaxonomyDecision("Alimentación", "Supermercado y conveniencia", "Tienda de alimentación", "Tienda de alimentación", True, "exact_code"),
    "471101": TaxonomyDecision("Alimentación", "Supermercado y conveniencia", "Supermercado", "Supermercado", True, "exact_code"),
    "471102": TaxonomyDecision("Alimentación", "Supermercado y conveniencia", "Gran superficie de alimentación", "Gran superficie de alimentación", True, "exact_code"),
    "471104": TaxonomyDecision("Alimentación", "Supermercado y conveniencia", "Alimentación envasada", "Alimentación envasada", True, "exact_code"),
    "471901": TaxonomyDecision("Retail especializado", "Conveniencia", "Tienda multiproducto", "Tienda multiproducto", True, "exact_code"),
    "471902": TaxonomyDecision("Retail especializado", "Conveniencia", "Bazar y precio único", "Bazar y precio único", True, "exact_code"),
    "477301": TaxonomyDecision("Salud y bienestar", "Salud retail", "Farmacia", "Farmacia", True, "exact_code"),
    "960201": TaxonomyDecision("Belleza y cuidado personal", "Peluquería y estética", "Peluquería", "Peluquería", True, "exact_code"),
    "960202": TaxonomyDecision("Belleza y cuidado personal", "Peluquería y estética", "Instituto de belleza", "Instituto de belleza", True, "exact_code"),
    "960203": TaxonomyDecision("Belleza y cuidado personal", "Peluquería y estética", "Centro de estética", "Centro de estética", True, "exact_code"),
    "960205": TaxonomyDecision("Belleza y cuidado personal", "Peluquería y estética", "Bronceado", "Bronceado", True, "exact_code"),
    "960206": TaxonomyDecision("Belleza y cuidado personal", "Peluquería y estética", "Fotodepilación", "Fotodepilación", True, "exact_code"),
    "960901": TaxonomyDecision("Belleza y cuidado personal", "Servicios personales", "Tattoo y piercing", "Tattoo y piercing", True, "exact_code"),
    "960101": TaxonomyDecision("Servicios", "Servicios personales", "Lavandería y tintorería", "Lavandería y tintorería", True, "exact_code"),
    "952004": TaxonomyDecision("Servicios", "Servicios personales", "Arreglo de ropa", "Arreglo de ropa", True, "exact_code"),
    "952002": TaxonomyDecision("Servicios", "Servicios personales", "Reparación de calzado", "Reparación de calzado", True, "exact_code"),
    "477101": TaxonomyDecision("Retail especializado", "Moda y complementos", "Moda", "Moda", True, "exact_code"),
    "477201": TaxonomyDecision("Retail especializado", "Moda y complementos", "Calzado", "Calzado", True, "exact_code"),
    "477701": TaxonomyDecision("Retail especializado", "Moda y complementos", "Joyería y relojería", "Joyería y relojería", True, "exact_code"),
    "477501": TaxonomyDecision("Belleza y cuidado personal", "Cosmética y perfumería", "Perfumería y cosmética", "Perfumería y cosmética", True, "exact_code"),
    "477601": TaxonomyDecision("Retail especializado", "Hogar y regalos", "Floristería", "Floristería", True, "exact_code"),
    "477602": TaxonomyDecision("Retail especializado", "Mascotas", "Mascotas", "Mascotas", True, "exact_code"),
    "477806": TaxonomyDecision("Salud y bienestar", "Salud retail", "Óptica", "Óptica", True, "exact_code"),
    "862003": TaxonomyDecision("Salud y bienestar", "Clínicas y consultas", "Clínica dental", "Clínica dental", True, "exact_code"),
    "862001": TaxonomyDecision("Salud y bienestar", "Clínicas y consultas", "Consulta médica", "Consulta médica", True, "exact_code"),
    "862002": TaxonomyDecision("Salud y bienestar", "Clínicas y consultas", "Consulta médica", "Consulta médica", True, "exact_code"),
    "861002": TaxonomyDecision("Salud y bienestar", "Clínicas y consultas", "Clínica médica", "Clínica médica", True, "exact_code"),
    "869007": TaxonomyDecision("Salud y bienestar", "Clínicas y consultas", "Fisioterapia", "Fisioterapia", True, "exact_code"),
    "869008": TaxonomyDecision("Salud y bienestar", "Clínicas y consultas", "Fisioterapia", "Fisioterapia", True, "exact_code"),
    "869003": TaxonomyDecision("Salud y bienestar", "Clínicas y consultas", "Podología", "Podología", True, "exact_code"),
    "869005": TaxonomyDecision("Salud y bienestar", "Clínicas y consultas", "Optometría", "Optometría", True, "exact_code"),
    "869009": TaxonomyDecision("Salud y bienestar", "Clínicas y consultas", "Parasanitario", "Parasanitario", True, "exact_code"),
    "750002": TaxonomyDecision("Salud y bienestar", "Clínicas y consultas", "Veterinaria", "Veterinaria", True, "exact_code"),
    "750003": TaxonomyDecision("Salud y bienestar", "Clínicas y consultas", "Veterinaria", "Veterinaria", True, "exact_code"),
    "475201": TaxonomyDecision("Retail especializado", "Hogar y reformas", "Ferretería", "Ferretería", True, "exact_code"),
    "475204": TaxonomyDecision("Retail especializado", "Hogar y reformas", "Bricolaje", "Bricolaje", True, "exact_code"),
    "475202": TaxonomyDecision("Retail especializado", "Hogar y reformas", "Materiales de construcción", "Materiales de construcción", True, "exact_code"),
    "475203": TaxonomyDecision("Retail especializado", "Hogar y reformas", "Puertas y ventanas", "Puertas y ventanas", True, "exact_code"),
    "475205": TaxonomyDecision("Retail especializado", "Hogar y reformas", "Saneamientos", "Saneamientos", True, "exact_code"),
    "475206": TaxonomyDecision("Retail especializado", "Hogar y reformas", "Material eléctrico", "Material eléctrico", True, "exact_code"),
    "475901": TaxonomyDecision("Retail especializado", "Hogar y decoración", "Muebles", "Muebles", True, "exact_code"),
    "475903": TaxonomyDecision("Retail especializado", "Hogar y decoración", "Muebles de cocina", "Muebles de cocina", True, "exact_code"),
    "475905": TaxonomyDecision("Retail especializado", "Hogar y decoración", "Colchonería", "Colchonería", True, "exact_code"),
    "475906": TaxonomyDecision("Retail especializado", "Hogar y decoración", "Iluminación", "Iluminación", True, "exact_code"),
    "475907": TaxonomyDecision("Retail especializado", "Hogar y decoración", "Hogar y menaje", "Hogar y menaje", True, "exact_code"),
    "475902": TaxonomyDecision("Retail especializado", "Hogar y decoración", "Menaje del hogar", "Menaje del hogar", True, "exact_code"),
    "475101": TaxonomyDecision("Retail especializado", "Hogar y decoración", "Textil hogar", "Textil hogar", True, "exact_code"),
    "475401": TaxonomyDecision("Retail especializado", "Electrónica y telecom", "Electrodomésticos", "Electrodomésticos", True, "exact_code"),
    "474201": TaxonomyDecision("Retail especializado", "Electrónica y telecom", "Telefonía", "Telefonía", True, "exact_code"),
    "474302": TaxonomyDecision("Retail especializado", "Electrónica y telecom", "Electrónica", "Electrónica", True, "exact_code"),
    "474102": TaxonomyDecision("Retail especializado", "Electrónica y telecom", "Informática", "Informática", True, "exact_code"),
    "476201": TaxonomyDecision("Retail especializado", "Cultura y ocio", "Papelería y prensa", "Papelería y prensa", True, "exact_code"),
    "476101": TaxonomyDecision("Retail especializado", "Cultura y ocio", "Librería", "Librería", True, "exact_code"),
    "476403": TaxonomyDecision("Retail especializado", "Cultura y ocio", "Deporte", "Deporte", True, "exact_code"),
    "476401": TaxonomyDecision("Retail especializado", "Cultura y ocio", "Bicicletas", "Bicicletas", True, "exact_code"),
    "476501": TaxonomyDecision("Retail especializado", "Cultura y ocio", "Juguetería", "Juguetería", True, "exact_code"),
    "452001": TaxonomyDecision("Automoción", "Taller y reparación", "Taller chapa y pintura", "Taller chapa y pintura", True, "exact_code"),
    "452002": TaxonomyDecision("Automoción", "Taller y reparación", "Taller mecánica", "Taller mecánica", True, "exact_code"),
    "452003": TaxonomyDecision("Automoción", "Taller y reparación", "Accesorios automóvil", "Accesorios automóvil", True, "exact_code"),
    "452004": TaxonomyDecision("Automoción", "Taller y reparación", "Taller automóvil", "Taller automóvil", True, "exact_code"),
    "453001": TaxonomyDecision("Automoción", "Venta y recambios", "Recambios automóvil", "Recambios automóvil", True, "exact_code"),
    "451001": TaxonomyDecision("Automoción", "Venta y recambios", "Venta de coches nuevos", "Venta de coches nuevos", True, "exact_code"),
    "451002": TaxonomyDecision("Automoción", "Venta y recambios", "Venta de coches usados", "Venta de coches usados", True, "exact_code"),
    "454001": TaxonomyDecision("Automoción", "Venta y recambios", "Motos y reparación", "Motos y reparación", True, "exact_code"),
    "454002": TaxonomyDecision("Automoción", "Venta y recambios", "Venta de motos", "Venta de motos", True, "exact_code"),
    "473001": TaxonomyDecision("Automoción", "Servicios automoción", "Gasolinera", "Gasolinera", True, "exact_code"),
    "821001": TaxonomyDecision("Servicios", "Servicios profesionales", "Oficina y administración", "Oficina y administración", True, "exact_code"),
    "683001": TaxonomyDecision("Servicios", "Servicios profesionales", "Inmobiliaria", "Inmobiliaria", True, "exact_code"),
    "692001": TaxonomyDecision("Servicios", "Servicios profesionales", "Asesoría y contabilidad", "Asesoría y contabilidad", True, "exact_code"),
    "691001": TaxonomyDecision("Servicios", "Servicios profesionales", "Despacho jurídico", "Despacho jurídico", True, "exact_code"),
    "691002": TaxonomyDecision("Servicios", "Servicios profesionales", "Despacho jurídico", "Despacho jurídico", True, "exact_code"),
    "702001": TaxonomyDecision("Servicios", "Servicios profesionales", "Consultoría empresarial", "Consultoría empresarial", True, "exact_code"),
    "710001": TaxonomyDecision("Servicios", "Servicios profesionales", "Arquitectura e ingeniería", "Arquitectura e ingeniería", True, "exact_code"),
    "710002": TaxonomyDecision("Servicios", "Servicios profesionales", "Arquitectura e ingeniería", "Arquitectura e ingeniería", True, "exact_code"),
    "730001": TaxonomyDecision("Servicios", "Servicios profesionales", "Publicidad y marketing", "Publicidad y marketing", True, "exact_code"),
    "741001": TaxonomyDecision("Servicios", "Servicios profesionales", "Diseño", "Diseño", True, "exact_code"),
    "742001": TaxonomyDecision("Servicios", "Servicios profesionales", "Fotografía", "Fotografía", True, "exact_code"),
    "620001": TaxonomyDecision("Servicios", "Servicios profesionales", "Tecnología y software", "Tecnología y software", True, "exact_code"),
    "631001": TaxonomyDecision("Servicios", "Servicios profesionales", "Servicios digitales", "Servicios digitales", True, "exact_code"),
    "641001": TaxonomyDecision("Finanzas", "Finanzas y seguros", "Banco y caja", "Banco y caja", True, "exact_code"),
    "651001": TaxonomyDecision("Finanzas", "Finanzas y seguros", "Seguros", "Seguros", True, "exact_code"),
    "661002": TaxonomyDecision("Finanzas", "Finanzas y seguros", "Cambio y envío de moneda", "Cambio y envío de moneda", True, "exact_code"),
    "662001": TaxonomyDecision("Finanzas", "Finanzas y seguros", "Servicios auxiliares seguros", "Servicios auxiliares seguros", True, "exact_code"),
    "790001": TaxonomyDecision("Servicios", "Servicios al consumidor", "Agencia de viajes", "Agencia de viajes", True, "exact_code"),
    "610002": TaxonomyDecision("Servicios", "Servicios al consumidor", "Locutorio", "Locutorio", True, "exact_code"),
    "610001": TaxonomyDecision("Servicios", "Servicios profesionales", "Telecomunicaciones", "Telecomunicaciones", True, "exact_code"),
    "931008": TaxonomyDecision("Deporte y ocio", "Fitness y deporte", "Gimnasio", "Gimnasio", True, "exact_code"),
    "931001": TaxonomyDecision("Deporte y ocio", "Fitness y deporte", "Instalación deportiva", "Instalación deportiva", True, "exact_code"),
    "931009": TaxonomyDecision("Deporte y ocio", "Fitness y deporte", "Club deportivo", "Club deportivo", True, "exact_code"),
    "932006": TaxonomyDecision("Hostelería", "Ocio nocturno", "Discoteca", "Discoteca", True, "exact_code"),
    "932007": TaxonomyDecision("Deporte y ocio", "Ocio y entretenimiento", "Salón recreativo", "Salón recreativo", True, "exact_code"),
    "932002": TaxonomyDecision("Deporte y ocio", "Ocio y entretenimiento", "Celebraciones infantiles", "Celebraciones infantiles", True, "exact_code"),
    "561001": TaxonomyDecision("Hostelería", "Restauración", "Restaurante", "Restaurante", True, "exact_code"),
    "561002": TaxonomyDecision("Hostelería", "Restauración", "Comida rápida", "Comida rápida", True, "exact_code"),
    "561004": TaxonomyDecision("Hostelería", "Bar y cafetería", "Bar restaurante", "Bar restaurante", True, "exact_code"),
    "561005": TaxonomyDecision("Hostelería", "Bar y cafetería", "Bar con cocina", "Bar con cocina", True, "exact_code"),
    "561006": TaxonomyDecision("Hostelería", "Bar y cafetería", "Cafetería", "Cafetería", True, "exact_code"),
    "561007": TaxonomyDecision("Hostelería", "Bar y cafetería", "Heladería y salón de té", "Heladería y salón de té", True, "exact_code"),
    "562101": TaxonomyDecision("Hostelería", "Catering y colectividades", "Eventos y banquetes", "Eventos y banquetes", True, "exact_code"),
    "562901": TaxonomyDecision("Hostelería", "Catering y colectividades", "Comedor colectivo", "Comedor colectivo", True, "exact_code"),
    "562902": TaxonomyDecision("Hostelería", "Catering y colectividades", "Comedor colectivo", "Comedor colectivo", True, "exact_code"),
    "562903": TaxonomyDecision("Hostelería", "Catering y colectividades", "Comedor colectivo", "Comedor colectivo", True, "exact_code"),
    "563001": TaxonomyDecision("Hostelería", "Bar y cafetería", "Bodega con consumo", "Bodega con consumo", True, "exact_code"),
    "563002": TaxonomyDecision("Hostelería", "Bar y cafetería", "Bar especial", "Bar especial", True, "exact_code"),
    "563003": TaxonomyDecision("Hostelería", "Bar y cafetería", "Bar especial con actuaciones", "Bar especial con actuaciones", True, "exact_code"),
    "563004": TaxonomyDecision("Hostelería", "Bar y cafetería", "Taberna", "Taberna", True, "exact_code"),
    "563005": TaxonomyDecision("Hostelería", "Bar y cafetería", "Bar sin cocina", "Bar sin cocina", True, "exact_code"),
    "563007": TaxonomyDecision("Hostelería", "Ocio nocturno", "Café espectáculo", "Café espectáculo", True, "exact_code"),
    "551001": TaxonomyDecision("Alojamiento", "Alojamiento turístico", "Hotel", "Hotel", True, "exact_code"),
    "551003": TaxonomyDecision("Alojamiento", "Alojamiento turístico", "Hostal", "Hostal", True, "exact_code"),
    "551005": TaxonomyDecision("Alojamiento", "Alojamiento turístico", "Vivienda turística", "Vivienda turística", True, "exact_code"),
    "552001": TaxonomyDecision("Alojamiento", "Alojamiento turístico", "Albergue", "Albergue", True, "exact_code"),
    "855001": TaxonomyDecision("Educación", "Formación", "Autoescuela", "Autoescuela", True, "exact_code"),
    "855002": TaxonomyDecision("Educación", "Formación", "Formación no reglada", "Formación no reglada", True, "exact_code"),
    "855003": TaxonomyDecision("Educación", "Formación", "Idiomas", "Idiomas", True, "exact_code"),
    "851001": TaxonomyDecision("Educación", "Educación infantil", "Escuela infantil", "Escuela infantil", True, "exact_code"),
    "851002": TaxonomyDecision("Educación", "Educación infantil", "Escuela infantil", "Escuela infantil", True, "exact_code"),
    "851003": TaxonomyDecision("Educación", "Educación infantil", "Centro de cuidado infantil", "Centro de cuidado infantil", True, "exact_code"),
}


NON_INVESTABLE_PREFIXES = (
    "01", "02", "03", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "35", "36", "37", "38", "39", "41", "42", "43", "46", "49", "50", "51", "52", "53", "58", "59", "60", "64", "65", "66", "68", "69", "70", "71", "72", "73", "74", "77", "78", "79", "80", "81", "82", "84", "85", "87", "88", "89", "90", "91", "94", "95", "97", "98", "99",
)


MACRO_CATEGORY_DEFINITIONS: dict[str, tuple[str, str]] = {
    "fresh_produce": ("Frutería y verdulería", "Locales especializados en fruta, verdura y hortaliza fresca."),
    "butcher": ("Carnicería y proteína fresca", "Carnicerías, charcuterías, pollerías, casquerías y negocios equivalentes de proteína fresca."),
    "fish_shop": ("Pescadería y marisquería", "Venta especializada de pescado, marisco y productos del mar."),
    "bakery_pastry": ("Panadería y pastelería", "Pan, bollería, pastelería, confitería y repostería."),
    "ready_meals": ("Comida preparada", "Comida para llevar, platos preparados y oferta alimentaria lista para consumir."),
    "supermarket": ("Supermercado", "Supermercados, autoservicios y gran distribución alimentaria."),
    "food_convenience": ("Tienda de alimentación", "Tiendas de proximidad con surtido general de alimentación y conveniencia."),
    "food_specialty": ("Especialistas de alimentación", "Negocios especializados en café, bodega, lácteos, congelados, frutos secos, chuches u otras categorías gourmet."),
    "bar_cafe": ("Bar y cafetería", "Bares, cafeterías, tabernas y formatos de hostelería ligera sin foco principal en restauración completa."),
    "restaurant": ("Restaurante", "Restaurantes, comida rápida y formatos de restauración con cocina principal."),
    "nightlife": ("Ocio nocturno", "Discotecas, cafés espectáculo y locales nocturnos de consumo y entretenimiento."),
    "catering_collective": ("Catering y colectividades", "Catering, banquetes, comedores colectivos y restauración para grupos."),
    "tourist_accommodation": ("Alojamiento turístico", "Hoteles, hostales, albergues y otros alojamientos de corta estancia."),
    "pharmacy_optics": ("Farmacia, óptica y salud retail", "Farmacias, ópticas, herbolarios y retail sanitario de alta recurrencia."),
    "clinic_health": ("Clínicas y consultas", "Clínicas, consultas médicas, dentales, fisioterapia, podología, veterinaria y servicios sanitarios equivalentes."),
    "beauty_personal_care": ("Belleza y cuidado personal", "Peluquería, barbería, estética y otros servicios de cuidado personal recurrente."),
    "fashion_accessories": ("Moda y complementos", "Moda, calzado, joyería, relojería y complementos personales."),
    "home_decor": ("Hogar y decoración", "Muebles, textil hogar, iluminación, menaje y decoración."),
    "home_improvement": ("Ferretería y reformas", "Ferretería, bricolaje, materiales, saneamientos y equipamiento para reforma o mantenimiento del hogar."),
    "electronics_telecom": ("Electrónica y telecom", "Electrónica de consumo, electrodomésticos, informática y telefonía."),
    "books_leisure_retail": ("Cultura, papelería y ocio retail", "Librerías, papelerías, jugueterías, bicicletas, deporte retail y comercios afines de ocio."),
    "bazaar_gifts": ("Bazar, regalos y retail variado", "Bazares, floristerías, multiproducto y comercios especializados de regalo o surtido variado."),
    "pet_retail": ("Mascotas", "Tiendas de animales, accesorios y alimentación para mascotas."),
    "personal_services_repair": ("Servicios personales y reparación ligera", "Lavandería, tintorería, arreglo de ropa, reparación de calzado y servicios personales similares."),
    "business_services": ("Servicios profesionales y oficina", "Asesoría, legal, consultoría, administración e inmobiliaria orientada a oficina o servicios empresariales."),
    "creative_tech_services": ("Servicios creativos y tecnología", "Arquitectura, ingeniería, publicidad, diseño, fotografía, software, servicios digitales y telecomunicaciones."),
    "consumer_services": ("Servicios al consumidor", "Agencias de viaje, locutorios y otros servicios presenciales para consumidor final."),
    "logistics_mobility": ("Logística y movilidad", "Mensajería, paquetería, almacenamiento ligero y otros servicios logísticos o de movilidad."),
    "finance_insurance": ("Finanzas y seguros", "Banca, seguros, cambio de divisa y servicios financieros presenciales."),
    "auto_repair": ("Taller y reparación de vehículos", "Talleres, chapa, pintura, mecánica y mantenimiento del automóvil o moto."),
    "vehicle_sales_parts": ("Venta y recambios de vehículos", "Venta de vehículos, motos y recambios o accesorios relevantes."),
    "fuel_station": ("Gasolinera y servicios automoción", "Estaciones de servicio y formatos vinculados a repostaje o paso viario."),
    "early_childhood": ("Educación infantil", "Escuelas infantiles y centros de cuidado para primera infancia."),
    "training_languages": ("Formación e idiomas", "Autoescuelas, idiomas y formación no reglada."),
    "fitness_sports": ("Fitness y deporte", "Gimnasios, clubes y centros de práctica deportiva."),
    "entertainment": ("Ocio y entretenimiento", "Salones recreativos, celebraciones y ocio presencial no nocturno."),
    "non_priorizable": ("No priorizable", "Actividades industriales, institucionales o fuera del foco comercial de apertura minorista."),
}


DISPLAY_LABEL_TO_MACRO_CODE: dict[str, str] = {
    "Frutería": "fresh_produce",
    "Carnicería": "butcher",
    "Charcutería": "butcher",
    "Carnicería y charcutería": "butcher",
    "Aves y huevos": "butcher",
    "Casquería": "butcher",
    "Pescadería": "fish_shop",
    "Panadería": "bakery_pastry",
    "Pastelería y repostería": "bakery_pastry",
    "Panadería y pastelería": "bakery_pastry",
    "Comida preparada": "ready_meals",
    "Supermercado": "supermarket",
    "Gran superficie de alimentación": "supermarket",
    "Tienda de alimentación": "food_convenience",
    "Alimentación envasada": "food_convenience",
    "Lácteos y bebidas": "food_specialty",
    "Bodega": "food_specialty",
    "Heladería": "food_specialty",
    "Congelados": "food_specialty",
    "Golosinas": "food_specialty",
    "Frutos secos y encurtidos": "food_specialty",
    "Café e infusiones": "food_specialty",
    "Bar restaurante": "bar_cafe",
    "Bar con cocina": "bar_cafe",
    "Cafetería": "bar_cafe",
    "Heladería y salón de té": "bar_cafe",
    "Bodega con consumo": "bar_cafe",
    "Bar especial": "bar_cafe",
    "Taberna": "bar_cafe",
    "Bar sin cocina": "bar_cafe",
    "Churrería": "bar_cafe",
    "Restaurante": "restaurant",
    "Comida rápida": "restaurant",
    "Discoteca": "nightlife",
    "Café espectáculo": "nightlife",
    "Bar especial con actuaciones": "nightlife",
    "Eventos y banquetes": "catering_collective",
    "Comedor colectivo": "catering_collective",
    "Hotel": "tourist_accommodation",
    "Hostal": "tourist_accommodation",
    "Vivienda turística": "tourist_accommodation",
    "Albergue": "tourist_accommodation",
    "Alojamiento turístico": "tourist_accommodation",
    "Farmacia": "pharmacy_optics",
    "Óptica": "pharmacy_optics",
    "Herbolario": "pharmacy_optics",
    "Salud retail": "pharmacy_optics",
    "Clínica dental": "clinic_health",
    "Consulta médica": "clinic_health",
    "Clínica médica": "clinic_health",
    "Fisioterapia": "clinic_health",
    "Podología": "clinic_health",
    "Optometría": "clinic_health",
    "Parasanitario": "clinic_health",
    "Veterinaria": "clinic_health",
    "Clínicas y consultas": "clinic_health",
    "Peluquería": "beauty_personal_care",
    "Instituto de belleza": "beauty_personal_care",
    "Centro de estética": "beauty_personal_care",
    "Bronceado": "beauty_personal_care",
    "Fotodepilación": "beauty_personal_care",
    "Tattoo y piercing": "beauty_personal_care",
    "Belleza y cuidado personal": "beauty_personal_care",
    "Perfumería y cosmética": "beauty_personal_care",
    "Moda": "fashion_accessories",
    "Calzado": "fashion_accessories",
    "Joyería y relojería": "fashion_accessories",
    "Muebles": "home_decor",
    "Muebles de cocina": "home_decor",
    "Colchonería": "home_decor",
    "Iluminación": "home_decor",
    "Hogar y menaje": "home_decor",
    "Menaje del hogar": "home_decor",
    "Textil hogar": "home_decor",
    "Ferretería": "home_improvement",
    "Bricolaje": "home_improvement",
    "Materiales de construcción": "home_improvement",
    "Puertas y ventanas": "home_improvement",
    "Saneamientos": "home_improvement",
    "Material eléctrico": "home_improvement",
    "Electrodomésticos": "electronics_telecom",
    "Telefonía": "electronics_telecom",
    "Electrónica": "electronics_telecom",
    "Informática": "electronics_telecom",
    "Papelería y prensa": "books_leisure_retail",
    "Librería": "books_leisure_retail",
    "Deporte": "books_leisure_retail",
    "Bicicletas": "books_leisure_retail",
    "Juguetería": "books_leisure_retail",
    "Bazar y precio único": "bazaar_gifts",
    "Tienda multiproducto": "bazaar_gifts",
    "Floristería": "bazaar_gifts",
    "Otros comercios": "bazaar_gifts",
    "Mascotas": "pet_retail",
    "Lavandería y tintorería": "personal_services_repair",
    "Arreglo de ropa": "personal_services_repair",
    "Reparación de calzado": "personal_services_repair",
    "Reparación especializada": "personal_services_repair",
    "Oficina y administración": "business_services",
    "Inmobiliaria": "business_services",
    "Asesoría y contabilidad": "business_services",
    "Despacho jurídico": "business_services",
    "Consultoría empresarial": "business_services",
    "Servicios profesionales": "business_services",
    "Arquitectura e ingeniería": "creative_tech_services",
    "Publicidad y marketing": "creative_tech_services",
    "Diseño": "creative_tech_services",
    "Fotografía": "creative_tech_services",
    "Tecnología y software": "creative_tech_services",
    "Servicios digitales": "creative_tech_services",
    "Telecomunicaciones": "creative_tech_services",
    "Agencia de viajes": "consumer_services",
    "Locutorio": "consumer_services",
    "Logística y movilidad": "logistics_mobility",
    "Banco y caja": "finance_insurance",
    "Seguros": "finance_insurance",
    "Cambio y envío de moneda": "finance_insurance",
    "Servicios auxiliares seguros": "finance_insurance",
    "Taller chapa y pintura": "auto_repair",
    "Taller mecánica": "auto_repair",
    "Accesorios automóvil": "auto_repair",
    "Taller automóvil": "auto_repair",
    "Recambios automóvil": "vehicle_sales_parts",
    "Venta de coches nuevos": "vehicle_sales_parts",
    "Venta de coches usados": "vehicle_sales_parts",
    "Motos y reparación": "vehicle_sales_parts",
    "Venta de motos": "vehicle_sales_parts",
    "Gasolinera": "fuel_station",
    "Escuela infantil": "early_childhood",
    "Centro de cuidado infantil": "early_childhood",
    "Autoescuela": "training_languages",
    "Formación no reglada": "training_languages",
    "Idiomas": "training_languages",
    "Educación y formacion": "training_languages",
    "Gimnasio": "fitness_sports",
    "Instalación deportiva": "fitness_sports",
    "Club deportivo": "fitness_sports",
    "Ocio y entretenimiento": "entertainment",
    "Salón recreativo": "entertainment",
    "Celebraciones infantiles": "entertainment",
}


WEB_CATEGORY_TO_MACRO_CODE: dict[str, str] = {
    "Alimentación fresca": "food_specialty",
    "Panadería y pastelería": "bakery_pastry",
    "Comida preparada": "ready_meals",
    "Supermercado y conveniencia": "food_convenience",
    "Especialistas de alimentación": "food_specialty",
    "Bar y cafetería": "bar_cafe",
    "Restauración": "restaurant",
    "Ocio nocturno": "nightlife",
    "Catering y colectividades": "catering_collective",
    "Alojamiento turístico": "tourist_accommodation",
    "Salud retail": "pharmacy_optics",
    "Clínicas y consultas": "clinic_health",
    "Peluquería y estética": "beauty_personal_care",
    "Cosmética y perfumería": "beauty_personal_care",
    "Moda y complementos": "fashion_accessories",
    "Hogar y decoración": "home_decor",
    "Hogar y regalos": "bazaar_gifts",
    "Hogar y reformas": "home_improvement",
    "Electrónica y telecom": "electronics_telecom",
    "Cultura y ocio": "books_leisure_retail",
    "Conveniencia": "bazaar_gifts",
    "Mascotas": "pet_retail",
    "Servicios personales": "personal_services_repair",
    "Servicios profesionales": "business_services",
    "Servicios al consumidor": "consumer_services",
    "Logística y movilidad": "logistics_mobility",
    "Finanzas y seguros": "finance_insurance",
    "Taller y reparación": "auto_repair",
    "Venta y recambios": "vehicle_sales_parts",
    "Servicios automoción": "fuel_station",
    "Educación infantil": "early_childhood",
    "Formación": "training_languages",
    "Fitness y deporte": "fitness_sports",
    "Ocio y entretenimiento": "entertainment",
}


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
        return TaxonomyDecision("Hostelería", "Restauración", "Hostelería especializada", "Hostelería especializada", True, "prefix_56")
    if code.startswith("47"):
        return _classify_retail_epigrafe(code, desc)
    if code.startswith("96") or "PELUQUER" in desc or "BELLEZA" in desc or "ESTETIC" in desc:
        return TaxonomyDecision("Belleza y cuidado personal", "Servicios personales", "Belleza y cuidado personal", "Belleza y cuidado personal", True, "prefix_96")
    if code.startswith("86") or code.startswith("87") or code.startswith("75") or "CONSULTA" in desc or "CLINICA" in desc or "FISIOTER" in desc:
        return TaxonomyDecision("Salud y bienestar", "Clínicas y consultas", "Clínicas y consultas", "Clínicas y consultas", True, "prefix_health")
    if code.startswith("45") or code.startswith("47") and "VEHICUL" in desc:
        return TaxonomyDecision("Automoción", "Venta y recambios", "Automoción", "Automoción", True, "prefix_auto")
    if code.startswith("55"):
        return TaxonomyDecision("Alojamiento", "Alojamiento turístico", "Alojamiento turístico", "Alojamiento turístico", True, "prefix_55")
    if code.startswith("85"):
        return TaxonomyDecision("Educación", "Formación", "Educación y formacion", "Educación y formacion", True, "prefix_85")
    if code.startswith("93") or code.startswith("92"):
        return TaxonomyDecision("Deporte y ocio", "Ocio y entretenimiento", "Ocio y entretenimiento", "Ocio y entretenimiento", True, "prefix_92_93")
    if code.startswith("61") or code.startswith("62") or code.startswith("63") or code.startswith("69") or code.startswith("70") or code.startswith("71") or code.startswith("73") or code.startswith("74") or code.startswith("79") or code.startswith("82"):
        return TaxonomyDecision("Servicios", "Servicios profesionales", "Servicios profesionales", "Servicios profesionales", True, "prefix_services")
    if code.startswith("64") or code.startswith("65") or code.startswith("66"):
        return TaxonomyDecision("Finanzas", "Finanzas y seguros", "Finanzas y seguros", "Finanzas y seguros", True, "prefix_finance")
    if code.startswith("52") or code.startswith("53") or code.startswith("49"):
        return TaxonomyDecision("Servicios", "Logística y movilidad", "Logística y movilidad", "Logística y movilidad", True, "prefix_logistics")
    if code.startswith("95"):
        return TaxonomyDecision("Servicios", "Servicios personales", "Reparación especializada", "Reparación especializada", True, "prefix_95")
    if any(code.startswith(prefix) for prefix in NON_INVESTABLE_PREFIXES):
        return TaxonomyDecision("No priorizable", "Industrial o institucional", "Industrial o institucional", "Industrial o institucional", False, "non_investable_prefix")
    return TaxonomyDecision("No priorizable", "Otros", "Otros", "Otros", False, "fallback_other")


def _classify_retail_epigrafe(code: str, desc: str) -> TaxonomyDecision:
    if any(term in desc for term in ("FRUTAS", "HORTALIZAS")):
        return TaxonomyDecision("Alimentación", "Alimentación fresca", "Frutería", "Frutería", True, "keyword_fruit")
    if any(term in desc for term in ("CARNICER", "CHARCUTER", "SALCHICHER")):
        return TaxonomyDecision("Alimentación", "Alimentación fresca", "Carnicería y charcutería", "Carnicería y charcutería", True, "keyword_butcher")
    if any(term in desc for term in ("PESCADOS", "MARISCOS", "PESCA")):
        return TaxonomyDecision("Alimentación", "Alimentación fresca", "Pescadería", "Pescadería", True, "keyword_fish")
    if any(term in desc for term in ("PANADERIA", "BOLLERIA", "PASTELERIA", "CONFITERIA", "REPOSTERIA")):
        return TaxonomyDecision("Alimentación", "Panadería y pastelería", "Panadería y pastelería", "Panadería y pastelería", True, "keyword_bakery")
    if any(term in desc for term in ("HELADOS", "HELADERIA")):
        return TaxonomyDecision("Hostelería", "Bar y cafetería", "Heladería", "Heladería", True, "keyword_icecream")
    if any(term in desc for term in ("PLATOS PREPARADOS", "COMIDA RAPIDA", "COMIDAS")):
        return TaxonomyDecision("Alimentación", "Comida preparada", "Comida preparada", "Comida preparada", True, "keyword_prepared_food")
    if any(term in desc for term in ("AUTOSERVICIO", "SUPERMERC", "ESTABLECIMIENTOS NO ESPECIALIZADOS", "ALIMENTICIOS NO PERECEDEROS", "BAZARES", "PRECIO UNICO")):
        label = "Supermercado y conveniencia" if "ALIMENT" in desc or "AUTOSERVICIO" in desc else "Bazar y conveniencia"
        return TaxonomyDecision("Alimentación" if "Supermercado" in label else "Retail especializado", label, label, label, True, "keyword_general_retail")
    if any(term in desc for term in ("FARMACIA", "OPTICA", "ORTOPED", "DROGUERIA", "PERFUMERIA", "COSMETICA")):
        return TaxonomyDecision("Salud y bienestar", "Salud retail", "Salud retail", "Salud retail", True, "keyword_health_retail")
    if any(term in desc for term in ("PRENDAS DE VESTIR", "CALZADO", "BISUTERIA", "JOYAS", "RELOJERIA")):
        return TaxonomyDecision("Retail especializado", "Moda y complementos", "Moda y complementos", "Moda y complementos", True, "keyword_fashion")
    if any(term in desc for term in ("FERRETERIA", "BRICOLAJE", "MUEBLES", "ELECTRODOMESTICOS", "MENAJE", "ILUMINACION", "MATERIAL ELECTRICO", "MATERIALES DE CONSTRUCCION", "TEXTILES PARA EL HOGAR")):
        return TaxonomyDecision("Retail especializado", "Hogar y reformas", "Hogar y reformas", "Hogar y reformas", True, "keyword_home")
    if any(term in desc for term in ("PAPELERIA", "LIBROS", "JUGUETES", "DEPORTIVOS", "BICICLETAS")):
        return TaxonomyDecision("Retail especializado", "Cultura y ocio", "Cultura y ocio", "Cultura y ocio", True, "keyword_leisure_retail")
    if any(term in desc for term in ("TELEFONIA", "TELECOMUNICACIONES", "INFORMATICOS", "ELECTRONICO", "FOTOGRAFICO")):
        return TaxonomyDecision("Retail especializado", "Electrónica y telecom", "Electrónica y telecom", "Electrónica y telecom", True, "keyword_tech_retail")
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


def build_macro_activity_taxonomy(audit_frame: pd.DataFrame) -> pd.DataFrame:
    web_taxonomy = build_web_taxonomy(audit_frame)
    rows: list[dict[str, object]] = []
    for row in web_taxonomy.itertuples(index=False):
        decision = classify_macro_category(
            display_label=str(row.display_label),
            web_category=str(row.web_category),
            web_supercategory=str(row.web_supercategory),
            investable=bool(row.investable),
        )
        rows.append(
            {
                "epigrafe_code": row.epigrafe_code,
                "epigrafe_desc": row.epigrafe_desc,
                "display_label": row.display_label,
                "web_category": row.web_category,
                "web_supercategory": row.web_supercategory,
                "macro_category_code": decision.macro_category_code,
                "macro_category_name": decision.macro_category_name,
                "macro_category_definition": decision.macro_category_definition,
                "investable": decision.investable,
                "macro_mapping_rule": decision.mapping_rule,
                "source_rows": row.source_rows,
            }
        )
    mapped = pd.DataFrame(rows)
    mapped["needs_manual_review"] = mapped["macro_mapping_rule"].eq("fallback_non_priorizable")
    return mapped.sort_values(["investable", "macro_category_name", "display_label", "epigrafe_code"], ascending=[False, True, True, True]).reset_index(drop=True)


def classify_macro_category(
    *,
    display_label: str,
    web_category: str,
    web_supercategory: str,
    investable: bool,
) -> MacroCategoryDecision:
    label = str(display_label or "").strip()
    category = str(web_category or "").strip()
    supercategory = str(web_supercategory or "").strip()

    if not investable or supercategory == "No priorizable":
        return _macro_decision("non_priorizable", investable=False, mapping_rule="non_investable")
    if label in DISPLAY_LABEL_TO_MACRO_CODE:
        return _macro_decision(DISPLAY_LABEL_TO_MACRO_CODE[label], investable=investable, mapping_rule="display_label")
    if category in WEB_CATEGORY_TO_MACRO_CODE:
        return _macro_decision(WEB_CATEGORY_TO_MACRO_CODE[category], investable=investable, mapping_rule="web_category")
    if supercategory == "Alimentación":
        return _macro_decision("food_specialty", investable=investable, mapping_rule="supercategory_food")
    if supercategory == "Hostelería":
        return _macro_decision("bar_cafe", investable=investable, mapping_rule="supercategory_hosteleria")
    if supercategory == "Salud y bienestar":
        return _macro_decision("clinic_health", investable=investable, mapping_rule="supercategory_health")
    if supercategory == "Belleza y cuidado personal":
        return _macro_decision("beauty_personal_care", investable=investable, mapping_rule="supercategory_beauty")
    if supercategory == "Retail especializado":
        return _macro_decision("bazaar_gifts", investable=investable, mapping_rule="supercategory_retail")
    if supercategory == "Servicios":
        return _macro_decision("business_services", investable=investable, mapping_rule="supercategory_services")
    if supercategory == "Automoción":
        return _macro_decision("auto_repair", investable=investable, mapping_rule="supercategory_auto")
    if supercategory == "Educación":
        return _macro_decision("training_languages", investable=investable, mapping_rule="supercategory_education")
    if supercategory == "Deporte y ocio":
        return _macro_decision("entertainment", investable=investable, mapping_rule="supercategory_leisure")
    if supercategory == "Finanzas":
        return _macro_decision("finance_insurance", investable=investable, mapping_rule="supercategory_finance")
    if supercategory == "Alojamiento":
        return _macro_decision("tourist_accommodation", investable=investable, mapping_rule="supercategory_accommodation")
    return _macro_decision("non_priorizable", investable=False, mapping_rule="fallback_non_priorizable")


def render_macro_glossary(macro_taxonomy: pd.DataFrame) -> str:
    lines: list[str] = []
    lines.append("# ACTIVITY_GLOSSARY")
    lines.append("")
    lines.append("Glosario de macrocategorías comerciales usadas para el nuevo target de supervivencia de la actividad.")
    lines.append("")
    lines.append(f"- Epígrafes cubiertos: {len(macro_taxonomy):,}")
    lines.append(f"- Macrocategorías activas: {macro_taxonomy['macro_category_name'].nunique(dropna=True):,}")
    lines.append("")
    grouped = (
        macro_taxonomy.groupby(["macro_category_code", "macro_category_name", "macro_category_definition"], dropna=False)
        .agg(
            epigrafes=("epigrafe_code", "nunique"),
            source_rows=("source_rows", "sum"),
            fine_labels=("display_label", lambda s: ", ".join(pd.Series(s).dropna().astype(str).drop_duplicates().sort_values().head(8).tolist())),
        )
        .reset_index()
        .sort_values(["source_rows", "macro_category_name"], ascending=[False, True])
    )
    for row in grouped.itertuples(index=False):
        lines.append(f"## {row.macro_category_name}")
        lines.append("")
        lines.append(f"- Código: {row.macro_category_code}")
        lines.append(f"- Definición: {row.macro_category_definition}")
        lines.append(f"- Epígrafes mapeados: {int(row.epigrafes):,}")
        lines.append(f"- Cobertura histórica bruta: {int(row.source_rows):,} filas")
        lines.append(f"- Ejemplos de etiquetas finas: {row.fine_labels}")
        lines.append("")
    return "\n".join(lines)


def macro_category_feature_names() -> list[str]:
    return [f"macro_category__{code}" for code in MACRO_CATEGORY_DEFINITIONS if code != "non_priorizable"]


def _macro_decision(code: str, *, investable: bool, mapping_rule: str) -> MacroCategoryDecision:
    name, definition = MACRO_CATEGORY_DEFINITIONS[code]
    return MacroCategoryDecision(
        macro_category_code=code,
        macro_category_name=name,
        macro_category_definition=definition,
        investable=investable and code != "non_priorizable",
        mapping_rule=mapping_rule,
    )


def _normalize_text(value: object) -> str:
    text = str(value or "").upper()
    text = re.sub(r"[^A-Z0-9ÑÁÉÍÓÚÜ ]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text