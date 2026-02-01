import requests
import xmltodict

def calcular_frete_real(cep_origem, cep_destino, peso_g, comp, alt, larg):
    """
    Consulta a API pública dos Correios (Legacy)
    Retorna uma lista de opções (SEDEX, PAC)
    """
    # URL oficial de cálculo (ainda funciona para consultas simples)
    url = "http://ws.correios.com.br/calculador/CalcPrecoPrazo.asmx/CalcPrecoPrazo"
    
    # Códigos de serviço: 04014=SEDEX, 04510=PAC
    servicos = ['04014', '04510'] 
    
    resultados = []

    for servico in servicos:
        params = {
            'nCdEmpresa': '',
            'sDsSenha': '',
            'nCdServico': servico,
            'sCepOrigem': cep_origem.replace('-', '').replace('.', ''),
            'sCepDestino': cep_destino.replace('-', '').replace('.', ''),
            'nVlPeso': str(peso_g / 1000), # Correios pede em Kg (ex: 0.2)
            'nCdFormato': '1', # 1 = Caixa
            'nVlComprimento': str(comp),
            'nVlAltura': str(alt),
            'nVlLargura': str(larg),
            'nVlDiametro': '0',
            'sCdMaoPropria': 'N',
            'nVlValorDeclarado': '0',
            'sCdAvisoRecebimento': 'N',
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                # Transforma o XML feio em um dicionário Python
                dados = xmltodict.parse(response.content)
                servicos_resp = dados.get('cResultado', {}).get('Servicos', {}).get('cServico', {})

                # Verifica erros (0 = sem erro)
                if servicos_resp.get('Erro') == '0':
                    nome_servico = 'SEDEX' if servico == '04014' else 'PAC'
                    valor = servicos_resp.get('Valor').replace(',', '.')
                    prazo = servicos_resp.get('PrazoEntrega')
                    
                    resultados.append({
                        'nome': nome_servico,
                        'valor': valor,
                        'prazo': prazo,
                        'codigo': servico
                    })
        except Exception as e:
            print(f"Erro ao consultar Correios ({servico}): {e}")
            
    return resultados