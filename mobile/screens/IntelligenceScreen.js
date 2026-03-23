import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, StyleSheet, ActivityIndicator } from 'react-native';
import Constants from 'expo-constants';

const API = Constants.expoConfig?.extra?.dashboardApiUrl || 'http://localhost:8005';

export default function IntelligenceScreen() {
  const [insights, setInsights] = useState([]);
  const [meta, setMeta] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchInsights();
  }, []);

  async function fetchInsights() {
    try {
      const res = await fetch(`${API}/api/v1/intelligence`);
      const data = await res.json();
      setInsights(data.insights || []);
      setMeta(data.data_sources);
    } catch (e) {
      console.error('Intelligence fetch failed:', e);
    } finally {
      setLoading(false);
    }
  }

  const severityColor = (s) => ({ high: '#fc8181', medium: '#f6ad55', low: '#68d391' }[s] || '#718096');

  if (loading) return <View style={s.center}><ActivityIndicator color="#6c63ff" /></View>;

  return (
    <View style={s.container}>
      <Text style={s.title}>🧠 Deep Brain</Text>
      <Text style={s.subtitle}>Cross-app behavioral insights</Text>
      {meta && (
        <View style={s.metaBar}>
          <Text style={s.metaText}>Habits: {meta.habits_analyzed}</Text>
          <Text style={s.metaText}>Sessions: {meta.screen_sessions}</Text>
          <Text style={s.metaText}>Journal: {meta.journal_entries}</Text>
        </View>
      )}
      {insights.length === 0 && (
        <Text style={s.empty}>🎉 No negative correlations found. Your habits are strong!</Text>
      )}
      <FlatList
        data={insights}
        keyExtractor={(item, i) => `${i}-${item.habit}`}
        renderItem={({ item }) => (
          <View style={[s.card, { borderLeftColor: severityColor(item.severity), borderLeftWidth: 3 }]}>
            <Text style={s.insightText}>{item.insight}</Text>
            <Text style={s.confidence}>Confidence: {Math.round(item.confidence * 100)}%</Text>
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
  title: { color: '#e2e8f0', fontSize: 26, fontWeight: '700' },
  subtitle: { color: '#718096', fontSize: 14, marginBottom: 16 },
  metaBar: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 12,
    backgroundColor: 'rgba(108,99,255,0.15)', borderRadius: 8, padding: 10 },
  metaText: { color: '#a0aec0', fontSize: 12 },
  card: { backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: 12, padding: 14,
    marginBottom: 10, borderWidth: 1, borderColor: 'rgba(255,255,255,0.08)' },
  insightText: { color: '#e2e8f0', fontSize: 14, lineHeight: 22 },
  confidence: { color: '#718096', fontSize: 11, marginTop: 6 },
  empty: { color: '#68d391', textAlign: 'center', marginTop: 40, fontSize: 15 },
});
