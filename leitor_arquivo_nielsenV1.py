import streamlit as st
import pandas as pd

def parse_txt_file(file):
    """
    Função para parsear arquivo txt com layout específico baseado no layout fornecido.
    """
    # Ler o conteúdo do arquivo
    content = file.getvalue().decode('cp1252')

    # Lista para armazenar os dados parseados
    parsed_data = []

    # Processar linha por linha
    for linha in content.split('\n'):
        if linha.strip():  # Ignorar linhas em branco
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

                # Formatando os valores para o formato desejado
                qtd_vendida_formatada = f"{qtd_vendida:,.3f}".replace(",", " ").replace(".", ",").replace(" ", "")
                valor_venda_formatado = f"{valor_venda:,.2f}".replace(",", " ").replace(".", ",").replace(" ", "")

                # Adicionar os dados parseados à lista
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

    # Retornar como DataFrame
    return pd.DataFrame(parsed_data)

def main():
    st.title('Processador de Arquivo TXT com Filtro por Loja')
    st.write('Faça upload de um arquivo .txt com layout específico')

    # Upload do arquivo
    uploaded_file = st.file_uploader("Escolha um arquivo .txt", type="txt")

    if uploaded_file is not None:
        try:
            # Parsear o arquivo
            df = parse_txt_file(uploaded_file)

            # Filtrar por Código Loja
            st.subheader('Filtro por Código Loja')
            lojas = df['Código Loja'].unique()  # Obter lista de lojas únicas
            loja_selecionada = st.selectbox('Selecione o Código da Loja', sorted(lojas))

            # Filtrar os dados pela loja selecionada
            df_filtrado = df[df['Código Loja'] == loja_selecionada]

            # Mostrar prévia dos dados filtrados
            st.subheader('Dados Filtrados')
            st.dataframe(df_filtrado)

            # Opção para baixar dados como CSV (usando ponto e vírgula como separador)
            csv = df_filtrado.to_csv(index=False, sep=';')  # Alterado para usar ponto e vírgula
            st.download_button(
                label="Baixar dados filtrados como CSV",
                data=csv,
                file_name=f'dados_loja_{loja_selecionada}.csv',
                mime='text/csv'
            )

            # Estatísticas para a loja selecionada
            st.subheader(f'Estatísticas para a Loja {loja_selecionada}')
            total_registros = len(df_filtrado)
            total_quantidade_vendida = df_filtrado['Quantidade Vendida'].astype(str).str.replace(",", ".").astype(float).sum()
            total_valor_venda = df_filtrado['Valor Venda'].astype(str).str.replace(",", ".").astype(float).sum()

            col1, col2 = st.columns(2)

            with col1:
                st.metric('Total de Registros', total_registros)
                st.metric('Total Quantidade Vendida', f"{total_quantidade_vendida:,.3f}".replace(",", " ").replace(".", ",").replace(" ", ""))

            with col2:
                st.metric('Total Valor Venda', f'R$ {total_valor_venda:,.2f}'.replace(",", " ").replace(".", ",").replace(" ", ""))

        except Exception as e:
            st.error(f"Erro no processamento: {e}")

if __name__ == '__main__':
    main()
