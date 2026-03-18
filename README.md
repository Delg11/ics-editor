# 📅 ICS Editor Interativo (Alta Fidelidade)

Uma ferramenta visual e interativa em Python para visualização, filtragem e exclusão em lote de eventos de arquivos de calendário (`.ics`). 

Diferente de conversores comuns que quebram a estrutura do calendário ou perdem metadados, este editor foi construído com uma arquitetura de **alta fidelidade**: ele permite a edição visual em uma interface semelhante a uma planilha, mas preserva todos os dados complexos em background (como fusos horários, regras de recorrência complexas e alarmes `VALARM`), gerando um arquivo de exportação perfeito e pronto para o Google Agenda, Outlook ou Apple Calendar.

## ✨ Principais Recursos

- **Planilha Visual Interativa:** Visualize seus eventos do calendário em uma tabela ordenável.
- **Limpeza em Lote:** Filtre eventos indesejados e exclua todos os resultados visíveis com um único clique (ideal para limpar anos letivos passados ou eventos cancelados).
- **Filtros Avançados:** - Busca por palavras-chave (título, descrição, local).
  - Filtro de intervalo de datas (Data Inicial e Data Final).
  - Filtro inteligente de recorrência (mostrar todos, apenas com recorrência ou apenas sem recorrência).
- **Exportação Fidedigna (Lossless):** O arquivo `.ics` exportado mantém os `UIDs` originais (evitando duplicatas na importação), regras de `VTIMEZONE` e notificações de lembretes intactos.

## 🚀 Como instalar e executar

Certifique-se de ter o [Python](https://www.python.org/downloads/) instalado na sua máquina (versão 3.8 ou superior recomendada).

**1. Clone o repositório:**
```bash
git clone [https://github.com/Delg11/ics-editor.git](https://github.com/Delg11/ics-editor.git)
cd ics-editor
````

**2. Instale as dependências:**
A ferramenta utiliza bibliotecas populares de manipulação de dados e interfaces web. Execute o comando:

```bash
pip install -r requirements.txt
```

**3. Inicie o aplicativo:**

```bash
python main.py
```

O terminal exibirá um link local (geralmente `http://127.0.0.1:7860`). Clique nele para abrir a ferramenta diretamente no seu navegador\!

## 💡 Guia de Uso

1.  **Upload:** Na aba inicial, faça o upload do seu arquivo `.ics` original.
2.  **Filtre:** Use os campos de busca, recorrência e datas para isolar os eventos que você deseja **excluir**. Por exemplo: digite as datas do ano passado para ver apenas eventos antigos.
3.  **Apague:** Clique no botão vermelho `"🗑️ Apagar eventos visíveis na tabela"`. Isso removerá os eventos do banco de dados interno da ferramenta.
4.  **Exporte:** Limpe os filtros para visualizar os eventos restantes (se desejar) e clique no botão azul `"💾 2. Exportar Calendário Limpo"`. Faça o download do seu novo `.ics` otimizado\!

## 🤝 Créditos

Desenvolvido por **Gabriel Delgado** com o auxílio da inteligência artificial **Google Gemini**.

## 📄 Licença

Este projeto está sob a licença [MIT](https://www.google.com/search?q=LICENSE) - sinta-se livre para usar, modificar e distribuir conforme necessário\!
