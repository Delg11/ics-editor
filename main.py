"""
📅 Editor Interativo de ICS (Alta Fidelidade)

Ferramenta visual para importação, filtragem e exclusão em lote de eventos 
de arquivos de calendário (.ics). Projetado para manter a integridade total 
dos dados originais (alarmes, metadados, fusos horários) após a exportação.

Criado por: Gabriel Delgado
Desenvolvido com auxílio da ferramenta Google Gemini.
"""

# Instalação das bibliotecas necessárias (descomente a linha abaixo se for rodar no Colab/Jupyter)
# !pip install -q icalendar gradio pandas

import pandas as pd
from icalendar import Calendar
import gradio as gr
from datetime import datetime
import tempfile
import uuid
import copy # Biblioteca essencial para copiar os alarmes (subcomponentes)

# 1. Função para extrair dados preservando o original no background
def importar_ics(arquivo):
    if arquivo is None:
        return pd.DataFrame(), pd.DataFrame(), {}
    
    with open(arquivo.name, 'rb') as f:
        cal = Calendar.from_ical(f.read())
        
    cal_data = {
        'properties': [(k, v) for k, v in cal.items()],
        'timezones': [tz for tz in cal.walk('vtimezone')],
        'vevents': {}
    }
        
    eventos = []
    for component in cal.walk('vevent'):
        evento = {}
        
        uid = str(component.get('uid'))
        if not uid:
            uid = str(uuid.uuid4()) + '@seucalendario.com'
            component['uid'] = uid
            
        cal_data['vevents'][uid] = component
        
        evento['Título'] = str(component.get('summary', ''))
        
        dtstart = component.get('dtstart')
        if dtstart and hasattr(dtstart, 'dt'):
            if isinstance(dtstart.dt, datetime):
                evento['Início'] = dtstart.dt.strftime('%Y-%m-%d %H:%M')
            else:
                evento['Início'] = dtstart.dt.strftime('%Y-%m-%d')
        else:
            evento['Início'] = ''
            
        dtend = component.get('dtend')
        if dtend and hasattr(dtend, 'dt'):
            if isinstance(dtend.dt, datetime):
                evento['Fim'] = dtend.dt.strftime('%Y-%m-%d %H:%M')
            else:
                evento['Fim'] = dtend.dt.strftime('%Y-%m-%d')
        else:
            evento['Fim'] = ''
        
        rrule = component.get('rrule')
        evento['Recorrência'] = rrule.to_ical().decode('utf-8') if rrule else ''
            
        evento['Local'] = str(component.get('location', ''))
        evento['Descrição'] = str(component.get('description', ''))
        evento['UID'] = uid
        
        eventos.append(evento)
        
    df = pd.DataFrame(eventos)
    return df, df, cal_data 

# 2. Função para aplicar filtros de busca, recorrência e data
def filtrar_tabela(df_original, texto_busca, opcao_recorrencia, data_inicio, data_fim):
    if df_original.empty:
        return df_original
    
    df_filtrado = df_original.copy()
    
    if texto_busca:
        df_filtrado = df_filtrado[df_filtrado.apply(lambda row: row.astype(str).str.contains(texto_busca, case=False).any(), axis=1)]
        
    # Filtros de Recorrência
    if opcao_recorrencia == "Apenas COM recorrência":
        df_filtrado = df_filtrado[df_filtrado['Recorrência'] != '']
    elif opcao_recorrencia == "Apenas SEM recorrência":
        df_filtrado = df_filtrado[df_filtrado['Recorrência'] == '']
        
    # Filtros de Data
    if data_inicio or data_fim:
        datas_inicio_dt = pd.to_datetime(df_filtrado['Início'], errors='coerce')
        if data_inicio:
            try:
                dt_in = pd.to_datetime(data_inicio)
                mascara = datas_inicio_dt >= dt_in
                df_filtrado = df_filtrado[mascara]
                datas_inicio_dt = datas_inicio_dt[mascara]
            except: pass
        if data_fim:
            try:
                dt_out = pd.to_datetime(data_fim)
                if len(data_fim.strip()) <= 10: 
                    dt_out = dt_out + pd.Timedelta(days=1, seconds=-1)
                df_filtrado = df_filtrado[datas_inicio_dt <= dt_out]
            except: pass
                
    return df_filtrado

# 3. Funções de Exclusão e Limpeza
def excluir_visiveis(df_estado, df_visivel):
    if df_visivel.empty or df_estado.empty:
        return df_estado, df_estado
    uids_para_remover = df_visivel['UID'].tolist()
    novo_estado = df_estado[~df_estado['UID'].isin(uids_para_remover)]
    return novo_estado, novo_estado

def limpar_tudo():
    return pd.DataFrame(), pd.DataFrame()

# 4. Função para reconstruir e exportar o arquivo .ics fidedigno
def exportar_ics(df_estado_completo, cal_data):
    if df_estado_completo.empty or not cal_data:
        return None
        
    cal = Calendar()
    
    for k, v in cal_data['properties']:
        cal.add(k, v)
    for tz in cal_data['timezones']:
        cal.add_component(tz)
        
    for index, row in df_estado_completo.iterrows():
        uid = row.get('UID')
        if uid in cal_data['vevents']:
            evento_original = cal_data['vevents'][uid]
            vevent = evento_original.copy()
            
            # Copiar explicitamente os alarmes (VALARM) e outros subcomponentes
            if hasattr(evento_original, 'subcomponents'):
                vevent.subcomponents = copy.deepcopy(evento_original.subcomponents)
            
            # Atualiza apenas os campos que podem ter sido editados visualmente
            if 'summary' in vevent: del vevent['summary']
            if row.get('Título'): vevent.add('summary', row.get('Título'))
            
            if 'location' in vevent: del vevent['location']
            if row.get('Local'): vevent.add('location', row.get('Local'))
            
            if 'description' in vevent: del vevent['description']
            if row.get('Descrição'): vevent.add('description', row.get('Descrição'))
            
            cal.add_component(vevent)
        
    fd, path = tempfile.mkstemp(suffix=".ics")
    with os.fdopen(fd, 'wb') as f:
        f.write(cal.to_ical())
        
    return path

# 5. Interface Visual (Gradio)
def criar_interface():
    with gr.Blocks(theme=gr.themes.Soft()) as app:
        gr.Markdown("# 📅 Editor Interativo de ICS (Alta Fidelidade)")
        
        estado_df = gr.State(pd.DataFrame()) 
        estado_cal = gr.State({}) 
        
        with gr.Row():
            arquivo_entrada = gr.File(label="1. Subir arquivo .ics", file_types=[".ics"])
            arquivo_saida = gr.File(label="3. Arquivo Final", interactive=False)
            
        gr.Markdown("### 🔍 Filtros de Busca")
        with gr.Row():
            filtro_texto = gr.Textbox(label="Palavra-chave", placeholder="Ex: Prova")
            filtro_recorrente = gr.Radio(choices=["Todos", "Apenas COM recorrência", "Apenas SEM recorrência"], value="Todos", label="Filtro de Recorrência")
        
        with gr.Row():
            filtro_data_inicio = gr.Textbox(label="Data Inicial (AAAA-MM-DD)", placeholder="Ex: 2024-01-01")
            filtro_data_fim = gr.Textbox(label="Data Final (AAAA-MM-DD)", placeholder="Ex: 2024-12-31")
            
        with gr.Row():
            btn_excluir_visiveis = gr.Button("🗑️ Apagar eventos visíveis na tabela", variant="stop")
            btn_limpar = gr.Button("🧹 Zerar a ferramenta")
            
        tabela = gr.Dataframe(
            label="Planilha de Eventos", 
            interactive=True, 
            wrap=True,
            row_count=(5, "dynamic")
        )
        
        btn_exportar = gr.Button("💾 2. Exportar Calendário Limpo para .ics", variant="primary")
        
        filtros = [estado_df, filtro_texto, filtro_recorrente, filtro_data_inicio, filtro_data_fim]
        
        arquivo_entrada.change(fn=importar_ics, inputs=arquivo_entrada, outputs=[tabela, estado_df, estado_cal])
        
        filtro_texto.submit(fn=filtrar_tabela, inputs=filtros, outputs=tabela)
        filtro_recorrente.change(fn=filtrar_tabela, inputs=filtros, outputs=tabela)
        filtro_data_inicio.submit(fn=filtrar_tabela, inputs=filtros, outputs=tabela)
        filtro_data_fim.submit(fn=filtrar_tabela, inputs=filtros, outputs=tabela)
        
        btn_excluir_visiveis.click(fn=excluir_visiveis, inputs=[estado_df, tabela], outputs=[estado_df, tabela])
        btn_limpar.click(fn=limpar_tudo, inputs=[], outputs=[estado_df, tabela])
        
        btn_exportar.click(fn=exportar_ics, inputs=[estado_df, estado_cal], outputs=arquivo_saida)
        
    return app

if __name__ == "__main__":
    app = criar_interface()
    app.launch(debug=True)