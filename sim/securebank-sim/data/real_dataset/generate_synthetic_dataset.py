#!/usr/bin/env python3
"""
Gerador de Dataset Sintético Realista de Fraude Bancária

Baseado em características de datasets públicos conhecidos:
- IEEE-CIS Fraud Detection
- Credit Card Fraud Detection (Kaggle)
- European Credit Card Dataset

Este dataset sintético mantém características estatísticas realistas:
- Desbalanceamento (fraude ~2-5% das transações)
- Distribuições realistas de valores
- Padrões temporais e geográficos
- Atributos de dispositivos e identidades
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import random

# Seed para reprodutibilidade
np.random.seed(42)
random.seed(42)

def generate_realistic_fraud_dataset(num_transactions=10000, fraud_rate=0.035):
    """
    Gera dataset sintético realista de transações bancárias.
    
    Args:
        num_transactions: Número total de transações
        fraud_rate: Taxa de fraude (default: 3.5% similar a datasets reais)
    
    Returns:
        DataFrame com transações
    """
    
    # Número de usuários e dispositivos
    num_users = int(num_transactions * 0.1)  # 10% do total de transações
    num_devices = int(num_users * 1.6)  # Média de 1.6 dispositivos por usuário
    num_cards = int(num_users * 1.3)  # Média de 1.3 cartões por usuário
    
    # IDs de usuários, cartões e dispositivos
    user_ids = np.arange(num_users)
    card_ids = np.arange(num_cards)
    device_ids = np.arange(num_devices)
    
    # Tipos de usuários e seus perfis de risco
    user_types = np.random.choice(
        ['retail_customer', 'business_customer', 'employee', 'corporate'],
        size=num_users,
        p=[0.70, 0.15, 0.10, 0.05]
    )
    
    # Base risk por tipo de usuário
    user_base_risk = {
        'retail_customer': np.random.uniform(0.1, 0.4, num_users),
        'business_customer': np.random.uniform(0.05, 0.3, num_users),
        'employee': np.random.uniform(0.03, 0.25, num_users),
        'corporate': np.random.uniform(0.02, 0.20, num_users),
    }
    
    # Mapeia usuários para dispositivos
    user_to_devices = {}
    for uid in user_ids:
        # Cada usuário tem entre 1 e 4 dispositivos
        num_dev = np.random.choice([1, 2, 3, 4], p=[0.5, 0.3, 0.15, 0.05])
        user_to_devices[uid] = np.random.choice(device_ids, size=num_dev, replace=False).tolist()
    
    # Tipos de serviços bancários
    services = [
        'payments', 'settlement', 'risk_analytics', 
        'aml', 'customer_identity', 'wire_transfer',
        'credit_card', 'debit_card', 'mobile_payment'
    ]
    
    # Probabilidades de cada serviço
    service_probs = [0.25, 0.10, 0.05, 0.08, 0.07, 0.12, 0.18, 0.10, 0.05]
    
    # Canais de acesso
    channels = ['web', 'mobile', 'api', 'atm', 'pos']
    channel_probs = [0.30, 0.35, 0.15, 0.10, 0.10]
    
    # Geolocalizações (países e cidades)
    geo_locations = [
        'US-NY', 'US-CA', 'US-FL', 'US-TX', 'US-IL',
        'BR-SP', 'BR-RJ', 'BR-MG',
        'GB-LND', 'DE-BER', 'FR-PAR',
        'RU-MOS', 'CN-BEI', 'NG-LGS', 'IN-MUM'
    ]
    
    # Probabilidades de localização (locais comuns vs. suspeitos)
    geo_probs_normal = np.array([
        0.20, 0.15, 0.12, 0.10, 0.08,  # US
        0.10, 0.08, 0.05,  # BR
        0.04, 0.03, 0.03,  # Europa
        0.01, 0.005, 0.005, 0.01  # Locais suspeitos
    ])
    geo_probs_normal = geo_probs_normal / geo_probs_normal.sum()
    
    geo_probs_fraud = np.array([
        0.05, 0.05, 0.05, 0.03, 0.02,  # US (reduzido)
        0.03, 0.02, 0.02,  # BR (reduzido)
        0.05, 0.05, 0.03,  # Europa
        0.25, 0.20, 0.15, 0.05  # Locais suspeitos (aumentado)
    ])
    geo_probs_fraud = geo_probs_fraud / geo_probs_fraud.sum()
    
    # Timestamp inicial
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    
    # Lista para armazenar transações
    transactions = []
    
    # Número de transações fraudulentas
    num_fraud = int(num_transactions * fraud_rate)
    fraud_indices = set(np.random.choice(num_transactions, size=num_fraud, replace=False))
    
    # Tipos de fraude (baseado nos cenários do SecureBank)
    fraud_scenarios = [
        'credential_compromise',
        'insider_lateral_movement',
        'api_abuse',
        'money_laundering',
        'session_hijacking',
        'card_theft',
        'synthetic_identity'
    ]
    
    for i in range(num_transactions):
        is_fraud = i in fraud_indices
        
        # Seleciona usuário
        user_id = np.random.choice(user_ids)
        user_type = user_types[user_id]
        
        # Seleciona dispositivo do usuário
        device_id = np.random.choice(user_to_devices[user_id])
        
        # Seleciona cartão
        card_id = np.random.choice(card_ids)
        
        # Timestamp (distribuição realista ao longo do tempo)
        # Mais transações durante horário comercial
        hours_offset = np.random.exponential(scale=2.0) * 24 * 30  # ~2 meses
        hour_probs = np.array([
            0.01, 0.01, 0.01, 0.01, 0.01, 0.02,  # 0-5h (madrugada)
            0.03, 0.04, 0.05, 0.06, 0.07, 0.08,  # 6-11h (manhã)
            0.08, 0.08, 0.08, 0.07, 0.06, 0.05,  # 12-17h (tarde)
            0.05, 0.04, 0.03, 0.02, 0.02, 0.01   # 18-23h (noite)
        ])
        hour_probs = hour_probs / hour_probs.sum()  # Normaliza para somar 1.0
        hour_of_day = np.random.choice(24, p=hour_probs)
        timestamp = start_date + timedelta(hours=hours_offset + hour_of_day)
        
        # Valor da transação (distribuição log-normal)
        if not is_fraud:
            # Transações normais: valores menores
            amount = np.random.lognormal(mean=4.5, sigma=1.2)
            amount = max(5.0, min(amount, 50000.0))  # entre $5 e $50k
        else:
            # Transações fraudulentas: valores maiores ou padrões específicos
            fraud_type = np.random.choice(['high_value', 'structured', 'normal'])
            if fraud_type == 'high_value':
                amount = np.random.lognormal(mean=8.0, sigma=0.8)
                amount = max(5000.0, min(amount, 500000.0))
            elif fraud_type == 'structured':
                # Estruturação (valores logo abaixo de thresholds)
                amount = np.random.uniform(9000, 9999)
            else:
                amount = np.random.lognormal(mean=5.5, sigma=1.0)
                amount = max(100.0, min(amount, 20000.0))
        
        # Serviço
        service = np.random.choice(services, p=service_probs)
        
        # Canal
        if not is_fraud:
            channel = np.random.choice(channels, p=channel_probs)
        else:
            # Fraudes têm maior probabilidade de API abuse
            channel = np.random.choice(channels, p=[0.15, 0.20, 0.40, 0.15, 0.10])
        
        # Geolocalização
        if not is_fraud:
            geo = np.random.choice(geo_locations, p=geo_probs_normal)
        else:
            geo = np.random.choice(geo_locations, p=geo_probs_fraud)
        
        # Cenário de fraude
        fraud_scenario = None
        if is_fraud:
            fraud_scenario = np.random.choice(fraud_scenarios)
        
        # Atributos adicionais (característicos de datasets reais)
        transaction = {
            'TransactionID': f'T{i:08d}',
            'Timestamp': timestamp.isoformat(),
            'Amount': round(amount, 2),
            'UserID': f'U{user_id:06d}',
            'UserType': user_type,
            'CardID': f'C{card_id:06d}',
            'DeviceID': f'D{device_id:06d}',
            'Service': service,
            'Channel': channel,
            'GeoLocation': geo,
            'HourOfDay': hour_of_day,
            'DayOfWeek': timestamp.weekday(),
            'IsFraud': int(is_fraud),
            'FraudScenario': fraud_scenario if is_fraud else None,
            
            # Atributos adicionais realistas
            'DeviceType': np.random.choice(['mobile', 'desktop', 'tablet'], p=[0.5, 0.4, 0.1]),
            'OS': np.random.choice(['iOS', 'Android', 'Windows', 'MacOS', 'Linux'], p=[0.25, 0.30, 0.25, 0.15, 0.05]),
            'Browser': np.random.choice(['Chrome', 'Safari', 'Firefox', 'Edge', 'Other'], p=[0.45, 0.25, 0.15, 0.10, 0.05]),
            'IPCountry': geo.split('-')[0],
            
            # Velocidade de transação (transações nas últimas 24h)
            'TransactionVelocity24h': np.random.poisson(3) if not is_fraud else np.random.poisson(15),
            
            # Distância da última transação (em km)
            'DistanceFromLastTx': np.random.exponential(50) if not is_fraud else np.random.exponential(2000),
            
            # Indicadores de risco
            'IsNewDevice': int(np.random.random() < 0.1) if not is_fraud else int(np.random.random() < 0.6),
            'IsInternational': int(geo not in ['US-NY', 'US-CA', 'US-FL', 'US-TX', 'US-IL']),
            'IsHighRiskMerchant': int(is_fraud and np.random.random() < 0.4),
        }
        
        transactions.append(transaction)
    
    # Converte para DataFrame
    df = pd.DataFrame(transactions)
    
    # Ordena por timestamp
    df = df.sort_values('Timestamp').reset_index(drop=True)
    
    return df


def save_dataset(df, output_dir='/home/ubuntu/securebank_analysis/securebank-sim/data/real_dataset'):
    """Salva o dataset em múltiplos formatos."""
    
    # CSV
    csv_path = f'{output_dir}/fraud_transactions.csv'
    df.to_csv(csv_path, index=False)
    print(f"✓ Dataset saved to: {csv_path}")
    
    # JSON (para facilitar importação)
    json_path = f'{output_dir}/fraud_transactions.json'
    df.to_json(json_path, orient='records', indent=2)
    print(f"✓ Dataset saved to: {json_path}")
    
    # Estatísticas do dataset
    stats = {
        'total_transactions': len(df),
        'fraud_transactions': int(df['IsFraud'].sum()),
        'fraud_rate': float(df['IsFraud'].mean()),
        'date_range': {
            'start': df['Timestamp'].min(),
            'end': df['Timestamp'].max()
        },
        'amount_statistics': {
            'mean': float(df['Amount'].mean()),
            'median': float(df['Amount'].median()),
            'std': float(df['Amount'].std()),
            'min': float(df['Amount'].min()),
            'max': float(df['Amount'].max())
        },
        'fraud_scenarios': df[df['IsFraud'] == 1]['FraudScenario'].value_counts().to_dict(),
        'services': df['Service'].value_counts().to_dict(),
        'channels': df['Channel'].value_counts().to_dict(),
        'unique_users': len(df['UserID'].unique()),
        'unique_devices': len(df['DeviceID'].unique()),
        'unique_cards': len(df['CardID'].unique()),
    }
    
    stats_path = f'{output_dir}/dataset_statistics.json'
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"✓ Statistics saved to: {stats_path}")
    
    # Relatório descritivo
    report = f"""
# Synthetic Fraud Dataset - Statistical Report

## Dataset Overview
- **Total Transactions:** {stats['total_transactions']:,}
- **Fraudulent Transactions:** {stats['fraud_transactions']:,} ({stats['fraud_rate']*100:.2f}%)
- **Legitimate Transactions:** {stats['total_transactions'] - stats['fraud_transactions']:,} ({(1-stats['fraud_rate'])*100:.2f}%)

## Temporal Coverage
- **Start Date:** {stats['date_range']['start']}
- **End Date:** {stats['date_range']['end']}

## Transaction Amounts
- **Mean:** ${stats['amount_statistics']['mean']:,.2f}
- **Median:** ${stats['amount_statistics']['median']:,.2f}
- **Std Dev:** ${stats['amount_statistics']['std']:,.2f}
- **Range:** ${stats['amount_statistics']['min']:,.2f} - ${stats['amount_statistics']['max']:,.2f}

## Entities
- **Unique Users:** {stats['unique_users']:,}
- **Unique Devices:** {stats['unique_devices']:,}
- **Unique Cards:** {stats['unique_cards']:,}

## Fraud Scenarios Distribution
"""
    for scenario, count in sorted(stats['fraud_scenarios'].items(), key=lambda x: x[1], reverse=True):
        report += f"- **{scenario}:** {count} ({count/stats['fraud_transactions']*100:.1f}%)\n"
    
    report += "\n## Service Distribution\n"
    for service, count in sorted(stats['services'].items(), key=lambda x: x[1], reverse=True):
        report += f"- **{service}:** {count} ({count/stats['total_transactions']*100:.1f}%)\n"
    
    report += "\n## Channel Distribution\n"
    for channel, count in sorted(stats['channels'].items(), key=lambda x: x[1], reverse=True):
        report += f"- **{channel}:** {count} ({count/stats['total_transactions']*100:.1f}%)\n"
    
    report_path = f'{output_dir}/dataset_report.md'
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"✓ Report saved to: {report_path}")
    
    return stats


if __name__ == '__main__':
    print("=" * 70)
    print("Generating Synthetic Fraud Detection Dataset")
    print("=" * 70)
    print("\nBased on characteristics of public datasets:")
    print("- IEEE-CIS Fraud Detection")
    print("- Credit Card Fraud Detection")
    print("- European Credit Card Dataset")
    print()
    
    # Gera dataset com 10.000 transações (3.5% de fraude)
    df = generate_realistic_fraud_dataset(num_transactions=10000, fraud_rate=0.035)
    
    print(f"\nDataset generated: {len(df)} transactions")
    print(f"Fraud rate: {df['IsFraud'].mean()*100:.2f}%")
    print(f"Fraud transactions: {df['IsFraud'].sum()}")
    print()
    
    # Salva dataset
    stats = save_dataset(df)
    
    print("\n" + "=" * 70)
    print("Dataset Generation Complete!")
    print("=" * 70)
    
    # Preview
    print("\n### Sample Transactions (first 5):")
    print(df.head().to_string())
    
    print("\n### Fraud Sample (first 3 fraud cases):")
    fraud_df = df[df['IsFraud'] == 1].head(3)
    if len(fraud_df) > 0:
        print(fraud_df.to_string())
