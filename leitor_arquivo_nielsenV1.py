import streamlit as st
import pandas as pd
import io
import time

def identificar_layout(primeira_linha):
    soma_caracteres = len(primeira_linha.strip())

    if soma_caracteres == 124:
        return "2016", soma_caracteres
    elif soma_caracteres == 140:
        return "Full", soma_caracteres
    else:
        return "Desconhecido", soma_caracteres

def limpar_linhas(file):
    """
    Limpa as linhas do arquivo:
    - Remove caracteres invisíveis.
    - Ajusta o comprimento das linhas.
    """
    linhas_limpas = []
    content = file.getvalue().decode('cp1252')

    for linha in content.split('\n'):
        linha = linha.strip()  # Remove espaços no início e fim
        linha = linha.replace('\r', '')  # Remove caracteres de retorno de carro
        if linha:  # Ignorar linhas vazias
            linhas_limpas.append(linha)

    return '\n'.join(linhas_limpas)

def formatar_valores(qtd_vendida, valor_venda):
    """
    Formata os valores de quantidade vendida e valor de venda
    """
    qtd_vendida_formatada = f"{qtd_vendida:,.3f}".replace(",", " ").replace(".", ",").replace(" ", "")
    valor_venda_formatado = f"{valor_venda:,.2f}".replace(",", " ").replace(".", ",").replace(" ", "")
    return qtd_vendida_formatada, valor_venda_formatado

def parse_txt_2016(file):
    """
    Função para parsear arquivo txt com layout 2016
    """
    content = limpar_linhas(file)
    parsed_data = []

    for linha in content.split('\n'):
        if linha.strip():
            try:
                # Mapeamento de campos baseado no layout fornecido
                codigo_loja = linha[0:10].strip()
                cod_barras = linha[10:23].strip()
                descricao = linha[23:93].strip()
                semana = linha[93:99].strip()
                qtd_vendida = float(linha[99:108].strip()) / 1000  # Divisão para ajustar o formato
                valor_venda = float(linha[108:119].strip()) / 100   # Divisão para ajustar o formato
                oferta = linha[119:120].strip()
                dia_inicial = linha[120:122].strip()
                dia_final = linha[122:124].strip()

                qtd_vendida_formatada, valor_venda_formatado = formatar_valores(qtd_vendida, valor_venda)

                parsed_data.append({
                    'Código Loja': codigo_loja,
                    'Código Barras': cod_barras,
                    'Descrição': descricao,
                    'Semana': semana,
                    'Quantidade Vendida': qtd_vendida_formatada,
                    'Valor Venda': valor_venda_formatado,
                    'Oferta': oferta,
                    'Dia Inicial': dia_inicial,
                    'Dia Final': dia_final
                })
            except Exception as e:
                st.error(f"Erro ao processar linha: {e}")

    return pd.DataFrame(parsed_data)

def parse_txt_full(file):
    """
    Função para parsear arquivo txt com layout Full
    """
    content = limpar_linhas(file)
    parsed_data = []

    for linha in content.split('\n'):
        if linha.strip():
            try:
                codigo_loja = linha[0:10].strip()
                cod_barras = linha[10:24].strip()
                descricao = linha[24:94].strip()
                semana = linha[94:100].strip()
                qtd_vendida = float(linha[100:109].strip()) / 1000
                valor_venda = float(linha[109:120].strip()) / 100
                estoque = float(linha[120:129].strip()) / 1000
                seq_promocao = linha[129:135].strip()
                oferta = linha[135:136].strip()
                dia_inicial = linha[136:138].strip()
                dia_final = linha[138:140].strip()

                qtd_vendida_formatada, valor_venda_formatado = formatar_valores(qtd_vendida, valor_venda)

                parsed_data.append({
                    'Código Loja': codigo_loja,
                    'Código Barras': cod_barras,
                    'Descrição': descricao,
                    'Semana': semana,
                    'Quantidade Vendida': qtd_vendida_formatada,
                    'Valor Venda': valor_venda_formatado,
                    'Estoque': f"{estoque:,.3f}".replace(",", " ").replace(".", ",").replace(" ", ""),
                    'Seq Promoção': seq_promocao,
                    'Oferta': oferta,
                    'Dia Inicial': dia_inicial,
                    'Dia Final': dia_final
                })
            except Exception as e:
                st.error(f"Erro ao processar linha: {e}")

    return pd.DataFrame(parsed_data)

def main():
    st.title("Processador de Arquivo Nielsen - TOTVS .txt")
    st.write("Faça upload de um arquivo .txt com layout específico")

    uploaded_file = st.file_uploader("Escolha um arquivo .txt", type="txt")

    if uploaded_file is not None:
        st.info("Arquivo carregado com sucesso! Clique no botão para iniciar a análise.")

        if st.button("Analisar"):
            with st.status("Processando o arquivo...", expanded=True) as status:
                st.write("Identificando layout...")
                time.sleep(2)

                primeira_linha = uploaded_file.readline().decode('cp1252').strip()
                layout, soma_caracteres = identificar_layout(primeira_linha)
                uploaded_file.seek(0)

                if layout == "2016":
                    st.success(f"Layout: 2016 (Caracteres: {soma_caracteres})")
                    df = parse_txt_2016(uploaded_file)
                elif layout == "Full":
                    st.success(f"Layout: Full (Caracteres: {soma_caracteres})")
                    df = parse_txt_full(uploaded_file)
                else:
                    st.error(f"Fora do Layout Reconhecido Pelo Leitor (Caracteres: {soma_caracteres}), Verifique!")
                    return

                status.update(
                    label="Análise completa!", state="complete", expanded=False
                )

            # Filtro por loja
            lojas_disponiveis = df['Código Loja'].unique()
            loja_selecionada = st.selectbox("Selecione uma loja para filtrar:", options=["Todas"] + list(lojas_disponiveis))

            if loja_selecionada != "Todas":
                df = df[df['Código Loja'] == loja_selecionada]

            st.subheader("Prévia dos Dados")
            st.dataframe(df)

            csv = df.to_csv(index=False, sep=';')
            st.download_button(
                label="Baixar dados como CSV",
                data=csv,
                file_name='dados_processados.csv',
                mime='text/csv'
            )

            st.subheader("Estatísticas")
            col1, col2 = st.columns(2)

            with col1:
                st.metric("Total de Registros", len(df))
                st.metric("Total Quantidade Vendida", df['Quantidade Vendida'].str.replace(',', '.').astype(float).sum())

            with col2:
                st.metric("Total Valor Venda", f"R$ {df['Valor Venda'].str.replace(',', '.').astype(float).sum():.2f}")

if __name__ == '__main__':
    main()
