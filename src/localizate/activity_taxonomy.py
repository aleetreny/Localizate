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


MACRO_CATEGORY_DEFINITIONS: dict[str, tuple[str, str]] = {
    "fresh_produce": ("Fruteria y verduleria", "Locales especializados en fruta, verdura y hortaliza fresca."),
    "butcher": ("Carniceria y proteina fresca", "Carnicerias, charcuterias, pollerias, casquerias y negocios equivalentes de proteina fresca."),
    "fish_shop": ("Pescaderia y marisqueria", "Venta especializada de pescado, marisco y productos del mar."),
    "bakery_pastry": ("Panaderia y pasteleria", "Pan, bolleria, pasteleria, confiteria y reposteria."),
    "ready_meals": ("Comida preparada", "Comida para llevar, platos preparados y oferta alimentaria lista para consumir."),
    "supermarket": ("Supermercado", "Supermercados, autoservicios y gran distribucion alimentaria."),
    "food_convenience": ("Tienda de alimentacion", "Tiendas de proximidad con surtido general de alimentacion y conveniencia."),
    "food_specialty": ("Especialistas de alimentacion", "Negocios especializados en cafe, bodega, lacteos, congelados, frutos secos, chuches u otras categorias gourmet."),
    "bar_cafe": ("Bar y cafeteria", "Bares, cafeterias, tabernas y formatos de hosteleria ligera sin foco principal en restauracion completa."),
    "restaurant": ("Restaurante", "Restaurantes, comida rapida y formatos de restauracion con cocina principal."),
    "nightlife": ("Ocio nocturno", "Discotecas, cafes espectaculo y locales nocturnos de consumo y entretenimiento."),
    "catering_collective": ("Catering y colectividades", "Catering, banquetes, comedores colectivos y restauracion para grupos."),
    "tourist_accommodation": ("Alojamiento turistico", "Hoteles, hostales, albergues y otros alojamientos de corta estancia."),
    "pharmacy_optics": ("Farmacia, optica y salud retail", "Farmacias, opticas, herbolarios y retail sanitario de alta recurrencia."),
    "clinic_health": ("Clinicas y consultas", "Clinicas, consultas medicas, dentales, fisioterapia, podologia, veterinaria y servicios sanitarios equivalentes."),
    "beauty_personal_care": ("Belleza y cuidado personal", "Peluqueria, barberia, estetica y otros servicios de cuidado personal recurrente."),
    "fashion_accessories": ("Moda y complementos", "Moda, calzado, joyeria, relojeria y complementos personales."),
    "home_decor": ("Hogar y decoracion", "Muebles, textil hogar, iluminacion, menaje y decoracion."),
    "home_improvement": ("Ferreteria y reformas", "Ferreteria, bricolaje, materiales, saneamientos y equipamiento para reforma o mantenimiento del hogar."),
    "electronics_telecom": ("Electronica y telecom", "Electronica de consumo, electrodomesticos, informatica y telefonia."),
    "books_leisure_retail": ("Cultura, papeleria y ocio retail", "Librerias, papelerias, jugueterias, bicicletas, deporte retail y comercios afines de ocio."),
    "bazaar_gifts": ("Bazar, regalos y retail variado", "Bazares, floristerias, multiproducto y comercios especializados de regalo o surtido variado."),
    "pet_retail": ("Mascotas", "Tiendas de animales, accesorios y alimentacion para mascotas."),
    "personal_services_repair": ("Servicios personales y reparacion ligera", "Lavanderia, tintoreria, arreglo de ropa, reparacion de calzado y servicios personales similares."),
    "business_services": ("Servicios profesionales y oficina", "Asesoria, legal, consultoria, administracion e inmobiliaria orientada a oficina o servicios empresariales."),
    "creative_tech_services": ("Servicios creativos y tecnologia", "Arquitectura, ingenieria, publicidad, diseno, fotografia, software, servicios digitales y telecomunicaciones."),
    "consumer_services": ("Servicios al consumidor", "Agencias de viaje, locutorios y otros servicios presenciales para consumidor final."),
    "logistics_mobility": ("Logistica y movilidad", "Mensajeria, paqueteria, almacenamiento ligero y otros servicios logísticos o de movilidad."),
    "finance_insurance": ("Finanzas y seguros", "Banca, seguros, cambio de divisa y servicios financieros presenciales."),
    "auto_repair": ("Taller y reparacion de vehiculos", "Talleres, chapa, pintura, mecanica y mantenimiento del automovil o moto."),
    "vehicle_sales_parts": ("Venta y recambios de vehiculos", "Venta de vehiculos, motos y recambios o accesorios relevantes."),
    "fuel_station": ("Gasolinera y servicios automocion", "Estaciones de servicio y formatos vinculados a repostaje o paso viario."),
    "early_childhood": ("Educacion infantil", "Escuelas infantiles y centros de cuidado para primera infancia."),
    "training_languages": ("Formacion e idiomas", "Autoescuelas, idiomas y formacion no reglada."),
    "fitness_sports": ("Fitness y deporte", "Gimnasios, clubes y centros de practica deportiva."),
    "entertainment": ("Ocio y entretenimiento", "Salones recreativos, celebraciones y ocio presencial no nocturno."),
    "non_priorizable": ("No priorizable", "Actividades industriales, institucionales o fuera del foco comercial de apertura minorista."),
}


DISPLAY_LABEL_TO_MACRO_CODE: dict[str, str] = {
    "Fruteria": "fresh_produce",
    "Carniceria": "butcher",
    "Charcuteria": "butcher",
    "Carniceria y charcuteria": "butcher",
    "Aves y huevos": "butcher",
    "Casqueria": "butcher",
    "Pescaderia": "fish_shop",
    "Panaderia": "bakery_pastry",
    "Pasteleria y reposteria": "bakery_pastry",
    "Panaderia y pasteleria": "bakery_pastry",
    "Comida preparada": "ready_meals",
    "Supermercado": "supermarket",
    "Gran superficie alimentacion": "supermarket",
    "Tienda de alimentacion": "food_convenience",
    "Alimentacion envasada": "food_convenience",
    "Lacteos y bebidas": "food_specialty",
    "Bodega": "food_specialty",
    "Heladeria": "food_specialty",
    "Congelados": "food_specialty",
    "Golosinas": "food_specialty",
    "Frutos secos y encurtidos": "food_specialty",
    "Cafe e infusiones": "food_specialty",
    "Bar restaurante": "bar_cafe",
    "Bar con cocina": "bar_cafe",
    "Cafeteria": "bar_cafe",
    "Heladeria y salon de te": "bar_cafe",
    "Bodega con consumo": "bar_cafe",
    "Bar especial": "bar_cafe",
    "Taberna": "bar_cafe",
    "Bar sin cocina": "bar_cafe",
    "Churreria": "bar_cafe",
    "Restaurante": "restaurant",
    "Comida rapida": "restaurant",
    "Discoteca": "nightlife",
    "Cafe espectaculo": "nightlife",
    "Bar especial con actuaciones": "nightlife",
    "Eventos y banquetes": "catering_collective",
    "Comedor colectivo": "catering_collective",
    "Hotel": "tourist_accommodation",
    "Hostal": "tourist_accommodation",
    "Vivienda turistica": "tourist_accommodation",
    "Albergue": "tourist_accommodation",
    "Alojamiento turistico": "tourist_accommodation",
    "Farmacia": "pharmacy_optics",
    "Optica": "pharmacy_optics",
    "Herbolario": "pharmacy_optics",
    "Salud retail": "pharmacy_optics",
    "Clinica dental": "clinic_health",
    "Consulta medica": "clinic_health",
    "Clinica medica": "clinic_health",
    "Fisioterapia": "clinic_health",
    "Podologia": "clinic_health",
    "Optometria": "clinic_health",
    "Parasanitario": "clinic_health",
    "Veterinaria": "clinic_health",
    "Clinicas y consultas": "clinic_health",
    "Peluqueria": "beauty_personal_care",
    "Instituto de belleza": "beauty_personal_care",
    "Centro de estetica": "beauty_personal_care",
    "Bronceado": "beauty_personal_care",
    "Fotodepilacion": "beauty_personal_care",
    "Tattoo y piercing": "beauty_personal_care",
    "Belleza y cuidado personal": "beauty_personal_care",
    "Perfumeria y cosmetica": "beauty_personal_care",
    "Moda": "fashion_accessories",
    "Calzado": "fashion_accessories",
    "Joyeria y relojeria": "fashion_accessories",
    "Muebles": "home_decor",
    "Muebles de cocina": "home_decor",
    "Colchoneria": "home_decor",
    "Iluminacion": "home_decor",
    "Hogar y menaje": "home_decor",
    "Menaje del hogar": "home_decor",
    "Textil hogar": "home_decor",
    "Ferreteria": "home_improvement",
    "Bricolaje": "home_improvement",
    "Materiales de construccion": "home_improvement",
    "Puertas y ventanas": "home_improvement",
    "Saneamientos": "home_improvement",
    "Material electrico": "home_improvement",
    "Electrodomesticos": "electronics_telecom",
    "Telefonia": "electronics_telecom",
    "Electronica": "electronics_telecom",
    "Informatica": "electronics_telecom",
    "Papeleria y prensa": "books_leisure_retail",
    "Libreria": "books_leisure_retail",
    "Deporte": "books_leisure_retail",
    "Bicicletas": "books_leisure_retail",
    "Jugueteria": "books_leisure_retail",
    "Bazar y precio unico": "bazaar_gifts",
    "Tienda multiproducto": "bazaar_gifts",
    "Floristeria": "bazaar_gifts",
    "Otros comercios": "bazaar_gifts",
    "Mascotas": "pet_retail",
    "Lavanderia y tintoreria": "personal_services_repair",
    "Arreglo de ropa": "personal_services_repair",
    "Reparacion de calzado": "personal_services_repair",
    "Reparacion especializada": "personal_services_repair",
    "Oficina y administracion": "business_services",
    "Inmobiliaria": "business_services",
    "Asesoria y contabilidad": "business_services",
    "Despacho juridico": "business_services",
    "Consultoria empresarial": "business_services",
    "Servicios profesionales": "business_services",
    "Arquitectura e ingenieria": "creative_tech_services",
    "Publicidad y marketing": "creative_tech_services",
    "Diseno": "creative_tech_services",
    "Fotografia": "creative_tech_services",
    "Tecnologia y software": "creative_tech_services",
    "Servicios digitales": "creative_tech_services",
    "Telecomunicaciones": "creative_tech_services",
    "Agencia de viajes": "consumer_services",
    "Locutorio": "consumer_services",
    "Logistica y movilidad": "logistics_mobility",
    "Banco y caja": "finance_insurance",
    "Seguros": "finance_insurance",
    "Cambio y envio de moneda": "finance_insurance",
    "Servicios auxiliares seguros": "finance_insurance",
    "Taller chapa y pintura": "auto_repair",
    "Taller mecanica": "auto_repair",
    "Accesorios automovil": "auto_repair",
    "Taller automovil": "auto_repair",
    "Recambios automovil": "vehicle_sales_parts",
    "Venta de coches nuevos": "vehicle_sales_parts",
    "Venta de coches usados": "vehicle_sales_parts",
    "Motos y reparacion": "vehicle_sales_parts",
    "Venta de motos": "vehicle_sales_parts",
    "Gasolinera": "fuel_station",
    "Escuela infantil": "early_childhood",
    "Centro de cuidado infantil": "early_childhood",
    "Autoescuela": "training_languages",
    "Formacion no reglada": "training_languages",
    "Idiomas": "training_languages",
    "Educacion y formacion": "training_languages",
    "Gimnasio": "fitness_sports",
    "Instalacion deportiva": "fitness_sports",
    "Club deportivo": "fitness_sports",
    "Ocio y entretenimiento": "entertainment",
    "Salon recreativo": "entertainment",
    "Celebraciones infantiles": "entertainment",
}


WEB_CATEGORY_TO_MACRO_CODE: dict[str, str] = {
    "Alimentacion fresca": "food_specialty",
    "Panaderia y pasteleria": "bakery_pastry",
    "Comida preparada": "ready_meals",
    "Supermercado y conveniencia": "food_convenience",
    "Especialistas alimentacion": "food_specialty",
    "Bar y cafeteria": "bar_cafe",
    "Restauracion": "restaurant",
    "Ocio nocturno": "nightlife",
    "Catering y colectividades": "catering_collective",
    "Alojamiento turistico": "tourist_accommodation",
    "Salud retail": "pharmacy_optics",
    "Clinicas y consultas": "clinic_health",
    "Peluqueria y estetica": "beauty_personal_care",
    "Cosmetica y perfumeria": "beauty_personal_care",
    "Moda y complementos": "fashion_accessories",
    "Hogar y decoracion": "home_decor",
    "Hogar y regalos": "bazaar_gifts",
    "Hogar y reformas": "home_improvement",
    "Electronica y telecom": "electronics_telecom",
    "Cultura y ocio": "books_leisure_retail",
    "Conveniencia": "bazaar_gifts",
    "Mascotas": "pet_retail",
    "Servicios personales": "personal_services_repair",
    "Servicios profesionales": "business_services",
    "Servicios al consumidor": "consumer_services",
    "Logistica y movilidad": "logistics_mobility",
    "Finanzas y seguros": "finance_insurance",
    "Taller y reparacion": "auto_repair",
    "Venta y recambios": "vehicle_sales_parts",
    "Servicios automocion": "fuel_station",
    "Educacion infantil": "early_childhood",
    "Formacion": "training_languages",
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
    if supercategory == "Alimentacion":
        return _macro_decision("food_specialty", investable=investable, mapping_rule="supercategory_food")
    if supercategory == "Hosteleria":
        return _macro_decision("bar_cafe", investable=investable, mapping_rule="supercategory_hosteleria")
    if supercategory == "Salud y bienestar":
        return _macro_decision("clinic_health", investable=investable, mapping_rule="supercategory_health")
    if supercategory == "Belleza y cuidado personal":
        return _macro_decision("beauty_personal_care", investable=investable, mapping_rule="supercategory_beauty")
    if supercategory == "Retail especializado":
        return _macro_decision("bazaar_gifts", investable=investable, mapping_rule="supercategory_retail")
    if supercategory == "Servicios":
        return _macro_decision("business_services", investable=investable, mapping_rule="supercategory_services")
    if supercategory == "Automocion":
        return _macro_decision("auto_repair", investable=investable, mapping_rule="supercategory_auto")
    if supercategory == "Educacion":
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
    lines.append("Glosario de macrocategorias comerciales usadas para el nuevo target de supervivencia de la actividad.")
    lines.append("")
    lines.append(f"- Epigrafes cubiertos: {len(macro_taxonomy):,}")
    lines.append(f"- Macrocategorias activas: {macro_taxonomy['macro_category_name'].nunique(dropna=True):,}")
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
        lines.append(f"- Codigo: {row.macro_category_code}")
        lines.append(f"- Definicion: {row.macro_category_definition}")
        lines.append(f"- Epigrafes mapeados: {int(row.epigrafes):,}")
        lines.append(f"- Cobertura historica bruta: {int(row.source_rows):,} filas")
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