import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import pandas as pd
import time
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def consultar_multas(driver):
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "resultadoConsulta")))
        resultado = driver.find_element(By.ID, "resultadoConsulta").text
        logging.info(f"Resultado da consulta: {resultado}")
        return "Não foram encontradas multas" not in resultado
    except Exception as e:
        logging.error(f"Erro ao consultar multas: {e}")
        return False

def preencher_planilha_com_multas(planilha_path):
    try:
        workbook_data = pd.read_excel(planilha_path, names=["PLACA", "RENAVAM"])  
        
        logging.info("Planilha carregada com sucesso.")
        logging.info("Dados da planilha:\n" + str(workbook_data.head()))
        
        resultado_multas = []
        
        for index, row in workbook_data.iterrows():
            driver = None
            try:
                driver = webdriver.Chrome()
                driver.get("https://sistemas.detran.ce.gov.br/central")

                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "taxas_multas"))).click()

                placa = row["PLACA"]
                renavam = row["RENAVAM"]
                
                logging.info(f"Consultando multas para Placa: {placa}, Renavam: {renavam}")

                placa_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@id='veiculo_placa']")))
                placa_input.clear()
                placa_input.send_keys(placa)

                renavam_input = driver.find_element(By.XPATH, "//input[@id='veiculo_renavam_chassi']")
                renavam_input.clear()
                renavam_input.send_keys(renavam)

                time.sleep(1)  

                driver.find_element(By.XPATH, "//button[@id='submit-veiculo']").click()

                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "resultadoConsulta")))
                
                tem_multas = consultar_multas(driver)

                resultado_multas.append({"PLACA": placa, "RENAVAM": renavam, "TEM_MULTAS": 'SIM' if tem_multas else 'NÃO'})

                time.sleep(2)  
            except Exception as e:
                logging.error(f"Erro ao consultar multas para Placa: {placa}, Renavam: {renavam}: {e}")
            finally:
                if driver:
                    driver.quit()

        resultado_df = pd.DataFrame(resultado_multas)
        logging.info("Resultados das multas:\n" + str(resultado_df.head()))  
        
        resultado_df.to_excel("resultado_multas.xlsx", index=False)
        
        messagebox.showinfo("Sucesso", "Planilha atualizada com sucesso!")
        logging.info("Planilha atualizada com sucesso.")

        
        os.startfile("resultado_multas.xlsx")
        
    except Exception as e:
        messagebox.showerror("Erro", f'Ocorreu um erro ao processar a planilha: {e}')
        logging.error(f'Ocorreu um erro ao processar a planilha: {e}')


def selecionar_arquivo():
    filepath = filedialog.askopenfilename()
    if filepath:
        preencher_planilha_com_multas(filepath)

root = tk.Tk()
root.title("Consulta de Multas")

btn_selecionar_arquivo = tk.Button(root, text="Selecionar Arquivo", command=selecionar_arquivo)
btn_selecionar_arquivo.pack(pady=10)

root.mainloop()
