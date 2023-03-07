from setting import PALABRAS,CODIGOS,URL_BASE,MONDAY_API_KEY,BASE_DIR,OBJECT_KEY,LOCAL_FILE,MONDAY_API_URL,BUCKET
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import re
import os
import requests
import pytz
import datetime
from monday import MondayClient
import datetime
import boto3
MONDAY=MondayClient(MONDAY_API_KEY)
#Columnas monday
BOARD_PRUEBAS='3684630399'
NOMBRE='Bases'

#ids columnas monday
COLUMNA_INSTITUCION='texto40'
COLUMNA_ID_LICITACION='texto'
COLUMNA_FECHA_INICIO_PREGUNTAS='fecha6'
COLUMNA_FECHA_CIERRE_PREGUNTAS='fecha_11'
COLUMNA_LINK_LICITACION='enlace'
COLUMNA_FECHA_CIERRE='fecha_1'
COLUMNA_MONTO='n_meros76'
COLUMNA_BASES='dup__of_anexo'
COLUMNA_OTROS='archivo'



def initChromeDriver():
    options = Options()
    options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 2,
        "download.default_directory" : BASE_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,
        "profile.default_content_setting_values.automatic_downloads": 1})
    options.add_experimental_option("excludeSwitches", ["disable-popup-blocking"])
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-notifications")
    options.add_argument('--start-maximized')
    options.add_argument("--window-size=1280x1696")
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--no-zygote")
    options.add_argument("--incognito")
    options.add_argument('--disable-blink-features=AutomationControlled')
    ser = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=ser,options=options)
    wait = WebDriverWait(driver, 70)
    
    return driver,wait
    
def obtenerID_OC(text):
    regex = re.compile(r'(ID: )[0-9-A-Z]+')
    return regex.search(text).group().replace('ID: ','')

def click_element(wait,by,item):
    elemento = wait.until(ec.visibility_of_element_located((by, item)))    
    elemento.click()
    
def getSubidos():
    s3_client = boto3.client("s3")
    
    # Se limpia el TXT antes de insertar el texto descargado
    try:
        with open(LOCAL_FILE, "r+") as f:
            f.truncate()
    except:
        pass
    s3_client.download_file(BUCKET, OBJECT_KEY, LOCAL_FILE)

    with open(LOCAL_FILE) as f:
        lines = f.readlines()
    # print(lines)
    f.close()
    lines = [x.strip() for x in lines]

    return lines

def get_item_by_id(element_id: str)->dict:
    """
        busca en el elemento con el id element_id, retorna el elemento con sus columnas
    """
    query =f'''{{
        items (ids: {str(element_id)}) {{ id name
            column_values{{ id title text }}
            assets {{ id url name public_url }}  }} }}'''
    data = {'query' : query}
    r = requests.post(url=MONDAY_API_URL, json=data, headers= {"Authorization" : MONDAY_API_KEY})
    return r.json()["data"]["items"][0]

def lcomp(string_1: str, string_2: str) -> bool:
    """Compara dos strings ignorando mayusculas, tildes y limpiandolas primero"""
    replaces = {'á':'a','é':'e','í':'i','ó':'o','ú':'u', 'ñ':'n'}
    string_1 = str(string_1).strip().lower().replace("  ","")
    string_2 = str(string_2).strip().lower().replace("  ","")
    for key, value in replaces.items():
        string_1 = string_1.replace(key, value)
        string_2 = string_2.replace(key, value)
        
    
    return string_1 == string_2


def obtenerURLPublica(item:dict,id_file):
    assets=item['assets']
    for asset in assets:
      if asset['id']==id_file:
        return asset['public_url']

def cambio_fecha_hora_utc(fecha):
    timezone =   pytz.timezone('America/Santiago')
    fecha_local = timezone.localize(fecha, is_dst=None)
    fecha_utc = fecha_local.astimezone(pytz.utc)
    return fecha_utc

def remover(my_string=""):
    values = "abcdefghijklmnñopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "
    return ''.join(c for c in my_string if c in values)

def subirMonday(licitacion):
    # idLic=licitacion['idLic']
    idLic, nombreLic, fecha_cierre, fecha_inicio_preguntas, fecha_cierre_preguntas, link, organismo, monto, anexos = (
        licitacion.get(key, '') for key in (
            'idLic', 'nombreLic', 'fecha_cierre', 'fecha_inicio_preguntas', 'fecha_cierre_preguntas', 'link', 'organismo', 'monto', 'anexos'
        )
    )
    print('Subiendo '+idLic)
    nombreLic = remover(nombreLic) or idLic 
    
    # fecha_cierre=licitacion['fecha_cierre']
    # anexos=licitacion['anexos']
    # link=licitacion['link']
    # organismo=licitacion['organismo']
    # monto=licitacion['monto']
    # nombreLic=remover(licitacion['nombreLic'])
    # if not nombreLic:
    #     nombreLic=idLic
    # fecha_inicio_preguntas=licitacion['fecha_inicio_preguntas']
    # fecha_cierre_preguntas=licitacion['fecha_cierre_preguntas']
    
    fila=MONDAY.items.create_item(BOARD_PRUEBAS,'grupo_nuevo60572',nombreLic)['data']['create_item']['id']
    #Obtener Fila completa con sus columnas
    
    for archivo in anexos:
        if 'anexos' in archivo.lower() or 'anexo' in archivo.lower() or '.jpg' in archivo.lower() or '.xls'in archivo.lower():      
            MONDAY.items.add_file_to_column(fila,COLUMNA_OTROS,BASE_DIR+'/'+archivo)
        else:
            MONDAY.items.add_file_to_column(fila,COLUMNA_BASES,BASE_DIR+'/'+archivo)
            
            
    for f in os.listdir(BASE_DIR):
        os.remove(os.path.join(BASE_DIR, f))        
    
    
    MONDAY.items.change_item_value(BOARD_PRUEBAS,fila,COLUMNA_INSTITUCION,organismo)
    MONDAY.items.change_item_value(BOARD_PRUEBAS,fila,COLUMNA_ID_LICITACION,idLic)
    #Fecha Inicio Preguntas
    if fecha_inicio_preguntas:
        utc=cambio_fecha_hora_utc(fecha_inicio_preguntas)
        formated_datetime= utc.strftime("%Y-%m-%d %H:%M:%S")
        MONDAY.items.change_item_value(BOARD_PRUEBAS,fila,COLUMNA_FECHA_INICIO_PREGUNTAS,{"date" : formated_datetime.split(' ')[0],"time" : formated_datetime.split(' ')[1]})
    #Fecha Cierre Preguntas
    if fecha_cierre_preguntas:
        utc=cambio_fecha_hora_utc(fecha_cierre_preguntas)
        formated_datetime= utc.strftime("%Y-%m-%d %H:%M:%S")
        MONDAY.items.change_item_value(BOARD_PRUEBAS,fila,COLUMNA_FECHA_CIERRE_PREGUNTAS,{"date" : formated_datetime.split(' ')[0],"time" : formated_datetime.split(' ')[1]})
    
    MONDAY.items.change_item_value(BOARD_PRUEBAS,fila,COLUMNA_LINK_LICITACION, {"url" : link,"text" : "Ir a "+idLic})
    utc=cambio_fecha_hora_utc(fecha_cierre)
    formated_datetime= utc.strftime("%Y-%m-%d %H:%M:%S")
    MONDAY.items.change_item_value(BOARD_PRUEBAS,fila,COLUMNA_FECHA_CIERRE,{"date" : formated_datetime.split(' ')[0],"time" : formated_datetime.split(' ')[1]})
    MONDAY.items.change_item_value(BOARD_PRUEBAS,fila,COLUMNA_MONTO,monto)
    time.sleep(20)
    item = get_item_by_id(element_id= fila)
    bases_file=next((col["text"] for col in item["column_values"] if lcomp(col["title"], NOMBRE)), "")
    array_bases=bases_file.split(",")
    if array_bases!=['']:  
        for file in array_bases:
            file_chiquito=file.lower()
            if "anexo" not in file_chiquito:
                ruta=file.split('https://izieduca.monday.com/protected_static/')
                array_ruta=ruta[1].split('/')
                id_file=array_ruta[2]
                url=obtenerURLPublica(item,id_file)
                client = boto3.client('lambda')
                
                payload = {}
                payload['file']=url
                payload['curso']=item["id"]
                payload['board_id']=BOARD_PRUEBAS
                client.invoke_async(FunctionName="pdf_to_jpg", InvokeArgs=json.dumps(payload))
           
    return True


def obtenerDatosAdjuntos(driver,wait,idLic:str):
    driver.get(URL_BASE+idLic)
    estado=driver.find_element(By.ID,'imgEstado').get_attribute('src')
    try:
        monto=driver.find_element(By.ID,'lblFicha7MontoEstimado').get_attribute("innerHTML")
        monto=int(monto)
    except:
        monto=0
    try:
        organismo=driver.find_element(By.ID,'lblFicha2Razon').text
    except:
        organismo=""
    
    try:
        fecha_cierre=driver.find_element(By.ID,'lblCierre').text
        fecha_cierre=datetime.datetime.strptime(fecha_cierre, '%d-%m-%Y %H:%M:%S')
    except:
        try:
            fecha_cierre=driver.find_element(By.ID,'lblFicha3Cierre').text
            fecha_cierre=datetime.datetime.strptime(fecha_cierre, '%d-%m-%Y %H:%M:%S')
        except:
            fecha_cierre=datetime.datetime.now()
    
    try:
        nombreLic=driver.find_element(By.ID,'lblNombreLicitacion').text
    except:
        nombreLic="*"
    
    try:
        fecha_inicio_preguntas=driver.find_element(By.ID,'lblFicha3Inicio').text
        fecha_inicio_preguntas=datetime.datetime.strptime(fecha_inicio_preguntas, '%d-%m-%Y %H:%M:%S')
        
    except:
        fecha_inicio_preguntas=None
        
    try:
        fecha_cierre_preguntas=driver.find_element(By.ID,'lblFicha3Fin').text
        fecha_cierre_preguntas=datetime.datetime.strptime(fecha_cierre_preguntas, '%d-%m-%Y %H:%M:%S')
        
    except:
        fecha_cierre_preguntas=None
    
    time.sleep(2)
    if '/publicadas.png' not in estado:
        print('Ya no esta publicada '+idLic)
    else:
        link ="https://www.mercadopublico.cl/Procurement/Modules"+str(wait.until(ec.visibility_of_element_located((By.XPATH, f'//*[@id="imgAdjuntos"]'))).get_attribute("onclick").replace("open('..","").replace("','MercadoPublico', 'width=850, height=700, status=yes, scrollbars=yes, left=0, top=0, resizable=yes');window.event.returnValue=false;", ""))
        driver.get(link)
        rows=len(driver.find_elements(By.XPATH,'//*[@id="DWNL_grdId"]/tbody/tr'))
        filas=1 
            
        while(filas<rows):
            x=filas+1
            if x<10:
                y='0'+str(x)
            else:
                y=x
            try:
                elemento=wait.until(ec.visibility_of_all_elements_located((By.XPATH, f'//*[@id="DWNL_grdId_ctl{y}_search"]')))
                vueltas=0
                for link in elemento:
                    if vueltas<=len(elemento):
                        link.click()
                        time.sleep(5)
                        filas+=1
                    else:
                        break
                    break
                
            except:
                pass
        time.sleep(20)

        anexos=os.listdir(BASE_DIR)
        licitacionDic={}
        licitacionDic['idLic']=idLic
        licitacionDic['monto']=monto
        licitacionDic['organismo']=organismo
        licitacionDic['fecha_cierre']=fecha_cierre
        licitacionDic['anexos']=anexos
        licitacionDic['link']=URL_BASE+idLic
        licitacionDic['nombreLic']=nombreLic
        licitacionDic['fecha_inicio_preguntas']=fecha_inicio_preguntas
        licitacionDic['fecha_cierre_preguntas']=fecha_cierre_preguntas
        if subirMonday(licitacionDic):
            with open(LOCAL_FILE, 'a') as f:
                    f.writelines('\n'+str(idLic))
            s3_client=boto3.client('s3')   
            s3_client.upload_file(LOCAL_FILE, BUCKET, OBJECT_KEY)
            return True



def stopInstance():
    region = 'us-east-1'
    instances = ['i-00e6570384f7befc3']
    ec2 = boto3.client('ec2', region_name=region)
    ec2.stop_instances(InstanceIds=instances)
    print('Para la Instancia: ' + str(instances))

def lcomps(string_1):
    """Compara dos strings ignorando mayusculas, tildes y limpiandolas primero"""
    replaces = {'á':'a','é':'e','í':'i','ó':'o','ú':'u', 'ñ':'n'}
    string_1 = str(string_1).strip().lower().replace("  ","")
    for key, value in replaces.items():
        string_1 = string_1.replace(key, value)
    return string_1



def index():
    os.makedirs(BASE_DIR,exist_ok=True)
    SUBIDOS=getSubidos()
    print('Subidos '+str(len(SUBIDOS)))
    driver,wait=initChromeDriver()
    def main():
        print("Comenze")
        driver.get('https://www.mercadopublico.cl/Home/')
        elemento = driver.find_element(By.XPATH, "//button[contains(text(), 'Iniciar Sesión')]")
        elemento.click()
        try:
            elemento = driver.find_element(By.CLASS_NAME, 'btn-clave-unica')
            elemento.click()
        except:
            main()
        
        if driver.current_url.startswith('https://accounts.claveunica.gob.cl/'):
            try:
                print('Logueando')
                elemento=  wait.until(ec.visibility_of_element_located((By.XPATH, '//input[@name="run"]')))
                elemento.send_keys('16.418.605-9')
                elemento= wait.until(ec.visibility_of_element_located((By.XPATH, '//input[@name="password"]')))
                elemento.send_keys('Coni13061.')
                elemento = wait.until(ec.visibility_of_element_located((By.ID, "login-submit")))    
                elemento.click()
            except:
                main()

    while True:
        main()
        print('Dentro de Mercado')
        try:
            print('Buscando Modal')
            elemento = wait.until(ec.presence_of_element_located((By.XPATH, '//*[@id="rdbOrg1293151"]'))) 
            elemento.click()   
            print('Click Mondal')
            break
        except:
            print('ELEMENTO rdb  NO DISPONIBLE')
            pass

    elemento=wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="myModal"]/div/div/div[3]/a')))    
    elemento.click()

    # # ORDEN DE COMPRA
    elemento = wait.until(ec.frame_to_be_available_and_switch_to_it((By.XPATH, "//*[@id='fraDetalle']")))
    elementos=driver.find_elements(By.XPATH,'//span[contains(text(),"Órden de compra")]')
    for orden in elementos:
        if 'recepción conforme' in orden.text:
            idOC=obtenerID_OC(orden.text)
            orden.click()
            click_element(wait,By.XPATH,'//*[@id="lblCode2"]')
            time.sleep(10)
            idLic=driver.find_element(By.XPATH,'//*[@id="lblProvenienceValue"]').text 
            fila=MONDAY.items.fetch_items_by_column_value('3549229417','texto32',idLic)['data']['items_by_column_values'] 
            if fila:
                fila=fila[0].get('id',None)   
                MONDAY.items.change_item_value('3549229417',fila,'estado8',{"label":"Recepción Conforme"})
                archivo=os.path.join(BASE_DIR,idOC+'.pdf')
                MONDAY.items.add_file_to_column(fila,'file',archivo)    
                pdf=driver.find_element(By.ID,'imgPDF').get_attribute('onClick')
                link="https://www.mercadopublico.cl/PurchaseOrder/Modules/PO/" + str(pdf.replace("open('","").replace("','MercadoPublico', 'width=750, height=500, status=yes, scrollbars=yes, left=0, top=0, resizable=yes');window.event.returnValue=false;", ""))
                old = driver.current_window_handle 
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[1])
                driver.get(link)
                time.sleep(5)
                driver.switch_to.window(old)
                #Agregar a Monday
                print(idOC)
            
    print('Salii de Subir Orden de Compra') 


    #Búsqueda de Licitaciones para Ofertar
    # elemento = wait.until(ec.visibility_of_element_located((By.XPATH, "//a[contains(text(), 'Licitaciones ')]")))    
    # elemento.click()

    # elemento = wait.until(ec.visibility_of_element_located((By.XPATH, "//a[contains(text(), 'Búsqueda de Licitaciones para Ofertar')]")))    
    # elemento.click()
    driver.get('https://www.mercadopublico.cl/BID/Modules/RFB/NEwSearchProcurement.aspx')
    # elemento = wait.until(ec.frame_to_be_available_and_switch_to_it((By.XPATH, "//*[@id='fraDetalle']")))

    time.sleep(2)
    links_fichas=[]
    elemento = wait.until(ec.visibility_of_element_located((By.XPATH, '//select[@name ="cboRegion"]')))
    elemento.click()

    elemento = wait.until(ec.visibility_of_element_located((By.XPATH, '//option[@value =" "]')))
    elemento.click()
    time.sleep(2)

    #filtro por FECHA DE INICIO
    try:
        elemento = wait.until(ec.visibility_of_element_located((By.XPATH, '//input[@name= "calFrom"]')))
    except:
        stopInstance()
        exit()
    elemento.clear()

    cl_tz = pytz.timezone('America/Santiago')
    cl_time = datetime.datetime.now(cl_tz)
    ayer = cl_time - datetime.timedelta(days=1)

    elemento.send_keys(str(ayer.strftime('%d-%m-%Y')))
    time.sleep(5)
    #BOTON BUSCAR LICITACIONES
    elemento = wait.until(ec.visibility_of_element_located((By.XPATH, '//input[@name = "btnSearch"]')))
    elemento.click()
    time.sleep(15)

    import re
    regex=re.compile(r'[0-9]{1,}')

    try:
        cantidadElementos=int(regex.search(wait.until(ec.visibility_of_element_located((By.ID, 'lblSearchResult2'))).text).group())
    except Exception as e:
        stopInstance()
        print(e)
        # stopInstance()
            
    print('Encontre '+str(cantidadElementos)+' licitaciones')
    y=1
    while y<=(int(cantidadElementos/10)+1):
        fichas=driver.find_elements(By.XPATH,'''//a[contains(@onclick, "OpenGlobalPopup('/Procurement/Modules/RFB/DetailsAcquisition.aspx?")]''')
        time.sleep(2)
        for link in fichas:
            link_ficha=link.text
            # and link_ficha not in SUBIDOS
            if link_ficha not in links_fichas and link_ficha not in SUBIDOS:
                links_fichas.append(link_ficha)
        driver.execute_script(f'''javascript:fnMovePage({y},"wucPager");''')
        y+=1
        time.sleep(5)
        
        

    URL_BASE="https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idLicitacion="
    subir=[]
    print('REVISARE '+str(len(links_fichas)))
    for ficha in links_fichas:    
        classification=[]
        
        # if ficha not in SUBIDOS:
        driver.get(URL_BASE+ficha)
        try:
            tabla=wait.until(ec.visibility_of_all_elements_located((By.XPATH, '//*[@id="grvProducto"]/tbody/tr')))
        except:
            tabla=None
        titulo=wait.until(ec.visibility_of_element_located((By.ID, 'lblNombreLicitacion'))).text
        try:
            descripcion=wait.until(ec.visibility_of_element_located((By.ID, 'lblFicha1Descripcion'))).text
        except:
            descripcion=""
        if tabla:
            for i in range(len(tabla)):
                x=i+2
                if x<10:
                    y='0'+str(x)
                else:
                    y=x
                classification.append(driver.find_element(By.ID, f'grvProducto_ctl{y}_lblCategoria').text) 
        
            if any(onu in CODIGOS for onu in classification) or any(lcomps(palabra) in lcomps(titulo) or lcomps(palabra) in lcomps(descripcion) for palabra in PALABRAS):
                print('ME SIRVE ' + str(ficha))
                subir.append(ficha)

                
                    
    
    
    
    print('Me sirven '+str(len(subir))+ ' licitaciones')
    for lic in subir:
        obtenerDatosAdjuntos(driver,wait,lic)

        
        
    return True
       
    
# inicio = time.perf_counter()
# response=index()
# while(not response):
#     response=index()
# time.sleep(4)
# fin = time.perf_counter()
# tiempo = fin - inicio
# print("El tiempo de ejecución de la función es:", tiempo)
# stopInstance()
os.makedirs(BASE_DIR,exist_ok=True)

for f in os.listdir(BASE_DIR):
    os.remove(os.path.join(BASE_DIR, f))
driver,wait=initChromeDriver()
obtenerDatosAdjuntos(driver,wait,'1079967-14-L123')
