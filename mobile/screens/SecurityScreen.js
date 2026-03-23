import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, StyleSheet, ActivityIndicator } from 'react-native';
import Constants from 'expo-constants';

const API = Constants.expoConfig?.extra?.visionApiUrl || 'http://localhost:8003';

export default function SecurityScreen() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/api/v1/vision/dashboard`)
      .then(r => r.json()).then(setDashboard)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <View style={s.center}><ActivityIndicator color="#6c63ff" /></View>;

  return (
    <View style={s.container}>
      <Text style={s.title}>🔍 Visual Intelligence</Text>
      <View style={s.statsGrid}>
        <View style={s.statBox}>
          <Text style={s.statValue}>{dashboard?.stats?.total_events ?? 0}</Text>
          <Text style={s.statLabel}>Events Detected</Text>
        </View>
        <View style={s.statBox}>
          <Text style={s.statValue}>{dashboard?.stats?.total_alerts ?? 0}</Text>
          <Text style={[s.statLabel, { color: '#fc8181' }]}>⚡ Alerts</Text>
        </View>
      </View>
      <Text style={s.sectionTitle}>Recent Events</Text>
      <FlatList
        data={dashboard?.events?.slice(0, 10) ?? []}
        keyExtractor={(item, i) => `${i}-${item.timestamp}`}
        renderItem={({ item }) => (
          <View style={s.event}>
            <Text style={s.label}>{item.label}</Text>
            <Text style={s.ts}>{new Date(item.timestamp).toLocaleTimeString()}</Text>
          </View>
        )}
        contentContainerStyle={{ paddingBottom: 80 }}
      />
    </View>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0a1a', padding: 16, paddingTop: 60 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#0a0a1a' },
  title: { color: '#e2e8f0', fontSize: 26, fontWeight: '700', marginBottom: 16 },
  statsGrid: { flexDirection: 'row', gap: 12, marginBottom: 20 },
  statBox: { flex: 1, backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: 12, padding: 16, alignItems: 'center' },
  statValue: { color: '#e2e8f0', fontSize: 36, fontWeight: '700' },
  statLabel: { color: '#718096', fontSize: 12, marginTop: 4 },
  sectionTitle: { color: '#a0aec0', fontSize: 13, fontWeight: '600', marginBottom: 8, textTransform: 'uppercase', letterSpacing: 1 },
  event: { backgroundColor: 'rgba(255,255,255,0.04)', borderRadius: 8, padding: 12, marginBottom: 6, flexDirection: 'row', justifyContent: 'space-between' },
  label: { color: '#e2e8f0', fontSize: 14, textTransform: 'capitalize' },
  ts: { color: '#718096', fontSize: 12 },
});
