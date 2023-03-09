import os
KEEP_FILES = ['index-final.py', 'licitaciones-subidas.txt', 'setting.py','.git','__pycache__','Buscador-EC2','felipito']
BASE=os.path.dirname(os.path.abspath(__file__))
MONDAY_API_URL = "https://api.monday.com/v2"
OBJECT_KEY = "licitaciones-subidas.txt"
LOCAL_FILE = os.path.join(BASE,OBJECT_KEY)
# BASE_DIR=BASE
BASE_DIR='/home/ubuntu'
LOGS_BASE=os.path.join(BASE_DIR,'felipito')
LOGS='logs.txt'
LOG_FILE=os.path.join(LOGS_BASE,LOGS)
BUCKET = 'res-certificados'
URL_BASE="https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idLicitacion="
MONDAY_API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjE4NjUyNzcwNCwidWlkIjoyNTE1MDE3NCwiaWFkIjoiMjAyMi0xMC0xN1QyMzowMzoxMy4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6NjQwOTE1NCwicmduIjoidXNlMSJ9.p4MW-Jjxo8GGKLfJ_Fif5EpYscJahLg9BXeNtj1GSXI"
CODIGOS = [
    "86111504",
    "80141617",
    "80111715",
    "86111604",
    "77101701",
    "80111504",
    "90111601",
    "43232408",
    "80111711",
    "80111608",
    "80111801",
    "43231505",
    "86141501",
    "86111601",
    "80111604",
    "86101710",
    "86101808",
    "43232107",
    "90111603",
    "81112105",
    "93141514",
    "90101603",
    "81111802",
    "80101507",
    "80101505",
    "80101604",
    "80101901",
    "43231513",
    "43233205",
    "43232804",
    "81112003",
    "81111805",
    "43231512",
    "80111716",
    "81111504",
    "43232915",
    "45111701",
    "43211501",
    "43211711",
    "81141601",
    "80111610",
    "82141502",
    "43223207",
    "86101708",
    "86111502",
    "81111506",
    "81141801",
    "80111713",
    "86101605",
    "86111503",
    "43232502"
]

PALABRAS = [
    "acoso laboral y sexual",
    "acreditación en salud",
    "aseo terminal",
    "atención integral del adulto mayor",
    "atención prehospitalaria capreb",
    "atención remota en salud, telemedicina",
    "calidad y seguridad del paciente",
    "cardiovascular",
    "clima laboral",
    "competencias parentales",
    "manejo de confictos",
    "comunicación efectiva ",
    "control y gestión de bodega",
    "covid",
    "cuidado y protección psicoemocional",
    "derecho y deberes de los funcionarios",
    "derecho y deberes de los pacientes",
    "diseño instruccional",
    "diversidad  de género",
    "dolor crónico no oncológico",
    "electrocardiograma",
    "emergencia y desastres",
    "esi",
    "estatuto administrativo",
    "ética y probidad",
    "excel",
    "educación inclusiva",
    "tea",
    "ges",
    "gestión del desempeño",
    "gestion del tiempo",
    "grd",
    "iaas",
    "violencia de género",
    "equidad de género",
    "inmovilización",
    "intervención en crisis",
    "junji",
    "lactancia materna",
    "legislación laboral",
    "lenguaje de señas",
    "liderazgo",
    "manejo de heridas",
    "manejo del estrés y autocuidado",
    "manejo del paciente crítico",
    "manejo paciente dificil",
    "multimorbilidad",
    "musculo esqueletico",
    "ofimática",
    "prehospitalaria",
    "presión arterial",
    "prevención de riesgos",
    "prevención e intervención de la violencia en establecimientos",
    "primeros auxilios psicológicos y primera respuesta psicólogica",
    "protección radiológica",
    "rcp",
    "rcp pediátrico",
    "reas",
    "reuniones efectivas",
    "riss",
    "salud familiar",
    "salud mental",
    "salud sexual y ets",
    "salud y migración",
    "técnicas de redacción y ortografía",
    "trabajo en equipo",
    "trato al usuario",
    "urgencias ginecoobstétricas",
    "vacunas",
    "vida sana",
    "procediemientos de enfermería",
    "medio ambiente",
    "manipulación de alimentos",
    "manejo del paciente postrado",
    "manejo del duelo",
    "ira - era",
    "alcohol y drogas",
    "abordaje integral adolescente",
    "capacitación",
    "capacitar",
    "capacitaciones",
    "jornada",
    "jornadas",
    "taller",
    "talleres",
    "curso",
    "cursos",
    "salud",
]