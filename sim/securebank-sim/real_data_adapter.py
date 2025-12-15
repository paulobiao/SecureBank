"""
real_data_adapter.py

Adaptador para converter datasets reais de fraude bancária para o formato
usado pela simulação SecureBank™.

Permite executar os PDPs (baseline e SecureBank) sobre dados reais,
possibilitando validação empírica dos resultados da simulação.
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any
from collections import defaultdict


class RealDataAdapter:
    """
    Adaptador que converte dados reais de fraude bancária para o formato
    esperado pelos PDPs da simulação SecureBank™.
    """
    
    def __init__(self, dataset_path: str = None):
        """
        Inicializa o adaptador.
        
        Args:
            dataset_path: Caminho para o dataset real (CSV ou JSON)
        """
        self.dataset_path = dataset_path
        self.df = None
        self.users = {}
        self.devices = {}
        self.user_to_devices = defaultdict(list)
        
    def load_real_dataset(self, dataset_path: str = None) -> pd.DataFrame:
        """
        Carrega dataset real de transações bancárias.
        
        Args:
            dataset_path: Caminho para o arquivo (CSV ou JSON)
            
        Returns:
            DataFrame com as transações
        """
        if dataset_path:
            self.dataset_path = dataset_path
            
        if not self.dataset_path:
            raise ValueError("dataset_path must be provided")
            
        path = Path(self.dataset_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Dataset not found: {self.dataset_path}")
        
        # Carrega baseado na extensão
        if path.suffix == '.csv':
            self.df = pd.read_csv(self.dataset_path)
        elif path.suffix == '.json':
            self.df = pd.read_json(self.dataset_path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
        
        print(f"✓ Loaded {len(self.df)} transactions from {path.name}")
        print(f"  - Fraud rate: {self.df['IsFraud'].mean()*100:.2f}%")
        print(f"  - Date range: {self.df['Timestamp'].min()} to {self.df['Timestamp'].max()}")
        
        return self.df
    
    def extract_user_profiles(self) -> Dict[str, Dict[str, Any]]:
        """
        Extrai perfis de usuários do dataset real.
        
        Returns:
            Dict mapeando UserID para perfil do usuário
        """
        if self.df is None:
            raise ValueError("Dataset not loaded. Call load_real_dataset() first.")
        
        unique_users = self.df['UserID'].unique()
        
        for user_id in unique_users:
            user_transactions = self.df[self.df['UserID'] == user_id]
            
            # Extrai tipo de usuário e calcula base_risk
            user_type = user_transactions['UserType'].iloc[0]
            
            # Base risk baseado em:
            # - Taxa de fraude histórica do usuário
            # - Tipo de usuário
            # - Volatilidade das transações
            fraud_rate = user_transactions['IsFraud'].mean()
            amount_std = user_transactions['Amount'].std()
            amount_mean = user_transactions['Amount'].mean()
            volatility = amount_std / amount_mean if amount_mean > 0 else 0
            
            # Calcula base_risk
            base_risk = min(0.9, max(0.05, 
                fraud_rate * 0.5 + 
                volatility * 0.3 + 
                {'retail_customer': 0.2, 'business_customer': 0.15, 
                 'employee': 0.1, 'corporate': 0.05}.get(user_type, 0.2)
            ))
            
            # Extrai ID numérico do UserID (formato: "U000000")
            user_id_num = int(user_id[1:])
            
            self.users[user_id] = {
                'id': user_id_num,
                'user_id_str': user_id,
                'type': user_type,
                'base_risk': base_risk,
                'historical_fraud_rate': fraud_rate,
                'avg_amount': amount_mean,
                'amount_volatility': volatility,
                'total_transactions': len(user_transactions),
            }
        
        print(f"✓ Extracted {len(self.users)} user profiles")
        return self.users
    
    def extract_device_profiles(self) -> Dict[str, Dict[str, Any]]:
        """
        Extrai perfis de dispositivos do dataset real.
        
        Returns:
            Dict mapeando DeviceID para perfil do dispositivo
        """
        if self.df is None:
            raise ValueError("Dataset not loaded. Call load_real_dataset() first.")
        
        if not self.users:
            self.extract_user_profiles()
        
        unique_devices = self.df['DeviceID'].unique()
        
        for device_id in unique_devices:
            device_transactions = self.df[self.df['DeviceID'] == device_id]
            
            # Identifica o dono do dispositivo (usuário mais frequente)
            owner_id = device_transactions['UserID'].mode()[0]
            owner_id_num = self.users[owner_id]['id']
            
            # Dispositivo comprometido se taxa de fraude > threshold
            fraud_rate = device_transactions['IsFraud'].mean()
            is_compromised = fraud_rate > 0.15  # 15% threshold
            
            # Extrai ID numérico do DeviceID
            device_id_num = int(device_id[1:])
            
            self.devices[device_id] = {
                'id': device_id_num,
                'device_id_str': device_id,
                'owner_id': owner_id_num,
                'owner_id_str': owner_id,
                'compromised': is_compromised,
                'fraud_rate': fraud_rate,
                'device_type': device_transactions['DeviceType'].iloc[0],
                'os': device_transactions['OS'].iloc[0],
                'total_transactions': len(device_transactions),
            }
            
            # Mapeia usuário para dispositivos
            self.user_to_devices[owner_id_num].append(device_id_num)
        
        print(f"✓ Extracted {len(self.devices)} device profiles")
        print(f"  - Compromised devices: {sum(1 for d in self.devices.values() if d['compromised'])}")
        
        return self.devices
    
    def identify_attack_patterns(self) -> Dict[str, Any]:
        """
        Identifica padrões de ataque no dataset real.
        
        Returns:
            Dict com estatísticas de ataques por cenário
        """
        if self.df is None:
            raise ValueError("Dataset not loaded. Call load_real_dataset() first.")
        
        fraud_df = self.df[self.df['IsFraud'] == 1]
        
        attack_stats = {
            'total_attacks': len(fraud_df),
            'attack_rate': len(fraud_df) / len(self.df),
            'scenarios': {},
            'characteristics': {}
        }
        
        # Estatísticas por cenário
        if 'FraudScenario' in fraud_df.columns:
            scenario_counts = fraud_df['FraudScenario'].value_counts().to_dict()
            for scenario, count in scenario_counts.items():
                attack_stats['scenarios'][scenario] = {
                    'count': count,
                    'percentage': count / len(fraud_df) * 100
                }
        
        # Características das transações fraudulentas
        attack_stats['characteristics'] = {
            'avg_amount': float(fraud_df['Amount'].mean()),
            'median_amount': float(fraud_df['Amount'].median()),
            'max_amount': float(fraud_df['Amount'].max()),
            'geo_distribution': fraud_df['GeoLocation'].value_counts().head(10).to_dict(),
            'channel_distribution': fraud_df['Channel'].value_counts().to_dict(),
            'service_distribution': fraud_df['Service'].value_counts().to_dict(),
            'hour_distribution': fraud_df['HourOfDay'].value_counts().sort_index().to_dict(),
        }
        
        print(f"✓ Identified {attack_stats['total_attacks']} attacks ({attack_stats['attack_rate']*100:.2f}%)")
        
        return attack_stats
    
    def map_to_simulation_format(self) -> List[Dict[str, Any]]:
        """
        Converte dataset real para o formato esperado pela simulação.
        
        Cada evento no formato da simulação contém:
        - user: dict com dados do usuário
        - device: dict com dados do dispositivo
        - tx: dict com dados da transação
        - ctx: dict com contexto (geo, hora, canal)
        - is_attack: bool indicando se é fraude
        - scenario: ID do cenário de ataque (se aplicável)
        
        Returns:
            Lista de eventos no formato da simulação
        """
        if self.df is None:
            raise ValueError("Dataset not loaded. Call load_real_dataset() first.")
        
        if not self.users:
            self.extract_user_profiles()
        
        if not self.devices:
            self.extract_device_profiles()
        
        events = []
        
        for idx, row in self.df.iterrows():
            user_id_str = row['UserID']
            device_id_str = row['DeviceID']
            
            # Busca perfis de usuário e dispositivo
            user_profile = self.users[user_id_str]
            device_profile = self.devices[device_id_str]
            
            # Monta usuário (formato da simulação)
            user = {
                'id': user_profile['id'],
                'type': user_profile['type'],
                'base_risk': user_profile['base_risk'],
            }
            
            # Monta dispositivo (formato da simulação)
            device = {
                'id': device_profile['id'],
                'owner_id': device_profile['owner_id'],
                'compromised': device_profile['compromised'],
            }
            
            # Monta transação
            tx = {
                'user_id': user_profile['id'],
                'service': row['Service'],
                'amount': float(row['Amount']),
                'is_attack': bool(row['IsFraud']),
                'scenario': self._map_scenario_to_id(row.get('FraudScenario')),
            }
            
            # Monta contexto
            ctx = {
                'geo': row['GeoLocation'],
                'hour': int(row['HourOfDay']),
                'channel': row['Channel'],
            }
            
            # Evento completo
            event = {
                'user': user,
                'device': device,
                'tx': tx,
                'ctx': ctx,
                'is_attack': bool(row['IsFraud']),
                'scenario': self._map_scenario_to_id(row.get('FraudScenario')),
            }
            
            events.append(event)
        
        print(f"✓ Mapped {len(events)} transactions to simulation format")
        
        return events
    
    def _map_scenario_to_id(self, scenario_name: str) -> int:
        """
        Mapeia nome do cenário de fraude para ID usado na simulação.
        
        Args:
            scenario_name: Nome do cenário no dataset real
            
        Returns:
            ID do cenário (1-5) ou None se não for ataque
        """
        if scenario_name is None or pd.isna(scenario_name):
            return None
        
        # Mapeia nomes para IDs da simulação
        scenario_mapping = {
            'credential_compromise': 1,
            'insider_lateral_movement': 2,
            'api_abuse': 3,
            'money_laundering': 4,
            'session_hijacking': 5,
            # Cenários adicionais do dataset sintético
            'card_theft': 1,  # Similar a credential compromise
            'synthetic_identity': 2,  # Similar a insider lateral movement
        }
        
        return scenario_mapping.get(scenario_name)
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Retorna estatísticas resumidas do dataset real.
        
        Returns:
            Dict com estatísticas descritivas
        """
        if self.df is None:
            raise ValueError("Dataset not loaded. Call load_real_dataset() first.")
        
        return {
            'total_transactions': len(self.df),
            'total_users': len(self.df['UserID'].unique()),
            'total_devices': len(self.df['DeviceID'].unique()),
            'fraud_transactions': int(self.df['IsFraud'].sum()),
            'fraud_rate': float(self.df['IsFraud'].mean()),
            'date_range': {
                'start': str(self.df['Timestamp'].min()),
                'end': str(self.df['Timestamp'].max()),
            },
            'amount_stats': {
                'mean': float(self.df['Amount'].mean()),
                'median': float(self.df['Amount'].median()),
                'std': float(self.df['Amount'].std()),
                'min': float(self.df['Amount'].min()),
                'max': float(self.df['Amount'].max()),
            },
            'services': self.df['Service'].value_counts().to_dict(),
            'channels': self.df['Channel'].value_counts().to_dict(),
            'geolocations': self.df['GeoLocation'].value_counts().head(10).to_dict(),
        }


def load_and_adapt_real_data(dataset_path: str) -> Tuple[List[Dict], Dict[str, Any]]:
    """
    Função auxiliar para carregar e adaptar dados reais em uma única chamada.
    
    Args:
        dataset_path: Caminho para o dataset real
        
    Returns:
        Tupla (eventos_adaptados, estatísticas)
    """
    adapter = RealDataAdapter(dataset_path)
    
    # Carrega e processa
    adapter.load_real_dataset()
    adapter.extract_user_profiles()
    adapter.extract_device_profiles()
    attack_stats = adapter.identify_attack_patterns()
    
    # Converte para formato da simulação
    events = adapter.map_to_simulation_format()
    
    # Estatísticas
    stats = adapter.get_summary_statistics()
    stats['attack_patterns'] = attack_stats
    
    return events, stats


# CLI para testar o adaptador
if __name__ == '__main__':
    import sys
    
    # Caminho padrão do dataset
    default_dataset = '/home/ubuntu/securebank_analysis/securebank-sim/data/real_dataset/fraud_transactions.csv'
    
    dataset_path = sys.argv[1] if len(sys.argv) > 1 else default_dataset
    
    print("=" * 70)
    print("Real Data Adapter - Testing")
    print("=" * 70)
    print()
    
    # Testa o adaptador
    events, stats = load_and_adapt_real_data(dataset_path)
    
    print()
    print("=" * 70)
    print("Adaptation Complete!")
    print("=" * 70)
    print()
    print(f"Total events: {len(events)}")
    print(f"Fraud rate: {stats['fraud_rate']*100:.2f}%")
    print()
    
    # Mostra exemplos
    print("Sample events (first 3):")
    for i, event in enumerate(events[:3]):
        print(f"\n--- Event {i+1} ---")
        print(f"User: {event['user']['id']} ({event['user']['type']}, risk={event['user']['base_risk']:.3f})")
        print(f"Device: {event['device']['id']} (compromised={event['device']['compromised']})")
        print(f"Transaction: ${event['tx']['amount']:.2f} via {event['tx']['service']}")
        print(f"Context: {event['ctx']['geo']}, hour={event['ctx']['hour']}, channel={event['ctx']['channel']}")
        print(f"Is Attack: {event['is_attack']}")
    
    # Salva estatísticas
    output_path = Path(dataset_path).parent / 'adaptation_stats.json'
    with open(output_path, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"\n✓ Statistics saved to: {output_path}")
